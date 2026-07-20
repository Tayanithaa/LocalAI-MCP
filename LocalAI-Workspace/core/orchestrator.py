"""
Orchestrator: runs the plan -> execute -> observe loop until the planner
emits a final_answer or the step budget runs out. This is the piece that
turns "single tool call" into "multi-step execution" (e.g. the resume-email
example in the project brief: locate file -> read file -> [send] -> confirm).
"""
from __future__ import annotations

from config.settings import settings
from config.logger import get_logger
from core.planner import Planner, PlanStep
from ollama.client import OllamaClient
from registry.tool_registry import ToolRegistry

log = get_logger("core.orchestrator")


class Orchestrator:
    def __init__(self, registry: ToolRegistry, client: OllamaClient | None = None):
        self.registry = registry
        self.client = client or OllamaClient()
        self.planner = Planner(self.client, registry.describe_tools_for_prompt())

    async def run(self, user_query: str, *, max_steps: int | None = None) -> str:
        max_steps = max_steps or settings.max_planner_steps
        transcript: list[dict[str, str]] = [{"role": "user", "content": user_query}]

        for step_num in range(1, max_steps + 1):
            step: PlanStep = await self.planner.next_step(transcript)
            log.info(f"[step {step_num}] {step.action}: {step.tool or step.answer or step.raw}")

            if step.action == "invalid":
                transcript.append({
                    "role": "user",
                    "content": (
                        "Your last response was not valid. Respond with ONLY one JSON "
                        'object: either {"action": "call_tool", "tool": "<server.tool>", '
                        '"arguments": {...}} or {"action": "final_answer", "answer": "..."}. '
                        "Both 'tool' and 'answer' must be non-empty when used."
                    ),
                })
                continue

            if step.action == "final_answer":
                return step.answer or "(no answer produced)"

            # action == "call_tool"
            if not step.tool:
                transcript.append({"role": "assistant",
                                    "content": "Error: no tool specified. Retrying."})
                continue

            observation = await self.registry.call(step.tool, step.arguments or {})
            transcript.append({
                "role": "assistant",
                "content": f'Called {step.tool}({step.arguments}) -> {observation}',
            })

        return (
            "I hit the step limit before finishing. Here's what I found so far:\n"
            + "\n".join(m["content"] for m in transcript[1:])
        )
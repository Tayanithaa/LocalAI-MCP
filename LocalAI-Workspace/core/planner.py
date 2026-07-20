"""
Planner. Not fine-tuned function calling -- plain local models like Llama
3.1 via Ollama don't reliably support that, so instead we constrain output
with a strict JSON-only system prompt and Ollama's `format: json` mode, then
validate/parse defensively. This is the same trick most local-first agent
frameworks use under the hood.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from ollama.client import OllamaClient
from config.logger import get_logger

log = get_logger("core.planner")

SYSTEM_TEMPLATE = """You are the planning module of a local AI assistant.
You decide ONE next action at a time. You have access to these tools:

{tool_list}

Given the user's request and the conversation so far (including any prior
tool results), respond with ONLY a JSON object, no prose, no markdown fences,
matching exactly one of these two shapes:

1. To call a tool:
{{"action": "call_tool", "tool": "<server.tool_name>", "arguments": {{...}}}}

2. To answer the user directly because you have enough information:
{{"action": "final_answer", "answer": "<your answer to the user>"}}

Rules:
- Only use tool names exactly as listed above. Tool names always contain a
  dot: "<server>.<tool>", e.g. "calendar.list_events". Never call just the
  server name ("calendar") on its own -- that is not a valid tool name.
- Prefer final_answer as soon as you have enough information to respond.
- If a tool result already answers the request, do not call another tool.

Worked example:
User: "what's on my calendar tomorrow?"
Your response: {{"action": "call_tool", "tool": "calendar.list_events", "arguments": {{"days_ahead": 1}}}}
"""


@dataclass
class PlanStep:
    action: Literal["call_tool", "final_answer", "invalid"]
    tool: str | None = None
    arguments: dict[str, Any] | None = None
    answer: str | None = None
    raw: str | None = None


class Planner:
    def __init__(self, client: OllamaClient, tool_description_block: str):
        self.client = client
        self.system_prompt = SYSTEM_TEMPLATE.format(tool_list=tool_description_block)

    async def next_step(self, transcript: list[dict[str, str]]) -> PlanStep:
        messages = [{"role": "system", "content": self.system_prompt}, *transcript]
        raw = await self.client.chat(messages, json_mode=True, temperature=0.1)
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> PlanStep:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            log.warning(f"Planner returned non-JSON: {raw[:200]}")
            return PlanStep(action="invalid", raw=raw)

        action = data.get("action")
        if action == "call_tool" and data.get("tool"):
            return PlanStep(
                action="call_tool",
                tool=data.get("tool"),
                arguments=data.get("arguments") or {},
            )
        if action == "final_answer" and data.get("answer"):
            return PlanStep(action="final_answer", answer=data.get("answer", ""))

        log.warning(f"Planner returned unusable action shape: {data}")
        return PlanStep(action="invalid", raw=raw)
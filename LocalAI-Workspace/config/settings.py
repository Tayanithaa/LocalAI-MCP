"""
Central config. Loads from environment variables (with .env fallback via
python-dotenv if present) so every module reads settings from one place
instead of scattering os.environ calls around the codebase.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv  # optional dependency
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    ollama_host: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.environ.get("OLLAMA_MODEL", "llama3.1")
    fs_sandbox_root: Path = field(
        default_factory=lambda: Path(
            os.environ.get("FS_SANDBOX_ROOT", "./sandbox")
        ).resolve()
    )
    max_planner_steps: int = int(os.environ.get("MAX_PLANNER_STEPS", "6"))
    request_timeout_seconds: float = float(os.environ.get("REQUEST_TIMEOUT", "60"))


settings = Settings()
settings.fs_sandbox_root.mkdir(parents=True, exist_ok=True)

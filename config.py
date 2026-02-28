from __future__ import annotations

import os
from typing import Literal, Optional, Dict

from dotenv import load_dotenv


# Load environment variables from a local .env if present
load_dotenv()


Provider = Literal["openai", "gemini", "none"]


def get_provider() -> Provider:
    provider = os.getenv("MODEL_PROVIDER", "none").strip().lower()
    if provider in ("openai", "gemini"):
        return provider  # type: ignore[return-value]
    return "none"  # type: ignore[return-value]


def get_api_keys() -> Dict[str, Optional[str]]:
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    }


def validate_keys() -> tuple[bool, str]:
    provider = get_provider()
    keys = get_api_keys()

    if provider == "openai":
        if not keys["OPENAI_API_KEY"]:
            return False, "OPENAI_API_KEY is not set."
    elif provider == "gemini":
        if not keys["GOOGLE_API_KEY"]:
            return False, "GOOGLE_API_KEY is not set."
    return True, "OK"


# AI-Assisted by Copilot: Simple env loader and validation helpers
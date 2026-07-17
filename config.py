"""Centralized configuration loaded once from the environment / .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Application settings, validated at startup."""

    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_openai_api_version: str
    azure_openai_api_key: str | None  # falls back to Azure AD auth when absent

    # GoDaddy
    godaddy_api_endpoint: str
    godaddy_api_key: str
    godaddy_api_secret: str
    max_usd_price: float

    # Azure Speech (optional)
    voice_on: bool
    azure_speech_key: str | None
    azure_speech_region: str | None

    @classmethod
    def load(cls) -> "Settings":
        missing = [
            name
            for name in (
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT",
                "GODADDY_API_ENDPOINT",
                "GODADDY_API_KEY",
                "GODADDY_API_SECRET",
            )
            if not os.environ.get(name)
        ]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        max_price_raw = os.environ.get("MAX_USD_PRICE")
        return cls(
            azure_openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_openai_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            azure_openai_api_version=os.environ.get(
                "AZURE_OPENAI_API_VERSION", "2024-10-21"
            ),
            azure_openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY") or None,
            godaddy_api_endpoint=os.environ["GODADDY_API_ENDPOINT"].rstrip("/"),
            godaddy_api_key=os.environ["GODADDY_API_KEY"],
            godaddy_api_secret=os.environ["GODADDY_API_SECRET"],
            max_usd_price=float(max_price_raw) if max_price_raw else float("inf"),
            voice_on=_as_bool(os.environ.get("VOICE_ON")),
            azure_speech_key=os.environ.get("AZURE_SPEECH_TTS_KEY") or None,
            azure_speech_region=os.environ.get("AZURE_SPEECH_TTS_REGION") or None,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.load()

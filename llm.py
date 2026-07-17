"""Azure OpenAI access, replacing the previous promptflow/.prompty layer."""
from __future__ import annotations

import logging
from functools import lru_cache

from openai import AzureOpenAI, OpenAI
from pydantic import ValidationError

from config import get_settings
from models import DomainSuggestions

logger = logging.getLogger(__name__)

FIND_DOMAINS_SYSTEM_PROMPT = (
    "You are an AI assistant that helps people brainstorm creative, available "
    "'.com' domain names. Use only 1 existing or made up word. Avoid the "
    "letters x, y and z. Always structure your response as a JSON object in "
    "the following format:\n"
    '{"domain_suggestions": [{"domain": "example.com"}, {"domain": "another.com"}]}'
)

EVALUATE_DOMAINS_SYSTEM_PROMPT = (
    "You are an AI assistant that helps people evaluate the best domain name: "
    "catchy for branding and easy to spell around the world. You are provided "
    "with a list of domains. Explain why by category with pros and cons, and "
    "scores. Spot if any are awkward or not safe for work. Make sure you "
    "consider the full list from start to finish."
)


def _bearer_token_provider():
    """Azure AD token provider for keyless auth (managed identity / az login)."""
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    logger.info("Using Azure AD credentials for Azure OpenAI")
    return get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )


@lru_cache(maxsize=1)
def _client() -> OpenAI | AzureOpenAI:
    settings = get_settings()
    endpoint = settings.azure_openai_endpoint

    # Azure AI Foundry / v1 endpoints expose an OpenAI-compatible surface at
    # `/openai/v1` and reject the `api-version` query parameter that the
    # AzureOpenAI client always appends, so use the plain OpenAI client there.
    if "/openai/v1" in endpoint or endpoint.rstrip("/").endswith("/v1"):
        base_url = endpoint.rstrip("/")
        if settings.azure_openai_api_key:
            return OpenAI(base_url=base_url, api_key=settings.azure_openai_api_key)
        provider = _bearer_token_provider()
        return OpenAI(base_url=base_url, api_key=provider())

    common = dict(
        azure_endpoint=endpoint,
        api_version=settings.azure_openai_api_version,
    )
    if settings.azure_openai_api_key:
        return AzureOpenAI(api_key=settings.azure_openai_api_key, **common)
    return AzureOpenAI(azure_ad_token_provider=_bearer_token_provider(), **common)


def find_domains(question: str) -> DomainSuggestions:
    """Ask the LLM for domain ideas and return validated suggestions."""
    settings = get_settings()
    response = _client().chat.completions.create(
        model=settings.azure_openai_deployment,
        temperature=1,
        max_completion_tokens=3000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": FIND_DOMAINS_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        return DomainSuggestions.model_validate_json(content)
    except ValidationError as exc:
        logger.error("LLM returned unexpected JSON: %s", exc)
        return DomainSuggestions()


def evaluate_domains(domains: str) -> str:
    """Have the LLM rank/critique a list of domains and return prose."""
    settings = get_settings()
    response = _client().chat.completions.create(
        model=settings.azure_openai_deployment,
        temperature=0,
        max_completion_tokens=16000,
        messages=[
            {"role": "system", "content": EVALUATE_DOMAINS_SYSTEM_PROMPT},
            {"role": "user", "content": domains},
        ],
    )
    return response.choices[0].message.content or ""

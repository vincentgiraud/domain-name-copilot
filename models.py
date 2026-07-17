"""Pydantic models describing the structured LLM output."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DomainSuggestion(BaseModel):
    domain: str


class DomainSuggestions(BaseModel):
    """Schema the LLM must return; validated on parse."""

    domain_suggestions: list[DomainSuggestion] = Field(default_factory=list)

    def names(self) -> list[str]:
        return [s.domain.strip().lower() for s in self.domain_suggestions if s.domain.strip()]

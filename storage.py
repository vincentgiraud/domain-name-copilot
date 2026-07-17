"""Persistence of discovered domains in a flat file."""
from __future__ import annotations

from pathlib import Path

DEFAULT_PATH = Path("domains.txt")


def load_domains(path: Path = DEFAULT_PATH) -> set[str]:
    """Return the set of domains already recorded."""
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return set()
    return {d.strip().lower() for d in content.split(",") if d.strip()}


def add_domain(domain: str, path: Path = DEFAULT_PATH) -> bool:
    """Append `domain` if new. Returns True if it was added."""
    existing = load_domains(path)
    if domain.lower() in existing:
        return False
    with path.open("a", encoding="utf-8") as f:
        f.write(domain + ", ")
    return True

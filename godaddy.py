"""GoDaddy domain-availability lookups."""
from __future__ import annotations

import logging

import requests

from config import get_settings

logger = logging.getLogger(__name__)

_VERIFY_URL = (
    "https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={domain}"
)


def check_domains_availability(domains: list[str]) -> dict[str, str]:
    """
    Check availability of domain names via the GoDaddy API.

    Returns a mapping of available domain -> price (or a verification URL when
    the domain is available but above the configured price threshold).
    """
    if not domains:
        return {}

    settings = get_settings()
    url = f"{settings.godaddy_api_endpoint}/v1/domains/available?checkType=FULL"
    headers = {
        "Authorization": f"sso-key {settings.godaddy_api_key}:{settings.godaddy_api_secret}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=domains, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Error while checking domain availability: %s", exc)
        return {}

    availability: dict[str, str] = {}
    for info in response.json().get("domains", []):
        domain = info["domain"]
        if not info.get("available"):
            continue
        # A non-definitive result is a fast heuristic guess, not a real check;
        # trusting it produces "available" domains that are in fact taken.
        if not info.get("definitive"):
            logger.warning(
                "Skipping %s: GoDaddy returned a non-definitive availability result",
                domain,
            )
            continue
        # GoDaddy prices are in micro-units (e.g. 11990000 == 11.99).
        price = info.get("price", 0) / 1_000_000
        if price < settings.max_usd_price:
            availability[domain] = f"{info.get('currency', 'USD')} {price:.2f}"
        else:
            availability[domain] = "Verify at " + _VERIFY_URL.format(domain=domain)
    return availability

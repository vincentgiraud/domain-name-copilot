"""Domain-name copilot: brainstorm domains, check availability, optionally speak."""
from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from config import get_settings
from godaddy import check_domains_availability
from llm import evaluate_domains, find_domains
from speech import text_to_speech
from storage import add_domain, load_domains

logger = logging.getLogger(__name__)


def run_once(brief: str, settings) -> None:
    """One generation → availability → persistence cycle."""
    suggestions = find_domains(brief)
    names = suggestions.names()
    if not names:
        logger.info("Empty domain list")
        return

    known = load_domains()
    fresh = [d for d in names if d not in known]
    for skipped in set(names) - set(fresh):
        logger.info("Domain %s already recorded, skipping check", skipped)
    if not fresh:
        return

    for domain, price in check_domains_availability(fresh).items():
        logger.info("%s available at: %s", domain, price)
        if add_domain(domain) and settings.voice_on:
            text_to_speech(domain)


def cmd_generate(args: argparse.Namespace) -> None:
    settings = get_settings()
    brief = Path(args.brief).read_text(encoding="utf-8")
    count = 0
    while args.rounds == 0 or count < args.rounds:
        run_once(brief, settings)
        count += 1
        if args.rounds != 1:
            time.sleep(args.delay)


def cmd_evaluate(args: argparse.Namespace) -> None:
    get_settings()
    domains = Path(args.file).read_text(encoding="utf-8")
    print(evaluate_domains(domains))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug logging"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="brainstorm and check domain availability")
    gen.add_argument("--brief", default="user.md", help="path to the brief prompt file")
    gen.add_argument(
        "--rounds",
        type=int,
        default=0,
        help="number of generation rounds (0 = loop forever)",
    )
    gen.add_argument(
        "--delay", type=float, default=1.0, help="seconds to wait between rounds"
    )
    gen.set_defaults(func=cmd_generate)

    ev = sub.add_parser("evaluate", help="rank/critique a list of domains")
    ev.add_argument("--file", default="domains.txt", help="file listing domains")
    ev.set_defaults(func=cmd_evaluate)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        args.func(args)
    except KeyboardInterrupt:
        logger.info("Interrupted, exiting")


if __name__ == "__main__":
    main()

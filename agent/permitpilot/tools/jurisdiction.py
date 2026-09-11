from __future__ import annotations

import json
from pathlib import Path

from strands import tool


FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "fixtures"
    / "oak-ridge"
    / "jurisdiction-research.json"
)


@tool
def research_jurisdiction(
    jurisdiction: str,
) -> dict:
    """Research known permit-jurisdiction evidence.

    This milestone uses a deterministic fixture representing official-source
    evidence for the PermitPilot demo.

    Args:
        jurisdiction: Jurisdiction to research.
    """

    if not jurisdiction or not jurisdiction.strip():
        return {
            "status": "needs_human_review",
            "jurisdiction": None,
            "verified": False,
            "sources": [],
            "observations": [
                "No jurisdiction was supplied.",
                "Jurisdiction must be identified before permit requirements "
                "can be treated as authoritative.",
            ],
        }

    normalized = jurisdiction.strip().lower()

    if normalized not in {
        "houston",
        "houston, texas",
        "houston, tx",
    }:
        return {
            "status": "unverified",
            "jurisdiction": jurisdiction.strip(),
            "verified": False,
            "sources": [],
            "observations": [
                "No verified jurisdiction fixture is available for this "
                "jurisdiction.",
                "Live official-source research or human review is required.",
            ],
        }

    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    verified_sources = [
        source for source in data["sources"] if source.get("verified") is True
    ]

    return {
        "status": "verified_fixture",
        "jurisdiction": data["jurisdiction"],
        "authority": data["authority"],
        "verified": bool(verified_sources),
        "sources": verified_sources,
        "observations": [
            "Official-source fixture evidence was found.",
            "Requirements are demo evidence and are not an exhaustive legal "
            "permit determination.",
        ],
    }

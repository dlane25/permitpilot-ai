from __future__ import annotations

import os

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

from .prompts import PERMITPILOT_SYSTEM_PROMPT
from .tools import (
    analyze_document_compliance,
    analyze_permit_applicability,
    inspect_project,
    research_jurisdiction,
)

load_dotenv()


def build_permitpilot_agent() -> Agent:
    """Create the PermitPilot Strands agent."""

    model_id = os.getenv("BEDROCK_MODEL_ID")
    region = os.getenv("AWS_REGION", "us-east-1")

    tools = [
        inspect_project,
        research_jurisdiction,
        analyze_permit_applicability,
        analyze_document_compliance,
    ]

    if model_id:
        model = BedrockModel(
            model_id=model_id,
            region_name=region,
            temperature=0.2,
        )

        return Agent(
            name="PermitPilot",
            description=(
                "Autonomous permit and compliance operations agent "
                "for construction professionals."
            ),
            model=model,
            system_prompt=PERMITPILOT_SYSTEM_PROMPT,
            tools=tools,
        )

    return Agent(
        name="PermitPilot",
        description=(
            "Autonomous permit and compliance operations agent "
            "for construction professionals."
        ),
        system_prompt=PERMITPILOT_SYSTEM_PROMPT,
        tools=tools,
    )

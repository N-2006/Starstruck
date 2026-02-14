from __future__ import annotations

import asyncio

from app.models.state import PipelineState
from app.services.llm import LLMService


async def analyze_node(state: PipelineState) -> dict:
    llm = LLMService()

    raw_a = state.get("user_a", {}).get("raw_data", {})
    raw_b = state.get("user_b", {}).get("raw_data", {})

    dossier_a, dossier_b = await asyncio.gather(
        llm.profile_analysis(raw_a),
        llm.profile_analysis(raw_b),
    )

    return {
        "user_a": {**state.get("user_a", {}), "dossier": dossier_a},
        "user_b": {**state.get("user_b", {}), "dossier": dossier_b},
    }

from __future__ import annotations

from app.models.state import PipelineState
from app.services.llm import LLMService


async def crossref_node(state: PipelineState) -> dict:
    llm = LLMService()

    dossier_a = state.get("user_a", {}).get("dossier", {})
    dossier_b = state.get("user_b", {}).get("dossier", {})

    cross_ref, venue_appropriate = await llm.cross_reference(dossier_a, dossier_b)

    return {"cross_ref": cross_ref, "include_venue": venue_appropriate}

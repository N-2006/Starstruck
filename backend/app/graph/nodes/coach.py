from __future__ import annotations

from app.models.state import PipelineState


from app.services.llm import LLMService


async def coach_node(state: PipelineState) -> dict:
    llm = LLMService()

    cross_ref = state.get("cross_ref", {})
    user_a_dossier = state.get("user_a", {}).get("dossier", {})
    user_b_dossier = state.get("user_b", {}).get("dossier", {})
    venues = state.get("venues", [])

    # If venues were suggested, pick the top one as context
    selected_venue = venues[0] if venues else None

    # Generate briefing for User A (how to talk to B)
    briefing_a = await llm.generate_coaching(
        target_user=user_a_dossier,
        other_user=user_b_dossier,
        cross_ref=cross_ref,
        venue=selected_venue
    )

    # Generate briefing for User B (how to talk to A)
    briefing_b = await llm.generate_coaching(
        target_user=user_b_dossier,
        other_user=user_a_dossier,
        cross_ref=cross_ref,
        venue=selected_venue
    )

    return {
        "coaching_a": briefing_a,
        "coaching_b": briefing_b
    }

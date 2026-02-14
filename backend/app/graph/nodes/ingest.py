from __future__ import annotations

import asyncio
from app.models.state import PipelineState
from app.services.letterboxd import LetterboxdService


async def ingest_node(state: PipelineState) -> dict:
    lb = LetterboxdService()
    
    user_a = state.get("user_a", {})
    user_b = state.get("user_b", {})
    
    # Simple multi-user ingestion
    async def ingest_user(user: dict):
        raw_data = {}
        lb_user = user.get("letterboxd_username")
        if lb_user:
            # LetterboxdService.get_recent_activity is sync, wrapping in gather might hit blocking
            # but for now we'll just call it
            raw_data["letterboxd"] = lb.get_recent_activity(lb_user)
        return raw_data

    # Use gather for potential parallel ingestion (if we add more services)
    raw_a, raw_b = await asyncio.gather(
        ingest_user(user_a),
        ingest_user(user_b)
    )

    return {
        "user_a": {**user_a, "raw_data": raw_a},
        "user_b": {**user_b, "raw_data": raw_b},
    }

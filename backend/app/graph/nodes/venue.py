from __future__ import annotations

from app.models.state import PipelineState
from app.services.llm import LLMService
from app.services.places import PlacesService


async def venue_node(state: PipelineState) -> dict:
    llm = LLMService()
    places = PlacesService()

    cross_ref = state.get("cross_ref", {})
    # Use user_b's location as a default bias, or user_a's if B's is missing
    location = state.get("user_b", {}).get("location") or state.get("user_a", {}).get("location")

    # 1. Brainstorm creative ideas and search queries
    suggested_queries = await llm.brainstorm_venue_queries(cross_ref)

    # 2. Search for real-world candidates based on those queries
    candidates = []
    for q in suggested_queries:
        query_text = q.get("search_query") or q.get("name")
        real_places = await places.search_venue(query_text, location=location)
        
        # Take up to 5 matches per query as candidates
        candidates.extend(real_places[:5])

    # 3. Rank the candidates and contextualize them for the match
    final_venues = await llm.rank_venues(candidates, cross_ref)

    return {"venues": final_venues}

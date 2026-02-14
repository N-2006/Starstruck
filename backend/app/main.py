from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.connectors import (
    GitHubConnector,
    LetterboxdConnector,
    InstagramConnector,
    LinkedInConnector,
)
from app.graph.builder import build_graph
from app.graph.nodes.ingest import _fetch_user_data
from app.models.schemas import (
    MatchRequest,
    CoachingResponse,
    ConnectRequest,
    ConnectResponse,
    AnalyzeRequest,
    AnalysisResult,
    MatchInput,
    MatchResult,
)
from app.services.findings import generate_findings
from app.services.llm import LLMService
from app.services.preview import generate_preview

logger = logging.getLogger(__name__)

app = FastAPI(title="Starstruck", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = build_graph()

CONNECTOR_MAP: dict[str, type] = {
    "github": GitHubConnector,
    "letterboxd": LetterboxdConnector,
    "instagram": InstagramConnector,
    "linkedin": LinkedInConnector,
}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── New frontend-facing endpoints ─────────────────────────────


@app.post("/api/connect", response_model=ConnectResponse)
async def connect_service(request: ConnectRequest):
    """Run a single connector and return a preview string."""
    connector_cls = CONNECTOR_MAP.get(request.service)
    if not connector_cls:
        return ConnectResponse(success=False, preview=f"Unknown service: {request.service}")

    try:
        connector = connector_cls()
        data = await connector.fetch(request.username)
        preview = generate_preview(request.service, data)
        return ConnectResponse(success=True, preview=preview)
    except Exception:
        logger.exception("Connector %s failed", request.service)
        return ConnectResponse(success=True, preview="Connected (limited data)")


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_user(request: AnalyzeRequest):
    """Run all connectors + LLM analysis for one user."""
    raw_data = await _fetch_user_data(request.identifiers)

    llm = LLMService()
    dossier = await llm.profile_analysis(raw_data)

    public = dossier.get("public", {})
    findings = generate_findings(dossier, raw_data)

    return AnalysisResult(
        bio=public.get("vibe", ""),
        findings=findings,
        tags=public.get("tags", []),
        schedule=public.get("schedule_pattern", "mixed"),
        dossier=dossier,
    )


@app.post("/api/match", response_model=MatchResult)
async def match_users(request: MatchInput):
    """Run full pipeline for two users: ingest → analyze → crossref."""
    # Ingest both users in parallel
    raw_a, raw_b = await asyncio.gather(
        _fetch_user_data(request.user_a),
        _fetch_user_data(request.user_b),
    )

    # Analyze both in parallel
    llm = LLMService()
    dossier_a, dossier_b = await asyncio.gather(
        llm.profile_analysis(raw_a),
        llm.profile_analysis(raw_b),
    )

    # Cross-reference
    cross_ref, _venue_appropriate = await llm.cross_reference(dossier_a, dossier_b)

    # Calculate compatibility from crossref
    shared = cross_ref.get("shared", [])
    complementary = cross_ref.get("complementary", [])
    tensions = cross_ref.get("tension_points", [])
    total = len(shared) + len(complementary) + len(tensions)
    if total > 0:
        score = int(((len(shared) + len(complementary) * 0.7) / total) * 100)
        compatibility = f"{score}%"
    else:
        compatibility = "N/A"

    shared_tags_a = set(dossier_a.get("public", {}).get("tags", []))
    shared_tags_b = set(dossier_b.get("public", {}).get("tags", []))
    shared_tags = list(shared_tags_a & shared_tags_b)

    public_a = dossier_a.get("public", {})
    private_a = dossier_a.get("private", {})

    return MatchResult(
        compatibility=compatibility,
        shared_tags=shared_tags,
        public_profile={
            "vibe": public_a.get("vibe", ""),
            "tags": public_a.get("tags", []),
            "schedule": public_a.get("schedule_pattern", "mixed"),
        },
        private_profile={
            "summary": private_a.get("summary", ""),
            "traits": private_a.get("traits", []),
            "interests": private_a.get("interests", []),
            "deepCuts": private_a.get("deep_cuts", []),
            "dataSources": dossier_a.get("data_sources", []),
        },
        suggestion=None,
        cross_ref=cross_ref,
    )


# ── Existing pipeline endpoints (updated) ────────────────────


def _build_identifiers(user: Any) -> dict[str, str | None]:
    return {
        "github": user.github_username,
        "spotify": user.spotify_username,
        "letterboxd": user.letterboxd_username,
        "instagram": user.instagram_username,
        "linkedin": user.linkedin_username,
    }


@app.post("/run", response_model=CoachingResponse)
async def run_pipeline(request: MatchRequest):
    initial_state = {
        "user_a": {
            "username": request.user_a.github_username or "",
            "identifiers": _build_identifiers(request.user_a),
        },
        "user_b": {
            "username": request.user_b.github_username or "",
            "identifiers": _build_identifiers(request.user_b),
        },
        "include_venue": request.include_venue,
    }
    _result = await pipeline.ainvoke(initial_state)
    return CoachingResponse(user_a_cards=[], user_b_cards=[])


@app.post("/stream")
async def stream_pipeline(request: MatchRequest):
    async def event_generator():
        initial_state = {
            "user_a": {
                "username": request.user_a.github_username or "",
                "identifiers": _build_identifiers(request.user_a),
            },
            "user_b": {
                "username": request.user_b.github_username or "",
                "identifiers": _build_identifiers(request.user_b),
            },
            "include_venue": request.include_venue,
        }
        async for event in pipeline.astream(initial_state):
            yield {"event": "node_complete", "data": str(event)}
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())

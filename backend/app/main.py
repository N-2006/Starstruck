from __future__ import annotations
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.models.schemas import MatchRequest, CoachingResponse, ProfileResponse, UserInput
from app.graph.builder import build_graph

app = FastAPI(title="Starstruck", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = build_graph()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/profile", response_model=ProfileResponse)
async def analyze_profile(request: UserInput):
    from app.services.llm import LLMService
    from app.services.letterboxd import LetterboxdService
    
    lb = LetterboxdService()
    llm = LLMService()
    
    raw_data = {}
    if request.letterboxd_username:
        raw_data["letterboxd"] = lb.get_recent_activity(request.letterboxd_username)
    
    dossier = await llm.profile_analysis(raw_data)
    return ProfileResponse(dossier=dossier)


@app.post("/run", response_model=CoachingResponse)
async def run_pipeline(request: MatchRequest):
    initial_state = {
        "user_a": {
            "spotify_username": request.user_a.spotify_username,
            "letterboxd_username": request.user_a.letterboxd_username,
            "github_username": request.user_a.github_username,
            "book_titles": request.user_a.book_titles or [],
            "location": request.user_a.location
        },
        "user_b": {
            "spotify_username": request.user_b.spotify_username,
            "letterboxd_username": request.user_b.letterboxd_username,
            "github_username": request.user_b.github_username,
            "book_titles": request.user_b.book_titles or [],
            "location": request.user_b.location
        },
        "include_venue": request.include_venue,
    }
    result = await pipeline.ainvoke(initial_state)
    return CoachingResponse(
        venues=result.get("venues", []),
        coaching_a=result.get("coaching_a", {}),
        coaching_b=result.get("coaching_b", {}),
        cross_ref=result.get("cross_ref", {})
    )


@app.post("/stream")
async def stream_pipeline(request: MatchRequest):
    async def event_generator():
        initial_state = {
            "user_a": {
                "spotify_username": request.user_a.spotify_username,
                "letterboxd_username": request.user_a.letterboxd_username,
                "github_username": request.user_a.github_username,
                "book_titles": request.user_a.book_titles or [],
                "location": request.user_a.location
            },
            "user_b": {
                "spotify_username": request.user_b.spotify_username,
                "letterboxd_username": request.user_b.letterboxd_username,
                "github_username": request.user_b.github_username,
                "book_titles": request.user_b.book_titles or [],
                "location": request.user_b.location
            },
            "include_venue": request.include_venue,
        }
        async for event in pipeline.astream(initial_state):
            yield {"event": "node_complete", "data": json.dumps(event)}
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UserInput(BaseModel):
    github_username: str | None = None
    spotify_username: str | None = None
    letterboxd_username: str | None = None
    instagram_username: str | None = None
    linkedin_username: str | None = None
    book_titles: list[str] | None = None
    location: str | None = None


class MatchRequest(BaseModel):
    user_a: UserInput
    user_b: UserInput
    include_venue: bool = True


class CoachingCard(BaseModel):
    label: str
    icon: str
    content: str


class CoachingResponse(BaseModel):
    user_a_cards: list[CoachingCard] = []
    user_b_cards: list[CoachingCard] = []
    venues: list[dict] = []
    coaching_a: dict = {}
    coaching_b: dict = {}
    cross_ref: dict = {}


class ChatMessage(BaseModel):
    role: str
    content: str


class CoachChatRequest(BaseModel):
    user_a_name: str = ""
    user_b_name: str = ""
    user_a_dossier: dict
    user_b_dossier: dict
    crossref: dict
    message: str
    history: list[ChatMessage] = []


class CoachChatResponse(BaseModel):
    reply: str


class ConnectRequest(BaseModel):
    service: str
    username: str


class ConnectResponse(BaseModel):
    success: bool
    preview: str


class AnalyzeRequest(BaseModel):
    identifiers: dict[str, str | None]


class AnalysisResult(BaseModel):
    bio: str
    findings: list[dict[str, Any]]
    tags: list[str]
    schedule: str
    dossier: dict[str, Any]


class MatchInput(BaseModel):
    user_a: dict[str, str | None]
    user_b: dict[str, str | None]


class MatchResult(BaseModel):
    compatibility: str
    shared_tags: list[str]
    public_profile: dict[str, Any]
    private_profile: dict[str, Any]
    suggestion: dict[str, Any] | None = None
    cross_ref: dict[str, Any]


class ProfileResponse(BaseModel):
    dossier: dict

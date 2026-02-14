from __future__ import annotations

from typing import Any
from typing_extensions import TypedDict


class UserDataBundle(TypedDict, total=False):
    spotify: dict[str, Any]
    letterboxd: dict[str, Any]
    github: dict[str, Any]
    books: dict[str, Any]
    instagram: dict[str, Any]
    linkedin: dict[str, Any]
    places: dict[str, Any]


class UserProfile(TypedDict, total=False):
    username: str
    raw_data: UserDataBundle
    dossier: dict[str, Any]


class CrossRefResult(TypedDict, total=False):
    shared: list[dict[str, Any]]
    complementary: list[dict[str, Any]]
    tension_points: list[dict[str, Any]]
    citations: list[str]


class VenueRecommendation(TypedDict, total=False):
    name: str
    reason: str
    tips: list[str]
    relevance_score: float


class CoachingBriefing(TypedDict, total=False):
    match_intel: str
    conversation_playbook: list[str]
    minefield_map: list[str]
    venue_cheat_sheet: str
    vibe_calibration: str


class PipelineState(TypedDict, total=False):
    user_a: UserProfile
    user_b: UserProfile
    cross_ref: CrossRefResult
    venues: list[VenueRecommendation]
    coaching_a: CoachingBriefing
    coaching_b: CoachingBriefing
    include_venue: bool
    error: str | None

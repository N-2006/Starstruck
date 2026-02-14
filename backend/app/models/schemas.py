from __future__ import annotations

from pydantic import BaseModel


class UserInput(BaseModel):
    spotify_username: str | None = None
    letterboxd_username: str | None = None
    github_username: str | None = None
    book_titles: list[str] | None = None
    instagram_screenshot_url: str | None = None
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

class ProfileResponse(BaseModel):
    dossier: dict

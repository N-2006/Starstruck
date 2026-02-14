from __future__ import annotations


class LLMService:
    async def profile_analysis(self, raw_data: dict) -> dict:
        return {}

    async def cross_reference(self, profile_a: dict, profile_b: dict) -> dict:
        return {}

    async def rank_venues(self, venues: list[dict], context: dict) -> list[dict]:
        return []

    async def generate_coaching(self, cross_ref: dict, profile: dict, venues: list[dict]) -> dict:
        return {}

    async def analyze_image(self, image_url: str) -> dict:
        return {}

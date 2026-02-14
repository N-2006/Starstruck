from __future__ import annotations

import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings

PROFILE_SYSTEM_PROMPT = """\
You are a personality analyst. Given a user's digital footprint data from various platforms, \
synthesize a structured personality dossier.

Return ONLY valid JSON with these exact keys:
- "summary": 2-3 sentence personality sketch
- "traits": list of 3-6 personality trait phrases (e.g. "night owl", "deep-focus builder")
- "interests": list of 3-8 specific interests extracted from the data
- "vibe": one sentence capturing their overall energy/aesthetic
- "schedule_pattern": one of "night_owl", "early_bird", or "mixed" (infer from activity timestamps if available)

Do NOT wrap the JSON in markdown code fences. Return raw JSON only."""


def _empty_dossier() -> dict:
    return {
        "summary": "",
        "traits": [],
        "interests": [],
        "vibe": "",
        "schedule_pattern": "mixed",
        "data_sources": [],
    }


class LLMService:
    def __init__(self) -> None:
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.7,
        )

    async def profile_analysis(self, raw_data: dict) -> dict:
        filtered = {k: v for k, v in raw_data.items() if v}
        if not filtered:
            return _empty_dossier()

        data_sources = list(filtered.keys())
        human_content = json.dumps(filtered, indent=2, default=str)

        response = await self._llm.ainvoke([
            SystemMessage(content=PROFILE_SYSTEM_PROMPT),
            HumanMessage(content=human_content),
        ])

        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        dossier = json.loads(text)
        dossier["data_sources"] = data_sources
        return dossier

    async def cross_reference(self, profile_a: dict, profile_b: dict) -> dict:
        return {}

    async def rank_venues(self, venues: list[dict], context: dict) -> list[dict]:
        return []

    async def generate_coaching(self, cross_ref: dict, profile: dict, venues: list[dict]) -> dict:
        return {}

    async def analyze_image(self, image_url: str) -> dict:
        return {}

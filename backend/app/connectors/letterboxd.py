from __future__ import annotations

import asyncio
import re
from typing import Any

import feedparser
import httpx

from app.connectors.base import BaseConnector

FEED_URL = "https://letterboxd.com/{username}/rss/"


class LetterboxdConnector(BaseConnector):
    """Fetch recent Letterboxd activity from a user's public RSS feed."""

    async def fetch(self, identifier: str) -> dict[str, Any]:
        username = identifier.strip().lstrip("@")
        feed_data = await self._fetch_feed(username)
        return {
            "recent_films": self._extract_films(feed_data),
        }

    # ── data fetching ──────────────────────────────────────────────

    async def _fetch_feed(self, username: str) -> dict:
        url = FEED_URL.format(username=username)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
        # feedparser is sync, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, feedparser.parse, resp.text)

    # ── data extraction ────────────────────────────────────────────

    @staticmethod
    def _extract_films(feed: dict) -> list[dict[str, Any]]:
        entries = feed.get("entries", [])
        films: list[dict[str, Any]] = []
        for entry in entries[:20]:
            title_raw = entry.get("title", "")
            link = entry.get("link", "")
            rating = LetterboxdConnector._parse_rating(entry)

            # Extract clean title: strip trailing " - ★★★½" rating part
            title = re.sub(r"\s*-\s*★.*$", "", title_raw).strip()

            films.append({
                "title": title,
                "rating": rating,
                "link": link,
            })
        return films

    @staticmethod
    def _parse_rating(entry: dict) -> float | None:
        """Extract numeric rating from letterboxd_memberrating or star symbols."""
        # Letterboxd RSS includes a numeric rating field
        member_rating = entry.get("letterboxd_memberrating")
        if member_rating:
            try:
                return float(member_rating)
            except (ValueError, TypeError):
                pass

        # Fallback: parse ★/½ symbols from title
        title = entry.get("title", "")
        if "★" not in title and "½" not in title:
            return None
        star_part = title.split("-")[-1].strip() if "-" in title else ""
        full = star_part.count("★")
        half = 0.5 if "½" in star_part else 0.0
        rating = full + half
        return rating if rating > 0 else None

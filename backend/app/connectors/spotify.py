from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any

import httpx

from app.connectors.base import BaseConnector

API_BASE = "https://api.spotify.com/v1"


class SpotifyConnector(BaseConnector):
    """Fetch Spotify listening profile using an OAuth access token."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    async def fetch(self, identifier: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=API_BASE,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=15,
        ) as client:
            artists, tracks, recent = await asyncio.gather(
                self._fetch_top_artists(client),
                self._fetch_top_tracks(client),
                self._fetch_recently_played(client),
            )

        return {
            "top_artists": self._extract_artists(artists),
            "top_genres": self._extract_top_genres(artists),
            "top_tracks": self._extract_tracks(tracks),
            "listening_hours": self._extract_listening_hours(recent),
        }

    # ── individual API calls ──────────────────────────────────────

    async def _fetch_top_artists(self, client: httpx.AsyncClient) -> dict:
        resp = await client.get(
            "/me/top/artists", params={"limit": 50, "time_range": "medium_term"}
        )
        if resp.status_code == 401:
            raise PermissionError("Spotify token expired or invalid")
        resp.raise_for_status()
        return resp.json()

    async def _fetch_top_tracks(self, client: httpx.AsyncClient) -> dict:
        resp = await client.get(
            "/me/top/tracks", params={"limit": 50, "time_range": "medium_term"}
        )
        if resp.status_code == 401:
            raise PermissionError("Spotify token expired or invalid")
        resp.raise_for_status()
        return resp.json()

    async def _fetch_recently_played(self, client: httpx.AsyncClient) -> dict:
        resp = await client.get("/me/player/recently-played", params={"limit": 50})
        if resp.status_code == 401:
            raise PermissionError("Spotify token expired or invalid")
        resp.raise_for_status()
        return resp.json()

    # ── data extraction ───────────────────────────────────────────

    @staticmethod
    def _extract_artists(data: dict) -> list[dict[str, Any]]:
        return [
            {
                "name": a["name"],
                "genres": a.get("genres", []),
                "popularity": a.get("popularity", 0),
            }
            for a in data.get("items", [])
        ]

    @staticmethod
    def _extract_top_genres(data: dict) -> list[str]:
        counts: Counter[str] = Counter()
        for a in data.get("items", []):
            for g in a.get("genres", []):
                counts[g] += 1
        return [g for g, _ in counts.most_common(20)]

    @staticmethod
    def _extract_tracks(data: dict) -> list[dict[str, str]]:
        return [
            {
                "name": t["name"],
                "artist": t["artists"][0]["name"] if t.get("artists") else "",
            }
            for t in data.get("items", [])
        ]

    @staticmethod
    def _extract_listening_hours(data: dict) -> list[int]:
        from datetime import datetime

        hours: list[int] = []
        for item in data.get("items", []):
            ts = item.get("played_at", "")
            if ts:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hours.append(dt.hour)
        return hours

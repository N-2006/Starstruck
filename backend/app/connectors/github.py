from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.connectors.base import BaseConnector

API_BASE = "https://api.github.com"


class GitHubConnector(BaseConnector):
    """Fetch public GitHub profile data for a username."""

    async def fetch(self, identifier: str) -> dict[str, Any]:
        username = identifier.strip().lstrip("@")
        async with httpx.AsyncClient(
            base_url=API_BASE,
            headers={"Accept": "application/vnd.github+json"},
            timeout=15,
        ) as client:
            repos_task = self._fetch_repos(client, username)
            events_task = self._fetch_events(client, username)
            starred_task = self._fetch_starred(client, username)
            repos, events, starred = await asyncio.gather(
                repos_task, events_task, starred_task
            )

        return {
            "languages": self._extract_languages(repos),
            "repos": self._extract_repos(repos),
            "commit_hours": self._extract_commit_hours(events),
            "starred_topics": self._extract_starred_topics(starred),
        }

    # ── individual API calls ──────────────────────────────────────

    async def _fetch_repos(
        self, client: httpx.AsyncClient, username: str
    ) -> list[dict]:
        resp = await client.get(
            f"/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"},
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()

    async def _fetch_events(
        self, client: httpx.AsyncClient, username: str
    ) -> list[dict]:
        resp = await client.get(
            f"/users/{username}/events/public", params={"per_page": 100}
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()

    async def _fetch_starred(
        self, client: httpx.AsyncClient, username: str
    ) -> list[dict]:
        resp = await client.get(
            f"/users/{username}/starred", params={"per_page": 100}
        )
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        return resp.json()

    # ── data extraction ───────────────────────────────────────────

    @staticmethod
    def _extract_languages(repos: list[dict]) -> list[str]:
        langs: list[str] = []
        seen: set[str] = set()
        for r in repos:
            lang = r.get("language")
            if lang and lang not in seen:
                seen.add(lang)
                langs.append(lang)
        return langs

    @staticmethod
    def _extract_repos(repos: list[dict]) -> list[dict[str, Any]]:
        return [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language") or "",
            }
            for r in repos
        ]

    @staticmethod
    def _extract_commit_hours(events: list[dict]) -> list[int]:
        from datetime import datetime

        hours: list[int] = []
        for e in events:
            if e.get("type") != "PushEvent":
                continue
            ts = e.get("created_at", "")
            if ts:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                hours.append(dt.hour)
        return hours

    @staticmethod
    def _extract_starred_topics(starred: list[dict]) -> list[str]:
        topics: list[str] = []
        seen: set[str] = set()
        for r in starred:
            for t in r.get("topics", []):
                if t not in seen:
                    seen.add(t)
                    topics.append(t)
        return topics

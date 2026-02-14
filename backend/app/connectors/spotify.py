from __future__ import annotations

from typing import Any

from app.connectors.base import BaseConnector


class SpotifyConnector(BaseConnector):
    async def fetch(self, identifier: str) -> dict[str, Any]:
        return {}

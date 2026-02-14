from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.connectors import (
    GitHubConnector,
    LetterboxdConnector,
    InstagramConnector,
    LinkedInConnector,
)
from app.models.state import PipelineState, UserDataBundle

logger = logging.getLogger(__name__)

# Map identifier keys to connector classes (no-arg constructors only)
CONNECTOR_MAP: dict[str, type] = {
    "github": GitHubConnector,
    "letterboxd": LetterboxdConnector,
    "instagram": InstagramConnector,
    "linkedin": LinkedInConnector,
}


async def _fetch_one(service: str, identifier: str) -> tuple[str, dict[str, Any]]:
    """Fetch data from a single connector, returning (service, data)."""
    try:
        connector_cls = CONNECTOR_MAP.get(service)
        if not connector_cls:
            logger.warning("No connector for service: %s", service)
            return service, {}
        connector = connector_cls()
        data = await connector.fetch(identifier)
        # Strip screenshot_b64 from instagram — too large for LLM
        if service == "instagram":
            data.pop("screenshot_b64", None)
        return service, data
    except Exception:
        logger.exception("Connector %s failed for %s", service, identifier)
        return service, {}


async def _fetch_user_data(identifiers: dict[str, str | None]) -> UserDataBundle:
    """Run all non-null connectors in parallel for a user."""
    tasks = []
    for service, identifier in identifiers.items():
        if identifier:
            tasks.append(_fetch_one(service, identifier))

    if not tasks:
        return {}

    results = await asyncio.gather(*tasks)
    bundle: dict[str, Any] = {}
    for service, data in results:
        if data:
            bundle[service] = data
    return bundle


async def ingest_node(state: PipelineState) -> dict:
    user_a = state.get("user_a", {})
    user_b = state.get("user_b", {})

    ids_a = user_a.get("identifiers", {})
    ids_b = user_b.get("identifiers", {})

    raw_a, raw_b = await asyncio.gather(
        _fetch_user_data(ids_a),
        _fetch_user_data(ids_b),
    )

    return {
        "user_a": {**user_a, "raw_data": raw_a},
        "user_b": {**user_b, "raw_data": raw_b},
    }

from __future__ import annotations

from typing import Literal

from app.models.state import PipelineState


def should_include_venue(state: PipelineState) -> Literal["venue", "coach"]:
    if state.get("include_venue", False):
        return "venue"
    return "coach"

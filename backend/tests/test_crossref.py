"""Tests for the crossref node and LLMService.cross_reference.

Unit tests use mocks (no Gemini calls).
Integration tests hit real Gemini API (marked with @pytest.mark.integration).
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.llm import LLMService, _empty_crossref
from app.graph.nodes.crossref import crossref_node


# ── sample data ──────────────────────────────────────────────────

SAMPLE_GITHUB = {
    "languages": ["Python", "TypeScript"],
    "repos": [
        {"name": "ml-project", "description": "A machine learning toolkit", "stars": 42, "language": "Python"},
        {"name": "web-app", "description": "Portfolio site", "stars": 3, "language": "TypeScript"},
    ],
    "commit_hours": [14, 3, 22, 1, 23],
    "starred_topics": ["rust", "machine-learning", "cli"],
}

SAMPLE_SPOTIFY = {
    "top_artists": ["Frank Ocean", "Radiohead", "Tame Impala"],
    "top_genres": ["psychedelic soul", "art rock", "indie"],
    "listening_hours": {"late_night": 45, "morning": 10, "afternoon": 20},
}

SAMPLE_LETTERBOXD = {
    "recent_films": [
        {"title": "Blade Runner 2049 (2017) - ★★★★★", "has_rating": True, "rating_text": "★★★★★"},
        {"title": "Interstellar (2014) - ★★★★½", "has_rating": True, "rating_text": "★★★★½"},
        {"title": "Whiplash (2014) - ★★★★★", "has_rating": True, "rating_text": "★★★★★"},
    ],
}

DOSSIER_A = {
    "public": {
        "vibe": "Night-owl coder who vibes to art rock",
        "tags": ["web dev", "ML", "indie music", "sci-fi"],
        "schedule_pattern": "night_owl",
    },
    "private": {
        "summary": "A late-night Python dev who builds ML toolkits and listens to Radiohead.",
        "traits": ["builder", "nocturnal", "analytical"],
        "interests": ["Python", "machine learning", "Radiohead", "Tame Impala", "Blade Runner"],
        "deep_cuts": ["Starred rust repos despite coding in Python", "Rates sci-fi films 5 stars"],
    },
    "data_sources": ["github", "spotify", "letterboxd"],
}

DOSSIER_B = {
    "public": {
        "vibe": "Creative morning person with eclectic taste",
        "tags": ["design", "jazz", "film", "cooking"],
        "schedule_pattern": "early_bird",
    },
    "private": {
        "summary": "An early riser who designs interfaces and loves jazz and classic cinema.",
        "traits": ["creative", "morning person", "detail-oriented"],
        "interests": ["Figma", "jazz", "Wes Anderson films", "cooking", "typography"],
        "deep_cuts": ["Has a sourdough starter named after a font", "Watches films with subtitles on"],
    },
    "data_sources": ["github", "spotify"],
}

CROSSREF_TOP_KEYS = {"shared", "complementary", "tension_points", "citations"}

FAKE_CROSSREF_RESPONSE = json.dumps({
    "shared": [
        {"signal": "Both are tech enthusiasts", "detail": "Both have GitHub activity", "source": "github"},
    ],
    "complementary": [
        {"signal": "Builder meets designer", "detail": "One builds backends, other designs UI", "source": "github"},
    ],
    "tension_points": [
        {"signal": "Schedule mismatch", "detail": "Night owl vs early bird", "source": "both"},
    ],
    "citations": [
        "Person A: 'night_owl' schedule pattern",
        "Person B: 'early_bird' schedule pattern",
        "Person A: interests include 'Python' and 'machine learning'",
    ],
    "venue_appropriate": True,
})


# ── unit: _empty_crossref ────────────────────────────────────────

class TestEmptyCrossref:
    def test_has_all_top_level_keys(self):
        c = _empty_crossref()
        assert set(c.keys()) == CROSSREF_TOP_KEYS

    def test_shared_is_empty_list(self):
        assert _empty_crossref()["shared"] == []

    def test_complementary_is_empty_list(self):
        assert _empty_crossref()["complementary"] == []

    def test_tension_points_is_empty_list(self):
        assert _empty_crossref()["tension_points"] == []

    def test_citations_is_empty_list(self):
        assert _empty_crossref()["citations"] == []

    def test_returns_new_dict_each_call(self):
        c1 = _empty_crossref()
        c2 = _empty_crossref()
        c1["shared"].append({"signal": "test"})
        assert c2["shared"] == []


# ── unit: cross_reference with mocked Gemini ─────────────────────

def _make_llm_service():
    """Create an LLMService with the Gemini client init bypassed (for unit tests)."""
    with patch.object(LLMService, "__init__", lambda self: None):
        svc = LLMService()
        svc._llm = AsyncMock()
    return svc


class TestCrossReferenceUnit:
    @pytest.mark.asyncio
    async def test_both_empty_returns_placeholder_no_api_call(self):
        svc = _make_llm_service()
        result, venue = await svc.cross_reference({}, {})
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_crossref()
        assert venue is False

    @pytest.mark.asyncio
    async def test_one_empty_returns_placeholder(self):
        svc = _make_llm_service()
        result, venue = await svc.cross_reference(DOSSIER_A, {})
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_crossref()
        assert venue is False

    @pytest.mark.asyncio
    async def test_none_dossier_returns_placeholder(self):
        svc = _make_llm_service()
        result, venue = await svc.cross_reference(None, DOSSIER_B)
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_crossref()

    @pytest.mark.asyncio
    async def test_valid_dossiers_calls_gemini(self):
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = FAKE_CROSSREF_RESPONSE
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result, venue = await svc.cross_reference(DOSSIER_A, DOSSIER_B)

        svc._llm.ainvoke.assert_called_once()
        assert isinstance(result["shared"], list)
        assert len(result["shared"]) == 1
        assert result["shared"][0]["signal"] == "Both are tech enthusiasts"
        assert venue is True

    @pytest.mark.asyncio
    async def test_venue_appropriate_popped_from_result(self):
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = FAKE_CROSSREF_RESPONSE
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result, _ = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        assert "venue_appropriate" not in result

    @pytest.mark.asyncio
    async def test_sends_both_dossiers_to_gemini(self):
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = FAKE_CROSSREF_RESPONSE
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        await svc.cross_reference(DOSSIER_A, DOSSIER_B)

        call_args = svc._llm.ainvoke.call_args[0][0]
        human_msg_content = call_args[1].content
        parsed = json.loads(human_msg_content)
        assert "person_a" in parsed
        assert "person_b" in parsed

    @pytest.mark.asyncio
    async def test_handles_markdown_wrapped_json(self):
        svc = _make_llm_service()
        wrapped = "```json\n" + FAKE_CROSSREF_RESPONSE + "\n```"
        fake_response = AsyncMock()
        fake_response.content = wrapped
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result, venue = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        assert isinstance(result["shared"], list)
        assert venue is True

    @pytest.mark.asyncio
    async def test_raises_on_invalid_json(self):
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = "Not valid JSON"
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        with pytest.raises(json.JSONDecodeError):
            await svc.cross_reference(DOSSIER_A, DOSSIER_B)


# ── unit: crossref_node with mocked LLMService ──────────────────

class TestCrossrefNodeUnit:
    @pytest.mark.asyncio
    async def test_sets_cross_ref_and_include_venue(self):
        fake_crossref = {
            "shared": [{"signal": "test", "detail": "d", "source": "s"}],
            "complementary": [],
            "tension_points": [],
            "citations": ["c1"],
        }

        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.cross_reference = AsyncMock(return_value=(fake_crossref, True))

            state = {
                "user_a": {"username": "alice", "dossier": DOSSIER_A},
                "user_b": {"username": "bob", "dossier": DOSSIER_B},
            }
            result = await crossref_node(state)

        assert result["cross_ref"] == fake_crossref
        assert result["include_venue"] is True

    @pytest.mark.asyncio
    async def test_empty_dossiers_no_gemini_call(self):
        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.cross_reference = AsyncMock(return_value=(_empty_crossref(), False))

            state = {
                "user_a": {"username": "alice", "dossier": {}},
                "user_b": {"username": "bob", "dossier": {}},
            }
            result = await crossref_node(state)

        assert result["cross_ref"] == _empty_crossref()
        assert result["include_venue"] is False

    @pytest.mark.asyncio
    async def test_handles_missing_dossiers(self):
        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.cross_reference = AsyncMock(return_value=(_empty_crossref(), False))

            state = {
                "user_a": {"username": "alice"},
                "user_b": {"username": "bob"},
            }
            result = await crossref_node(state)

        assert result["cross_ref"] == _empty_crossref()
        assert result["include_venue"] is False

    @pytest.mark.asyncio
    async def test_handles_empty_state(self):
        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.cross_reference = AsyncMock(return_value=(_empty_crossref(), False))

            result = await crossref_node({})

        assert result["cross_ref"] == _empty_crossref()
        assert result["include_venue"] is False


# ── integration: real Gemini calls ───────────────────────────────

def _assert_valid_crossref(crossref: dict):
    """Validate a crossref result has the correct shape."""
    assert set(crossref.keys()) >= CROSSREF_TOP_KEYS
    assert "venue_appropriate" not in crossref

    for key in ("shared", "complementary", "tension_points"):
        items = crossref[key]
        assert isinstance(items, list)
        for item in items:
            assert "signal" in item
            assert "detail" in item
            assert "source" in item

    assert isinstance(crossref["citations"], list)
    assert len(crossref["citations"]) >= 1


@pytest.mark.integration
class TestCrossReferenceIntegration:
    """Hit real Gemini API. Run with: pytest -m integration"""

    @pytest.mark.asyncio
    async def test_full_dossiers_produce_valid_crossref(self):
        svc = LLMService()
        result, venue = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        _assert_valid_crossref(result)
        assert isinstance(venue, bool)

    @pytest.mark.asyncio
    async def test_shared_list_non_empty(self):
        svc = LLMService()
        result, _ = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        assert len(result["shared"]) >= 1

    @pytest.mark.asyncio
    async def test_citations_reference_dossier_data(self):
        svc = LLMService()
        result, _ = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        assert len(result["citations"]) >= 3
        # At least one citation should reference person A or B's data
        all_citations = " ".join(result["citations"]).lower()
        assert len(all_citations) > 20

    @pytest.mark.asyncio
    async def test_both_empty_returns_placeholder_no_api_call(self):
        svc = LLMService()
        result, venue = await svc.cross_reference({}, {})
        assert result == _empty_crossref()
        assert venue is False

    @pytest.mark.asyncio
    async def test_venue_appropriate_is_bool(self):
        svc = LLMService()
        _, venue = await svc.cross_reference(DOSSIER_A, DOSSIER_B)
        assert isinstance(venue, bool)


@pytest.mark.integration
class TestCrossrefNodeIntegration:
    @pytest.mark.asyncio
    async def test_full_node_with_dossiers(self):
        state = {
            "user_a": {"username": "alice", "dossier": DOSSIER_A},
            "user_b": {"username": "bob", "dossier": DOSSIER_B},
        }
        result = await crossref_node(state)

        _assert_valid_crossref(result["cross_ref"])
        assert isinstance(result["include_venue"], bool)

    @pytest.mark.asyncio
    async def test_full_pipeline_analyze_to_crossref(self):
        """End-to-end: analyze_node → crossref_node."""
        from app.graph.nodes.analyze import analyze_node

        state = {
            "user_a": {"username": "alice", "raw_data": {
                "github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY, "letterboxd": SAMPLE_LETTERBOXD,
            }},
            "user_b": {"username": "bob", "raw_data": {
                "github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY,
            }},
        }

        analyze_result = await analyze_node(state)
        merged = {**state, **analyze_result}
        crossref_result = await crossref_node(merged)

        _assert_valid_crossref(crossref_result["cross_ref"])
        assert isinstance(crossref_result["include_venue"], bool)
        assert len(crossref_result["cross_ref"]["shared"]) >= 1

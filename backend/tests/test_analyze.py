"""Tests for the analyze node and LLMService.profile_analysis.

Unit tests use mocks (no Gemini calls).
Integration tests hit real Gemini API (marked with @pytest.mark.integration).
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.llm import LLMService, _empty_dossier
from app.graph.nodes.analyze import analyze_node


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

DOSSIER_TOP_KEYS = {"public", "private", "data_sources"}
PUBLIC_KEYS = {"vibe", "tags", "schedule_pattern"}
PRIVATE_KEYS = {"summary", "traits", "interests", "deep_cuts"}


# ── unit: _empty_dossier ─────────────────────────────────────────

class TestEmptyDossier:
    def test_has_all_top_level_keys(self):
        d = _empty_dossier()
        assert set(d.keys()) == DOSSIER_TOP_KEYS

    def test_public_has_correct_keys(self):
        assert set(_empty_dossier()["public"].keys()) == PUBLIC_KEYS

    def test_private_has_correct_keys(self):
        assert set(_empty_dossier()["private"].keys()) == PRIVATE_KEYS

    def test_public_vibe_is_empty_string(self):
        assert _empty_dossier()["public"]["vibe"] == ""

    def test_public_tags_is_empty_list(self):
        assert _empty_dossier()["public"]["tags"] == []

    def test_public_schedule_defaults_to_mixed(self):
        assert _empty_dossier()["public"]["schedule_pattern"] == "mixed"

    def test_private_summary_is_empty_string(self):
        assert _empty_dossier()["private"]["summary"] == ""

    def test_private_traits_is_empty_list(self):
        assert _empty_dossier()["private"]["traits"] == []

    def test_private_interests_is_empty_list(self):
        assert _empty_dossier()["private"]["interests"] == []

    def test_private_deep_cuts_is_empty_list(self):
        assert _empty_dossier()["private"]["deep_cuts"] == []

    def test_data_sources_is_empty_list(self):
        assert _empty_dossier()["data_sources"] == []

    def test_returns_new_dict_each_call(self):
        """Ensure no shared mutable state between calls."""
        d1 = _empty_dossier()
        d2 = _empty_dossier()
        d1["public"]["tags"].append("test")
        d1["private"]["traits"].append("test")
        assert d2["public"]["tags"] == []
        assert d2["private"]["traits"] == []


# ── unit: connector data filtering ──────────────────────────────

def _make_llm_service():
    """Create an LLMService with the Gemini client init bypassed (for unit tests)."""
    with patch.object(LLMService, "__init__", lambda self: None):
        svc = LLMService()
        svc._llm = AsyncMock()
    return svc


FAKE_GEMINI_RESPONSE = json.dumps({
    "public": {
        "vibe": "Chill coder",
        "tags": ["web dev", "ML"],
        "schedule_pattern": "night_owl",
    },
    "private": {
        "summary": "A coder who builds things",
        "traits": ["builder"],
        "interests": ["python", "ml-project"],
        "deep_cuts": ["Starred rust repos despite coding in Python"],
    },
})


class TestDataFiltering:
    @pytest.mark.asyncio
    async def test_all_empty_returns_placeholder(self):
        """When all connector data is empty, return placeholder without calling Gemini."""
        svc = _make_llm_service()
        result = await svc.profile_analysis({"github": {}, "spotify": {}})
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_dossier()

    @pytest.mark.asyncio
    async def test_empty_dict_returns_placeholder(self):
        svc = _make_llm_service()
        result = await svc.profile_analysis({})
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_dossier()

    @pytest.mark.asyncio
    async def test_none_values_filtered_out(self):
        """None values should be treated as empty."""
        svc = _make_llm_service()
        result = await svc.profile_analysis({"github": None, "spotify": None})
        svc._llm.ainvoke.assert_not_called()
        assert result == _empty_dossier()

    @pytest.mark.asyncio
    async def test_partial_data_only_sends_populated(self):
        """Only populated connectors should be sent to Gemini."""
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = FAKE_GEMINI_RESPONSE
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result = await svc.profile_analysis({"github": SAMPLE_GITHUB, "spotify": {}})

        call_args = svc._llm.ainvoke.call_args[0][0]
        human_msg_content = call_args[1].content
        parsed = json.loads(human_msg_content)
        assert "github" in parsed
        assert "spotify" not in parsed
        assert result["data_sources"] == ["github"]

    @pytest.mark.asyncio
    async def test_three_sources_all_sent(self):
        """All three connectors should be sent when populated."""
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = FAKE_GEMINI_RESPONSE
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result = await svc.profile_analysis({
            "github": SAMPLE_GITHUB,
            "spotify": SAMPLE_SPOTIFY,
            "letterboxd": SAMPLE_LETTERBOXD,
        })

        call_args = svc._llm.ainvoke.call_args[0][0]
        human_msg_content = call_args[1].content
        parsed = json.loads(human_msg_content)
        assert "github" in parsed
        assert "spotify" in parsed
        assert "letterboxd" in parsed
        assert set(result["data_sources"]) == {"github", "spotify", "letterboxd"}


# ── unit: analyze_node with mocked LLMService ───────────────────

class TestAnalyzeNodeUnit:
    @pytest.mark.asyncio
    async def test_both_users_get_dossiers(self):
        fake_dossier = _empty_dossier()

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.profile_analysis = AsyncMock(return_value=fake_dossier)

            state = {
                "user_a": {"username": "alice", "raw_data": {"github": SAMPLE_GITHUB}},
                "user_b": {"username": "bob", "raw_data": {"spotify": SAMPLE_SPOTIFY}},
            }
            result = await analyze_node(state)

        assert result["user_a"]["dossier"] == fake_dossier
        assert result["user_b"]["dossier"] == fake_dossier

    @pytest.mark.asyncio
    async def test_preserves_original_user_data(self):
        fake_dossier = _empty_dossier()

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.profile_analysis = AsyncMock(return_value=fake_dossier)

            state = {
                "user_a": {"username": "alice", "raw_data": {"github": SAMPLE_GITHUB}},
                "user_b": {"username": "bob", "raw_data": {"spotify": SAMPLE_SPOTIFY}},
            }
            result = await analyze_node(state)

        assert result["user_a"]["username"] == "alice"
        assert result["user_a"]["raw_data"] == {"github": SAMPLE_GITHUB}
        assert result["user_b"]["username"] == "bob"
        assert result["user_b"]["raw_data"] == {"spotify": SAMPLE_SPOTIFY}

    @pytest.mark.asyncio
    async def test_calls_profile_analysis_for_each_user(self):
        fake_dossier = _empty_dossier()

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.profile_analysis = AsyncMock(return_value=fake_dossier)

            state = {
                "user_a": {"username": "alice", "raw_data": {"github": SAMPLE_GITHUB}},
                "user_b": {"username": "bob", "raw_data": {"spotify": SAMPLE_SPOTIFY}},
            }
            await analyze_node(state)

        assert instance.profile_analysis.call_count == 2
        instance.profile_analysis.assert_any_call({"github": SAMPLE_GITHUB})
        instance.profile_analysis.assert_any_call({"spotify": SAMPLE_SPOTIFY})

    @pytest.mark.asyncio
    async def test_handles_empty_state(self):
        fake_dossier = _empty_dossier()

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.profile_analysis = AsyncMock(return_value=fake_dossier)

            result = await analyze_node({})

        assert result["user_a"]["dossier"] == fake_dossier
        assert result["user_b"]["dossier"] == fake_dossier

    @pytest.mark.asyncio
    async def test_handles_missing_raw_data(self):
        fake_dossier = _empty_dossier()

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            instance = MockLLM.return_value
            instance.profile_analysis = AsyncMock(return_value=fake_dossier)

            state = {
                "user_a": {"username": "alice"},
                "user_b": {"username": "bob"},
            }
            result = await analyze_node(state)

        assert result["user_a"]["dossier"] == fake_dossier
        assert result["user_b"]["dossier"] == fake_dossier


# ── unit: JSON parsing edge cases ───────────────────────────────

class TestJSONParsing:
    @pytest.mark.asyncio
    async def test_handles_markdown_wrapped_json(self):
        """Gemini sometimes wraps JSON in ```json ... ``` fences."""
        svc = _make_llm_service()
        wrapped = '```json\n' + FAKE_GEMINI_RESPONSE + '\n```'
        fake_response = AsyncMock()
        fake_response.content = wrapped
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        result = await svc.profile_analysis({"github": SAMPLE_GITHUB})
        assert result["public"]["vibe"] == "Chill coder"
        assert result["data_sources"] == ["github"]

    @pytest.mark.asyncio
    async def test_raises_on_invalid_json(self):
        """Malformed JSON should raise, not silently fail."""
        svc = _make_llm_service()
        fake_response = AsyncMock()
        fake_response.content = "This is not JSON at all"
        svc._llm.ainvoke = AsyncMock(return_value=fake_response)

        with pytest.raises(json.JSONDecodeError):
            await svc.profile_analysis({"github": SAMPLE_GITHUB})


# ── integration: real Gemini calls ──────────────────────────────

def _assert_valid_dossier(dossier: dict, expected_sources: set[str] | None = None):
    """Validate a dossier has the correct public/private shape."""
    assert set(dossier.keys()) >= DOSSIER_TOP_KEYS

    pub = dossier["public"]
    assert isinstance(pub["vibe"], str)
    assert len(pub["vibe"]) > 5
    assert isinstance(pub["tags"], list)
    assert len(pub["tags"]) >= 3
    assert pub["schedule_pattern"] in ("night_owl", "early_bird", "mixed")

    priv = dossier["private"]
    assert isinstance(priv["summary"], str)
    assert len(priv["summary"]) > 10
    assert isinstance(priv["traits"], list)
    assert len(priv["traits"]) >= 1
    assert isinstance(priv["interests"], list)
    assert len(priv["interests"]) >= 1
    assert isinstance(priv["deep_cuts"], list)

    if expected_sources:
        assert set(dossier["data_sources"]) == expected_sources


@pytest.mark.integration
class TestProfileAnalysisIntegration:
    """Hit real Gemini API. Run with: pytest -m integration"""

    @pytest.mark.asyncio
    async def test_both_sources_produces_valid_dossier(self):
        svc = LLMService()
        result = await svc.profile_analysis({"github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY})
        _assert_valid_dossier(result, {"github", "spotify"})

    @pytest.mark.asyncio
    async def test_github_only_produces_valid_dossier(self):
        svc = LLMService()
        result = await svc.profile_analysis({"github": SAMPLE_GITHUB, "spotify": {}})
        _assert_valid_dossier(result, {"github"})

    @pytest.mark.asyncio
    async def test_spotify_only_produces_valid_dossier(self):
        svc = LLMService()
        result = await svc.profile_analysis({"github": {}, "spotify": SAMPLE_SPOTIFY})
        _assert_valid_dossier(result, {"spotify"})

    @pytest.mark.asyncio
    async def test_all_three_sources(self):
        svc = LLMService()
        result = await svc.profile_analysis({
            "github": SAMPLE_GITHUB,
            "spotify": SAMPLE_SPOTIFY,
            "letterboxd": SAMPLE_LETTERBOXD,
        })
        _assert_valid_dossier(result, {"github", "spotify", "letterboxd"})

    @pytest.mark.asyncio
    async def test_all_empty_returns_placeholder_no_api_call(self):
        svc = LLMService()
        result = await svc.profile_analysis({"github": {}, "spotify": {}})
        assert result == _empty_dossier()

    @pytest.mark.asyncio
    async def test_public_tags_are_broad_not_specific(self):
        """Public tags should be broad categories, not specific names."""
        svc = LLMService()
        result = await svc.profile_analysis({"github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY})
        tags = result["public"]["tags"]
        # Tags should be short and broad
        for tag in tags:
            assert len(tag) < 30, f"Tag too long (should be broad): {tag}"

    @pytest.mark.asyncio
    async def test_private_interests_are_specific(self):
        """Private interests should include specific names."""
        svc = LLMService()
        result = await svc.profile_analysis({"github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY})
        interests = result["private"]["interests"]
        assert len(interests) >= 3


@pytest.mark.integration
class TestAnalyzeNodeIntegration:
    @pytest.mark.asyncio
    async def test_full_node_both_users(self):
        state = {
            "user_a": {"username": "alice", "raw_data": {"github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY}},
            "user_b": {"username": "bob", "raw_data": {"github": SAMPLE_GITHUB}},
        }
        result = await analyze_node(state)

        for user_key in ("user_a", "user_b"):
            _assert_valid_dossier(result[user_key]["dossier"])

        assert result["user_a"]["username"] == "alice"
        assert result["user_b"]["username"] == "bob"

    @pytest.mark.asyncio
    async def test_full_node_all_three_sources(self):
        state = {
            "user_a": {"username": "alice", "raw_data": {
                "github": SAMPLE_GITHUB, "spotify": SAMPLE_SPOTIFY, "letterboxd": SAMPLE_LETTERBOXD,
            }},
            "user_b": {"username": "bob", "raw_data": {
                "github": SAMPLE_GITHUB, "letterboxd": SAMPLE_LETTERBOXD,
            }},
        }
        result = await analyze_node(state)

        _assert_valid_dossier(result["user_a"]["dossier"], {"github", "spotify", "letterboxd"})
        _assert_valid_dossier(result["user_b"]["dossier"], {"github", "letterboxd"})

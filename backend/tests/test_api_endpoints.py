"""Tests for the new frontend-facing API endpoints and helper services."""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.preview import (
    github_preview,
    letterboxd_preview,
    spotify_preview,
    instagram_preview,
    linkedin_preview,
    generate_preview,
)
from app.services.findings import generate_findings
from app.graph.nodes.ingest import _fetch_user_data


# ── Fake data ────────────────────────────────────────────────────

FAKE_GITHUB_DATA = {
    "languages": ["Python", "TypeScript", "Go"],
    "repos": [
        {"name": "ml-project", "description": "ML toolkit", "stars": 42, "language": "Python"},
        {"name": "web-app", "description": "Portfolio", "stars": 3, "language": "TypeScript"},
    ],
    "commit_hours": [14, 3, 22],
    "starred_topics": ["machine-learning"],
}

FAKE_LETTERBOXD_DATA = {
    "recent_films": [
        {"title": "Anora", "rating": 4.5, "link": "https://letterboxd.com/film/anora/"},
        {"title": "Past Lives", "rating": None, "link": "https://letterboxd.com/film/past-lives/"},
    ],
}

FAKE_SPOTIFY_DATA = {
    "top_artists": [
        {"name": "Khruangbin", "genres": ["funk"], "popularity": 72},
    ],
    "top_genres": ["funk", "soul"],
    "top_tracks": [{"name": "Evan Finds", "artist": "Khruangbin"}],
    "listening_hours": [22, 23],
}

FAKE_INSTAGRAM_DATA = {
    "bio": "Photographer | NYC based | archdigest.com",
    "screenshot_b64": "",
    "login_wall": False,
}

FAKE_LINKEDIN_DATA = {
    "name": "Jane Doe",
    "headline": "Senior Engineer at BigCo",
    "about": "Passionate about distributed systems.",
    "login_wall": False,
}

FAKE_DOSSIER = {
    "public": {
        "vibe": "Curious night-owl engineer",
        "tags": ["engineer", "cinephile", "music-nerd"],
        "schedule_pattern": "night_owl",
    },
    "private": {
        "summary": "Deep technical thinker",
        "traits": ["analytical", "creative"],
        "interests": ["machine learning", "indie film"],
        "deep_cuts": ["codes at 3am"],
    },
    "data_sources": ["github", "spotify", "letterboxd"],
}


# ── Preview generators ───────────────────────────────────────────

class TestPreviewGenerators:
    def test_github_preview_full(self):
        result = github_preview(FAKE_GITHUB_DATA)
        assert "2 repos" in result
        assert "Python" in result

    def test_github_preview_empty(self):
        result = github_preview({})
        assert "limited" in result.lower()

    def test_letterboxd_preview(self):
        result = letterboxd_preview(FAKE_LETTERBOXD_DATA)
        assert "2 films" in result

    def test_letterboxd_preview_empty(self):
        result = letterboxd_preview({})
        assert "limited" in result.lower()

    def test_spotify_preview(self):
        result = spotify_preview(FAKE_SPOTIFY_DATA)
        assert "Khruangbin" in result

    def test_spotify_preview_empty(self):
        result = spotify_preview({"top_artists": []})
        assert "limited" in result.lower()

    def test_instagram_preview_with_bio(self):
        result = instagram_preview(FAKE_INSTAGRAM_DATA)
        assert "Photographer" in result

    def test_instagram_preview_login_wall(self):
        result = instagram_preview({"login_wall": True, "bio": ""})
        assert "limited" in result.lower()

    def test_instagram_preview_long_bio(self):
        result = instagram_preview({"bio": "x" * 100, "login_wall": False})
        assert result.endswith("…")
        assert len(result) <= 52  # 50 + "…"

    def test_linkedin_preview_full(self):
        result = linkedin_preview(FAKE_LINKEDIN_DATA)
        assert "Jane Doe" in result
        assert "Senior Engineer" in result

    def test_linkedin_preview_login_wall(self):
        result = linkedin_preview({"login_wall": True})
        assert "limited" in result.lower()

    def test_generate_preview_unknown_service(self):
        result = generate_preview("unknown_service", {})
        assert result == "Connected"


# ── Findings generator ───────────────────────────────────────────

class TestFindingsGenerator:
    def test_generates_findings_for_each_source(self):
        raw_data = {
            "github": FAKE_GITHUB_DATA,
            "spotify": FAKE_SPOTIFY_DATA,
            "letterboxd": FAKE_LETTERBOXD_DATA,
        }
        findings = generate_findings(FAKE_DOSSIER, raw_data)
        labels = [f["label"] for f in findings]
        assert "Code" in labels
        assert "Music" in labels
        assert "Film" in labels

    def test_findings_have_required_fields(self):
        raw_data = {"github": FAKE_GITHUB_DATA}
        dossier = {**FAKE_DOSSIER, "data_sources": ["github"]}
        findings = generate_findings(dossier, raw_data)
        assert len(findings) == 1
        assert "label" in findings[0]
        assert "value" in findings[0]
        assert "detail" in findings[0]

    def test_empty_dossier_returns_empty(self):
        findings = generate_findings({"data_sources": []}, {})
        assert findings == []


# ── Ingest node ──────────────────────────────────────────────────

def _make_connector_cls(return_value=None, side_effect=None):
    """Create a mock connector class whose instances have a .fetch() AsyncMock."""
    mock = AsyncMock(return_value=return_value, side_effect=side_effect)

    class FakeConnector:
        async def fetch(self, identifier):
            return await mock(identifier)

    return FakeConnector, mock


class TestIngestNode:
    async def test_fetch_user_data_with_mocked_connectors(self):
        identifiers = {"github": "testuser", "letterboxd": "testuser"}

        GHCls, _ = _make_connector_cls(return_value=FAKE_GITHUB_DATA)
        LBCls, _ = _make_connector_cls(return_value=FAKE_LETTERBOXD_DATA)

        mock_map = {"github": GHCls, "letterboxd": LBCls}
        with patch.dict("app.graph.nodes.ingest.CONNECTOR_MAP", mock_map, clear=True):
            result = await _fetch_user_data(identifiers)

        assert "github" in result
        assert "letterboxd" in result
        assert result["github"]["languages"] == ["Python", "TypeScript", "Go"]

    async def test_fetch_user_data_skips_null_identifiers(self):
        identifiers = {"github": "testuser", "letterboxd": None, "instagram": None}

        GHCls, _ = _make_connector_cls(return_value=FAKE_GITHUB_DATA)
        mock_map = {"github": GHCls}
        with patch.dict("app.graph.nodes.ingest.CONNECTOR_MAP", mock_map, clear=True):
            result = await _fetch_user_data(identifiers)

        assert "github" in result
        assert "letterboxd" not in result

    async def test_fetch_user_data_handles_connector_failure(self):
        identifiers = {"github": "testuser"}

        GHCls, _ = _make_connector_cls(side_effect=Exception("API error"))
        mock_map = {"github": GHCls}
        with patch.dict("app.graph.nodes.ingest.CONNECTOR_MAP", mock_map, clear=True):
            result = await _fetch_user_data(identifiers)

        assert result == {}

    async def test_fetch_user_data_empty_identifiers(self):
        result = await _fetch_user_data({})
        assert result == {}


# ── API endpoint tests ───────────────────────────────────────────

@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestConnectEndpoint:
    async def test_connect_github(self, async_client):
        GHCls, _ = _make_connector_cls(return_value=FAKE_GITHUB_DATA)
        with patch.dict("app.main.CONNECTOR_MAP", {"github": GHCls}):
            resp = await async_client.post("/api/connect", json={
                "service": "github",
                "username": "testuser",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "2 repos" in data["preview"]

    async def test_connect_unknown_service(self, async_client):
        resp = await async_client.post("/api/connect", json={
            "service": "tiktok",
            "username": "test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False

    async def test_connect_handles_failure(self, async_client):
        GHCls, _ = _make_connector_cls(side_effect=Exception("timeout"))
        with patch.dict("app.main.CONNECTOR_MAP", {"github": GHCls}):
            resp = await async_client.post("/api/connect", json={
                "service": "github",
                "username": "testuser",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "limited" in data["preview"].lower()


class TestAnalyzeEndpoint:
    async def test_analyze_user(self, async_client):
        with patch("app.main._fetch_user_data", new_callable=AsyncMock) as mock_fetch, \
             patch("app.main.LLMService") as MockLLM:
            mock_fetch.return_value = {"github": FAKE_GITHUB_DATA}
            MockLLM.return_value.profile_analysis = AsyncMock(return_value=FAKE_DOSSIER)

            resp = await async_client.post("/api/analyze", json={
                "identifiers": {"github": "testuser"},
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["bio"] == "Curious night-owl engineer"
        assert "engineer" in data["tags"]
        assert data["schedule"] == "night_owl"
        assert len(data["findings"]) > 0


class TestMatchEndpoint:
    async def test_match_users(self, async_client):
        fake_crossref = {
            "shared": [{"signal": "film lovers", "detail": "both watch arthouse", "source": "letterboxd"}],
            "complementary": [{"signal": "different skills", "detail": "code vs design", "source": "github"}],
            "tension_points": [],
            "citations": ["Both rated Anora highly"],
        }

        with patch("app.main._fetch_user_data", new_callable=AsyncMock) as mock_fetch, \
             patch("app.main.LLMService") as MockLLM:
            mock_fetch.return_value = {"github": FAKE_GITHUB_DATA}
            MockLLM.return_value.profile_analysis = AsyncMock(return_value=FAKE_DOSSIER)
            MockLLM.return_value.cross_reference = AsyncMock(
                return_value=(fake_crossref, True)
            )

            resp = await async_client.post("/api/match", json={
                "user_a": {"github": "user1"},
                "user_b": {"github": "user2"},
            })

        assert resp.status_code == 200
        data = resp.json()
        assert "%" in data["compatibility"]
        assert "cross_ref" in data
        assert "public_profile" in data
        assert "private_profile" in data

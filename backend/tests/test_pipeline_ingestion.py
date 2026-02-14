"""End-to-end pipeline tests.

1. Unit test: fake data through ALL connectors → extract → build UserDataBundle
   → analyze_node (mocked LLM) → crossref_node (mocked LLM) → validate output shape
2. Integration tests: real API calls for connector subsets

These follow the same test patterns as test_github.py and test_spotify.py.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.connectors.github import GitHubConnector
from app.connectors.spotify import SpotifyConnector
from app.connectors.letterboxd import LetterboxdConnector
from app.connectors.linkedin import LinkedInConnector
from app.connectors.instagram import InstagramConnector
from app.graph.nodes.analyze import analyze_node
from app.graph.nodes.crossref import crossref_node
from app.models.state import PipelineState, UserDataBundle


# ── fake connector data (same shape as real output) ──────────────

FAKE_GITHUB_DATA = {
    "languages": ["Python", "TypeScript", "Go"],
    "repos": [
        {"name": "ml-project", "description": "ML toolkit", "stars": 42, "language": "Python"},
        {"name": "web-app", "description": "Portfolio", "stars": 3, "language": "TypeScript"},
    ],
    "commit_hours": [14, 3, 22, 10, 15],
    "starred_topics": ["machine-learning", "web", "rust"],
}

FAKE_SPOTIFY_DATA = {
    "top_artists": [
        {"name": "Khruangbin", "genres": ["psychedelic soul", "funk"], "popularity": 72},
        {"name": "Frank Ocean", "genres": ["r&b", "art pop"], "popularity": 88},
    ],
    "top_genres": ["psychedelic soul", "funk", "r&b", "art pop"],
    "top_tracks": [
        {"name": "Nights", "artist": "Frank Ocean"},
        {"name": "Evan Finds the Third Room", "artist": "Khruangbin"},
    ],
    "listening_hours": [22, 23, 1, 14],
}

FAKE_LETTERBOXD_DATA = {
    "recent_films": [
        {"title": "The Substance, 2024", "rating": 4.0, "link": "https://letterboxd.com/u/film/the-substance/"},
        {"title": "Anora, 2024", "rating": 4.5, "link": "https://letterboxd.com/u/film/anora/"},
        {"title": "Past Lives, 2023", "rating": None, "link": "https://letterboxd.com/u/film/past-lives/"},
    ],
}

FAKE_LINKEDIN_DATA = {
    "name": "Jane Doe",
    "headline": "Senior Engineer at BigCo",
    "about": "Passionate about distributed systems and open source.",
    "login_wall": False,
}

FAKE_INSTAGRAM_DATA = {
    "bio": "Photographer | NYC\narchdigest.com",
    "screenshot_b64": "iVBORw0KGgo=",  # tiny fake b64
    "login_wall": False,
}

FAKE_DOSSIER = {
    "public": {
        "vibe": "Curious night-owl engineer with eclectic taste",
        "tags": ["engineer", "cinephile", "music-nerd"],
        "schedule": "night_owl",
    },
    "private": {
        "summary": "Deep technical thinker with broad artistic interests",
        "traits": ["analytical", "creative", "introverted"],
        "interests": ["machine learning", "indie film", "psychedelic soul"],
        "deep_cuts": ["watches obscure arthouse films", "codes at 3am"],
    },
    "data_sources": ["github", "spotify", "letterboxd", "linkedin", "instagram"],
}

FAKE_CROSSREF = {
    "shared": [{"trait": "night owls"}, {"trait": "film lovers"}],
    "complementary": [{"trait": "one codes, one designs"}],
    "tension_points": [{"trait": "different music tastes"}],
    "citations": ["Both commit code after midnight", "Both rated Anora highly"],
    "venue_appropriate": True,
}


# ── helpers ──────────────────────────────────────────────────────

def _build_bundle(
    github=None, spotify=None, letterboxd=None, linkedin=None, instagram=None
) -> UserDataBundle:
    """Build a UserDataBundle from connector outputs."""
    return {
        "github": github or {},
        "spotify": spotify or {},
        "letterboxd": letterboxd or {},
        "linkedin": linkedin or {},
        "instagram": instagram or {},
        "books": {},
        "places": {},
    }


def _build_pipeline_state(bundle_a: dict, bundle_b: dict) -> PipelineState:
    """Build a PipelineState with two users ready for analyze."""
    return {
        "user_a": {"username": "user_a", "raw_data": bundle_a, "dossier": {}},
        "user_b": {"username": "user_b", "raw_data": bundle_b, "dossier": {}},
        "cross_ref": {},
        "venues": [],
        "coaching_a": {},
        "coaching_b": {},
        "include_venue": False,
        "error": None,
    }


def _validate_bundle_shape(bundle: dict) -> None:
    """Assert a bundle has correct shape for analyze/crossref."""
    for key in ("github", "letterboxd", "linkedin", "instagram"):
        assert key in bundle, f"Missing key: {key}"
        assert isinstance(bundle[key], dict), f"{key} should be a dict"


# ── Step 1: unit test connector extraction (fake data) ───────────

class TestConnectorExtraction:
    """Verify each connector's extract methods produce correct shapes from fake data."""

    def test_github_extraction(self):
        c = GitHubConnector()
        repos = c._extract_repos([
            {"name": "test", "description": "desc", "stargazers_count": 5, "language": "Python"},
        ])
        assert repos[0]["name"] == "test"
        assert repos[0]["stars"] == 5

    def test_spotify_extraction(self):
        c = SpotifyConnector(access_token="fake")
        artists = c._extract_artists({"items": [
            {"name": "TestArtist", "genres": ["pop"], "popularity": 50},
        ]})
        assert artists[0]["name"] == "TestArtist"

    def test_letterboxd_extraction(self):
        c = LetterboxdConnector()
        films = c._extract_films({"entries": [
            {"title": "Test Movie, 2024 - ★★★★", "link": "https://example.com", "letterboxd_memberrating": "4.0"},
        ]})
        assert films[0]["title"] == "Test Movie, 2024"
        assert films[0]["rating"] == 4.0

    def test_linkedin_extraction(self):
        c = LinkedInConnector()
        result = c._extract_profile_data({
            "name_text": "Test User",
            "meta_description": "Engineer at Co",
            "title": "Test User - Engineer | LinkedIn",
            "headline_text": "Engineer at Co",
        })
        assert result["name"] == "Test User"
        assert result["login_wall"] is False

    def test_instagram_extraction(self):
        c = InstagramConnector()
        result = c._extract_profile_data({
            "title": "testuser on Instagram",
            "bio_text": "Test bio",
            "screenshot_bytes": b"\x89PNG" + b"\x00" * 10,
        })
        assert result["bio"] == "Test bio"
        assert result["login_wall"] is False
        assert len(result["screenshot_b64"]) > 0


# ── Step 2: build UserDataBundle from fake connector outputs ─────

class TestBundleConstruction:
    def test_full_bundle_shape(self):
        bundle = _build_bundle(
            github=FAKE_GITHUB_DATA,
            spotify=FAKE_SPOTIFY_DATA,
            letterboxd=FAKE_LETTERBOXD_DATA,
            linkedin=FAKE_LINKEDIN_DATA,
            instagram=FAKE_INSTAGRAM_DATA,
        )
        _validate_bundle_shape(bundle)
        assert len(bundle["github"]["repos"]) == 2
        assert len(bundle["letterboxd"]["recent_films"]) == 3
        assert bundle["linkedin"]["name"] == "Jane Doe"

    def test_partial_bundle_still_valid(self):
        bundle = _build_bundle(github=FAKE_GITHUB_DATA)
        _validate_bundle_shape(bundle)

    def test_empty_bundle_shape(self):
        bundle = _build_bundle()
        _validate_bundle_shape(bundle)


# ── Step 3: analyze_node with mocked LLM ────────────────────────

class TestAnalyzeNodeWithFakeData:
    @pytest.mark.asyncio
    async def test_analyze_produces_dossiers(self):
        """Feed fake bundle through analyze_node, mock the LLM, verify dossiers."""
        bundle_a = _build_bundle(
            github=FAKE_GITHUB_DATA,
            spotify=FAKE_SPOTIFY_DATA,
            letterboxd=FAKE_LETTERBOXD_DATA,
            linkedin=FAKE_LINKEDIN_DATA,
            instagram=FAKE_INSTAGRAM_DATA,
        )
        bundle_b = _build_bundle(
            github=FAKE_GITHUB_DATA,
            letterboxd=FAKE_LETTERBOXD_DATA,
        )
        state = _build_pipeline_state(bundle_a, bundle_b)

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            mock_instance = MockLLM.return_value
            mock_instance.profile_analysis = AsyncMock(return_value=FAKE_DOSSIER)

            result = await analyze_node(state)

        assert "user_a" in result
        assert "user_b" in result
        assert result["user_a"]["dossier"] == FAKE_DOSSIER
        assert result["user_b"]["dossier"] == FAKE_DOSSIER
        # Raw data should be preserved
        assert result["user_a"]["raw_data"] == bundle_a

    @pytest.mark.asyncio
    async def test_analyze_calls_llm_for_each_user(self):
        bundle = _build_bundle(github=FAKE_GITHUB_DATA)
        state = _build_pipeline_state(bundle, bundle)

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            mock_instance = MockLLM.return_value
            mock_instance.profile_analysis = AsyncMock(return_value=FAKE_DOSSIER)

            await analyze_node(state)

        assert mock_instance.profile_analysis.call_count == 2


# ── Step 4: crossref_node with mocked LLM ───────────────────────

class TestCrossrefNodeWithFakeData:
    @pytest.mark.asyncio
    async def test_crossref_produces_result(self):
        """Feed fake dossiers through crossref_node, mock LLM, verify output."""
        state: PipelineState = {
            "user_a": {"username": "user_a", "raw_data": {}, "dossier": FAKE_DOSSIER},
            "user_b": {"username": "user_b", "raw_data": {}, "dossier": FAKE_DOSSIER},
            "cross_ref": {},
            "venues": [],
            "coaching_a": {},
            "coaching_b": {},
            "include_venue": False,
            "error": None,
        }

        # cross_reference returns (result_dict, venue_appropriate_bool)
        fake_crossref_no_venue = {k: v for k, v in FAKE_CROSSREF.items() if k != "venue_appropriate"}

        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            mock_instance = MockLLM.return_value
            mock_instance.cross_reference = AsyncMock(
                return_value=(fake_crossref_no_venue, True)
            )

            result = await crossref_node(state)

        assert "cross_ref" in result
        assert "include_venue" in result
        assert result["include_venue"] is True
        assert isinstance(result["cross_ref"]["shared"], list)
        assert isinstance(result["cross_ref"]["complementary"], list)
        assert isinstance(result["cross_ref"]["tension_points"], list)
        assert isinstance(result["cross_ref"]["citations"], list)


# ── Full pipeline: Steps 1→2→3→4 with fake data ─────────────────

class TestFullPipelineFakeData:
    @pytest.mark.asyncio
    async def test_ingest_to_crossref_full_pipeline(self):
        """
        End-to-end with fake data:
        1. Extract data from all connectors (fake)
        2. Build UserDataBundle
        3. Run analyze_node (mocked LLM)
        4. Run crossref_node (mocked LLM)
        5. Validate final output shape
        """
        # Step 1: "Ingest" — simulate connector extraction
        gh = GitHubConnector()
        sp = SpotifyConnector(access_token="fake")
        lb = LetterboxdConnector()
        li = LinkedInConnector()
        ig = InstagramConnector()

        # Run extraction methods on fake data (same as real connectors would)
        github_out = {
            "languages": gh._extract_languages([
                {"language": "Python"}, {"language": "Go"}, {"language": "Python"},
            ]),
            "repos": gh._extract_repos([
                {"name": "proj", "description": "My proj", "stargazers_count": 10, "language": "Python"},
            ]),
            "commit_hours": gh._extract_commit_hours([
                {"type": "PushEvent", "created_at": "2025-12-01T14:30:00Z"},
                {"type": "PushEvent", "created_at": "2025-12-01T03:15:00Z"},
            ]),
            "starred_topics": gh._extract_starred_topics([
                {"topics": ["ml", "python"]},
            ]),
        }
        spotify_out = {
            "top_artists": sp._extract_artists({"items": [
                {"name": "Khruangbin", "genres": ["funk"], "popularity": 72},
            ]}),
            "top_genres": sp._extract_top_genres({"items": [
                {"name": "Khruangbin", "genres": ["funk", "soul"]},
            ]}),
            "top_tracks": sp._extract_tracks({"items": [
                {"name": "Evan Finds", "artists": [{"name": "Khruangbin"}]},
            ]}),
            "listening_hours": sp._extract_listening_hours({"items": [
                {"played_at": "2025-12-01T22:30:00Z"},
            ]}),
        }
        letterboxd_out = {
            "recent_films": lb._extract_films({"entries": [
                {"title": "Anora, 2024 - ★★★★½", "link": "https://letterboxd.com/x", "letterboxd_memberrating": "4.5"},
                {"title": "Past Lives, 2023", "link": "https://letterboxd.com/y"},
            ]}),
        }
        linkedin_out = li._extract_profile_data({
            "name_text": "Jane Doe",
            "meta_description": "Engineer passionate about systems",
            "title": "Jane Doe | LinkedIn",
            "headline_text": "Senior Engineer",
        })
        instagram_out = ig._extract_profile_data({
            "title": "janedoe on Instagram",
            "bio_text": "Engineer | NYC",
            "screenshot_bytes": b"\x89PNG\x00" * 5,
        })

        # Step 2: Build bundles
        bundle_a = _build_bundle(
            github=github_out,
            spotify=spotify_out,
            letterboxd=letterboxd_out,
            linkedin=linkedin_out,
            instagram=instagram_out,
        )
        bundle_b = _build_bundle(
            github=github_out,
            letterboxd=letterboxd_out,
            linkedin=linkedin_out,
        )
        _validate_bundle_shape(bundle_a)
        _validate_bundle_shape(bundle_b)

        # Verify extracted data quality
        assert github_out["languages"] == ["Python", "Go"]
        assert len(github_out["repos"]) == 1
        assert github_out["commit_hours"] == [14, 3]
        assert letterboxd_out["recent_films"][0]["rating"] == 4.5
        assert letterboxd_out["recent_films"][1]["rating"] is None
        assert linkedin_out["name"] == "Jane Doe"
        assert instagram_out["login_wall"] is False

        # Step 3: Analyze
        state = _build_pipeline_state(bundle_a, bundle_b)

        with patch("app.graph.nodes.analyze.LLMService") as MockLLM:
            mock_instance = MockLLM.return_value
            mock_instance.profile_analysis = AsyncMock(return_value=FAKE_DOSSIER)
            analyzed = await analyze_node(state)

        assert analyzed["user_a"]["dossier"]["public"]["vibe"] != ""
        assert analyzed["user_b"]["dossier"]["public"]["vibe"] != ""
        assert analyzed["user_a"]["raw_data"] == bundle_a

        # Step 4: Crossref
        state_for_crossref: PipelineState = {
            **state,
            "user_a": analyzed["user_a"],
            "user_b": analyzed["user_b"],
        }

        fake_crossref_result = {
            "shared": [{"trait": "night owls"}],
            "complementary": [{"trait": "different skills"}],
            "tension_points": [],
            "citations": ["Both code late at night"],
        }

        with patch("app.graph.nodes.crossref.LLMService") as MockLLM:
            mock_instance = MockLLM.return_value
            mock_instance.cross_reference = AsyncMock(
                return_value=(fake_crossref_result, True)
            )
            crossref_result = await crossref_node(state_for_crossref)

        # Final validation
        assert crossref_result["include_venue"] is True
        assert len(crossref_result["cross_ref"]["shared"]) > 0
        assert isinstance(crossref_result["cross_ref"]["citations"], list)


# ── integration: real API calls ──────────────────────────────────

@pytest.mark.integration
class TestFullPipelineIntegration:
    """Real API calls for connectors (no Playwright — just GitHub + Letterboxd)."""

    @pytest.mark.asyncio
    async def test_two_bundles_ready_for_crossref(self):
        """Build two bundles from real APIs and verify shape."""
        github = GitHubConnector()
        letterboxd = LetterboxdConnector()

        gh_a = await github.fetch("pranavjain20")
        lb_a = await letterboxd.fetch("dave")
        gh_b = await github.fetch("Aditya-ice")
        lb_b = await letterboxd.fetch("davidehrlich")

        bundle_a = _build_bundle(
            github=gh_a,
            letterboxd=lb_a,
            linkedin={"name": "", "headline": "", "about": "", "login_wall": False},
            instagram={"bio": "", "screenshot_b64": "", "login_wall": False},
        )
        bundle_b = _build_bundle(
            github=gh_b,
            letterboxd=lb_b,
            linkedin={"name": "", "headline": "", "about": "", "login_wall": False},
            instagram={"bio": "", "screenshot_b64": "", "login_wall": False},
        )

        _validate_bundle_shape(bundle_a)
        _validate_bundle_shape(bundle_b)
        assert len(bundle_a["github"]["repos"]) > 0
        assert len(bundle_b["github"]["repos"]) > 0
        assert len(bundle_a["letterboxd"]["recent_films"]) > 0
        assert len(bundle_b["letterboxd"]["recent_films"]) > 0

"""Tests for the GitHub connector.

Unit tests exercise extraction logic with fake data.
Integration tests hit the real GitHub API (marked with @pytest.mark.integration).
"""

import pytest

from app.connectors.github import GitHubConnector


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def connector():
    return GitHubConnector()


FAKE_REPOS = [
    {
        "name": "ml-project",
        "description": "A machine learning toolkit",
        "stargazers_count": 42,
        "language": "Python",
        "topics": [],
    },
    {
        "name": "web-app",
        "description": "My portfolio site",
        "stargazers_count": 3,
        "language": "TypeScript",
        "topics": [],
    },
    {
        "name": "dotfiles",
        "description": None,
        "stargazers_count": 0,
        "language": None,
        "topics": [],
    },
    {
        "name": "another-py",
        "description": "Another Python repo",
        "stargazers_count": 1,
        "language": "Python",
        "topics": [],
    },
]

FAKE_EVENTS = [
    {"type": "PushEvent", "created_at": "2025-12-01T14:30:00Z"},
    {"type": "PushEvent", "created_at": "2025-12-01T03:15:00Z"},
    {"type": "WatchEvent", "created_at": "2025-12-01T10:00:00Z"},  # not a push
    {"type": "PushEvent", "created_at": "2025-12-02T22:45:00Z"},
    {"type": "CreateEvent", "created_at": "2025-12-02T08:00:00Z"},  # not a push
]

FAKE_STARRED = [
    {"topics": ["rust", "systems-programming", "cli"]},
    {"topics": ["machine-learning", "rust"]},  # "rust" is a duplicate
    {"topics": []},
    {"topics": ["web", "react"]},
]


# ── unit: _extract_languages ──────────────────────────────────────

class TestExtractLanguages:
    def test_deduplicates(self, connector):
        langs = connector._extract_languages(FAKE_REPOS)
        assert langs == ["Python", "TypeScript"]

    def test_skips_none(self, connector):
        langs = connector._extract_languages([{"language": None}])
        assert langs == []

    def test_empty_repos(self, connector):
        assert connector._extract_languages([]) == []

    def test_preserves_order(self, connector):
        repos = [
            {"language": "Go"},
            {"language": "Rust"},
            {"language": "Go"},
        ]
        assert connector._extract_languages(repos) == ["Go", "Rust"]


# ── unit: _extract_repos ──────────────────────────────────────────

class TestExtractRepos:
    def test_extracts_fields(self, connector):
        repos = connector._extract_repos(FAKE_REPOS)
        assert len(repos) == 4
        assert repos[0] == {
            "name": "ml-project",
            "description": "A machine learning toolkit",
            "stars": 42,
            "language": "Python",
        }

    def test_null_description_becomes_empty_string(self, connector):
        repos = connector._extract_repos(FAKE_REPOS)
        assert repos[2]["description"] == ""

    def test_null_language_becomes_empty_string(self, connector):
        repos = connector._extract_repos(FAKE_REPOS)
        assert repos[2]["language"] == ""

    def test_empty_list(self, connector):
        assert connector._extract_repos([]) == []


# ── unit: _extract_commit_hours ───────────────────────────────────

class TestExtractCommitHours:
    def test_extracts_push_event_hours(self, connector):
        hours = connector._extract_commit_hours(FAKE_EVENTS)
        assert hours == [14, 3, 22]

    def test_ignores_non_push_events(self, connector):
        events = [{"type": "WatchEvent", "created_at": "2025-12-01T10:00:00Z"}]
        assert connector._extract_commit_hours(events) == []

    def test_empty_events(self, connector):
        assert connector._extract_commit_hours([]) == []

    def test_missing_created_at(self, connector):
        events = [{"type": "PushEvent"}]
        assert connector._extract_commit_hours(events) == []


# ── unit: _extract_starred_topics ─────────────────────────────────

class TestExtractStarredTopics:
    def test_deduplicates(self, connector):
        topics = connector._extract_starred_topics(FAKE_STARRED)
        assert "rust" in topics
        assert topics.count("rust") == 1

    def test_all_topics_present(self, connector):
        topics = connector._extract_starred_topics(FAKE_STARRED)
        expected = {"rust", "systems-programming", "cli", "machine-learning", "web", "react"}
        assert set(topics) == expected

    def test_preserves_order(self, connector):
        topics = connector._extract_starred_topics(FAKE_STARRED)
        assert topics[0] == "rust"
        assert topics[1] == "systems-programming"

    def test_empty_starred(self, connector):
        assert connector._extract_starred_topics([]) == []

    def test_all_empty_topics(self, connector):
        assert connector._extract_starred_topics([{"topics": []}, {"topics": []}]) == []


# ── integration: real API calls ───────────────────────────────────

@pytest.mark.integration
class TestGitHubIntegration:
    """Hit real GitHub API. Run with: pytest -m integration"""

    @pytest.mark.asyncio
    async def test_fetch_real_user(self, connector):
        """Fetch a well-known user and verify output shape."""
        result = await connector.fetch("torvalds")

        assert isinstance(result["languages"], list)
        assert isinstance(result["repos"], list)
        assert isinstance(result["commit_hours"], list)
        assert isinstance(result["starred_topics"], list)

        # torvalds definitely has repos
        assert len(result["repos"]) > 0
        # each repo has the right shape
        repo = result["repos"][0]
        assert "name" in repo
        assert "description" in repo
        assert "stars" in repo
        assert "language" in repo

    @pytest.mark.asyncio
    async def test_fetch_nonexistent_user(self, connector):
        """Nonexistent user should return empty lists, not crash."""
        result = await connector.fetch("thisuser-definitely-does-not-exist-zzzzz999")

        assert result["languages"] == []
        assert result["repos"] == []
        assert result["commit_hours"] == []
        assert result["starred_topics"] == []

    @pytest.mark.asyncio
    async def test_fetch_strips_at_sign(self, connector):
        """Should handle '@torvalds' the same as 'torvalds'."""
        result = await connector.fetch("@torvalds")
        assert len(result["repos"]) > 0

    @pytest.mark.asyncio
    async def test_fetch_strips_whitespace(self, connector):
        """Should handle '  torvalds  ' the same as 'torvalds'."""
        result = await connector.fetch("  torvalds  ")
        assert len(result["repos"]) > 0

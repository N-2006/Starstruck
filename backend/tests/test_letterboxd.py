"""Tests for the Letterboxd connector.

Unit tests exercise extraction logic with fake RSS data.
Integration tests hit the real Letterboxd RSS feed (marked with @pytest.mark.integration).
"""

import pytest

from app.connectors.letterboxd import LetterboxdConnector


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def connector():
    return LetterboxdConnector()


FAKE_ENTRIES_RATED = [
    {
        "title": "The Substance, 2024 - ★★★★",
        "link": "https://letterboxd.com/user/film/the-substance-2024/",
        "letterboxd_memberrating": "4.0",
    },
    {
        "title": "Anora, 2024 - ★★★★½",
        "link": "https://letterboxd.com/user/film/anora-2024/",
        "letterboxd_memberrating": "4.5",
    },
    {
        "title": "Nosferatu, 2024 - ★★★",
        "link": "https://letterboxd.com/user/film/nosferatu-2024/",
        "letterboxd_memberrating": "3.0",
    },
]

FAKE_ENTRIES_MIXED = [
    {
        "title": "Dune: Part Two, 2024 - ★★★★★",
        "link": "https://letterboxd.com/user/film/dune-part-two/",
        "letterboxd_memberrating": "5.0",
    },
    {
        # No rating — just a log
        "title": "Past Lives, 2023",
        "link": "https://letterboxd.com/user/film/past-lives/",
    },
    {
        # Half star rating, no memberrating field
        "title": "Some Movie, 2024 - ★½",
        "link": "https://letterboxd.com/user/film/some-movie/",
    },
]

FAKE_FEED_RATED = {"entries": FAKE_ENTRIES_RATED}
FAKE_FEED_MIXED = {"entries": FAKE_ENTRIES_MIXED}
FAKE_FEED_EMPTY = {"entries": []}


# ── unit: _extract_films ─────────────────────────────────────────

class TestExtractFilms:
    def test_extracts_all_films(self, connector):
        films = connector._extract_films(FAKE_FEED_RATED)
        assert len(films) == 3

    def test_extracts_title_without_rating(self, connector):
        films = connector._extract_films(FAKE_FEED_RATED)
        assert films[0]["title"] == "The Substance, 2024"
        assert films[1]["title"] == "Anora, 2024"

    def test_extracts_link(self, connector):
        films = connector._extract_films(FAKE_FEED_RATED)
        assert films[0]["link"] == "https://letterboxd.com/user/film/the-substance-2024/"

    def test_extracts_rating_from_memberrating(self, connector):
        films = connector._extract_films(FAKE_FEED_RATED)
        assert films[0]["rating"] == 4.0
        assert films[1]["rating"] == 4.5
        assert films[2]["rating"] == 3.0

    def test_empty_feed(self, connector):
        films = connector._extract_films(FAKE_FEED_EMPTY)
        assert films == []

    def test_empty_dict(self, connector):
        films = connector._extract_films({})
        assert films == []

    def test_no_rating_returns_none(self, connector):
        films = connector._extract_films(FAKE_FEED_MIXED)
        # "Past Lives, 2023" has no rating
        assert films[1]["rating"] is None
        assert films[1]["title"] == "Past Lives, 2023"

    def test_caps_at_20_entries(self, connector):
        big_feed = {"entries": [
            {"title": f"Film {i}, 2024", "link": f"https://example.com/{i}"}
            for i in range(30)
        ]}
        films = connector._extract_films(big_feed)
        assert len(films) == 20


# ── unit: _parse_rating ──────────────────────────────────────────

class TestParseRating:
    def test_numeric_memberrating(self, connector):
        entry = {"title": "Whatever - ★★★", "letterboxd_memberrating": "3.5"}
        assert connector._parse_rating(entry) == 3.5

    def test_star_fallback_full_stars(self, connector):
        entry = {"title": "Movie - ★★★★"}
        assert connector._parse_rating(entry) == 4.0

    def test_star_fallback_half_star(self, connector):
        entry = {"title": "Movie - ★★★½"}
        assert connector._parse_rating(entry) == 3.5

    def test_no_rating(self, connector):
        entry = {"title": "Movie, 2024"}
        assert connector._parse_rating(entry) is None

    def test_empty_entry(self, connector):
        assert connector._parse_rating({}) is None

    def test_invalid_memberrating_falls_to_stars(self, connector):
        entry = {"title": "Movie - ★★", "letterboxd_memberrating": "not-a-number"}
        assert connector._parse_rating(entry) == 2.0

    def test_five_stars(self, connector):
        entry = {"title": "Masterpiece - ★★★★★", "letterboxd_memberrating": "5.0"}
        assert connector._parse_rating(entry) == 5.0

    def test_half_star_only(self, connector):
        entry = {"title": "Bad Movie - ½"}
        assert connector._parse_rating(entry) == 0.5


# ── unit: full extraction with realistic feed shape ──────────────

class TestFullExtraction:
    def test_output_shape(self, connector):
        films = connector._extract_films(FAKE_FEED_RATED)
        for film in films:
            assert "title" in film
            assert "rating" in film
            assert "link" in film
            assert isinstance(film["title"], str)
            assert isinstance(film["link"], str)
            assert isinstance(film["rating"], (float, int, type(None)))

    def test_mixed_feed_all_present(self, connector):
        films = connector._extract_films(FAKE_FEED_MIXED)
        assert len(films) == 3
        # First has rating, second doesn't, third uses star fallback
        assert films[0]["rating"] == 5.0
        assert films[1]["rating"] is None
        assert films[2]["rating"] == 1.5  # ★½


# ── integration: real RSS feed ───────────────────────────────────

@pytest.mark.integration
class TestLetterboxdIntegration:
    """Hit real Letterboxd RSS. Run with: pytest -m integration"""

    @pytest.mark.asyncio
    async def test_fetch_real_user(self, connector):
        """Fetch a known active user and verify output shape."""
        result = await connector.fetch("dave")

        assert isinstance(result["recent_films"], list)
        # dave is very active on Letterboxd
        assert len(result["recent_films"]) > 0

        film = result["recent_films"][0]
        assert "title" in film
        assert "rating" in film
        assert "link" in film
        assert isinstance(film["title"], str)
        assert len(film["title"]) > 0

    @pytest.mark.asyncio
    async def test_fetch_nonexistent_user(self, connector):
        """Nonexistent user should return empty list, not crash."""
        result = await connector.fetch("thisuser-definitely-does-not-exist-zzzzz999")
        assert result["recent_films"] == []

    @pytest.mark.asyncio
    async def test_fetch_strips_whitespace(self, connector):
        """Should handle '  username  ' gracefully."""
        result = await connector.fetch("  dave  ")
        assert isinstance(result["recent_films"], list)

    @pytest.mark.asyncio
    async def test_fetch_strips_at_sign(self, connector):
        """Should handle '@username' gracefully."""
        result = await connector.fetch("@dave")
        assert isinstance(result["recent_films"], list)

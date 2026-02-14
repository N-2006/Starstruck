"""Tests for the LinkedIn connector.

Unit tests exercise extraction logic with fake page data.
Integration tests hit real LinkedIn (marked with @pytest.mark.integration).
"""

import pytest

from app.connectors.linkedin import LinkedInConnector


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def connector():
    return LinkedInConnector()


FAKE_PROFILE_FULL = {
    "name_text": "Jane Doe",
    "meta_description": "Senior Engineer at BigCo. Passionate about distributed systems and open source.",
    "title": "Jane Doe - Senior Engineer - BigCo | LinkedIn",
    "headline_text": "Senior Engineer at BigCo",
    "final_url": "https://www.linkedin.com/in/janedoe/",
}

FAKE_PROFILE_LOGIN_WALL = {
    "name_text": "",
    "meta_description": "",
    "title": "Sign In | LinkedIn",
    "headline_text": "",
    "final_url": "https://www.linkedin.com/authwall",
}

FAKE_PROFILE_SIGNUP_WALL = {
    "name_text": "Join LinkedIn",
    "meta_description": "750 million+ members | Manage your professional identity.",
    "title": "Sign Up | LinkedIn",
    "headline_text": "",
    "final_url": "https://www.linkedin.com/authwall?trk=gf&sessionRedirect=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fsomeuser%2F",
}

FAKE_PROFILE_PARTIAL = {
    "name_text": "",
    "meta_description": "Some info about this person from meta tag.",
    "title": "John Smith - Product Manager | LinkedIn",
    "headline_text": "",
    "final_url": "https://www.linkedin.com/in/johnsmith/",
}

FAKE_PROFILE_EMPTY = {
    "name_text": "",
    "meta_description": "",
    "title": "",
    "headline_text": "",
    "final_url": "",
}


# ── unit: _extract_profile_data ──────────────────────────────────

class TestExtractProfileData:
    def test_full_profile(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert result["name"] == "Jane Doe"
        assert result["headline"] == "Senior Engineer at BigCo"
        assert "distributed systems" in result["about"]
        assert result["login_wall"] is False

    def test_login_wall_detected(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert result["login_wall"] is True
        assert result["name"] == ""
        assert result["about"] == ""

    def test_partial_data_extracts_what_it_can(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_PARTIAL)
        assert result["login_wall"] is False
        # Name should be extracted from title when name_text is empty
        assert result["name"] == "John Smith"
        assert "Some info" in result["about"]

    def test_empty_profile(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_EMPTY)
        assert result["name"] == ""
        assert result["headline"] == ""
        assert result["about"] == ""
        assert result["login_wall"] is False

    def test_empty_dict(self, connector):
        result = connector._extract_profile_data({})
        assert result["name"] == ""
        assert result["headline"] == ""
        assert result["about"] == ""


# ── unit: output shape ───────────────────────────────────────────

class TestOutputShape:
    def test_all_keys_present(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert "name" in result
        assert "headline" in result
        assert "about" in result
        assert "login_wall" in result

    def test_all_values_correct_type(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert isinstance(result["name"], str)
        assert isinstance(result["headline"], str)
        assert isinstance(result["about"], str)
        assert isinstance(result["login_wall"], bool)

    def test_login_wall_all_strings(self, connector):
        """Even on login wall, string fields should be strings not None."""
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert isinstance(result["name"], str)
        assert isinstance(result["headline"], str)
        assert isinstance(result["about"], str)


# ── unit: name extraction from title ─────────────────────────────

class TestNameFromTitle:
    def test_name_from_title_with_dash(self, connector):
        raw = {"name_text": "", "meta_description": "", "title": "Alice Bob - Engineer | LinkedIn", "headline_text": "", "final_url": "https://www.linkedin.com/in/alicebob/"}
        result = connector._extract_profile_data(raw)
        assert result["name"] == "Alice Bob"

    def test_no_name_when_login_wall(self, connector):
        """Login wall title should not be parsed as a name."""
        raw = {"name_text": "", "meta_description": "", "title": "Sign In | LinkedIn", "headline_text": "", "final_url": ""}
        result = connector._extract_profile_data(raw)
        assert result["name"] == ""

    def test_name_text_takes_priority(self, connector):
        """If name_text is present, don't fall back to title."""
        raw = {"name_text": "Real Name", "meta_description": "", "title": "Different Name - X | LinkedIn", "headline_text": "", "final_url": "https://www.linkedin.com/in/realname/"}
        result = connector._extract_profile_data(raw)
        assert result["name"] == "Real Name"


# ── unit: auth wall detection ────────────────────────────────────

class TestAuthWallDetection:
    def test_sign_in_detected(self, connector):
        raw = {"name_text": "", "meta_description": "", "title": "Sign In | LinkedIn", "headline_text": "", "final_url": ""}
        assert connector._extract_profile_data(raw)["login_wall"] is True

    def test_sign_up_detected(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_SIGNUP_WALL)
        assert result["login_wall"] is True
        assert result["name"] == ""
        assert result["about"] == ""

    def test_authwall_url_detected(self, connector):
        raw = {"name_text": "", "meta_description": "", "title": "Some Page", "headline_text": "", "final_url": "https://www.linkedin.com/authwall?trk=gf"}
        assert connector._extract_profile_data(raw)["login_wall"] is True

    def test_join_linkedin_in_h1_detected(self, connector):
        raw = {"name_text": "Join LinkedIn", "meta_description": "", "title": "Whatever", "headline_text": "", "final_url": ""}
        assert connector._extract_profile_data(raw)["login_wall"] is True

    def test_normal_profile_not_flagged(self, connector):
        assert connector._extract_profile_data(FAKE_PROFILE_FULL)["login_wall"] is False


# ── integration: real LinkedIn ───────────────────────────────────

@pytest.mark.integration
class TestLinkedInIntegration:
    """Hit real LinkedIn. Run with: pytest -m integration

    Note: LinkedIn aggressively blocks bots. These tests may hit login walls.
    That's expected — we verify graceful degradation.
    """

    @pytest.mark.asyncio
    async def test_fetch_real_profile(self, connector):
        """Fetch a real profile — may hit login wall, that's OK."""
        result = await connector.fetch("williamhgates")

        # Output shape is always correct
        assert isinstance(result["name"], str)
        assert isinstance(result["headline"], str)
        assert isinstance(result["about"], str)
        assert isinstance(result["login_wall"], bool)

    @pytest.mark.asyncio
    async def test_fetch_graceful_on_nonexistent(self, connector):
        """Nonexistent user should return empty data, not crash."""
        result = await connector.fetch("thisuser-definitely-does-not-exist-zzzzz999")
        assert isinstance(result["name"], str)
        assert isinstance(result["login_wall"], bool)

    @pytest.mark.asyncio
    async def test_fetch_strips_whitespace(self, connector):
        result = await connector.fetch("  williamhgates  ")
        assert isinstance(result["name"], str)

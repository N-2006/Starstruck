"""Tests for the Instagram connector.

Unit tests exercise extraction logic with fake page data.
Integration tests hit real Instagram (marked with @pytest.mark.integration).
"""

import base64

import pytest

from app.connectors.instagram import InstagramConnector


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def connector():
    return InstagramConnector()


FAKE_SCREENSHOT = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # fake PNG bytes

FAKE_PROFILE_FULL = {
    "title": "archdigest on Instagram",
    "bio_text": "Architectural Digest\nThe international design authority.\narchdigest.com",
    "screenshot_bytes": FAKE_SCREENSHOT,
    "final_url": "https://www.instagram.com/archdigest/",
    "meta_description": "",
}

FAKE_PROFILE_LOGIN_WALL = {
    "title": "Instagram",
    "bio_text": "",
    "screenshot_bytes": b"\x89PNG" + b"\x00" * 50,
    "final_url": "https://www.instagram.com/accounts/login/?next=...",
    "meta_description": "Create an account or log in to Instagram",
}

FAKE_PROFILE_LOGIN_WALL_WITH_META = {
    "title": "Instagram",
    "bio_text": "",
    "screenshot_bytes": b"\x89PNG" + b"\x00" * 50,
    "final_url": "https://www.instagram.com/accounts/login/?next=...",
    "meta_description": "1,234 Followers, 567 Following, 89 Posts - See Instagram photos and videos from @someuser",
}

FAKE_PROFILE_PARTIAL = {
    "title": "someuser on Instagram",
    "bio_text": "",
    "screenshot_bytes": FAKE_SCREENSHOT,
    "final_url": "https://www.instagram.com/someuser/",
    "meta_description": "",
}

FAKE_PROFILE_EMPTY = {
    "title": "",
    "bio_text": "",
    "screenshot_bytes": b"",
    "final_url": "",
    "meta_description": "",
}


# ── unit: _extract_profile_data ──────────────────────────────────

class TestExtractProfileData:
    def test_full_profile(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert "Architectural Digest" in result["bio"]
        assert len(result["screenshot_b64"]) > 0
        assert result["login_wall"] is False

    def test_login_wall_detected(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert result["login_wall"] is True
        assert result["bio"] == ""  # meta has "log in" so gets filtered
        assert result["screenshot_b64"] == ""  # screenshot dropped on login wall

    def test_partial_data(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_PARTIAL)
        assert result["bio"] == ""
        assert len(result["screenshot_b64"]) > 0
        assert result["login_wall"] is False

    def test_empty_profile(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_EMPTY)
        assert result["bio"] == ""
        assert result["screenshot_b64"] == ""
        assert result["login_wall"] is False

    def test_empty_dict(self, connector):
        result = connector._extract_profile_data({})
        assert result["bio"] == ""
        assert result["screenshot_b64"] == ""


# ── unit: screenshot encoding ────────────────────────────────────

class TestScreenshotEncoding:
    def test_screenshot_roundtrips(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        decoded = base64.b64decode(result["screenshot_b64"])
        assert decoded == FAKE_SCREENSHOT

    def test_empty_screenshot_stays_empty(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert result["screenshot_b64"] == ""

    def test_none_screenshot_bytes(self, connector):
        raw = {"title": "", "bio_text": "", "screenshot_bytes": None, "final_url": "", "meta_description": ""}
        result = connector._extract_profile_data(raw)
        assert result["screenshot_b64"] == ""


# ── unit: output shape ───────────────────────────────────────────

class TestOutputShape:
    def test_all_keys_present(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert "bio" in result
        assert "screenshot_b64" in result
        assert "login_wall" in result

    def test_all_values_correct_type(self, connector):
        result = connector._extract_profile_data(FAKE_PROFILE_FULL)
        assert isinstance(result["bio"], str)
        assert isinstance(result["screenshot_b64"], str)
        assert isinstance(result["login_wall"], bool)

    def test_login_wall_values_are_strings(self, connector):
        """Even on login wall, string fields should be strings not None."""
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert isinstance(result["bio"], str)
        assert isinstance(result["screenshot_b64"], str)


# ── unit: login wall detection ───────────────────────────────────

class TestLoginWallDetection:
    def test_login_in_title(self, connector):
        raw = {"title": "Login • Instagram", "bio_text": "", "screenshot_bytes": b"", "final_url": "", "meta_description": ""}
        assert connector._extract_profile_data(raw)["login_wall"] is True

    def test_accounts_login_in_url(self, connector):
        raw = {"title": "Instagram", "bio_text": "", "screenshot_bytes": b"", "final_url": "https://www.instagram.com/accounts/login/?next=...", "meta_description": ""}
        assert connector._extract_profile_data(raw)["login_wall"] is True

    def test_normal_title_no_wall(self, connector):
        raw = {"title": "user on Instagram", "bio_text": "", "screenshot_bytes": b"", "final_url": "https://www.instagram.com/user/", "meta_description": ""}
        assert connector._extract_profile_data(raw)["login_wall"] is False

    def test_login_wall_with_useful_meta(self, connector):
        """When login wall but og:description has follower info, use it as bio."""
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL_WITH_META)
        assert result["login_wall"] is True
        assert "1,234 Followers" in result["bio"]

    def test_login_wall_screenshot_dropped(self, connector):
        """Screenshot should be empty string on login wall (it's just the login page)."""
        result = connector._extract_profile_data(FAKE_PROFILE_LOGIN_WALL)
        assert result["screenshot_b64"] == ""


# ── integration: real Instagram ──────────────────────────────────

@pytest.mark.integration
class TestInstagramIntegration:
    """Hit real Instagram. Run with: pytest -m integration

    Note: Instagram blocks bots aggressively. Login walls are expected.
    We verify graceful degradation.
    """

    @pytest.mark.asyncio
    async def test_fetch_real_profile(self, connector):
        """Fetch a real public profile — may hit login wall."""
        result = await connector.fetch("archdigest")

        assert isinstance(result["bio"], str)
        assert isinstance(result["screenshot_b64"], str)
        assert isinstance(result["login_wall"], bool)

    @pytest.mark.asyncio
    async def test_fetch_graceful_on_nonexistent(self, connector):
        """Nonexistent user should return empty data, not crash."""
        result = await connector.fetch("thisuser_definitely_does_not_exist_zzz999")
        assert isinstance(result["bio"], str)
        assert isinstance(result["login_wall"], bool)

    @pytest.mark.asyncio
    async def test_fetch_strips_whitespace(self, connector):
        result = await connector.fetch("  archdigest  ")
        assert isinstance(result["bio"], str)

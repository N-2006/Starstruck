from __future__ import annotations

import asyncio
from typing import Any

from playwright.async_api import async_playwright

from app.connectors.base import BaseConnector

PROFILE_URL = "https://www.linkedin.com/in/{username}/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Keywords that indicate we've been blocked by an auth wall
_AUTH_WALL_KEYWORDS = ("Sign In", "Sign Up", "Login", "Join LinkedIn", "authwall")


class LinkedInConnector(BaseConnector):
    """Scrape a public LinkedIn profile for basic info."""

    async def fetch(self, identifier: str) -> dict[str, Any]:
        username = identifier.strip().lstrip("@")
        page_content = await self._fetch_profile(username)
        return self._extract_profile_data(page_content)

    # ── data fetching ──────────────────────────────────────────────

    async def _fetch_profile(self, username: str) -> dict:
        """Launch headless browser and grab raw page data.

        Returns a dict with raw extracted fields; empty strings on failure.
        """
        url = PROFILE_URL.format(username=username)
        result: dict[str, str] = {
            "name_text": "",
            "meta_description": "",
            "title": "",
            "headline_text": "",
            "final_url": "",
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=USER_AGENT)
                page = await context.new_page()
                try:
                    # Use networkidle to wait for redirects to settle
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=15000)
                    except Exception:
                        pass

                    # Give redirects a moment to settle
                    await asyncio.sleep(1)

                    result["final_url"] = page.url
                    result["title"] = await page.title()

                    # Name — usually in h1
                    try:
                        name_el = await page.wait_for_selector("h1", timeout=5000)
                        if name_el:
                            result["name_text"] = (await name_el.inner_text()).strip()
                    except Exception:
                        pass

                    # Meta description often contains the bio/headline
                    try:
                        meta = await page.query_selector('meta[name="description"]')
                        if meta:
                            result["meta_description"] = (
                                await meta.get_attribute("content") or ""
                            )
                    except Exception:
                        pass

                    # Headline — the text right below the name
                    try:
                        headline_el = await page.query_selector(
                            ".top-card-layout__headline"
                        )
                        if headline_el:
                            result["headline_text"] = (
                                await headline_el.inner_text()
                            ).strip()
                    except Exception:
                        pass

                finally:
                    await browser.close()
        except Exception:
            pass

        return result

    # ── data extraction ────────────────────────────────────────────

    @staticmethod
    def _extract_profile_data(raw: dict) -> dict[str, Any]:
        """Turn raw page scrape into a clean profile dict."""
        title = raw.get("title", "")
        final_url = raw.get("final_url", "")

        # Detect auth wall from title, h1 text, or redirect URL
        hit_login_wall = (
            any(kw in title for kw in _AUTH_WALL_KEYWORDS)
            or any(kw in raw.get("name_text", "") for kw in ("Join LinkedIn", "Sign"))
            or "authwall" in final_url
        )

        name = raw.get("name_text", "")
        meta = raw.get("meta_description", "")
        headline = raw.get("headline_text", "")

        # If we hit the login wall, don't trust the scraped name/meta
        if hit_login_wall:
            name = ""
            headline = ""
            meta = ""

        # If no name from h1, try extracting from page title
        # e.g. "John Doe - Software Engineer | LinkedIn"
        if not name and title and not hit_login_wall:
            name = title.split(" - ")[0].strip() if " - " in title else ""

        # Meta description often has "about" info
        about = meta if meta else ""

        return {
            "name": name,
            "headline": headline,
            "about": about,
            "login_wall": hit_login_wall,
        }

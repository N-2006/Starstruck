from __future__ import annotations

import asyncio
import base64
from typing import Any

from playwright.async_api import async_playwright

from app.connectors.base import BaseConnector

PROFILE_URL = "https://www.instagram.com/{username}/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_LOGIN_KEYWORDS = ("Login", "login", "Log in", "accounts/login", "Log into")


class InstagramConnector(BaseConnector):
    """Scrape a public Instagram profile for bio and a screenshot."""

    async def fetch(self, identifier: str) -> dict[str, Any]:
        username = identifier.strip().lstrip("@")
        page_data = await self._fetch_profile(username)
        return self._extract_profile_data(page_data)

    # ── data fetching ──────────────────────────────────────────────

    async def _fetch_profile(self, username: str) -> dict:
        """Launch headless browser and grab raw page data + screenshot."""
        url = PROFILE_URL.format(username=username)
        result: dict[str, Any] = {
            "title": "",
            "bio_text": "",
            "screenshot_bytes": b"",
            "final_url": "",
            "meta_description": "",
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=USER_AGENT)
                page = await context.new_page()
                try:
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=20000)
                    except Exception:
                        pass

                    await asyncio.sleep(1)

                    result["title"] = await page.title()
                    result["final_url"] = page.url

                    # Bio text — in header section (only works if profile loaded)
                    try:
                        bio_el = await page.wait_for_selector(
                            "header section", timeout=5000
                        )
                        if bio_el:
                            result["bio_text"] = (await bio_el.inner_text()).strip()
                    except Exception:
                        pass

                    # Fallback: meta description sometimes has bio info
                    try:
                        meta = await page.query_selector(
                            'meta[property="og:description"]'
                        )
                        if meta:
                            result["meta_description"] = (
                                await meta.get_attribute("content") or ""
                            )
                    except Exception:
                        pass

                    # Screenshot of the viewport
                    try:
                        result["screenshot_bytes"] = await page.screenshot(
                            full_page=False
                        )
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
        """Turn raw page scrape into clean profile dict."""
        title = raw.get("title", "")
        final_url = raw.get("final_url", "")

        # Detect login wall from title, URL redirect, or page content
        hit_login_wall = (
            any(kw in title for kw in _LOGIN_KEYWORDS)
            or "accounts/login" in final_url
        )

        bio = raw.get("bio_text", "")
        meta_desc = raw.get("meta_description", "")
        screenshot_bytes = raw.get("screenshot_bytes", b"")

        # If login wall, don't trust scraped data
        if hit_login_wall:
            bio = ""
            # But meta_description might still have useful info from og tags
            # e.g. "1,234 Followers, 567 Following, 89 Posts - See Instagram photos..."
            if meta_desc and "log in" not in meta_desc.lower():
                bio = meta_desc

        screenshot_b64 = ""
        if screenshot_bytes and not hit_login_wall:
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        return {
            "bio": bio,
            "screenshot_b64": screenshot_b64,
            "login_wall": hit_login_wall,
        }

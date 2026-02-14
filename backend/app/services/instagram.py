from playwright.async_api import async_playwright
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import base64

class InstagramProfileService:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0.5)

    async def scrape_profile(self, username: str) -> dict:
        """
        Scrapes an Instagram profile using Playwright to get bio and screenshots.
        """
        url = f"https://www.instagram.com/{username}/"
        data = {"bio": "", "posts": []}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                print(f"📸 Scraping Instagram: {url}")
                await page.goto(url, wait_until="networkidle")
                
                # Check for login wall (common issue)
                if "Login" in await page.title():
                    print("⚠️ Hit Instagram Login Wall. Attempting basic extraction anyway...")

                # Extract Bio
                try:
                    # Generic selector for bio - might need adjustment as IG changes CSS classes often
                    # Fallback: Get all text and let LLM parse it
                    bio_element = await page.wait_for_selector("header section", timeout=5000)
                    if bio_element:
                        data["bio"] = await bio_element.inner_text()
                except Exception as e:
                    print(f"⚠️ Could not extract bio specifically: {e}")

                # Take Screenshots of top posts (or just the grid)
                # Instead of individual post URLs, let's take a screenshot of the viewport (the grid)
                screenshot_bytes = await page.screenshot(full_page=False)
                data["screenshot_b64"] = base64.b64encode(screenshot_bytes).decode('utf-8')
                
            except Exception as e:
                print(f"❌ Playwright Error: {e}")
            finally:
                await browser.close()
        
        return data

    async def analyze_profile(self, username: str) -> str:
        """
        End-to-end: Scrape -> Vision Analysis -> Vibe Description.
        """
        scraped_data = await self.scrape_profile(username)
        
        if not scraped_data.get("screenshot_b64"):
            return "Could not access Instagram profile (likely login wall or private)."

        # Prepare message for Claude Vision
        content_parts = [
            {"type": "text", "text": f"This is a screenshot of the Instagram profile for user '{username}'. The bio text found was: '{scraped_data.get('bio', 'N/A')}'. Analyze their aesthetic, hobbies, and social 'vibe' in 3 sentences."}
        ]
        
        content_parts.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": scraped_data["screenshot_b64"]
            }
        })

        msg = HumanMessage(content=content_parts)
        
        try:
            response = await self.llm.ainvoke([msg])
            return response.content
        except Exception as e:
            return f"Error during vision analysis: {e}"

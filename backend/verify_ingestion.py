import asyncio
import os
from dotenv import load_dotenv
from app.connectors.letterboxd import LetterboxdConnector
from app.connectors.instagram import InstagramConnector
from app.connectors.linkedin import LinkedInConnector
from app.services.places import PlacesService

load_dotenv()

async def main():
    print("🚀 Starting Data Ingestion Verification...")

    # 1. Test Letterboxd
    print("\n🎥 Testing Letterboxd (User: 'adityamaheshwari')")
    lb = LetterboxdConnector()
    try:
        result = await lb.fetch("adityamaheshwari")
        films = result.get("recent_films", [])
        print(f"Found {len(films)} recent films.")
        if films:
            print(f"Latest: {films[0]['title']} - Rating: {films[0].get('rating', 'N/A')}")
    except Exception as e:
        print(f"❌ Letterboxd Error: {e}")

    # 2. Test Google Places
    print("\n📍 Testing Google Places (Query: 'Jazz Bar NYC')")
    places = PlacesService()
    results = await places.search_venue("Jazz Bar in West Village, NYC")
    if results:
        print(f"Top Result: {results[0].get('displayName', {}).get('text')} ({results[0].get('formattedAddress')})")
    else:
        print("No places found (Check API Key).")

    # 3. Test Instagram
    print("\n📸 Testing Instagram Scrape")
    ig = InstagramConnector()
    try:
        result = await ig.fetch("archdigest")
        print(f"Bio length: {len(result.get('bio', ''))}")
        print(f"Screenshot: {'Yes' if result.get('screenshot_b64') else 'No'}")
        print(f"Login wall: {result.get('login_wall')}")
    except Exception as e:
        print(f"Instagram Scrape Failed: {e}")

    # 4. Test LinkedIn
    print("\n💼 Testing LinkedIn Scrape")
    li = LinkedInConnector()
    try:
        result = await li.fetch("adityamaheshwari")
        print(f"Name: {result.get('name', 'N/A')}")
        print(f"About: {result.get('about', 'N/A')[:100]}...")
        print(f"Login wall: {result.get('login_wall')}")
    except Exception as e:
        print(f"LinkedIn Scrape Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

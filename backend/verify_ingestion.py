import asyncio
import os
from dotenv import load_dotenv
from app.services.letterboxd import LetterboxdService
from app.services.places import PlacesService
from app.services.instagram import InstagramProfileService

load_dotenv()

async def main():
    print("🚀 Starting Data Ingestion Verification...")
    
    # 1. Test Letterboxd
    print("\n🎥 Testing Letterboxd (User: 'aditya')") # Replace with valid user if needed
    lb = LetterboxdService()
    try:
        activity = lb.get_recent_activity("adityamaheshwari") # Example user
        print(f"Found {len(activity)} recent entries.")
        if activity:
            print(f"Latest: {activity[0]['title']} - {activity[0].get('rating_text', 'No rating')}")
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

    # 3. Test Instagram (Playwright + Vision)
    print("\n📸 Testing Instagram Analysis (Simulated Scrape)")
    grams = InstagramProfileService()
    # Note: scraping public IG is flaky without residential proxies/cookies.
    try:
        # We'll try a public brand account that is less likely to block immediately, or just try the user provided one.
        # WARNING: This might hit a login wall on server IPs.
        vibe = await grams.analyze_profile("archdigest") 
        print(f"Vibe Analysis: {vibe}")
    except Exception as e:
        print(f"Instagram Scrape Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

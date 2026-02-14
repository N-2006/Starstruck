import httpx
import os
from typing import Dict, List, Optional

class PlacesService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    async def search_venue(self, query: str, location_bias: str = None) -> List[Dict]:
        """
        Search for a venue using Google Places API (New).
        Requires GOOGLE_MAPS_API_KEY.
        """
        if not self.api_key:
            print("⚠️ No GOOGLE_MAPS_API_KEY found. Returning mock data.")
            return [{"displayName": {"text": "Mock Jazz Bar"}, "formattedAddress": "123 Fake St", "rating": 4.8}]

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types"
        }
        
        data = {
            "textQuery": query
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=data, headers=headers)
            
            if resp.status_code != 200:
                print(f"Error calling Places API: {resp.text}")
                return []
            
            results = resp.json().get("places", [])
            return results

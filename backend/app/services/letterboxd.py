import feedparser
from typing import List, Dict

class LetterboxdService:
    def __init__(self):
        self.base_url = "https://letterboxd.com/{username}/rss/"

    def get_recent_activity(self, username: str) -> List[Dict]:
        """
        Fetches recent activity from Letterboxd public RSS feed.
        Returns a list of dicts with movie title, rating, and logic to parse description.
        """
        url = self.base_url.format(username=username)
        feed = feedparser.parse(url)
        
        activities = []
        for entry in feed.entries[:10]: # Top 10 recent
            # Letterboxd RSS title format: "Movie Title (Year) - Rating" or "Movie Title (Year)"
            # We can extract more structured data if needed, but for now prompt engineering can handle raw titles.
            
            activity = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "summary": entry.summary # Contains poster and sometimes review text
            }
            
            # Simple heuristic for rating in title
            if "★" in entry.title:
                activity["has_rating"] = True
                activity["rating_text"] = entry.title.split("-")[-1].strip()
            
            activities.append(activity)
            
        return activities

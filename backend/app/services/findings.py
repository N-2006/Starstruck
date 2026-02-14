from __future__ import annotations

from typing import Any


def generate_findings(dossier: dict, raw_data: dict) -> list[dict[str, Any]]:
    """Transform dossier + raw_data into findings cards for the frontend."""
    findings: list[dict[str, Any]] = []
    sources = dossier.get("data_sources", [])

    if "github" in sources:
        gh = raw_data.get("github", {})
        langs = gh.get("languages", [])
        repos = gh.get("repos", [])
        detail = ", ".join(langs[:5]) if langs else "Active on GitHub"
        findings.append({
            "label": "Code",
            "value": f"{len(repos)} repos",
            "detail": detail,
        })

    if "spotify" in sources:
        sp = raw_data.get("spotify", {})
        genres = sp.get("top_genres", [])
        artists = sp.get("top_artists", [])
        top_genre = genres[0] if genres else "music lover"
        top_artist = artists[0]["name"] if artists else None
        detail = f"Top: {top_artist}" if top_artist else f"Genre: {top_genre}"
        findings.append({
            "label": "Music",
            "value": top_genre,
            "detail": detail,
        })

    if "letterboxd" in sources:
        lb = raw_data.get("letterboxd", {})
        films = lb.get("recent_films", [])
        rated = [f for f in films if f.get("rating")]
        avg = sum(f["rating"] for f in rated) / len(rated) if rated else 0
        detail = f"Avg rating: {avg:.1f}/5" if rated else f"{len(films)} films logged"
        findings.append({
            "label": "Film",
            "value": f"{len(films)} films",
            "detail": detail,
        })

    if "instagram" in sources:
        ig = raw_data.get("instagram", {})
        bio = ig.get("bio", "")
        # Parse follower/following counts from meta description if available
        import re
        followers_match = re.search(r"([\d,.]+[KMkm]?)\s*Followers", bio)
        following_match = re.search(r"([\d,.]+[KMkm]?)\s*Following", bio)
        posts_match = re.search(r"([\d,.]+[KMkm]?)\s*Posts", bio)
        if followers_match:
            parts = []
            if followers_match:
                parts.append(f"{followers_match.group(1)} followers")
            if posts_match:
                parts.append(f"{posts_match.group(1)} posts")
            if following_match:
                parts.append(f"following {following_match.group(1)}")
            value = " · ".join(parts[:2]) if parts else "Instagram"
            findings.append({
                "label": "Social",
                "value": value,
                "detail": bio[:80] if bio else "Profile connected",
            })
        else:
            findings.append({
                "label": "Social",
                "value": "Instagram",
                "detail": bio[:80] if bio else "Profile connected",
            })

    if "linkedin" in sources:
        li = raw_data.get("linkedin", {})
        headline = li.get("headline", "")
        name = li.get("name", "")
        findings.append({
            "label": "Career",
            "value": name or "LinkedIn",
            "detail": headline or "Professional profile connected",
        })

    return findings

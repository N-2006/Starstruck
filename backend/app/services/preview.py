from __future__ import annotations


def github_preview(data: dict) -> str:
    repos = data.get("repos", [])
    langs = data.get("languages", [])
    if not repos and not langs:
        return "Connected (limited data)"
    parts = []
    if repos:
        parts.append(f"{len(repos)} repos")
    if langs:
        parts.append(", ".join(langs[:4]))
    return " · ".join(parts)


def letterboxd_preview(data: dict) -> str:
    films = data.get("recent_films", [])
    if not films:
        return "Connected (limited data)"
    return f"{len(films)} films logged"


def spotify_preview(data: dict) -> str:
    artists = data.get("top_artists", [])
    if not artists:
        return "Connected (limited data)"
    top = artists[0]["name"] if artists else "Unknown"
    return f"Top artist: {top}"


def instagram_preview(data: dict) -> str:
    bio = data.get("bio", "")
    if not bio:
        return "Profile connected (limited)" if data.get("login_wall") else "Profile connected"
    return bio[:50] + "…" if len(bio) > 50 else bio


def linkedin_preview(data: dict) -> str:
    if data.get("login_wall"):
        return "Profile connected (limited)"
    name = data.get("name", "")
    headline = data.get("headline", "")
    if headline:
        return f"{name} · {headline}" if name else headline
    return name or "Profile connected"


PREVIEW_GENERATORS: dict[str, callable] = {
    "github": github_preview,
    "letterboxd": letterboxd_preview,
    "spotify": spotify_preview,
    "instagram": instagram_preview,
    "linkedin": linkedin_preview,
}


def generate_preview(service: str, data: dict) -> str:
    gen = PREVIEW_GENERATORS.get(service)
    if gen:
        return gen(data)
    return "Connected"

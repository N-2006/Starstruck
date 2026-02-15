# Starstruck


# Submission for Columbia University AI Hackathon. Valentines Day 2026 <3
AI-powered dating app that builds personality profiles from your real online presence. Connect your accounts, and our pipeline scrapes, analyzes, and matches you based on who you actually are — not a curated bio.

## How It Works

1. **Upload a photo** — selfie for your profile card
2. **Connect accounts** — GitHub, Letterboxd, Instagram, LinkedIn, Spotify
3. **Get your profile** — AI-generated bio, vibe tags, and personality breakdown
4. **Swipe** — see compatibility scores and AI-suggested icebreakers

## Architecture

```
React/Vite Frontend ──► FastAPI Backend ──► LangGraph Pipeline
                                                │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                 ▼
                          Connectors         LLM Analysis      Matching
                          (GitHub,           (Personality       (Crossref,
                          Letterboxd,        Profiling)         Venue,
                          Instagram,                            Coach)
                          LinkedIn)
```

### Pipeline Nodes

| Node | What it does |
|------|-------------|
| **Ingest** | Dispatches connectors concurrently via `asyncio.gather`. GitHub REST API, Letterboxd RSS/XML, Instagram + LinkedIn via headless Playwright. Aggregates into `UserDataBundle`. |
| **Analyze** | Sends raw data to an LLM via `langchain`. Returns a two-tier personality profile: public (vibe, tags, schedule) and private (traits, interests, deep cuts). |
| **Crossref** | Feeds both users' profiles into an LLM comparison prompt. Returns `shared_interests[]`, `complementary_traits[]`, `talking_points[]`, `red_flags[]` + compatibility score. |
| **Venue** | Uses crossref output + location to suggest a date spot matching shared interests. |
| **Coach** | Generates personalized icebreakers grounded in actual shared data points. |

The pipeline runs as a **LangGraph DAG** — each node is an async function reading/writing to a shared `PipelineState` (nested `TypedDict`). State is immutable between nodes; each returns a partial dict merged upstream.

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Backend**: Python 3.12, FastAPI, LangGraph, LangChain
- **Connectors**: `httpx` (GitHub, Letterboxd), Playwright (Instagram, LinkedIn)
- **LLM**: Configurable via LangChain (default: Gemini 2.0 Flash)
- **Deployment**: Railway (Docker)

## Project Structure

```
starstruck/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + API endpoints
│   │   ├── config.py               # Pydantic settings
│   │   ├── connectors/             # Data scrapers (GitHub, Letterboxd, IG, LinkedIn)
│   │   ├── graph/                  # LangGraph pipeline
│   │   │   ├── pipeline.py         # DAG definition + edges
│   │   │   └── nodes/              # ingest, analyze, crossref, venue, coach
│   │   ├── models/
│   │   │   ├── schemas.py          # Pydantic request/response models
│   │   │   └── state.py            # Pipeline state TypedDicts
│   │   └── services/
│   │       ├── llm.py              # LLM service (profile analysis, crossref)
│   │       ├── preview.py          # Connector data → preview strings
│   │       └── findings.py         # Dossier → findings cards
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Step-based flow (photo → connect → analyze → swipe)
│   │   ├── components/
│   │   │   ├── PhotoUpload/        # Camera/upload step
│   │   │   ├── ConnectAccounts/    # Service connection UI
│   │   │   ├── ProfileAnalysis/    # AI profile review + edit
│   │   │   └── SwipeScreen/        # Match cards + compatibility
│   │   └── services/
│   │       └── api.ts              # API client
│   └── package.json
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/connect` | Run one connector, return preview string |
| `POST` | `/api/analyze` | Run all connectors + LLM analysis for one user |
| `POST` | `/api/match` | Full pipeline for two users → compatibility result |
| `POST` | `/run` | Run complete LangGraph pipeline |
| `POST` | `/stream` | Stream pipeline execution via SSE |

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
playwright install chromium

# Set environment variables
export GOOGLE_API_KEY=your_key
export SPOTIFY_CLIENT_ID=your_id        # optional
export SPOTIFY_CLIENT_SECRET=your_secret # optional

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to point at your backend (defaults to Railway deployment).

### Tests

```bash
cd backend
pytest tests/ -v
```

## Team

Built at a hackathon by Aditya & Pranav.

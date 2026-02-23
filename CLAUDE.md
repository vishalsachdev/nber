# CLAUDE.md

NBER Video Transcript Explorer — extracts YouTube transcripts from NBER Economics of AI Workshop videos and provides a React web interface for searching and chatting with content via UIUC Chat API.

## Commands

```bash
# Environment setup
uv sync

# Scripts (all in scripts/, always use uv run)
uv run python scripts/extract_transcripts.py      # Extract transcripts from YouTube videos
uv run python scripts/recheck_missing_transcripts.py  # Retry videos that had no transcript yet
uv run python scripts/generate_summaries.py        # Generate AI summaries via UIUC Chat API
uv run python scripts/analyze_presenters.py        # Interactive presenter search/analysis CLI
uv run python scripts/import_data.py               # Import data to Supabase

# Frontend
cd frontend && npm install && npm run dev          # http://localhost:5173
```

## Environment Variables

- `UIUC_CHAT_API_KEY` — API key for UIUC Chat
- `UIUC_CHAT_COURSE_NAME` — Course name (e.g., experimental-chatbot)

## Data Pipeline

1. **Extract** — Pull transcripts from YouTube video IDs defined in `extract_transcripts.py`
2. **Recheck** — Retry unavailable transcripts after 24-48 hours
3. **Summarize** — Generate 2-3 paragraph AI summaries per video
4. **Analyze** — Query presenter data interactively (search, export CSV, stats)
5. **Import** — Push video data from JSON into Supabase

## Deployment

- **Frontend**: Vercel — Edge Function at `frontend/api/chat.ts` proxies UIUC Chat API
- **Data**: Supabase — videos, transcripts, summaries stored and queried client-side

> Always use `uv run` for Python scripts, never bare `python`.

---

## Session Log

### 2025-12-27
- Added roadmap sections

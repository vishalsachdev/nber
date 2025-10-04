# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBER Video Transcript Extraction and Explorer - A system for extracting YouTube transcripts from NBER Economics of Transformative AI Workshop videos and providing an interactive React web interface for searching and chatting with the content using UIUC Chat API (Qwen2.5-VL-72B).

## Core Commands

### Environment Management
```bash
# Install dependencies (auto-creates .venv)
uv sync

# Add new dependencies
uv add package-name

# Add dev dependencies
uv add --dev pytest
```

### Running Scripts
All Python scripts are located in `scripts/` and MUST be run with `uv run`:

```bash
# Extract transcripts for videos (edit video IDs in script first)
uv run python scripts/extract_transcripts.py

# Retry fetching transcripts that were unavailable (wait 24-48 hours after first attempt)
uv run python scripts/recheck_missing_transcripts.py

# Generate AI summaries for all videos with transcripts
uv run python scripts/generate_summaries.py

# Interactive presenter analysis and search
uv run python scripts/analyze_presenters.py

# Import data to Supabase
uv run python scripts/import_data.py
```

### Running Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

## Architecture

### Data Pipeline (Python Scripts in `/scripts`)
1. **extract_transcripts.py**: Initial extraction of video transcripts
   - Hardcoded list of video IDs to process
   - Uses youtube-transcript-api to fetch transcripts
   - Outputs to `nber_videos_transcripts.json`
   - Creates/updates `video_status.json` tracking file

2. **recheck_missing_transcripts.py**: Retry logic for unavailable transcripts
   - Reads `video_status.json` to identify videos needing recheck
   - Updates both status file and main transcript JSON when transcripts become available

3. **generate_summaries.py**: AI-powered summarization
   - Reads transcripts from `nber_videos_transcripts.json`
   - Generates 2-3 paragraph summaries using UIUC Chat API
   - Adds `ai_summary` field to each video in JSON (positioned after `description`)
   - Limits transcript input to ~12k chars to stay within token limits

4. **analyze_presenters.py**: Interactive CLI utility
   - Query and analyze presenter data from JSON
   - Search by name/affiliation, export to CSV, view statistics

5. **import_data.py**: Supabase data import
   - Imports video data from JSON to Supabase database
   - One-time setup script for database initialization

### Web Application (React Frontend in `/frontend`)
React + TypeScript application with four main features:

1. **Search & Browse**:
   - Full-text search across titles, presenters, transcript content
   - Displays video cards with metadata, presenter info, AI summaries
   - "Start Chat" button switches to Chat tab with selected video

2. **Chat with Video**:
   - Single-video chat mode with transcript context
   - Context limited to first 15k chars of transcript
   - Uses UIUC Chat API (Qwen2.5-VL-72B) with streaming responses
   - Session state maintains conversation history

3. **Chat with All**:
   - Cross-presentation querying using AI summaries
   - Provides context from up to 10 video summaries
   - Synthesizes information across workshop presentations

4. **Presenters Directory**:
   - Directory of all presenters with affiliations
   - Google Scholar profile links
   - Shows all videos per presenter

### Data Structure
**nber_videos_transcripts.json** - Main data file with this schema per video:
```json
{
  "id": "video_id",
  "title": "Video Title",
  "url": "youtube_url",
  "presenters": [{"name": "...", "affiliation": "...", "scholar_url": "..."}],
  "num_presenters": 2,
  "description": "Full video description",
  "ai_summary": "AI-generated 2-3 paragraph summary",  // Added by generate_summaries.py
  "upload_date": "YYYY-MM-DD",
  "days_ago": 5,
  "has_transcript": true,
  "word_count": 5000,
  "char_count": 30000,
  "transcript": "Full transcript text..."
}
```

**video_status.json** - Tracking file for recheck logic:
- Lists all videos with completion status
- Flags videos needing transcript recheck (`needs_recheck: true`)
- Updated by both extract_transcripts.py and recheck_missing_transcripts.py

## Environment Variables

Required in `.env` file (never commit this file):
```
UIUC_CHAT_API_KEY=uc_your-key-here
UIUC_CHAT_COURSE_NAME=experimental-chatbot
```

The app validates credentials at startup and stops with error if missing (app.py:24-31).

## Key Implementation Details

### AI Integration (UIUC Chat API)
- Model: `Qwen/Qwen2.5-VL-72B-Instruct`
- Provider: UIUC.chat (self-hosted LLM)
- Endpoint: `https://uiuc.chat/api/chat-api/chat`
- Proxied through: Vercel Edge Function at `/frontend/api/chat.ts`
- Cost: Free for academic use
- Temperature: 0.7 for balanced creativity
- Streaming enabled for better UX

### Session State Management
React state management tracks:
- `messages`: Chat conversation history (stored in component state)
- `selectedVideo`: Currently selected video for single-video chat
- `searchQuery`: Current search query text
- Data fetched from Supabase on initial load

### Context Window Management
- Single video chat: First 15k chars of transcript
- Multi-video chat: First 10 video summaries
- Summary generation: First 12k chars of transcript (scripts/generate_summaries.py)
- These limits prevent token overflow while maintaining quality

### YouTube Transcript API
- Uses `YouTubeTranscriptApi.fetch()` to retrieve transcripts
- Returns `FetchedTranscript` object with `snippets` attribute
- Handles `TranscriptsDisabled` and `NoTranscriptFound` exceptions
- Transcripts may not be immediately available for new videos (wait 24-48 hours)

## Development Patterns

### Adding New Videos
1. Edit `scripts/extract_transcripts.py` to update `VIDEOS` list with new video IDs
2. Run `uv run python scripts/extract_transcripts.py`
3. For missing transcripts, wait 24-48 hours then run `uv run python scripts/recheck_missing_transcripts.py`
4. Generate summaries: `uv run python scripts/generate_summaries.py`
5. Import to Supabase: `uv run python scripts/import_data.py`

### Extending Search Functionality
Search is handled in React frontend (`frontend/src/App.tsx`):
1. Client-side filtering of videos fetched from Supabase
2. Searches: title, presenter names/affiliations, transcript content
3. To add new search fields, update the filter logic in the component

### Modifying AI Prompts
- Single video chat: `frontend/src/App.tsx` (ChatWithVideo component)
- Multi-video chat: `frontend/src/App.tsx` (ChatWithAll component)
- Summary generation: `scripts/generate_summaries.py`
- API proxy: `frontend/api/chat.ts` (Vercel Edge Function)

All prompts emphasize conciseness and citation of specific points.

### JSON Schema Modifications
If adding fields to video objects:
1. Update `scripts/generate_summaries.py` to include new field
2. Update Supabase schema if field should be stored in database
3. Update TypeScript types in `frontend/src/App.tsx`
4. Field order: identification → presenters → metadata → transcript

## Dependencies

### Python (scripts only - see pyproject.toml):
- **youtube-transcript-api**: YouTube transcript extraction
- **yt-dlp**: Video metadata extraction
- **python-dotenv**: Environment variable management
- **supabase**: Database client for data import

### Frontend (see frontend/package.json):
- **react**: UI framework
- **typescript**: Type safety
- **vite**: Build tool and dev server
- **@supabase/supabase-js**: Database client
- **react-markdown**: Markdown rendering for chat messages

## Typical Workflows

### Initial Setup
```bash
git clone <repo>
cd nber
uv sync
echo "UIUC_CHAT_API_KEY=uc_..." > .env
echo "UIUC_CHAT_COURSE_NAME=experimental-chatbot" >> .env
```

### Extract New Workshop Videos
```bash
# 1. Update VIDEOS list in scripts/extract_transcripts.py
# 2. Extract transcripts
uv run python scripts/extract_transcripts.py

# 3. Wait 24-48 hours for new videos, then retry
uv run python scripts/recheck_missing_transcripts.py

# 4. Generate AI summaries
uv run python scripts/generate_summaries.py

# 5. Import to Supabase
uv run python scripts/import_data.py
```

### Run Web App
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Query Presenter Data
```bash
uv run python scripts/analyze_presenters.py
# Interactive CLI menu for searching/analyzing presenters
```

## Important Notes

- Always use `uv run` for Python script execution (not bare `python`)
- All Python scripts are in the `/scripts` directory
- YouTube transcripts may not be immediately available for new uploads
- UIUC Chat API credentials must be set in `frontend/.env` before running app
- Free for academic use - no API costs
- Vercel Edge Functions proxy API requests to avoid CORS issues
- React app fetches data from Supabase on initial load
- Transcript context is truncated to ~15k chars for optimal performance
- Session state is managed client-side and cleared on browser refresh

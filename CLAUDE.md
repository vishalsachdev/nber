# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NBER Video Transcript Extraction and Explorer - A two-part system for extracting YouTube transcripts from NBER Economics of Transformative AI Workshop videos and providing an interactive Streamlit interface for searching and chatting with the content using OpenAI.

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
All Python scripts MUST be run with `uv run` for proper environment isolation:

```bash
# Extract transcripts for videos (edit video IDs in script first)
uv run python extract_transcripts.py

# Retry fetching transcripts that were unavailable (wait 24-48 hours after first attempt)
uv run python recheck_missing_transcripts.py

# Generate AI summaries for all videos with transcripts
uv run python generate_summaries.py

# Interactive presenter analysis and search
uv run python analyze_presenters.py

# Run Streamlit web app
uv run streamlit run app.py
```

## Architecture

### Data Pipeline
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
   - Generates 2-3 paragraph summaries using OpenAI GPT-4o-mini
   - Adds `ai_summary` field to each video in JSON (positioned after `description`)
   - Limits transcript input to ~12k chars to stay within token limits

4. **analyze_presenters.py**: Interactive CLI utility
   - Query and analyze presenter data from JSON
   - Search by name/affiliation, export to CSV, view statistics

### Web Application (app.py)
Streamlit-based interface with four main sections:

1. **Search & Browse Tab**:
   - Full-text search across titles, presenters, transcript content
   - Displays video cards with metadata, presenter info, AI summaries
   - "Start Chat" button switches to Chat tab with selected video

2. **Chat with Video Tab**:
   - Single-video chat mode with transcript context
   - Context limited to first 15k chars of transcript
   - Uses GPT-4o-mini with streaming responses
   - Session state maintains conversation history

3. **Chat with All Tab**:
   - Cross-presentation querying using AI summaries
   - Provides context from up to 10 video summaries
   - Synthesizes information across workshop presentations

4. **Presenters Tab**:
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
OPENAI_API_KEY=sk-your-key-here
```

The app validates this at startup and stops with error if missing (app.py:26-29).

## Key Implementation Details

### OpenAI Integration
- Model: `gpt-4o-mini` (cost-effective, fast)
- Input pricing: $0.15 per 1M tokens
- Output pricing: $0.60 per 1M tokens
- Typical chat cost: < $0.01 per conversation
- Temperature: 0.7 for balanced creativity
- Streaming enabled for better UX

### Session State Management
Streamlit session state tracks:
- `messages`: Chat conversation history
- `selected_video`: Currently selected video for single-video chat
- `search_query`: Current search query text

### Context Window Management
- Single video chat: First 15k chars of transcript (app.py:139)
- Multi-video chat: First 10 video summaries (app.py:184)
- Summary generation: First 12k chars of transcript (generate_summaries.py:42)
- These limits prevent token overflow while maintaining quality

### YouTube Transcript API
- Uses `YouTubeTranscriptApi.fetch()` to retrieve transcripts
- Returns `FetchedTranscript` object with `snippets` attribute
- Handles `TranscriptsDisabled` and `NoTranscriptFound` exceptions
- Transcripts may not be immediately available for new videos (wait 24-48 hours)

## Development Patterns

### Adding New Videos
1. Edit `extract_transcripts.py` to update `VIDEOS` list with new video IDs
2. Run `uv run python extract_transcripts.py`
3. For missing transcripts, wait 24-48 hours then run `uv run python recheck_missing_transcripts.py`
4. Generate summaries: `uv run python generate_summaries.py`

### Extending Search Functionality
The `search_videos()` function (app.py:75-103) searches in order:
1. Title match → add to results
2. Presenter name/affiliation match → add to results
3. Transcript content match → add to results

To add new search fields, insert additional checks before transcript search.

### Modifying AI Prompts
- Single video context: app.py:133-141
- Multi-video context: app.py:180-186
- Summary generation: generate_summaries.py:44-59

All prompts emphasize conciseness and citation of specific points.

### JSON Schema Modifications
If adding fields to video objects:
1. Update `restructure_with_summary()` in generate_summaries.py to include new field in correct position
2. Field order matters for readability: identification → presenters → metadata → transcript

## Dependencies

Core libraries (see pyproject.toml):
- **streamlit**: Web interface framework
- **openai**: OpenAI API client
- **youtube-transcript-api**: YouTube transcript extraction
- **yt-dlp**: Video metadata extraction (if needed)
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation (if needed for analysis)

## Typical Workflows

### Initial Setup
```bash
git clone <repo>
cd nber
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
```

### Extract New Workshop Videos
```bash
# 1. Update VIDEOS list in extract_transcripts.py
# 2. Extract transcripts
uv run python extract_transcripts.py

# 3. Wait 24-48 hours for new videos, then retry
uv run python recheck_missing_transcripts.py

# 4. Generate AI summaries
uv run python generate_summaries.py
```

### Run Web App
```bash
uv run streamlit run app.py
# Opens at http://localhost:8501
```

### Query Presenter Data
```bash
uv run python analyze_presenters.py
# Interactive CLI menu for searching/analyzing presenters
```

## Important Notes

- Always use `uv run` for script execution (not bare `python`)
- YouTube transcripts may not be immediately available for new uploads
- OpenAI API key must be set in `.env` before running app
- The app uses cached resources (`@st.cache_resource`, `@st.cache_data`) for performance
- Session state is cleared on browser refresh
- Transcript context is truncated to stay within API token limits

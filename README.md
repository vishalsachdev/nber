# NBER Economics of Transformative AI Workshop - Transcript Explorer

An interactive AI-powered tool for exploring presentations from the NBER Economics of Transformative AI Workshop (Fall 2025). Search through 17 presentations, chat with video transcripts using AI, and discover insights from leading economists on how transformative AI will reshape labor markets, innovation, competition, and economic policy.

**🌐 Live Demo (React)**: https://frontend-13nkin9ja-vishalsachdevs-projects.vercel.app

## About the Workshop

The [Economics of Transformative AI Workshop](https://www.nber.org/conferences/economics-transformative-ai-workshop-fall-2025) brings together leading economists to explore the economic implications of transformative artificial intelligence. Organized by Ajay K. Agrawal (University of Toronto), Anton Korinek (University of Virginia), and Erik Brynjolfsson (Stanford), the workshop features presentations from luminaries including:

- Daron Acemoglu (MIT)
- Paul Romer (NYU)
- Joseph Stiglitz (Columbia)
- And 31 other leading economists

**Workshop Coverage:**
- 17 video presentations
- 91,733 words of transcribed content
- 34 presenters from top institutions
- Topics: AI and labor markets, firm dynamics, innovation, competition, public finance, behavioral economics, and policy

## Features

🔍 **Search & Browse** - Full-text search across titles, presenters, and transcript content with AI-generated summaries

💬 **Chat with Video** - Have a conversation about specific presentations using AI that understands the full context

🌐 **Chat with All** - Ask questions that synthesize information across all workshop presentations

👥 **Presenters Directory** - Browse all 34 presenters with Google Scholar profiles and affiliations

## Quick Start

### Run the Web App

```bash
# Clone and setup
git clone https://github.com/vishalsachdev/nber.git
cd nber
uv sync

# Add OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Run the app
uv run streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Data Extraction Scripts

All scripts use [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Extract transcripts for new videos
uv run python extract_transcripts.py

# Retry missing transcripts (after 24-48 hours)
uv run python recheck_missing_transcripts.py

# Generate AI summaries for all videos
uv run python generate_summaries.py

# Analyze presenter statistics
uv run python analyze_presenters.py
```

## Project Structure

```
.
├── app.py                           # Streamlit web application
├── extract_transcripts.py           # YouTube transcript extraction
├── recheck_missing_transcripts.py   # Retry logic for missing transcripts
├── generate_summaries.py            # AI summary generation using GPT-4o-mini
├── analyze_presenters.py            # Interactive presenter analysis CLI
├── nber_videos_transcripts.json     # Complete dataset (17 videos, full metadata)
├── video_status.json                # Transcript availability tracking
├── CLAUDE.md                        # Codebase guide for AI assistants
├── FEATURES.md                      # Future features and cost control roadmap
└── articles/                        # Development documentation
    └── 2025-09-30-nber-ai-workshop-explorer.md
```

## Data Files

**`nber_videos_transcripts.json`** (Complete Dataset):
- 17 videos with full transcripts (91,733 words total)
- AI-generated summaries for all presentations
- 34 presenter profiles with Google Scholar links
- Complete metadata (descriptions, upload dates, word counts)

**`video_status.json`** (Tracking):
- 17/17 videos with transcripts ✓
- Status tracking for recheck operations

## Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **AI:** OpenAI GPT-4o-mini for chat and summaries
- **Data:** YouTube Transcript API, yt-dlp
- **Environment:** uv for fast dependency management
- **Cost:** ~$0.003-0.005 per chat interaction

## Cost Optimization

For public deployment, see `FEATURES.md` for comprehensive cost control strategies:
- Rate limiting (per-session and global)
- OpenAI budget caps
- Context window optimization
- Response caching

Estimated cost with controls: **$10-50/month** for moderate traffic.

## Development Setup

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Add Dependencies

```bash
# Add new packages
uv add package-name

# Add dev dependencies
uv add --dev pytest
```

### Why uv?

- **10-100x faster** than pip
- **Automatic virtual environments** - no manual activation needed
- **Lockfile for reproducibility** - ensures consistent environments
- **All-in-one tool** - replaces pip, venv, poetry, pyenv

## Documentation

- **`CLAUDE.md`** - Comprehensive codebase guide including architecture, data pipeline, API integration details
- **`FEATURES.md`** - Cost control roadmap, rate limiting strategies, and future feature planning
- **`articles/`** - Development blog posts documenting the build process

## Notes

- YouTube transcripts may not be immediately available for newly uploaded videos
- Video IDs can change on YouTube - use `recheck_missing_transcripts.py` to update
- OpenAI API key required for chat and summary features
- Streamlit caches loaded data - refresh browser to see updated JSON

## Links

- **[Workshop Website](https://www.nber.org/conferences/economics-transformative-ai-workshop-fall-2025)** - Official NBER conference page
- **[YouTube Channel](https://www.youtube.com/@NBERvideos/videos)** - Watch all presentations
- **[Development Article](articles/2025-09-30-nber-ai-workshop-explorer.md)** - Behind-the-scenes build story

## License

MIT

# NBER Video Transcript Extraction

Extract titles and transcripts from NBER YouTube videos for analysis.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast, automated Python environment management.

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/vishalsachdev/nber.git
cd nber

# Install dependencies (automatically creates .venv and installs packages)
uv sync
```

## Usage

All scripts should be run with `uv run` to ensure proper environment isolation:

### Extract Transcripts from Recent Videos

```bash
# Extract transcripts for specific video list (edit video IDs in script)
uv run python extract_transcripts.py
```

### Check for Missing Transcripts

```bash
# Retry fetching transcripts that were unavailable
uv run python recheck_missing_transcripts.py
```

### Analyze Presenters

```bash
# Get statistics and search through presenter information
uv run python analyze_presenters.py
```

## Project Structure

```
.
├── extract_transcripts.py          # Main script to extract transcripts
├── recheck_missing_transcripts.py  # Retry missing transcripts
├── analyze_presenters.py           # Analyze and query presenter data
├── video_status.json               # Track which videos need rechecking
├── nber_videos_transcripts.json    # Full transcript data with metadata
└── pyproject.toml                  # Project dependencies
```

## Data Files

- **`nber_videos_transcripts.json`** - Complete data: transcripts, metadata, presenters (17 videos, ~55K words)
- **`video_status.json`** - Tracking file showing completed (10) vs pending (7) videos

## Adding Dependencies

```bash
# Add new packages
uv add package-name

# Add dev dependencies
uv add --dev pytest
```

## Why uv?

- **10-100x faster** than pip
- **Automatic virtual environments** - no manual activation needed
- **Lockfile for reproducibility** - ensures consistent environments
- **All-in-one tool** - replaces pip, venv, poetry, pyenv

## Development

```bash
# Run any Python script with automatic environment management
uv run python your_script.py

# Or run Python directly
uv run python
```

## Notes

- YouTube transcripts may not be immediately available for newly uploaded videos
- Use `recheck_missing_transcripts.py` after 24-48 hours to retry failed extractions
- The project uses the official NBER YouTube channel: [@NBERvideos](https://www.youtube.com/@NBERvideos/videos)

## License

MIT
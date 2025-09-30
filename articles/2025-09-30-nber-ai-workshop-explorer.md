# Building an AI-Powered Research Assistant: From YouTube Transcripts to Interactive Knowledge Base

*September 30, 2025*

When the NBER Economics of Transformative AI Workshop dropped 17 presentations on YouTube, I saw an opportunity: what if researchers could have a conversation with these presentations instead of watching hours of video? Six hours of conversational development with Claude later, I had a fully functional AI-powered research assistant that lets you search, browse, and chat with 91,733 words of academic content.

This is the story of building that tool—from extracting YouTube transcripts to handling changed video IDs to optimizing for public launch—and what it taught me about the new paradigm of conversational software development.

## The Challenge: Making Dense Academic Content Accessible

Academic workshops are goldmines of cutting-edge research, but they're incredibly time-consuming to digest. The NBER's Economics of Transformative AI Workshop featured presentations from luminaries like Daron Acemoglu, Paul Romer, and Erik Brynjolfsson. Each video ran 30-60 minutes. For a researcher trying to find specific insights about, say, "AI's impact on labor markets," the traditional workflow meant:

1. Watch multiple hour-long videos
2. Manually skim through transcripts
3. Take notes on relevant sections
4. Cross-reference insights across presentations

What if you could just ask: *"What are the main concerns about AI and labor markets across all presentations?"* and get a synthesized answer citing specific talks?

That's what we built.

## Phase 1: The Data Pipeline (Hours 0-2)

### Starting Point: YouTube Transcripts

The first step was extracting transcripts from YouTube. I started with the `youtube-transcript-api` library, which provides a clean Python interface to YouTube's transcript data:

```python
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)

        if hasattr(transcript_data, 'snippets'):
            return ' '.join([snippet.text for snippet in transcript_data.snippets])
        return None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
```

This worked beautifully for 10 of the 17 videos. The remaining 7 returned "transcript not available." At first, I assumed they were simply too new—YouTube sometimes takes 24-48 hours to generate transcripts for newly uploaded videos.

### The Mystery of the Missing Transcripts

Fast forward a few hours. I rechecked those 7 "missing" videos and discovered something interesting: YouTube had *changed their video IDs*. The URLs I had originally scraped were returning "video unavailable" errors.

This is where `yt-dlp` (the maintained fork of youtube-dl) became essential. I fetched the channel's video list directly:

```bash
yt-dlp --dump-json --flat-playlist --playlist-end 20 \
  "https://www.youtube.com/@NBERvideos/videos"
```

Comparing the current channel listing against my original data revealed the ID changes:

```python
ID_MAPPING = {
    "5q31h9uxaUA": "G5teYbovYJ0",  # Artificial Intelligence in R&D
    "Lq2kIqBqTmY": "by7k-H7sZ8A",  # Genius on Demand
    "rYwpBKqCq_A": "SDU2oldSxqU",  # Welcome Talk
    # ... 4 more mappings
}
```

After updating the video IDs and re-running the transcript extraction, all 7 "missing" transcripts appeared. **Lesson learned:** YouTube's video management is more dynamic than expected. Always verify IDs when dealing with automated scraping.

**Final data corpus:**
- 17 videos with complete transcripts
- 91,733 total words (~360 pages)
- Average 5,400 words per video

## Phase 2: Enrichment - Adding Context and Intelligence

Raw transcripts are useful, but not enough. Researchers need context: *Who presented this? Where can I find their other work? What's this talk actually about?*

### Presenter Metadata with Google Scholar

I manually enriched each video with presenter information, pulling data from the NBER website and Google Scholar:

```python
{
    "id": "G5teYbovYJ0",
    "title": "Artificial Intelligence in Research and Development",
    "presenters": [
        {
            "name": "Iain M. Cockburn",
            "affiliation": "Boston University and NBER",
            "scholar_url": "https://scholar.google.com/citations?user=xMVq8WQAAAAJ"
        },
        # ... more presenters
    ]
}
```

This seemingly simple addition unlocked powerful features:
- Search by presenter name or affiliation
- Direct links to citation metrics and publication history
- Cross-referencing researchers across multiple presentations

### AI-Generated Summaries

Here's where things got interesting. Reading even a short academic transcript can take 10-15 minutes. What if we could generate concise 2-3 paragraph summaries using AI?

```python
def generate_summary(client, video):
    transcript_excerpt = video['transcript'][:12000]  # Stay within token limits

    prompt = f"""Summarize this NBER presentation:

    Title: {video['title']}
    Presenters: {presenters}

    Create a 2-3 paragraph summary capturing:
    1. Main research question
    2. Key findings
    3. Important implications

    Transcript: {transcript_excerpt}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )

    return response.choices[0].message.content
```

**Cost analysis:** With GPT-4o-mini at $0.15 per 1M input tokens and $0.60 per 1M output tokens:
- Per summary: ~4K input + 200 output tokens = **$0.0007**
- All 17 summaries: **$0.012 total**

For just over a penny, every video now had a publication-quality abstract. This became the foundation for both search results and the "Chat with All Transcripts" feature.

## Phase 3: The Interactive Interface

Now came the fun part: building an interface that made this knowledge accessible.

### Streamlit: Rapid Prototyping for Data Apps

I chose Streamlit because it lets you build data-heavy web apps with pure Python—no HTML, CSS, or JavaScript required. Here's the entire app startup:

```python
import streamlit as st

st.set_page_config(
    page_title="NBER AI Economics - Transcript Explorer",
    layout="wide"
)

@st.cache_data
def load_videos():
    with open('nber_videos_transcripts.json', 'r') as f:
        return json.load(f)

videos = load_videos()
```

Streamlit's `@st.cache_data` decorator means the JSON file is loaded once and cached, even as users interact with the app.

### Four-Tab Navigation Structure

The app evolved into four distinct modes:

**1. Search & Browse**
Full-text search across titles, presenters, and transcript content. Each result shows:
- AI-generated summary
- Presenter info with Google Scholar links
- Word count metrics
- "Start Chat" button to jump directly into conversation

**2. Chat with Video**
Select a specific presentation and have a conversation about it. The chat interface uses OpenAI's GPT-4o-mini with the transcript as context:

```python
def chat_with_transcript(video, user_message):
    context = f"""You are helping users understand this NBER presentation.

Video: {video['title']}
Presenters: {', '.join([p['name'] for p in video['presenters']])}

Transcript (excerpt):
{video['transcript'][:15000]}  # ~15K chars ≈ 4K tokens

Answer concisely and cite specific points from the presentation."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": context},
            *st.session_state.messages
        ],
        max_tokens=1000,
        stream=True
    )

    return response
```

**Key design decision:** Limiting transcript context to 15,000 characters (~4K tokens) keeps costs low while providing enough detail. For a 30-minute presentation, this covers roughly half the content—enough to answer most questions.

**3. Chat with All Transcripts**
The most ambitious feature: cross-video querying. Ask a question like "Which presentations discuss behavioral economics?" and get synthesized answers drawing from multiple talks.

Instead of sending all 91K words to the API (astronomically expensive), we use the AI-generated summaries as context:

```python
def chat_with_all_transcripts(user_message):
    # Build context from summaries, not full transcripts
    video_summaries = []
    for video in videos:
        summary = video['ai_summary']
        video_summaries.append(f"**{video['title']}** by {presenters}\n{summary}")

    context = f"""You have access to {len(videos)} NBER presentations:

    {chr(10).join(video_summaries[:10])}

    Synthesize information across presentations and cite specific talks."""

    # API call similar to single-video chat
```

This approach reduces context size by ~95% while maintaining semantic coverage. Cost per query: **~$0.003**

**4. Presenters Directory**
A browsable directory of all 38 presenters with their affiliations, Google Scholar profiles, and which videos they appeared in. Simple, but incredibly useful for researchers tracking specific scholars.

## Phase 4: UX Refinements and Cost Optimization

As the app neared completion, we focused on polish and preparing for public launch.

### Layout Optimization: Chat-First Design

Original design flaw: When you opened "Chat with Video," you saw the video metadata and AI summary *first*, with the chat interface buried below. But the chat is the primary feature!

We reorganized the layout:
```
Video Title & Metadata
---
Chat Interface (where you spend most time)
---
AI Summary (collapsed by default after first chat)
```

This simple reordering dramatically improved the flow. The summary now expands automatically when you first select a video, giving you context, then collapses to stay out of your way once you start chatting.

### Title Standardization

YouTube's title format was inconsistent:
```
❌ 2025, Economics of Transformative AI Workshop, "Artificial I...
❌ Economics of Transformative AI Workshop, Fall 2025 - Welcome
❌ The Coasean Singularity? Demand, Supply, and...
```

We standardized to clean, readable titles:
```
✅ Artificial Intelligence in Research and Development
✅ Economics of Transformative AI Workshop - Welcome
✅ The Coasean Singularity? Demand, Supply, and Markets
```

### Ordering: Welcome Talk First

Academic workshops typically start with a welcome/overview talk. We reordered the video list to put the welcome talk first, giving new users natural entry point.

## Technical Deep Dive: The Architecture

Let's talk about what makes this work under the hood.

### Data Structure

Everything centers on a single JSON file (`nber_videos_transcripts.json`) with this schema:

```json
{
  "id": "video_id",
  "title": "Video Title",
  "url": "https://youtube.com/watch?v=...",
  "presenters": [
    {
      "name": "Researcher Name",
      "affiliation": "Institution",
      "scholar_url": "https://scholar.google.com/..."
    }
  ],
  "num_presenters": 2,
  "description": "Full YouTube description",
  "ai_summary": "AI-generated 2-3 paragraph summary",
  "upload_date": "2025-09-29",
  "has_transcript": true,
  "word_count": 5400,
  "char_count": 28000,
  "transcript": "Full transcript text..."
}
```

**Why a single JSON file?** For this scale (17 videos, ~10MB), a database adds unnecessary complexity. JSON loads in milliseconds, is version-control friendly, and makes the project trivially deployable.

### OpenAI Integration: Context Windows and Token Management

The most critical cost consideration is token usage. Here's how we optimized:

**Single Video Chat:**
- Input: 15K char transcript + system prompt + message history ≈ 4.5K tokens
- Output: 500-1000 tokens
- Cost: **$0.002-0.005 per interaction**

**Multi-Video Chat:**
- Input: 10 video summaries (~3K chars each) + system prompt ≈ 8K tokens
- Output: 600-1200 tokens
- Cost: **$0.003-0.006 per interaction**

**Key optimizations:**
1. Truncate transcripts to 15K chars (full transcripts can be 40K+)
2. Use summaries instead of full text for cross-video queries
3. Limit `max_tokens` to prevent runaway responses
4. Stream responses for better perceived performance

### Streamlit Session State

Streamlit's session state manages conversation history:

```python
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None

# When user sends message
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate AI response
    response = chat_with_transcript(video, prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

This persists conversation history across interactions within a session, enabling natural multi-turn conversations.

## Preparing for Public Launch: Cost Controls

Before opening this to the public, we need to address the elephant in the room: **What if this goes viral?**

### Cost Analysis

**Current setup (no controls):**
- 1,000 users × 5 chats each = 5,000 requests
- At $0.004 average per request = **$20/month** ✅

- 10,000 users × 10 chats each = 100,000 requests
- At $0.004 average = **$400/month** ⚠️

### Planned Cost Controls

We documented a comprehensive cost control strategy in `FEATURES.md`:

**1. Rate Limiting (Critical)**
- Per-session limit: 10 messages max
- Global limit: 100 requests/hour
- Prevents abuse and runaway costs

**2. OpenAI Budget Caps**
- Set hard monthly limit in OpenAI dashboard ($50 to start)
- Graceful degradation when limit reached
- "Service temporarily unavailable" message

**3. Context Optimization**
- Reduce transcript context from 15K → 10K chars
- Reduce `max_tokens` from 1000 → 500
- Prune conversation history after 5 exchanges
- Expected savings: **30-40% per request**

**4. Response Caching (Future)**
- Cache common question/answer pairs
- Use semantic similarity to match related questions
- Could cut costs by 50% at scale

## Lessons Learned: Conversational Development

This entire project—from zero to production-ready—took approximately **6 hours of conversational development** with Claude. Here's what made that possible:

### 1. Start with Data

The first 2 hours focused entirely on getting clean, complete data. No UI, no features—just bulletproof data extraction and enrichment. This foundation made everything else trivial.

### 2. Embrace Iteration

The app went through 11 git commits as it evolved:
- Commit 1: Basic transcript extraction
- Commit 5: Streamlit UI prototype
- Commit 7: AI summaries integration
- Commit 11: Final UX polish

Each iteration added value. None required throwing away previous work. This is the power of conversational development: you can evolve the design in real-time based on what you see working.

### 3. Let AI Handle Boilerplate

Claude wrote:
- All the YouTube API integration code
- The OpenAI streaming response handlers
- Presenter metadata extraction scripts
- Data structure reorganization

I focused on:
- What features to build
- How to organize the information
- Which optimizations mattered

This division of labor—human intent, AI execution—is incredibly efficient.

### 4. Build for Real Use Cases

Every feature decision came from asking: *"How would a researcher actually use this?"*

- Search by presenter? Obvious need.
- Chat with single video? Essential for deep dives.
- Chat with all videos? Enables research questions like "compare different perspectives."
- AI summaries? Saves 10 minutes per video.

No "wouldn't it be cool if..." features. Only "researchers need to..." features.

## What's Next

With the app ready for public launch, the roadmap focuses on three areas:

**1. Cost Controls (Pre-Launch)**
- Implement rate limiting
- Set budget caps
- Optimize context windows

**2. Enhanced Search (Post-Launch)**
- Semantic search using embeddings
- "Related questions" suggestions
- Smart caching for common queries

**3. Extended Features (Future)**
- Export chat conversations as PDFs
- Video timestamp linking (jump to relevant moments)
- Multi-language support

## The Broader Lesson

This project exemplifies a new way of building software: **conversational development**. The paradigm shift isn't just that AI writes code faster—it's that you can think out loud and watch your ideas become real.

Traditional software development:
```
Idea → Spec → Architecture → Implementation → Testing → Deployment
        (weeks to months)
```

Conversational development:
```
Idea → "Let's build this" → Working prototype → Refinements → Deployment
              (hours to days)
```

The key insight: *You don't need to know how to implement everything.* You need to know what to build and how to evaluate whether it's working. The AI handles the translation from intent to implementation.

For this NBER transcript explorer:
- I didn't need to be an expert in YouTube APIs
- I didn't need to memorize Streamlit's documentation
- I didn't need to optimize OpenAI token usage from first principles

I needed to understand:
- What makes academic research accessible
- How to evaluate UX decisions
- When costs were acceptable vs. concerning

Everything else was conversational problem-solving with Claude.

## Try It Yourself

The full project is available at [repository URL]. Key files:

- `app.py` - The Streamlit application (440 lines)
- `extract_transcripts.py` - YouTube transcript extraction
- `generate_summaries.py` - AI summary generation
- `nber_videos_transcripts.json` - Complete dataset

To run locally:
```bash
git clone [repo-url]
cd nber
uv sync  # Install dependencies
echo "OPENAI_API_KEY=your-key" > .env
uv run streamlit run app.py
```

The app will be available at `http://localhost:8501`.

## Final Thoughts

When I started this project, I had 17 YouTube video URLs and a question: *How can we make this knowledge more accessible?*

A few hours later, I had:
- A complete data pipeline
- An AI-powered chat interface
- Cross-video synthesis capabilities
- 17 publication-quality summaries
- A cost-optimized architecture ready for public use

This is the promise of conversational development: turning ideas into reality at the speed of thought.

The future of software development isn't about replacing human creativity—it's about amplifying it. Give AI a clear intent and the autonomy to execute, and watch how quickly impossible becomes inevitable.

---

*Vishal is exploring the intersection of AI and education at the University of Illinois. This article describes a real project built in a single afternoon using Claude Code. All code and data are available in the project repository.*

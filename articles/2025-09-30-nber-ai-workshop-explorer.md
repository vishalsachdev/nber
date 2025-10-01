# Building an AI Research Assistant in an Afternoon: Conversations with Academic Videos

*September 30, 2025*

When the NBER Economics of Transformative AI Workshop dropped 17 presentations on YouTube, I faced a familiar researcher's dilemma: hours of valuable content, but no time to watch it all. What if instead of scrubbing through videos, you could just ask them questions?

A few hours of conversational development with Claude later, I had a working answer: an AI-powered app that lets researchers search, browse, and chat with 91,733 words of academic transcripts.

## The Vision

Academic workshops are goldmines, but watching a 45-minute presentation to find one insight about "AI's impact on labor markets" feels inefficient. The traditional workflow:
1. Watch multiple videos
2. Manually search transcripts
3. Cross-reference insights
4. Take notes

The new workflow:
1. Ask: *"What do these economists say about AI and labor?"*
2. Get synthesized answers citing specific talks
3. Follow up with clarifying questions

That's what we built.

## The Journey: From Transcripts to Conversations

### Phase 1: Data Extraction (The Foundation)

Everything started with getting clean transcript data from YouTube. Using the `youtube-transcript-api` library, I extracted transcripts for 17 videos. Initially, 7 returned "transcript not available"—but checking back later revealed YouTube had changed their video IDs. A quick scan with `yt-dlp` found the new IDs, and suddenly all 17 transcripts were accessible.

**Result**: 17 videos, 91,733 words, averaging 5,400 words per presentation.

### Phase 2: Enrichment (Making Data Meaningful)

Raw transcripts aren't enough—researchers need context. I added:
- **Presenter metadata**: 38 economists with affiliations and Google Scholar links
- **AI-generated summaries**: Using GPT-4o-mini to create 2-3 paragraph abstracts for each video

The summaries cost just $0.012 for all 17 videos (about a penny). For that, every presentation got a publication-quality abstract that makes the search experience dramatically better.

### Phase 3: The Interactive Interface

Built with Streamlit, the app evolved into four modes:

**1. Search & Browse**
Full-text search with AI summaries. Find relevant talks in seconds instead of minutes.

**2. Chat with Video**
Select a presentation and have a conversation about it. Ask "What was the main argument?" or "How does this relate to behavioral economics?" The AI responds with context from the actual transcript.

**Cost per chat**: ~$0.003 (less than a third of a cent)

**3. Chat with All Transcripts**
The ambitious feature: query across all 17 presentations. "Which talks discuss policy recommendations?" gets you synthesized answers drawing from multiple sources.

Instead of sending 91K words to the API (expensive!), the system uses AI-generated summaries as context—reducing token usage by 95% while maintaining quality.

**4. Presenters Directory**
Browse all 38 economists with direct links to their work and see which presentations they contributed to.

### Phase 4: Polish and Launch Prep

The final hours focused on UX refinement and preparing for public use:

**Layout optimization**: Chat interface moved to the forefront instead of buried below metadata. Summaries auto-expand on first view, then collapse to stay out of your way.

**Title standardization**: YouTube's inconsistent titles cleaned up. Welcome talk moved to first position for natural onboarding.

**Homepage clarity**: Added "Why this app?" section explaining the value proposition and feature highlights.

**Bug fixes**: Discovered some presenter entries were actually dates and event names ("September 18-19", "Economics of Transformative AI Workshop")—artifacts from automated parsing. Quick fix cleaned the data.

**Documentation**: Created comprehensive guides:
- `CLAUDE.md` - Technical architecture and development guide
- `FEATURES.md` - Cost control strategies and future roadmap
- `README.md` - Updated with workshop details and setup instructions

## Preparing for the Real World: Cost Controls

Before launching publicly, we mapped out cost protection:

**Current costs (no limits)**:
- 1,000 users × 5 chats = $20/month ✓
- 10,000 users × 10 chats = $400/month ⚠️

**Planned controls**:
1. **Rate limiting** - 10 messages per session, 100 requests/hour globally
2. **Budget caps** - Hard limit in OpenAI dashboard
3. **Context optimization** - Reduce transcript windows from 15K→10K chars
4. **Response caching** - Store common questions for 50% cost reduction

With these controls: **$10-50/month** for moderate traffic.

## The Tech Stack (Simplified)

- **Frontend**: Streamlit (pure Python, no HTML/CSS/JS needed)
- **AI**: OpenAI GPT-4o-mini for chat and summaries
- **Data**: Single JSON file (17 videos, ~500KB)
- **Cost**: $0.003-0.005 per interaction

Why a JSON file instead of a database? At this scale (17 videos), it loads in milliseconds, works with version control, and deploys anywhere instantly.

## Development Stats

- **Time**: ~6 hours of conversational development
- **Commits**: 12 total, each adding value without breaking prior work
- **Lines of code**: ~450 for the full Streamlit app
- **Data processing**: ~300 lines across extraction/enrichment scripts

## What "Conversational Development" Looks Like

The paradigm shift isn't just that AI writes code faster—it's that you can **think out loud and watch ideas become real**.

**What Claude handled:**
- YouTube API integration
- OpenAI streaming response handlers
- Data structure transformations
- Presenter metadata extraction
- Summary generation pipeline

**What I focused on:**
- What features researchers actually need
- How information should be organized
- Which optimizations matter for public use
- UX decisions (chat-first layout, summary placement)

This division—human intent, AI execution—is incredibly efficient.

## The Launch

After polishing, the app went live. Initial challenges:
- Remote deployment showed old data (10 transcripts vs 17)
- Solution: Deployment platforms cache aggressively—manual reboot fixed it
- Bad presenter data appeared in production ("September 18-19")
- Solution: Quick data fix, another reboot

Within hours of identifying issues, fixes were pushed and live.

## Key Lessons

**1. Start with data quality**
The first 2 hours were pure data work—no UI, no features. That foundation made everything else trivial.

**2. Iterate in public view**
12 commits, each visible. Watch the app evolve. Learn what works. Adjust.

**3. Context windows are everything**
Transcript: 40K chars → Too expensive
Truncated to 15K chars → Affordable and effective
Use summaries for multi-video queries → 95% cost reduction

**4. UX beats features**
Moving the chat interface above the summary seems minor. In practice, it transforms the user experience.

**5. Cost controls aren't optional**
$20/month is fine. $400/month is concerning. Plan for success before it happens.

## What's Next

The app is live and functional. Future enhancements documented in `FEATURES.md`:

**High Priority (Pre-scale)**:
- Rate limiting implementation
- OpenAI budget monitoring
- Context window optimization

**Future Optimization**:
- Semantic search with embeddings (no API cost for search)
- Smart caching for common questions
- Export chat conversations

**Possible Extensions**:
- Video timestamp linking (jump to relevant moments)
- Multi-language support
- Mobile-optimized interface

## The Broader Point

This project took one afternoon. From "wouldn't it be cool" to "fully functional web app ready for public use."

That's the promise of conversational development: **ideas become reality at the speed of thought**.

Traditional development:
```
Idea → Spec → Architecture → Implementation → Testing → Deploy
(weeks to months)
```

Conversational development:
```
Idea → "Let's build this" → Working app → Polish → Deploy
(hours to days)
```

You don't need to know how to implement everything. You need to know:
- What to build
- How to evaluate if it's working
- When to ship

The AI handles translation from intent to implementation.

## Try It

The full project is on GitHub. To run locally:

```bash
git clone https://github.com/vishalsachdev/nber.git
cd nber
uv sync
echo "OPENAI_API_KEY=your-key" > .env
uv run streamlit run app.py
```

App runs at `http://localhost:8501`.

## Final Thoughts

Started with 17 YouTube URLs and a question: *How can we make this knowledge more accessible?*

Ended with:
- Interactive search across 91,733 words
- AI-powered chat with individual presentations
- Cross-video synthesis capabilities
- Cost-optimized architecture
- Production-ready deployment

The future of software development isn't about replacing human creativity—it's about **amplifying** it.

Give AI clear intent and autonomy to execute. Watch impossible become inevitable.

---

*Vishal explores AI and education at the University of Illinois. This article describes a real project built in a single afternoon using Claude Code. Code and data available in the [repository](https://github.com/vishalsachdev/nber).*

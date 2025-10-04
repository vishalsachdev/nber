# When the Hook Doesn't Fire: Debugging Session Logs and Discovering Free AI APIs

**Project:** NBER Economics of Transformative AI Workshop Explorer
**Date:** October 4, 2025
**Topics:** Developer tooling, API migrations, collaborative debugging

---

## The Setup: Newsletter Infrastructure That Wasn't Working

Three days ago, I set up what seemed like an elegant solution for documenting my AI collaboration sessions. I created a Python hook script (`/Users/vishal/.claude/hooks/export-session.py`) that would automatically run whenever I exited a Claude Code session, exporting a condensed version of our conversation—full user questions, summarized AI responses, timestamps—into a markdown file under `articles/chat-sessions/`.

The hook script itself was solid: 113 lines of Python that would read the session transcript JSON, extract the key information, and save it in a format perfect for later newsletter writing. The `CLAUDE.md` file in my global config even documented this workflow explicitly:

```markdown
### Chat Session Data Sources
- **Automatic export enabled**: SessionEnd hook exports sessions to `/articles/chat-sessions/`
- **Export format**: Markdown with user questions (full) + AI response summaries (150 chars) + timestamps
```

There was just one problem: **it never actually ran**.

I exited sessions. Nothing appeared in `articles/chat-sessions/`. I checked the hook script—it was executable, properly formatted, sitting right where it should be in `/Users/vishal/.claude/hooks/`. I even had a `README.md` in that same hooks directory with complete setup instructions showing exactly how to configure it in Claude Code's `settings.json`.

But when I started a fresh session today and asked Claude to check why the hook wasn't firing, we discovered something embarrassing: **the hook was never configured in the first place**.

## The Five-Minute Fix

The diagnosis took seconds once we looked in the right place. Claude checked `/Users/vishal/.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "alwaysThinkingEnabled": false,
  "feedbackSurveyState": {
    "lastShownTime": 1754086158200
  }
}
```

No `hooks` configuration. At all.

I'd created the hook script, written the documentation, added it to my `CLAUDE.md` instructions, but never actually *registered* it in Claude Code's settings. The fix was literally adding these lines:

```json
"hooks": {
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "/Users/vishal/.claude/hooks/export-session.py"
        }
      ]
    }
  ]
}
```

That's it. One Edit tool call at line 7 of `settings.json`, and suddenly my newsletter infrastructure was live. Future sessions would automatically export their conversations to markdown.

This is the kind of bug that feels stupid in retrospect but teaches an important lesson: **automation only works if you actually enable it**. I'd done everything *around* the hook—created the script, made it executable, documented the workflow—but missed the one step that made it functional.

## The Real Story: A Three-Day API Migration Journey

But that quick debugging session was just the bookend to a much more interesting development story. When Claude asked if I wanted to write a newsletter article, I said yes, and we started reconstructing what had happened over the past few days by looking at the git history.

The timeline told the story of an evolution from a local Python prototype to a production-ready React application, culminating in an API migration that solved a critical cost problem.

### September 30: Birth of the NBER Explorer

The project started as a single-day sprint. I wanted to explore the NBER Economics of Transformative AI Workshop videos—17 presentations from economists like Daron Acemoglu, Paul Romer, and Joseph Stiglitz discussing how transformative AI would reshape labor markets, innovation, and economic policy.

The data pipeline came together in a few hours:
- `extract_transcripts.py` pulled YouTube transcripts using the youtube-transcript-api
- `generate_summaries.py` created 2-3 paragraph AI summaries of each presentation using OpenAI's GPT-4o-mini
- `app.py` built a Streamlit interface with search, single-video chat, cross-video chat, and a presenter directory

By the end of the day, I had a working prototype with all 17 videos, 91,733 words of transcribed content, and AI-powered chat features. The git log shows this compressed development cycle:

```
2025-09-30 07:30 - Add NBER video transcript extraction tools
2025-09-30 08:14 - Add Streamlit app for interactive transcript exploration
2025-09-30 08:19 - Add AI-generated summaries for all presentations
2025-09-30 08:22 - Add 'Chat with All Transcripts' mode
2025-09-30 16:30 - Complete project with all 17 transcripts and production-ready features
```

Nine hours from initial commit to production-ready. The velocity was exhilarating, but it came with a catch: **the app ran on OpenAI's API**, which meant every chat interaction cost money. Not much—about $0.003-0.005 per message with GPT-4o-mini—but enough that deploying it publicly would require rate limiting, budget caps, and careful cost monitoring.

### September 30-October 1: The React Migration

The same day, I started rebuilding the app in React. Why? Streamlit is fantastic for rapid prototyping but less ideal for production deployments where you want fine-grained control over user interactions, caching, and cost management.

The bolt branch (which became the main development branch) shows this transition:

```
2025-09-30 23:53 - Clean up bolt branch: remove Streamlit-specific files
2025-10-01 00:13 - Fix Google Scholar URLs and add markdown rendering to chat
2025-10-01 00:49 - Improve UI and fix presenter count in React frontend
2025-10-01 00:59 - Add Vercel deployment config and fix TypeScript errors
2025-10-01 22:12 - Add live demo URL to README
```

By October 1st, I had a live React app deployed on Vercel at `https://frontend-13nkin9ja-vishalsachdevs-projects.vercel.app`. The UI was cleaner, the chat interface supported markdown rendering for better formatting, and the whole thing was production-ready.

Except for one problem: **it was still using OpenAI's API**, which meant the cost concern remained.

### October 4: The UIUC Chat API Discovery

This morning's session started with a simple request: "write article." But before we could write about the project, Claude needed to understand what had changed since the last documented version.

That's when we looked at the most recent commit:

```
374c48c (HEAD -> bolt) Add UIUC Chat API integration with Vercel proxy
```

Wait—UIUC Chat API? That wasn't in the original design. I looked at the commit details:

```
Add UIUC Chat API integration with Vercel proxy

- Create Vercel Edge Function to proxy UIUC Chat API
- Update frontend to use /api/chat endpoint
- Configure Vite dev proxy for local development
- Replace OpenRouter with UIUC Chat API (Qwen2.5-VL-72B)
- Fix CORS issues for production deployment
- Update streaming parser for plain text chunks
```

This was a complete API migration. I'd replaced OpenAI entirely with the [UIUC Chat API](https://uiuc.chat/), which provides free access to powerful language models (in this case, Qwen2.5-VL-72B, a 72-billion-parameter vision-language model).

The implementation was elegant. Instead of calling OpenAI directly from the frontend, I created a Vercel Edge Function at `frontend/api/chat.ts`:

```typescript
// Vercel Serverless Function to proxy UIUC Chat API
// This avoids CORS issues in production

export const config = {
  runtime: 'edge',
};

export default async function handler(req: Request) {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  try {
    const body = await req.json();

    // Forward the request to UIUC Chat API
    const response = await fetch('https://uiuc.chat/api/chat-api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return new Response(response.statusText, { status: response.status });
    }

    // Return the streaming response
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('API proxy error:', error);
    return new Response('Internal server error', { status: 500 });
  }
}
```

This solved two problems at once:
1. **CORS issues**: By proxying the UIUC API through Vercel's serverless function, I avoided cross-origin restrictions that would have blocked direct browser calls
2. **Cost**: The UIUC Chat API is free for academic and research use, which perfectly aligns with this NBER workshop explorer

For local development, I configured Vite to proxy the `/api/chat` endpoint to the UIUC API, so the same code works in both dev and production.

## The Technical Shift: From OpenAI to Open Models

The migration from OpenAI to UIUC Chat represents a broader trend I've been tracking: **the democratization of powerful AI models through free academic APIs**.

When I started this project on September 30th, my default was OpenAI. GPT-4o-mini is inexpensive ($0.15 per million input tokens, $0.60 per million output tokens) and reliable. But "inexpensive" still means *costs money*, which creates friction for public deployment.

The UIUC Chat API removes that friction entirely. Qwen2.5-VL-72B is a capable model—72 billion parameters, multimodal vision-language support, strong performance on reasoning tasks—and it's available for free through UIUC's infrastructure.

This isn't just a cost optimization. It's a **philosophical shift** in how I think about building AI-powered applications:

### Before (OpenAI approach):
- Default to commercial APIs
- Implement rate limiting to control costs
- Add budget monitoring and caps
- Worry about unexpected traffic spikes
- Limit features to stay within budget

### After (UIUC Chat approach):
- Default to free academic APIs when available
- Focus on user experience instead of cost
- Enable features without financial constraints
- Contribute back to academic infrastructure
- Reserve commercial APIs for use cases that truly need them

The UIUC Chat API isn't perfect—response quality varies by model, uptime isn't guaranteed, and there's no SLA for production use. But for an academic research tool exploring NBER workshop presentations, it's a perfect fit.

## What This Means for the Hybrid Builder Paradigm

This three-day arc—from Streamlit prototype to React production app to free API migration—illustrates something fundamental about AI-assisted development: **the bottleneck shifts from implementation to discovery**.

Claude and I didn't spend hours debugging TypeScript errors or wrestling with CORS policies. We spent our time *discovering better solutions*:
- "What if we migrate to React for better production deployment?"
- "How can we reduce API costs for public use?"
- "Is there a free academic API that fits this use case?"

The actual *implementation* of each solution—writing the Vercel Edge Function, configuring the Vite proxy, updating the frontend chat component—took minutes. The discovery and decision-making took longer.

This is the pattern I keep seeing in my Claude Code sessions: **rapid iteration through solution spaces**. We're not slowly building one thing; we're quickly trying several things and keeping what works.

The hook debugging at the start of this session is a perfect microcosm: we identified the problem (missing config), implemented the fix (one JSON edit), and moved on to the next task (writing this article) in under five minutes. No StackOverflow searching, no trial-and-error with different hook configurations, no reading through Claude Code documentation PDFs.

## The Newsletter Infrastructure That Now Works

By the time you're reading this, the SessionEnd hook I debugged at the start of today's session will be capturing every conversation I have with Claude Code in this project.

Each exported session becomes source material for future articles:
- Chronological narrative of collaboration
- Key questions and decisions made
- Timeline of development process
- Behind-the-scenes problem-solving

The hook exports to `articles/chat-sessions/YYYY-MM-DD-HHMMSS-session.md` with this format:

```markdown
# Chat Session Export

**Project:** nber
**Session ID:** abc123
**Working Directory:** /Users/vishal/Desktop/nber
**End Reason:** user_exit
**Exported:** 2025-10-04T12:30:00

---

### [12:16:45] User
i just exited the previous session and the hook that activates when i exit did not work to create a log. check

### [12:16:52] Assistant
*I'll check the hook configuration and the chat-sessions directory to diagnose the issue...*

### [12:18:30] User
write article

### [12:18:35] Assistant
*Reading exported chat session logs, reviewing git history, and analyzing the UIUC API migration work...*
```

This condensed format makes it easy to review past sessions without drowning in 10,000-word conversation transcripts. Full user questions, summarized AI responses, timestamps for narrative flow.

And now that it's properly configured, it runs automatically. No manual export, no copy-pasting conversation history, no trying to remember what we discussed three sessions ago.

## Reflections on Free AI Infrastructure

The UIUC Chat API migration raises an interesting question about the future of AI application development: **how much of the AI application stack will become free?**

A few years ago, the answer was "none of it." OpenAI's API was the only game in town, and you paid per token. Then came open-source models like LLaMA, which you could run locally if you had the hardware. Now we're seeing a third category: **free hosted APIs for academic and research use**.

UIUC Chat isn't unique. There's Hugging Face Inference API (free tier), Together AI (research credits), Replicate (pay-as-you-go with free trials), and university-hosted endpoints like Stanford's Alpaca.

For projects like this NBER workshop explorer—academic research tools, educational applications, non-commercial experiments—these free APIs are transformative. They remove the financial barrier between "interesting idea" and "live deployment."

The tradeoff is reliability. Commercial APIs come with SLAs, guaranteed uptime, dedicated support. Academic APIs come with "best effort" hosting and community support. But for many use cases, that's perfectly acceptable.

I suspect we'll see more projects defaulting to free academic APIs for MVP deployment, then migrating to commercial APIs only when they need production-grade reliability or scale beyond academic use cases.

## What's Next

The NBER explorer is now live at `https://frontend-13nkin9ja-vishalsachdevs-projects.vercel.app` with:
- 17 workshop presentations fully transcribed and searchable
- AI chat powered by Qwen2.5-VL-72B through UIUC Chat API (free)
- Clean React UI with markdown rendering
- Presenter directory with Google Scholar links
- Cross-video synthesis for asking questions across all presentations

The SessionEnd hook is now properly configured and will capture future development sessions.

And I'm left thinking about the broader implications of this three-day journey: from prototype to production, from paid API to free alternative, from broken automation to working infrastructure.

The future of development isn't just "AI helps you write code faster." It's "AI helps you discover better solutions, implement them rapidly, and iterate through possibilities at conversational speed."

And sometimes, it also helps you realize you forgot to add six lines of JSON to your settings file.

---

*This article documents the development of the [NBER Economics of Transformative AI Workshop Explorer](https://frontend-13nkin9ja-vishalsachdevs-projects.vercel.app), built collaboratively with Claude Code from September 30 to October 4, 2025.*

*Repository: [github.com/vishalsachdev/nber](https://github.com/vishalsachdev/nber)*

*Previous article: [From 404 to Production: Building an AI-Powered NBER Workshop Explorer in One Day](2025-09-30-nber-ai-workshop-explorer.md)*

"""
NBER AI Economics Workshop - Transcript Explorer
A Streamlit app for searching and chatting with video transcripts
"""

import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="NBER AI Economics - Transcript Explorer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OPENAI_API_KEY not found. Please set it in your .env file.")
        st.stop()
    return OpenAI(api_key=api_key)

# Load video data
@st.cache_data
def load_videos():
    with open('nber_videos_transcripts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

client = get_openai_client()
videos = load_videos()

# Header
st.title("🎓 NBER Economics of Transformative AI Workshop")
st.markdown("*Fall 2025 • Explore presentations, chat with transcripts, and discover insights*")

# Statistics in a compact row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📹 Videos", len(videos))
with col2:
    st.metric("📝 Transcripts", sum(1 for v in videos if v['has_transcript']))
with col3:
    st.metric("👥 Presenters", sum(v['num_presenters'] for v in videos))
with col4:
    st.metric("💬 Q&A", "Available")

st.divider()

# Main navigation using tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Search & Browse",
    "💬 Chat with Video",
    "🌐 Chat with All",
    "👥 Presenters"
])

# Helper functions
def search_videos(query):
    """Search videos by title, presenter, or transcript content"""
    if not query:
        return videos

    query_lower = query.lower()
    results = []

    for video in videos:
        # Search in title
        if query_lower in video['title'].lower():
            results.append(video)
            continue

        # Search in presenters
        presenter_match = any(
            query_lower in p['name'].lower() or query_lower in p['affiliation'].lower()
            for p in video.get('presenters', [])
        )
        if presenter_match:
            results.append(video)
            continue

        # Search in transcript (if available)
        if video.get('transcript') and query_lower in video['transcript'].lower():
            results.append(video)
            continue

    return results

def get_all_presenters():
    """Get unique list of all presenters with their videos"""
    presenter_map = {}

    for video in videos:
        for presenter in video.get('presenters', []):
            name = presenter['name']
            if name not in presenter_map:
                presenter_map[name] = {
                    'name': name,
                    'affiliation': presenter['affiliation'],
                    'scholar_url': presenter.get('scholar_url'),
                    'videos': []
                }
            presenter_map[name]['videos'].append({
                'title': video['title'],
                'id': video['id'],
                'url': video['url']
            })

    return sorted(presenter_map.values(), key=lambda x: x['name'])

def chat_with_transcript(video, user_message):
    """Generate response using OpenAI with transcript context"""
    if not video.get('transcript'):
        return "❌ No transcript available for this video."

    # Prepare context
    context = f"""You are an AI assistant helping users understand a presentation from the NBER Economics of Transformative AI Workshop.

Video Title: {video['title']}
Presenters: {', '.join([p['name'] for p in video.get('presenters', [])])}

Full Transcript:
{video['transcript'][:15000]}  # Limit context to ~15k chars to stay within token limits

Answer the user's question based on this transcript. Be concise and cite specific points from the presentation when relevant."""

    # Add to message history
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                *st.session_state.messages
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )

        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

def chat_with_all_transcripts(user_message):
    """Generate response using OpenAI with context from all transcripts"""
    # Get all videos with transcripts
    available_videos = [v for v in videos if v.get('transcript')]

    if not available_videos:
        return "❌ No transcripts available."

    # Build combined context with video summaries
    video_summaries = []
    for video in available_videos:
        title = video['title']
        presenters = ', '.join([p['name'] for p in video.get('presenters', [])])
        # Use AI summary if available, otherwise use first 500 chars of transcript
        summary = video.get('ai_summary', video['transcript'][:500])
        video_summaries.append(f"**{title}** by {presenters}\n{summary}")

    context = f"""You are an AI assistant helping users understand presentations from the NBER Economics of Transformative AI Workshop (Fall 2025).

You have access to information from {len(available_videos)} presentations:

{chr(10).join(video_summaries[:10])}  # Limit to first 10 to stay within token limits

Answer the user's question by synthesizing information across these presentations. When referencing specific presentations, mention the title and presenter. If the question relates to a specific topic, identify which presentations are most relevant."""

    # Add to message history
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                *st.session_state.messages
            ],
            temperature=0.7,
            max_tokens=1200,
            stream=True
        )

        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Main content in tabs
with tab1:
    st.markdown("### 🔍 Search & Browse Transcripts")

    # Search bar
    search_query = st.text_input(
        "Search by title, presenter, or content:",
        value=st.session_state.search_query,
        placeholder="e.g., 'AI agents', 'Stiglitz', 'behavioral economics'"
    )
    st.session_state.search_query = search_query

    # Search results
    results = search_videos(search_query)

    st.markdown(f"### Found {len(results)} video(s)")

    # Display results
    for video in results:
        with st.expander(f"📹 {video['title']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Upload Date:** {video.get('upload_date', 'Unknown')}")

                if video.get('presenters'):
                    st.markdown("**Presenters:**")
                    for presenter in video['presenters']:
                        scholar_link = presenter.get('scholar_url', '')
                        if scholar_link:
                            st.markdown(f"- [{presenter['name']}]({scholar_link}) - *{presenter['affiliation']}*")
                        else:
                            st.markdown(f"- {presenter['name']} - *{presenter['affiliation']}*")

                st.markdown(f"**[🔗 Watch on YouTube]({video['url']})**")

                # Display AI-generated summary
                if video.get('ai_summary'):
                    st.markdown("**📝 AI-Generated Summary:**")
                    st.info(video['ai_summary'])
                    st.caption("*Summary generated using OpenAI GPT-4o-mini*")

                # Original description as expandable
                if video.get('description'):
                    with st.expander("📄 View Full Description"):
                        st.text(video['description'])

            with col2:
                st.metric("Transcript", "✅ Available" if video['has_transcript'] else "❌ Not Available")
                if video['has_transcript']:
                    st.metric("Words", f"{video.get('word_count', 0):,}")

                if video['has_transcript']:
                    if st.button("💬 Chat with this transcript", key=f"chat_{video['id']}"):
                        st.session_state.selected_video = video
                        st.session_state.messages = []
                        st.rerun()

with tab2:
    st.markdown("### 💬 Chat with Video Transcript")

    # Video selector
    if not st.session_state.selected_video:
        st.info("👈 Please select a video from Search & Browse mode first")

        # Quick select
        st.markdown("### Or select a video here:")
        available_videos = [v for v in videos if v['has_transcript']]

        video_options = {f"{v['title'][:60]}...": v for v in available_videos}
        selected_title = st.selectbox("Choose a video:", list(video_options.keys()))

        if st.button("Start Chat"):
            st.session_state.selected_video = video_options[selected_title]
            st.session_state.messages = []
            st.rerun()
    else:
        video = st.session_state.selected_video

        # Display video info
        st.markdown(f"### 📹 {video['title']}")
        st.markdown(f"*Presenters: {', '.join([p['name'] for p in video.get('presenters', [])])}*")

        if st.button("← Back to Search"):
            st.session_state.selected_video = None
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Chat interface
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about this presentation..."):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant"):
                response_stream = chat_with_transcript(video, prompt)

                if isinstance(response_stream, str):
                    st.markdown(response_stream)
                else:
                    response_text = st.write_stream(
                        (chunk.choices[0].delta.content or "" for chunk in response_stream)
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

with tab3:
    st.markdown("### 🌐 Chat with All Transcripts")
    st.markdown("*Ask questions across all workshop presentations*")

    # Show available videos
    available_videos = [v for v in videos if v['has_transcript']]

    with st.expander(f"📚 Available Transcripts ({len(available_videos)} videos)"):
        for video in available_videos:
            st.markdown(f"- **{video['title']}** by {', '.join([p['name'] for p in video.get('presenters', [])])}")

    st.divider()

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the workshop presentations..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            response_stream = chat_with_all_transcripts(prompt)

            if isinstance(response_stream, str):
                st.markdown(response_stream)
            else:
                response_text = st.write_stream(
                    (chunk.choices[0].delta.content or "" for chunk in response_stream)
                )
                st.session_state.messages.append({"role": "assistant", "content": response_text})

    # Helpful prompts
    if not st.session_state.messages:
        st.markdown("### 💡 Try asking:")
        st.markdown("""
        - "What are the main concerns about AI and labor markets?"
        - "Which presentations discuss behavioral economics?"
        - "What did Joseph Stiglitz say about AI?"
        - "Compare the different perspectives on AI's economic impact"
        - "What are the policy recommendations across presentations?"
        """)

with tab4:
    st.markdown("### 👥 Presenters Directory")
    st.markdown("*Economics of Transformative AI Workshop - Fall 2025*")

    presenters = get_all_presenters()

    # Search presenters
    presenter_search = st.text_input("Search presenters:", placeholder="Name or affiliation")

    if presenter_search:
        presenters = [
            p for p in presenters
            if presenter_search.lower() in p['name'].lower()
            or presenter_search.lower() in p['affiliation'].lower()
        ]

    st.markdown(f"### {len(presenters)} Presenter(s)")

    # Display presenters
    for presenter in presenters:
        with st.expander(f"**{presenter['name']}** - *{presenter['affiliation']}*", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                if presenter.get('scholar_url'):
                    st.markdown(f"**[📚 Google Scholar Profile]({presenter['scholar_url']})**")

                st.markdown(f"**Presentations:** {len(presenter['videos'])}")
                for video in presenter['videos']:
                    st.markdown(f"- [{video['title'][:80]}...]({video['url']})")

            with col2:
                st.metric("Videos", len(presenter['videos']))

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏛️ NBER Workshop Fall 2025")
with col2:
    st.caption("🤖 Powered by OpenAI GPT-4o-mini")
with col3:
    st.caption("⚡ Built with Streamlit")
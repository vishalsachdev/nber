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
    initial_sidebar_state="expanded"
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

# Sidebar
with st.sidebar:
    st.title("🎓 NBER AI Economics")
    st.markdown("### Workshop Transcripts")
    st.markdown("*Economics of Transformative AI*  \n*Fall 2025*")

    st.divider()

    mode = st.radio(
        "Choose Mode:",
        ["🔍 Search & Browse", "💬 Chat with Transcript", "👥 Presenters"],
        index=0
    )

    st.divider()

    # Video statistics
    total_videos = len(videos)
    videos_with_transcripts = sum(1 for v in videos if v['has_transcript'])
    total_presenters = sum(v['num_presenters'] for v in videos)

    st.metric("Total Videos", total_videos)
    st.metric("With Transcripts", videos_with_transcripts)
    st.metric("Presenters", total_presenters)

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

# Main content
if mode == "🔍 Search & Browse":
    st.title("🔍 Search & Browse Transcripts")

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

            with col2:
                st.metric("Transcript", "✅ Available" if video['has_transcript'] else "❌ Not Available")
                if video['has_transcript']:
                    st.metric("Words", f"{video.get('word_count', 0):,}")

                if video['has_transcript']:
                    if st.button("💬 Chat with this transcript", key=f"chat_{video['id']}"):
                        st.session_state.selected_video = video
                        st.session_state.messages = []
                        st.rerun()

elif mode == "💬 Chat with Transcript":
    st.title("💬 Chat with Transcript")

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

elif mode == "👥 Presenters":
    st.title("👥 Presenters Directory")
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
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Built with Streamlit • Powered by OpenAI GPT-4o-mini</p>
        <p>Data from NBER Economics of Transformative AI Workshop, Fall 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
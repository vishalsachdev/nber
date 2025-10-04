# NBER AI Economics - Transcript Explorer

An interactive Streamlit application for exploring and chatting with transcripts from the NBER Economics of Transformative AI Workshop (Fall 2025).

## Features

- **🔍 Search & Browse**: Search through 17 video transcripts by title, presenter, or content
- **💬 Chat with Transcripts**: Ask questions about specific presentations using AI
- **👥 Presenters Directory**: Browse all 26 presenters with Google Scholar profiles
- **Semantic Understanding**: Powered by OpenAI GPT-4o-mini for intelligent responses

## Setup

### 1. Install Dependencies

Using uv (recommended):
```bash
uv sync
uv add streamlit openai python-dotenv pandas
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Add your key to `.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

⚠️ **Never commit your `.env` file to git!**

### 3. Run the App

Using uv:
```bash
uv run streamlit run app.py
```

Or standard Python:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Search & Browse Mode

1. Enter keywords to search across titles, presenters, or transcript content
2. Browse results and view presenter information
3. Click "💬 Chat with this transcript" to start a conversation

### Chat with Transcript Mode

1. Select a video from the dropdown or navigate from Search mode
2. Ask questions about the presentation
3. Get AI-powered answers based on the actual transcript content
4. Chat history is maintained during your session

### Presenters Directory

1. Browse all workshop presenters
2. Click on presenter names to view their Google Scholar profiles
3. See all videos each presenter participated in

## Data

The app uses `nber_videos_transcripts.json` which contains:
- 17 videos from the workshop
- 10 complete transcripts (~55K words)
- 26 presenter profiles with Google Scholar links
- Full metadata (titles, dates, descriptions)

## Architecture

```
app.py                           # Main Streamlit application
nber_videos_transcripts.json     # Video data with transcripts
.env                             # Your OpenAI API key (not in git)
requirements.txt                 # Python dependencies
```

## API Costs

The app uses **GPT-4o-mini** which costs:
- **15¢ per 1M input tokens**
- **60¢ per 1M output tokens**

Typical cost per chat: **< $0.01**

## Features Explained

### Smart Search
- Full-text search across all transcripts
- Presenter name and affiliation matching
- Instant results with video metadata

### Context-Aware Chat
- Uses actual transcript content as context
- Maintains conversation history
- Streams responses for better UX
- Cites specific points from presentations

### Presenter Profiles
- Direct links to Google Scholar
- Shows all videos per presenter
- Affiliation information
- Citation metrics available on Scholar

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure you created `.env` file with your API key
- Check that the key starts with `sk-`

**"No such file: nber_videos_transcripts.json"**
- Run the app from the project root directory
- Ensure the JSON file exists

**Chat responses are slow**
- Normal for first response (loading model)
- Subsequent responses use streaming
- Large transcripts may take 5-10 seconds

**Import errors**
- Run `uv sync` or `pip install -r requirements.txt`
- Make sure you're in the correct virtual environment

## Development

To extend the app:

1. **Add semantic search**: Implement vector embeddings with ChromaDB
2. **Multi-video chat**: Allow questions across multiple transcripts
3. **Export features**: Download chat history or search results
4. **Advanced filters**: Filter by date, presenter, topic tags
5. **Comparison mode**: Compare presentations side-by-side

## Privacy & Security

- API key stored locally in `.env` file
- No data sent to third parties except OpenAI
- Transcript data is public (from YouTube)
- Session data cleared on browser close

## Credits

- **Data Source**: NBER Economics of Transformative AI Workshop, Fall 2025
- **Powered by**: OpenAI GPT-4o-mini, Streamlit
- **Organizers**: Ajay K. Agrawal, Anton Korinek, Erik Brynjolfsson

## License

MIT
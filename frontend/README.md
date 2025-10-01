# NBER AI Workshop Explorer - Modern Frontend

A modern, responsive web application for exploring presentations from the NBER Economics of Transformative AI Workshop (Fall 2025). Built with React, TypeScript, Vite, and Supabase.

## Features

- **Search & Browse**: Search through 17 presentations by title, presenter, or transcript content
- **AI-Powered Chat**: Chat with individual presentations using OpenAI GPT-4o-mini
- **Cross-Presentation Analysis**: Query across all presentations to compare perspectives
- **Presenters Directory**: Browse all 34 presenters with Google Scholar profiles
- **Modern UI**: Clean, responsive design with smooth animations and transitions
- **Real-time Streaming**: Streaming chat responses for immediate feedback

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4o-mini
- **Styling**: Custom CSS with CSS variables

## Prerequisites

- Node.js 18+ and npm
- Supabase account and project
- OpenAI API key

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:

   Create a `.env` file in the `frontend` directory with:
   ```env
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_OPENAI_API_KEY=your_openai_api_key
   ```

3. **Import data** (if needed):
   ```bash
   node import-data.mjs
   ```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Header.tsx
│   │   ├── SearchBrowse.tsx
│   │   ├── VideoCard.tsx
│   │   ├── ChatWithVideo.tsx
│   │   ├── ChatWithAll.tsx
│   │   └── Presenters.tsx
│   ├── lib/             # Utilities and API clients
│   │   ├── supabase.ts  # Supabase client and types
│   │   ├── api.ts       # Data fetching functions
│   │   └── openai.ts    # OpenAI chat functions
│   ├── App.tsx          # Main application component
│   ├── App.css          # Global styles
│   └── main.tsx         # Application entry point
├── import-data.mjs      # Data import script
└── package.json
```

## Features Overview

### Search & Browse
- Full-text search across titles, presenters, and transcripts
- Expandable video cards with metadata and AI-generated summaries
- Direct links to YouTube videos and Google Scholar profiles

### Chat with Video
- Select any presentation to start a conversation
- AI assistant answers questions based on the transcript
- Streaming responses for real-time interaction
- Context limited to 15k characters for optimal performance

### Chat with All
- Query across all presentations simultaneously
- AI synthesizes information from multiple videos
- Uses AI-generated summaries for efficient context
- Suggested questions to get started

### Presenters Directory
- Browse all workshop presenters
- Search by name or affiliation
- View number of presentations per presenter
- Direct links to Google Scholar profiles

## Database Schema

The application uses the following Supabase tables:

- `videos`: Video metadata and transcripts
- `presenters`: Presenter information
- `video_presenters`: Many-to-many relationship between videos and presenters
- `chat_sessions`: Chat session tracking (optional)
- `chat_messages`: Chat message history (optional)

## OpenAI Integration

- Model: `gpt-4o-mini`
- Temperature: 0.7
- Streaming enabled for better UX
- Cost: ~$0.01 per conversation

## Performance

- Lazy loading and code splitting
- Optimized database queries with proper indexing
- Client-side caching of video data
- Responsive design for all device sizes

## License

This project is for educational and research purposes.

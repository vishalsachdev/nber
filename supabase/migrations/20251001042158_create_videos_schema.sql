/*
  # NBER Video Transcript Explorer Schema

  1. New Tables
    - `videos`
      - `id` (text, primary key) - YouTube video ID
      - `title` (text) - Video title
      - `url` (text) - YouTube URL
      - `description` (text) - Full video description
      - `ai_summary` (text) - AI-generated summary
      - `upload_date` (date) - Video upload date
      - `has_transcript` (boolean) - Whether transcript is available
      - `word_count` (integer) - Transcript word count
      - `char_count` (integer) - Transcript character count
      - `transcript` (text) - Full transcript content
      - `created_at` (timestamptz) - Record creation timestamp
      - `updated_at` (timestamptz) - Record update timestamp

    - `presenters`
      - `id` (uuid, primary key) - Unique presenter ID
      - `name` (text) - Presenter name
      - `affiliation` (text) - Institution affiliation
      - `scholar_url` (text) - Google Scholar profile URL
      - `created_at` (timestamptz) - Record creation timestamp

    - `video_presenters`
      - `video_id` (text, foreign key) - References videos.id
      - `presenter_id` (uuid, foreign key) - References presenters.id
      - Composite primary key on (video_id, presenter_id)

    - `chat_sessions`
      - `id` (uuid, primary key) - Unique session ID
      - `video_id` (text, foreign key) - References videos.id (nullable for multi-video chat)
      - `is_multi_video` (boolean) - Whether chat spans multiple videos
      - `created_at` (timestamptz) - Session creation timestamp

    - `chat_messages`
      - `id` (uuid, primary key) - Unique message ID
      - `session_id` (uuid, foreign key) - References chat_sessions.id
      - `role` (text) - 'user' or 'assistant'
      - `content` (text) - Message content
      - `created_at` (timestamptz) - Message creation timestamp

  2. Security
    - Enable RLS on all tables
    - All tables are publicly readable (no authentication required for this public research tool)
*/

-- Create videos table
CREATE TABLE IF NOT EXISTS videos (
  id text PRIMARY KEY,
  title text NOT NULL,
  url text NOT NULL,
  description text DEFAULT '',
  ai_summary text,
  upload_date date,
  has_transcript boolean DEFAULT false,
  word_count integer DEFAULT 0,
  char_count integer DEFAULT 0,
  transcript text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create presenters table
CREATE TABLE IF NOT EXISTS presenters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  affiliation text NOT NULL,
  scholar_url text,
  created_at timestamptz DEFAULT now()
);

-- Create video_presenters junction table
CREATE TABLE IF NOT EXISTS video_presenters (
  video_id text NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  presenter_id uuid NOT NULL REFERENCES presenters(id) ON DELETE CASCADE,
  PRIMARY KEY (video_id, presenter_id)
);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id text REFERENCES videos(id) ON DELETE CASCADE,
  is_multi_video boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('user', 'assistant')),
  content text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_videos_has_transcript ON videos(has_transcript);
CREATE INDEX IF NOT EXISTS idx_videos_upload_date ON videos(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_video_presenters_video_id ON video_presenters(video_id);
CREATE INDEX IF NOT EXISTS idx_video_presenters_presenter_id ON video_presenters(presenter_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_video_id ON chat_sessions(video_id);

-- Enable full-text search on videos
CREATE INDEX IF NOT EXISTS idx_videos_title_search ON videos USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_videos_transcript_search ON videos USING gin(to_tsvector('english', coalesce(transcript, '')));
CREATE INDEX IF NOT EXISTS idx_presenters_name_search ON presenters USING gin(to_tsvector('english', name));

-- Enable RLS
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE presenters ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_presenters ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Public read access policies (no auth required)
CREATE POLICY "Public can read videos"
  ON videos FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can read presenters"
  ON presenters FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can read video_presenters"
  ON video_presenters FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can read chat_sessions"
  ON chat_sessions FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can insert chat_sessions"
  ON chat_sessions FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Public can read chat_messages"
  ON chat_messages FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Public can insert chat_messages"
  ON chat_messages FOR INSERT
  TO anon
  WITH CHECK (true);

import { useState, useEffect } from 'react';
import { fetchVideosWithPresenters, searchVideos } from './lib/api';
import type { VideoWithPresenters } from './lib/api';
import SearchBrowse from './components/SearchBrowse';
import ChatWithVideo from './components/ChatWithVideo';
import ChatWithAll from './components/ChatWithAll';
import Presenters from './components/Presenters';
import Header from './components/Header';
import './App.css';

type Tab = 'search' | 'chat-video' | 'chat-all' | 'presenters';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('search');
  const [videos, setVideos] = useState<VideoWithPresenters[]>([]);
  const [filteredVideos, setFilteredVideos] = useState<VideoWithPresenters[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVideo, setSelectedVideo] = useState<VideoWithPresenters | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      searchVideos(searchQuery, videos).then(setFilteredVideos);
    } else {
      setFilteredVideos(videos);
    }
  }, [searchQuery, videos]);

  async function loadVideos() {
    try {
      setLoading(true);
      const data = await fetchVideosWithPresenters();
      setVideos(data);
      setFilteredVideos(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load videos');
    } finally {
      setLoading(false);
    }
  }

  const handleStartChat = (video: VideoWithPresenters) => {
    setSelectedVideo(video);
    setActiveTab('chat-video');
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading videos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error-container">
          <p>Error: {error}</p>
          <button onClick={loadVideos}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header
        videosCount={videos.length}
        transcriptsCount={videos.filter(v => v.has_transcript).length}
        presentersCount={34}
      />

      <nav className="tabs">
        <button
          className={`tab ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <span className="tab-icon">🔍</span>
          Search & Browse
        </button>
        <button
          className={`tab ${activeTab === 'chat-video' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat-video')}
        >
          <span className="tab-icon">💬</span>
          Chat with Video
        </button>
        <button
          className={`tab ${activeTab === 'chat-all' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat-all')}
        >
          <span className="tab-icon">🌐</span>
          Chat with All
        </button>
        <button
          className={`tab ${activeTab === 'presenters' ? 'active' : ''}`}
          onClick={() => setActiveTab('presenters')}
        >
          <span className="tab-icon">👥</span>
          Presenters
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'search' && (
          <SearchBrowse
            videos={filteredVideos}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onStartChat={handleStartChat}
          />
        )}
        {activeTab === 'chat-video' && (
          <ChatWithVideo
            selectedVideo={selectedVideo}
            videos={videos.filter(v => v.has_transcript)}
            onVideoSelect={setSelectedVideo}
            onBackToSearch={() => {
              setSelectedVideo(null);
              setActiveTab('search');
            }}
          />
        )}
        {activeTab === 'chat-all' && (
          <ChatWithAll videos={videos.filter(v => v.has_transcript)} />
        )}
        {activeTab === 'presenters' && <Presenters />}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <span>🏛️ NBER Workshop Fall 2025</span>
          <span>🤖 Powered by UIUC Chat (Qwen2.5-VL-72B)</span>
          <span>⚡ Built with React + Vite</span>
        </div>
      </footer>
    </div>
  );
}

export default App;

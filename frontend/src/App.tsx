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
  const [chatAllPrefill, setChatAllPrefill] = useState<string>('');

  useEffect(() => {
    // Initialize from URL parameters
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    const qParam = params.get('q');
    const chatParam = params.get('chat');

    if (tabParam && ['search', 'chat-video', 'chat-all', 'presenters'].includes(tabParam)) {
      setActiveTab(tabParam as Tab);
    }
    if (qParam) setSearchQuery(qParam);
    if (chatParam) setChatAllPrefill(chatParam);

    loadVideos();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      searchVideos(searchQuery, videos).then(setFilteredVideos);
    } else {
      setFilteredVideos(videos);
    }
  }, [searchQuery, videos]);

  // Keep URL in sync with key state
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    params.set('tab', activeTab);
    if (searchQuery) params.set('q', searchQuery); else params.delete('q');
    if (chatAllPrefill) params.set('chat', chatAllPrefill); else params.delete('chat');
    const next = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, '', next);
  }, [activeTab, searchQuery, chatAllPrefill]);

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

  const handleSearchByPresenter = (name: string) => {
    setSearchQuery(name);
    setActiveTab('search');
  };

  const handleChatWithPresenter = (name: string) => {
    setChatAllPrefill(`What are the key points from presentations by ${name}?`);
    setActiveTab('chat-all');
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
        <div className="tabs-spacer" />
        <button
          className="tab share-link"
          onClick={() => {
            navigator.clipboard.writeText(window.location.href).catch(() => {});
          }}
          aria-label="Copy shareable link"
        >
          <span className="tab-icon">🔗</span>
          Share
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
          <ChatWithAll
            videos={videos.filter(v => v.has_transcript)}
            initialInput={chatAllPrefill}
          />
        )}
        {activeTab === 'presenters' && (
          <Presenters
            onSearchByName={handleSearchByPresenter}
            onChatWithPresenter={handleChatWithPresenter}
          />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <span>🏛️ NBER Workshop Fall 2025</span>
          <span>🤖 Powered by UIUC Chat (Qwen2.5-VL-72B)</span>
          <span>⚡ Built with React + Vite</span>
          <span>
            🐞 Feedback?{' '}
            <a
              href="https://github.com/vishalsachdev/nber/issues/new/choose"
              target="_blank"
              rel="noopener noreferrer"
            >
              Open an issue
            </a>
          </span>
          <span>
            ✍️ Build write-up:{' '}
            <a
              href="https://www.linkedin.com/feed/update/urn:li:ugcPost:7380332000815202304/"
              target="_blank"
              rel="noopener noreferrer"
            >
              LinkedIn article
            </a>
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;

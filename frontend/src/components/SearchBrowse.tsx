import type { VideoWithPresenters } from '../lib/api';
import VideoCard from './VideoCard';

interface SearchBrowseProps {
  videos: VideoWithPresenters[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onStartChat: (video: VideoWithPresenters) => void;
}

export default function SearchBrowse({
  videos,
  searchQuery,
  onSearchChange,
  onStartChat
}: SearchBrowseProps) {
  return (
    <div className="search-browse">
      <div className="section-header">
        <h2>Search & Browse Transcripts</h2>
        <p>Find presentations by topic, presenter, or keyword</p>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by title, presenter, or content (e.g., 'AI agents', 'Stiglitz', 'behavioral economics')"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="search-input"
        />
        {searchQuery && (
          <button
            className="search-clear"
            onClick={() => onSearchChange('')}
            aria-label="Clear search"
            title="Clear search"
          >
            ×
          </button>
        )}
      </div>

      <div className="results-count">
        Found <strong>{videos.length}</strong> video{videos.length !== 1 ? 's' : ''}
      </div>

      <div className="videos-grid">
        {videos.map((video) => (
          <VideoCard
            key={video.id}
            video={video}
            highlight={searchQuery}
            onStartChat={onStartChat}
          />
        ))}
      </div>

      {videos.length === 0 && (
        <div className="no-results">
          <p>No videos found matching your search.</p>
          <button onClick={() => onSearchChange('')}>Clear search</button>
        </div>
      )}
    </div>
  );
}

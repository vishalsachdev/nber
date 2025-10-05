import { useState } from 'react';
import type { VideoWithPresenters, Presenter } from '../lib/api';

interface VideoCardProps {
  video: VideoWithPresenters;
  onStartChat: (video: VideoWithPresenters) => void;
  highlight?: string;
}

function Highlight({ text, query }: { text: string; query?: string }) {
  if (!query) return <>{text}</>;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const parts = text.split(new RegExp(`(${escaped})`, 'ig'));
  return (
    <>
      {parts.map((part, i) => part.toLowerCase() === query.toLowerCase() ? <mark key={i}>{part}</mark> : <span key={i}>{part}</span>)}
    </>
  );
}

export default function VideoCard({ video, onStartChat, highlight }: VideoCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="video-card">
      <div
        className="video-card-header"
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer' }}
      >
        <h3><Highlight text={video.title} query={highlight} /></h3>
        <button
          className="expand-btn"
          aria-label={expanded ? 'Collapse' : 'Expand'}
        >
          {expanded ? '−' : '+'}
        </button>
      </div>

      {expanded && (
        <div className="video-card-content">
          <div className="video-info">
            <div className="video-meta">
              {video.upload_date && (
                <span className="meta-item">
                  📅 {new Date(video.upload_date).toLocaleDateString()}
                </span>
              )}
              {video.has_transcript && video.word_count && (
                <span className="meta-item">
                  📝 {video.word_count.toLocaleString()} words
                </span>
              )}
            </div>

            {video.presenters.length > 0 && (
              <div className="presenters">
                <strong>Presenters:</strong>
                <ul>
                  {video.presenters.map((presenter: Presenter, idx: number) => (
                    <li key={presenter.id || idx}>
                      {presenter.scholar_url ? (
                        <a
                          href={presenter.scholar_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="presenter-link"
                        >
                          <Highlight text={presenter.name} query={highlight} />
                        </a>
                      ) : (
                        <Highlight text={presenter.name} query={highlight} />
                      )}
                      {' '}- <span className="affiliation">{presenter.affiliation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {video.ai_summary && (
              <div className="summary">
                <strong>AI-Generated Summary:</strong>
                <p>{video.ai_summary}</p>
                <span className="summary-note">Summary generated using OpenAI GPT-4o-mini</span>
              </div>
            )}
          </div>

          <div className="video-actions">
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
            >
              🔗 Watch on YouTube
            </a>
            {video.has_transcript && (
              <button
                onClick={() => onStartChat(video)}
                className="btn btn-primary"
              >
                💬 Start Chat
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

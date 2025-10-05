import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import type { VideoWithPresenters, Presenter } from '../lib/api';
import { chatWithVideo, type ChatMessage } from '../lib/openai';

interface ChatWithVideoProps {
  selectedVideo: VideoWithPresenters | null;
  videos: VideoWithPresenters[];
  onVideoSelect: (video: VideoWithPresenters) => void;
  onBackToSearch: () => void;
}

export default function ChatWithVideo({
  selectedVideo,
  videos,
  onVideoSelect,
  onBackToSearch
}: ChatWithVideoProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    setMessages([]);
  }, [selectedVideo]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedVideo || isStreaming) return;

    const userMessage: ChatMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    const assistantMessage: ChatMessage = { role: 'assistant', content: '' };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const stream = chatWithVideo(
        selectedVideo.title,
        selectedVideo.presenters.map((p: Presenter) => p.name),
        selectedVideo.transcript || '',
        [...messages, userMessage]
      );

      for await (const chunk of stream) {
        assistantMessage.content += chunk;
        setMessages(prev => [...prev.slice(0, -1), { ...assistantMessage }]);
      }
    } catch (error) {
      assistantMessage.content = `Error: ${error instanceof Error ? error.message : 'Failed to generate response'}`;
      setMessages(prev => [...prev.slice(0, -1), { ...assistantMessage }]);
    } finally {
      setIsStreaming(false);
    }
  };

  if (!selectedVideo) {
    return (
      <div className="chat-with-video">
        <div className="section-header">
          <h2>Chat with Video Transcript</h2>
          <p>Select a video to start chatting</p>
        </div>

        <div className="video-selector">
          <h3>Choose a video to chat with:</h3>
          <div className="video-list">
            {videos.map((video) => (
              <button
                key={video.id}
                className="video-select-btn"
                onClick={() => onVideoSelect(video)}
              >
                <span className="video-select-title">{video.title}</span>
                <span className="video-select-meta">
                  {video.presenters.map(p => p.name).join(', ')}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-with-video">
      <div className="chat-header">
        <div>
          <h2>{selectedVideo.title}</h2>
          <div className="chat-meta">
            <span>
              {selectedVideo.presenters.map((p: Presenter, i: number) => (
                <span key={p.id || i}>
                  {p.scholar_url ? (
                    <a href={p.scholar_url} target="_blank" rel="noopener noreferrer">
                      {p.name}
                    </a>
                  ) : (
                    p.name
                  )}
                  {i < selectedVideo.presenters.length - 1 ? ', ' : ''}
                </span>
              ))}
            </span>
            <span>•</span>
            <a href={selectedVideo.url} target="_blank" rel="noopener noreferrer">
              Watch on YouTube
            </a>
          </div>
        </div>
        <button onClick={onBackToSearch} className="btn btn-secondary">
          ← Back to Search
        </button>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && selectedVideo.ai_summary && (
            <div className="chat-message assistant">
              <div className="message-content">
                <strong>Summary:</strong>
                <p>{selectedVideo.ai_summary}</p>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.role}`}>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about this presentation..."
            disabled={isStreaming}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="btn btn-primary"
          >
            {isStreaming ? '...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

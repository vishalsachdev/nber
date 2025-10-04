import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import type { VideoWithPresenters } from '../lib/api';
import { chatWithAllVideos, type ChatMessage } from '../lib/openai';

interface ChatWithAllProps {
  videos: VideoWithPresenters[];
}

export default function ChatWithAll({ videos }: ChatWithAllProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: ChatMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    const assistantMessage: ChatMessage = { role: 'assistant', content: '' };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const stream = chatWithAllVideos(videos, [...messages, userMessage]);

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

  const suggestedQuestions = [
    "What are the main concerns about AI and labor markets?",
    "Which presentations discuss behavioral economics?",
    "What did Joseph Stiglitz say about AI?",
    "Compare the different perspectives on AI's economic impact",
    "What are the policy recommendations across presentations?"
  ];

  return (
    <div className="chat-with-all">
      <div className="section-header">
        <h2>Chat with All Transcripts</h2>
        <p>Ask questions across all workshop presentations</p>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="suggestions">
              <h3>💡 Try asking:</h3>
              <ul>
                {suggestedQuestions.map((question, index) => (
                  <li key={index}>
                    <button
                      className="suggestion-btn"
                      onClick={() => setInput(question)}
                    >
                      {question}
                    </button>
                  </li>
                ))}
              </ul>
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
            placeholder="Ask a question about the workshop presentations..."
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

      <details className="available-videos">
        <summary>📚 Available Transcripts ({videos.length} videos)</summary>
        <ul>
          {videos.map((video) => (
            <li key={video.id}>
              <a href={video.url} target="_blank" rel="noopener noreferrer">
                {video.title}
              </a>
              {' '}by {video.presenters.map(p => p.name).join(', ')}
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}

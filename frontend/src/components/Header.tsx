interface HeaderProps {
  videosCount: number;
  transcriptsCount: number;
  presentersCount: number;
}

export default function Header({ videosCount, transcriptsCount, presentersCount }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h1>NBER Economics of Transformative AI Workshop</h1>
          <p className="header-subtitle">Fall 2025 • Explore presentations, chat with transcripts, and discover insights</p>
        </div>

        <div className="header-description">
          <p>
            This workshop brings together leading economists to explore the economic implications of transformative artificial intelligence.
            Organized by Ajay K. Agrawal, Anton Korinek, and Erik Brynjolfsson, the workshop examines how AI will reshape labor markets,
            firm dynamics, innovation, competition, and economic policy.
          </p>
          <p>
            <strong>Why this app?</strong> Academic workshops are goldmines of cutting-edge research, but incredibly time-consuming to digest.
            Instead of watching hours of video or manually searching through transcripts, you can now <strong>have a conversation</strong> with these presentations.
            Ask questions, compare perspectives across talks, and discover insights in seconds—powered by AI that understands the full context of the content.
          </p>
          <div className="header-links">
            <a href="https://www.youtube.com/@NBERvideos/videos" target="_blank" rel="noopener noreferrer">
              📺 Watch all presentations on YouTube
            </a>
            <span>•</span>
            <a href="https://www.nber.org/conferences/economics-transformative-ai-workshop-fall-2025" target="_blank" rel="noopener noreferrer">
              📄 Workshop Details (NBER)
            </a>
            <span>•</span>
            <a
              href="https://github.com/vishalsachdev/nber/issues/new/choose"
              target="_blank"
              rel="noopener noreferrer"
            >
              🐞 Open a GitHub issue
            </a>
            <span>•</span>
            <a
              href="https://www.linkedin.com/feed/update/urn:li:ugcPost:7380332000815202304/"
              target="_blank"
              rel="noopener noreferrer"
            >
              ✍️ Build write-up
            </a>
          </div>
        </div>

        <div className="header-stats">
          <div className="stat">
            <div className="stat-value">{videosCount}</div>
            <div className="stat-label">Videos</div>
          </div>
          <div className="stat">
            <div className="stat-value">{transcriptsCount}</div>
            <div className="stat-label">Transcripts</div>
          </div>
          <div className="stat">
            <div className="stat-value">{presentersCount}</div>
            <div className="stat-label">Presenters</div>
          </div>
        </div>
      </div>
    </header>
  );
}

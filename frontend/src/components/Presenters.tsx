import { useState, useEffect } from 'react';
import { getAllPresenters } from '../lib/api';
import type { Presenter } from '../lib/api';

export default function Presenters() {
  const [presenters, setPresenters] = useState<(Presenter & { videoCount: number })[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPresenters();
  }, []);

  async function loadPresenters() {
    try {
      setLoading(true);
      const data = await getAllPresenters();
      setPresenters(data);
    } catch (error) {
      console.error('Failed to load presenters:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredPresenters = searchQuery
    ? presenters.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.affiliation.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : presenters;

  if (loading) {
    return (
      <div className="presenters">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading presenters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="presenters">
      <div className="section-header">
        <h2>Presenters Directory</h2>
        <p>Economics of Transformative AI Workshop - Fall 2025</p>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by name or affiliation"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="results-count">
        {filteredPresenters.length} Presenter{filteredPresenters.length !== 1 ? 's' : ''}
      </div>

      <div className="presenters-grid">
        {filteredPresenters.map((presenter, idx) => (
          <div key={presenter.id || idx} className="presenter-card">
            <div className="presenter-header">
              <h3>{presenter.name}</h3>
              {presenter.scholar_url && (
                <a
                  href={presenter.scholar_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="scholar-link"
                  title="Google Scholar Profile"
                >
                  📚
                </a>
              )}
            </div>
            <p className="affiliation">{presenter.affiliation}</p>
            <div className="presenter-meta">
              <span className="video-count">
                {presenter.videoCount} presentation{presenter.videoCount !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
        ))}
      </div>

      {filteredPresenters.length === 0 && (
        <div className="no-results">
          <p>No presenters found matching your search.</p>
          <button onClick={() => setSearchQuery('')}>Clear search</button>
        </div>
      )}
    </div>
  );
}

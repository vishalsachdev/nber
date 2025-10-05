import { useState, useEffect, useMemo } from 'react';
import { getAllPresenters } from '../lib/api';
import type { Presenter } from '../lib/api';

interface PresentersProps {
  onSearchByName: (name: string) => void;
  onChatWithPresenter: (name: string) => void;
}

export default function Presenters({ onSearchByName, onChatWithPresenter }: PresentersProps) {
  const [presenters, setPresenters] = useState<(Presenter & { videoCount: number })[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'name' | 'affiliation' | 'count'>('name');
  const [selectedAffiliations, setSelectedAffiliations] = useState<Set<string>>(new Set());

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

  const allAffiliations = useMemo(() => {
    const set = new Set<string>();
    presenters.forEach(p => set.add(p.affiliation));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [presenters]);

  const filteredPresenters = useMemo(() => {
    const q = searchQuery.toLowerCase();
    let list = presenters.filter(p =>
      !q || p.name.toLowerCase().includes(q) || p.affiliation.toLowerCase().includes(q)
    );
    if (selectedAffiliations.size > 0) {
      list = list.filter(p => selectedAffiliations.has(p.affiliation));
    }
    switch (sortBy) {
      case 'affiliation':
        return list.sort((a, b) => a.affiliation.localeCompare(b.affiliation));
      case 'count':
        return list.sort((a, b) => b.videoCount - a.videoCount || a.name.localeCompare(b.name));
      default:
        return list.sort((a, b) => a.name.localeCompare(b.name));
    }
  }, [presenters, searchQuery, selectedAffiliations, sortBy]);

  function toggleAffiliation(aff: string) {
    const next = new Set(selectedAffiliations);
    if (next.has(aff)) next.delete(aff); else next.add(aff);
    setSelectedAffiliations(next);
  }

  function Highlight({ text, query }: { text: string; query: string }) {
    if (!query) return <>{text}</>;
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig'));
    return (
      <>
        {parts.map((part, i) => part.toLowerCase() === query.toLowerCase() ? <mark key={i}>{part}</mark> : <span key={i}>{part}</span>)}
      </>
    );
  }

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

      <div className="controls-row">
        <div className="search-bar" style={{ flex: 1 }}>
          <input
            type="text"
            placeholder="Search by name or affiliation"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="sort-control">
          <label htmlFor="presenters-sort" style={{ marginRight: 8 }}>Sort by</label>
          <select
            id="presenters-sort"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <option value="name">Name</option>
            <option value="affiliation">Affiliation</option>
            <option value="count">Presentations</option>
          </select>
        </div>
      </div>

      {allAffiliations.length > 1 && (
        <div className="filter-chips">
          {allAffiliations.map((aff) => (
            <button
              key={aff}
              className={`chip ${selectedAffiliations.has(aff) ? 'active' : ''}`}
              onClick={() => toggleAffiliation(aff)}
              aria-pressed={selectedAffiliations.has(aff)}
            >
              {aff}
            </button>
          ))}
          {selectedAffiliations.size > 0 && (
            <button className="chip" onClick={() => setSelectedAffiliations(new Set())}>Clear filters</button>
          )}
        </div>
      )}

      <div className="results-count">
        {filteredPresenters.length} Presenter{filteredPresenters.length !== 1 ? 's' : ''}
      </div>

      <div className="presenters-grid">
        {filteredPresenters.map((presenter, idx) => (
          <div key={presenter.id || idx} className="presenter-card">
            <div className="presenter-header">
              <h3><Highlight text={presenter.name} query={searchQuery} /></h3>
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
            <p className="affiliation"><Highlight text={presenter.affiliation} query={searchQuery} /></p>
            <div className="presenter-meta">
              <span className="video-count">
                {presenter.videoCount} presentation{presenter.videoCount !== 1 ? 's' : ''}
              </span>
              <div className="presenter-actions" style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                <button className="btn btn-secondary" onClick={() => onSearchByName(presenter.name)}>View talks</button>
                <button className="btn btn-primary" onClick={() => onChatWithPresenter(presenter.name)}>Chat across talks</button>
              </div>
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

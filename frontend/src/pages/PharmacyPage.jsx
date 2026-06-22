import React, { useState, useRef, useCallback, useEffect } from 'react';
import LoadingSpinner from '../components/common/LoadingSpinner';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

/* ── SVG Icons ────────────────────────────────────────────── */
const IconCamera = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
    <circle cx="12" cy="13" r="4"/>
  </svg>
);
const IconSearch = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
  </svg>
);
const IconScan = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/>
    <path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
    <line x1="7" y1="12" x2="17" y2="12"/>
  </svg>
);
const IconPill = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/>
    <path d="m8.5 8.5 7 7"/>
  </svg>
);
const IconUpload = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);
const IconCheck = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);
const IconInfo = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
  </svg>
);
const IconWarning = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
);
const IconRefresh = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
  </svg>
);
const IconChevron = ({ down }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
    style={{ transform: down ? 'rotate(180deg)' : 'none', transition: 'transform 0.3s' }}>
    <polyline points="6 9 12 15 18 9"/>
  </svg>
);

/* ── Confidence Bar Component ─────────────────────────────── */
const ConfidenceBar = ({ value }) => {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 85 ? '#10B981' : pct >= 65 ? '#F59E0B' : '#EF4444';
  return (
    <div className="ph-conf-bar-wrap">
      <div className="ph-conf-bar-track">
        <div className="ph-conf-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="ph-conf-pct" style={{ color }}>{pct}%</span>
    </div>
  );
};

/* ── Main Component ───────────────────────────────────────── */
const PharmacyPage = () => {
  const [activeTab, setActiveTab] = useState('scan');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [scanImage, setScanImage] = useState(null);
  const [scanPreview, setScanPreview] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedCard, setExpandedCard] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileRef = useRef(null);

  // Pillbox State
  const [pillbox, setPillbox] = useState(() => {
    try {
      const saved = localStorage.getItem('firstaid_pillbox');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [pillboxInteractions, setPillboxInteractions] = useState([]);
  const [pillboxSearchQuery, setPillboxSearchQuery] = useState('');
  const [pillboxSuggestions, setPillboxSuggestions] = useState([]);
  const [isCheckingInteractions, setIsCheckingInteractions] = useState(false);

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  });

  const checkInteractions = useCallback(async (currentPillbox) => {
    if (currentPillbox.length < 2) {
      setPillboxInteractions([]);
      return;
    }
    setIsCheckingInteractions(true);
    try {
      const medicineIds = currentPillbox.map(m => m.id);
      const res = await fetch(`${API_URL}/api/pharmacy/check-interactions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ medicine_ids: medicineIds })
      });
      const data = await res.json();
      if (res.ok) {
        setPillboxInteractions(data.interactions || []);
      }
    } catch (err) {
      console.error('Failed to check interactions:', err);
    } finally {
      setIsCheckingInteractions(false);
    }
  }, []);

  // Trigger initial check on load
  useEffect(() => {
    checkInteractions(pillbox);
  }, [checkInteractions]);

  const handleAddToPillbox = (medicine) => {
    if (!medicine) return;
    if (pillbox.some(m => m.id === medicine.id)) {
      setError(`"${medicine.name}" is already in your Virtual Pillbox.`);
      return;
    }
    const updated = [...pillbox, medicine];
    setPillbox(updated);
    localStorage.setItem('firstaid_pillbox', JSON.stringify(updated));
    setError('');
    checkInteractions(updated);
  };

  const handleRemoveFromPillbox = (medId) => {
    const updated = pillbox.filter(m => m.id !== medId);
    setPillbox(updated);
    localStorage.setItem('firstaid_pillbox', JSON.stringify(updated));
    checkInteractions(updated);
  };

  const handlePillboxSearchChange = async (val) => {
    setPillboxSearchQuery(val);
    if (!val.trim() || val.trim().length < 2) {
      setPillboxSuggestions([]);
      return;
    }
    try {
      const res = await fetch(
        `${API_URL}/api/pharmacy/search?q=${encodeURIComponent(val)}`,
        { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }
      );
      const data = await res.json();
      if (res.ok) {
        setPillboxSuggestions(data.results || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  /* ── File handling ───────────────────────────────────────── */
  const processFile = (file) => {
    if (!file) return;
    setScanImage(file);
    setScanResult(null);
    setExtractedText('');
    setError('');
    const reader = new FileReader();
    reader.onloadend = () => setScanPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleImageSelect = (e) => processFile(e.target.files[0]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) processFile(file);
  }, []);

  const handleDragOver = useCallback((e) => { e.preventDefault(); setIsDragging(true); }, []);
  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  /* ── Scan ────────────────────────────────────────────────── */
  const handleScan = async () => {
    if (!scanImage) { setError('Please select an image first'); return; }
    setIsLoading(true); setError('');
    try {
      const formData = new FormData();
      formData.append('image', scanImage);
      const res = await fetch(`${API_URL}/api/pharmacy/scan`, {
        method: 'POST', headers: getAuthHeaders(), body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Scan failed');
      setScanResult(data.medicine);
      setExtractedText(data.extracted_text || '');
    } catch (err) {
      setError(err.message || 'Failed to scan medicine.');
    } finally { setIsLoading(false); }
  };

  const handleReset = () => {
    setScanImage(null); setScanPreview(null); setScanResult(null);
    setExtractedText(''); setError('');
  };

  /* ── Search ──────────────────────────────────────────────── */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      setError('Enter at least 2 characters'); return;
    }
    setIsLoading(true); setError('');
    try {
      const res = await fetch(
        `${API_URL}/api/pharmacy/search?q=${encodeURIComponent(searchQuery)}`,
        { headers: getAuthHeaders() }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Search failed');
      setSearchResults(data.results || []);
      if ((data.results || []).length === 0) setError('No medicines found.');
    } catch (err) {
      setError(err.message || 'Search failed.');
    } finally { setIsLoading(false); }
  };

  return (
    <div className="ph-page" id="pharmacy-page">

      {/* ── PAGE HEADER ───────────────────────────────────── */}
      <div className="ph-header">
        <div className="ph-header-bg" />
        <div className="ph-header-grid" />
        <div className="ph-header-orb ph-orb-1" />
        <div className="ph-header-orb ph-orb-2" />
        <div className="ph-header-content">
          <div className="ph-header-badge">
            <span className="badge-dot-live" />
            <span>Pharmacy Module</span>
          </div>
          <h1 className="ph-header-title">
            Medicine <span className="text-highlight">Scanner</span>
          </h1>
          <p className="ph-header-subtitle">
            Scan any medicine label with AI-powered OCR or search our global database
            of 500+ medicines for dosage, interactions, and warnings.
          </p>
          {/* Quick stats */}
          <div className="ph-header-stats">
            {[
              { val: '500+', label: 'Medicines' },
              { val: '98%',  label: 'Accuracy' },
              { val: '<2s',  label: 'Response' },
            ].map((s, i) => (
              <div key={i} className="ph-header-stat">
                <span className="ph-stat-val">{s.val}</span>
                <span className="ph-stat-lbl">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── TABS ──────────────────────────────────────────── */}
      <div className="ph-tabs-bar">
        <div className="ph-tabs-inner">
          <button
            className={`ph-tab ${activeTab === 'scan' ? 'active' : ''}`}
            onClick={() => { setActiveTab('scan'); setError(''); }}
            id="tab-scan"
          >
            <IconCamera /> Scan Image
          </button>
          <button
            className={`ph-tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => { setActiveTab('search'); setError(''); }}
            id="tab-search"
          >
            <IconSearch /> Search Database
          </button>
          <button
            className={`ph-tab ${activeTab === 'pillbox' ? 'active' : ''}`}
            onClick={() => { setActiveTab('pillbox'); setError(''); }}
            id="tab-pillbox"
          >
            <IconPill /> Virtual Pillbox
            {pillbox.length > 0 && (
              <span className="ph-tab-badge">{pillbox.length}</span>
            )}
          </button>
        </div>
      </div>

      {/* ── MAIN CONTENT ─────────────────────────────────── */}
      <div className="ph-content">

        {error && (
          <div className="ph-error">
            <IconWarning /> {error}
          </div>
        )}

        {/* ── SCAN TAB ─────────────────────────────────── */}
        {activeTab === 'scan' && (
          <div className="ph-scan-layout animate-fadeInUp">

            {/* Left: Upload Panel */}
            <div className="ph-panel ph-upload-panel">
              <div className="ph-panel-header">
                <div className="ph-panel-icon" style={{ background: 'rgba(6,182,212,0.12)', color: '#06B6D4' }}>
                  <IconCamera />
                </div>
                <div>
                  <h3 className="ph-panel-title">Upload Medicine Image</h3>
                  <p className="ph-panel-sub">Strip, packaging, or label — any format</p>
                </div>
              </div>

              {/* Drop Zone */}
              <div
                className={`ph-dropzone ${isDragging ? 'dragging' : ''} ${scanPreview ? 'has-preview' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => !scanPreview && fileRef.current?.click()}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  id="medicine-image-input"
                  style={{ display: 'none' }}
                />
                {scanPreview ? (
                  <div className="ph-preview-wrap">
                    <img src={scanPreview} alt="Medicine preview" className="ph-preview-img" />
                    <button
                      className="ph-preview-change"
                      onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}
                    >
                      Change Image
                    </button>
                  </div>
                ) : (
                  <div className="ph-dropzone-empty">
                    <div className="ph-dropzone-icon">
                      <IconUpload />
                    </div>
                    <p className="ph-dropzone-title">Drop image here or click to upload</p>
                    <p className="ph-dropzone-hint">PNG, JPG, WEBP up to 10MB</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="ph-upload-actions">
                <button
                  onClick={handleScan}
                  disabled={!scanImage || isLoading}
                  className="btn btn-pharmacy btn-full btn-lg"
                  id="scan-btn"
                >
                  {isLoading ? (
                    <><span className="ph-btn-spinner" /> Scanning...</>
                  ) : (
                    <><IconScan /> Scan &amp; Identify Medicine</>
                  )}
                </button>
                {scanPreview && !isLoading && (
                  <button onClick={handleReset} className="btn btn-outline btn-full" id="reset-scan-btn">
                    <IconRefresh /> Clear &amp; Start Over
                  </button>
                )}
              </div>

              {/* Tips */}
              <div className="ph-tips">
                <p className="ph-tips-title">For best results</p>
                {['Ensure good lighting', 'Text must be clearly visible', 'Avoid blurry shots'].map((t, i) => (
                  <div key={i} className="ph-tip-item">
                    <span className="ph-tip-dot" style={{ background: '#06B6D4' }} />
                    {t}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Results Panel */}
            <div className="ph-panel ph-results-panel">
              {isLoading && (
                <div className="ph-loading-state">
                  <div className="ph-loading-orb" />
                  <LoadingSpinner message="Analyzing medicine image with AI..." />
                </div>
              )}

              {!isLoading && !scanResult && (
                <div className="ph-placeholder">
                  <div className="ph-placeholder-icon">
                    <IconPill />
                  </div>
                  <h3>Ready to Scan</h3>
                  <p>Upload a medicine image and click "Scan & Identify" — results appear here instantly.</p>
                  <div className="ph-placeholder-features">
                    {['Global brand recognition', 'Dosage extraction', 'Interaction warnings'].map((f, i) => (
                      <div key={i} className="ph-placeholder-feature">
                        <span className="ph-feature-check"><IconCheck /></span>
                        {f}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {scanResult && !isLoading && (
                <div className="ph-result animate-fadeInUp">
                  {/* Result Header */}
                  <div className="ph-result-header">
                    <div className="ph-result-title-row">
                      <div>
                        <h2 className="ph-result-name">{scanResult.name}</h2>
                        <p className="ph-result-generic">{scanResult.generic_name}</p>
                      </div>
                      <div className="ph-result-badge-group">
                        <span className="ph-type-badge">{scanResult.type}</span>
                      </div>
                    </div>
                    <ConfidenceBar value={scanResult.confidence || 0.85} />
                  </div>

                  {/* Grid Info */}
                  <div className="ph-result-grid">
                    {[
                      { label: 'Composition', val: scanResult.composition, icon: '⚗' },
                      { label: 'Dosage', val: scanResult.dosage, icon: '💊' },
                    ].map((item, i) => (
                      <div key={i} className="ph-info-card">
                        <span className="ph-info-icon">{item.icon}</span>
                        <div>
                          <p className="ph-info-label">{item.label}</p>
                          <p className="ph-info-val">{item.val}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Usage */}
                  <div className="ph-result-section">
                    <div className="ph-section-header">
                      <IconInfo /> Usage
                    </div>
                    <p className="ph-section-body">{scanResult.usage}</p>
                  </div>

                  {/* Side Effects */}
                  {scanResult.side_effects?.length > 0 && (
                    <div className="ph-result-section">
                      <div className="ph-section-header">
                        <IconInfo /> Side Effects
                      </div>
                      <div className="ph-pills-wrap">
                        {scanResult.side_effects.map((e, i) => (
                          <span key={i} className="ph-pill">{e}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Warnings */}
                  {scanResult.warnings?.length > 0 && (
                    <div className="ph-result-section ph-warning-section">
                      <div className="ph-section-header ph-warning-header">
                        <IconWarning /> Warnings
                      </div>
                      <ul className="ph-warning-list">
                        {scanResult.warnings.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Interactions */}
                  {scanResult.interactions?.length > 0 && (
                    <div className="ph-result-section">
                      <div className="ph-section-header">
                        <IconInfo /> Drug Interactions
                      </div>
                      <div className="ph-pills-wrap">
                        {scanResult.interactions.map((item, i) => (
                          <span key={i} className="ph-pill ph-pill-interaction">{item}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Storage */}
                  {scanResult.storage && (
                    <div className="ph-result-section">
                      <div className="ph-section-header"><IconInfo /> Storage</div>
                      <p className="ph-section-body">{scanResult.storage}</p>
                    </div>
                  )}

                  {/* OCR Text */}
                  {extractedText && (
                    <div className="ph-result-section">
                      <div className="ph-section-header"><IconInfo /> Extracted OCR Text</div>
                      <pre className="ph-ocr-text">{extractedText}</pre>
                    </div>
                  )}

                  <button
                    onClick={() => {
                      handleAddToPillbox(scanResult);
                      setActiveTab('pillbox');
                    }}
                    className="btn btn-pharmacy btn-full"
                    style={{ marginTop: '1rem' }}
                    id="add-to-pillbox-scan-btn"
                  >
                    + Add to Virtual Pillbox
                  </button>

                  <button onClick={handleReset} className="btn btn-outline btn-full" style={{ marginTop: '1rem' }}>
                    <IconRefresh /> Scan Another Medicine
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── SEARCH TAB ────────────────────────────────── */}
        {activeTab === 'search' && (
          <div className="ph-search-layout animate-fadeInUp">
            <form onSubmit={handleSearch} className="ph-search-form">
              <div className="ph-search-box">
                <span className="ph-search-icon"><IconSearch /></span>
                <input
                  type="text"
                  placeholder="Search by name — e.g. Aspirin, Paracetamol, Metformin..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="ph-search-input"
                  id="medicine-search-input"
                />
                <button type="submit" className="btn btn-pharmacy" disabled={isLoading} id="search-btn">
                  {isLoading ? 'Searching...' : 'Search'}
                </button>
              </div>
              <div className="ph-search-tags">
                {['Ibuprofen', 'Cetirizine', 'Omeprazole', 'Metformin', 'Azithromycin'].map(s => (
                  <button
                    key={s} type="button" className="ph-search-tag"
                    onClick={() => { setSearchQuery(s); }}
                  >{s}</button>
                ))}
              </div>
            </form>

            {isLoading && (
              <div className="ph-loading-center">
                <LoadingSpinner message="Searching global medicines database..." />
              </div>
            )}

            {!isLoading && searchResults.length > 0 && (
              <div className="ph-search-results">
                <p className="ph-results-count">
                  {searchResults.length} medicine{searchResults.length !== 1 ? 's' : ''} found
                </p>
                <div className="ph-results-grid">
                  {searchResults.map((med) => (
                    <div
                      key={med.id}
                      className={`ph-med-card ${expandedCard === med.id ? 'expanded' : ''}`}
                      id={`medicine-${med.id}`}
                    >
                      <div
                        className="ph-med-card-head"
                        onClick={() => setExpandedCard(expandedCard === med.id ? null : med.id)}
                      >
                        <div className="ph-med-card-icon">
                          <IconPill />
                        </div>
                        <div className="ph-med-card-info">
                          <h3 className="ph-med-name">{med.name}</h3>
                          <p className="ph-med-generic">{med.generic_name}</p>
                        </div>
                        <div className="ph-med-card-right">
                          <span className="ph-type-badge">{med.type}</span>
                          <span className="ph-expand-icon">
                            <IconChevron down={expandedCard === med.id} />
                          </span>
                        </div>
                      </div>

                      <p className="ph-med-usage">{med.usage}</p>

                      {expandedCard === med.id && (
                        <div className="ph-med-expanded animate-fadeInUp">
                          <div className="ph-med-detail-grid">
                            <div className="ph-med-detail">
                              <span className="ph-detail-label">Composition</span>
                              <span className="ph-detail-val">{med.composition}</span>
                            </div>
                            <div className="ph-med-detail">
                              <span className="ph-detail-label">Dosage</span>
                              <span className="ph-detail-val">{med.dosage}</span>
                            </div>
                          </div>

                          {med.side_effects?.length > 0 && (
                            <div className="ph-med-section">
                              <p className="ph-detail-label">Side Effects</p>
                              <div className="ph-pills-wrap">
                                {med.side_effects.map((e, i) => (
                                  <span key={i} className="ph-pill">{e}</span>
                                ))}
                              </div>
                            </div>
                          )}

                          {med.warnings?.length > 0 && (
                            <div className="ph-med-section ph-warning-section">
                              <p className="ph-detail-label" style={{ color: '#FCA5A5' }}>
                                <IconWarning /> Warnings
                              </p>
                              <ul className="ph-warning-list">
                                {med.warnings.map((w, i) => <li key={i}>{w}</li>)}
                              </ul>
                            </div>
                          )}

                          <div className="ph-med-actions" style={{ marginTop: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleAddToPillbox(med);
                                setActiveTab('pillbox');
                              }}
                              className="btn btn-pharmacy btn-sm"
                              id={`add-to-pillbox-search-${med.id}`}
                            >
                              + Add to Virtual Pillbox
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!isLoading && searchResults.length === 0 && !error && (
              <div className="ph-search-empty">
                <div className="ph-placeholder-icon"><IconSearch /></div>
                <h3>Search the Global Database</h3>
                <p>Enter a medicine name above — brand names, generic names, or drug categories all work.</p>
              </div>
            )}
          </div>
        )}

        {/* ── PILLBOX TAB ────────────────────────────────── */}
        {activeTab === 'pillbox' && (
          <div className="ph-pillbox-layout animate-fadeInUp">
            
            {/* Left side: Current list & warnings */}
            <div className="ph-pillbox-main">
              
              {/* Checking indicator */}
              {isCheckingInteractions && (
                <div className="ph-checking-status">
                  <span className="ph-btn-spinner" style={{ borderColor: 'rgba(6,182,212,0.3)', borderTopColor: '#06B6D4' }} /> Checking drug-to-drug interactions...
                </div>
              )}

              {/* Dynamic Alerts Banner */}
              {!isCheckingInteractions && pillboxInteractions.length > 0 && (
                <div className="ph-alert-banner ph-alert-danger animate-fadeInUp">
                  <div className="ph-alert-icon">
                    <IconWarning />
                  </div>
                  <div className="ph-alert-content">
                    <h4 className="ph-alert-title">{pillboxInteractions.length} Potential Interaction{pillboxInteractions.length > 1 ? 's' : ''} Detected</h4>
                    <ul className="ph-alert-list">
                      {pillboxInteractions.map((intr, idx) => (
                        <li key={idx} className="ph-alert-item">
                          <strong>{intr.med1.name}</strong> + <strong>{intr.med2.name}</strong>: {intr.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {!isCheckingInteractions && pillbox.length >= 2 && pillboxInteractions.length === 0 && (
                <div className="ph-alert-banner ph-alert-success animate-fadeInUp">
                  <div className="ph-alert-icon" style={{ background: 'rgba(16,185,129,0.15)', color: '#10B981' }}>
                    <IconCheck />
                  </div>
                  <div className="ph-alert-content">
                    <h4 className="ph-alert-title" style={{ color: '#A7F3D0' }}>No Interactions Detected</h4>
                    <p className="ph-alert-desc">No drug conflicts found among the {pillbox.length} medicines in your pillbox.</p>
                  </div>
                </div>
              )}

              {/* Pillbox Empty State or Grid List */}
              {pillbox.length === 0 ? (
                <div className="ph-panel ph-empty-pillbox">
                  <div className="ph-placeholder-icon">
                    <IconPill />
                  </div>
                  <h3>Your Virtual Pillbox is Empty</h3>
                  <p>Add medicines you are currently taking to check for dangerous interactions dynamically.</p>
                </div>
              ) : (
                <div className="ph-pillbox-grid">
                  {pillbox.map((med) => (
                    <div key={med.id} className="ph-pillbox-card" id={`pillbox-med-${med.id}`}>
                      <div className="ph-pillbox-card-header">
                        <div className="ph-pillbox-card-icon">
                          <IconPill />
                        </div>
                        <div className="ph-pillbox-card-title-wrap">
                          <h3 className="ph-pillbox-med-name">{med.name}</h3>
                          <p className="ph-pillbox-med-generic">{med.generic_name}</p>
                        </div>
                        <button
                          onClick={() => handleRemoveFromPillbox(med.id)}
                          className="ph-pillbox-remove-btn"
                          title="Remove from pillbox"
                        >
                          &times;
                        </button>
                      </div>
                      <div className="ph-pillbox-card-body">
                        <span className="ph-type-badge" style={{ marginBottom: '0.5rem', display: 'inline-block' }}>{med.type}</span>
                        <p className="ph-pillbox-detail"><strong>Composition:</strong> {med.composition}</p>
                        <p className="ph-pillbox-detail"><strong>Dosage:</strong> {med.dosage}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right side: Quick Add & Info */}
            <div className="ph-pillbox-sidebar">
              <div className="ph-panel">
                <div className="ph-panel-header">
                  <div className="ph-panel-icon" style={{ background: 'rgba(6,182,212,0.12)', color: '#06B6D4' }}>
                    <IconSearch />
                  </div>
                  <div>
                    <h3 className="ph-panel-title">Quick Add Medicine</h3>
                    <p className="ph-panel-sub">Type to search and add from database</p>
                  </div>
                </div>

                <div className="ph-quickadd-box">
                  <input
                    type="text"
                    placeholder="Search medicine name..."
                    value={pillboxSearchQuery}
                    onChange={(e) => handlePillboxSearchChange(e.target.value)}
                    className="ph-quickadd-input"
                  />
                  {pillboxSuggestions.length > 0 && (
                    <div className="ph-suggestions-dropdown">
                      {pillboxSuggestions.map((med) => (
                        <div
                          key={med.id}
                          className="ph-suggestion-item"
                          onClick={() => {
                            handleAddToPillbox(med);
                            setPillboxSearchQuery('');
                            setPillboxSuggestions([]);
                          }}
                        >
                          <span className="ph-suggestion-name">{med.name}</span>
                          <span className="ph-suggestion-type">{med.type}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="ph-tips" style={{ marginTop: '0.5rem' }}>
                  <p className="ph-tips-title">Pillbox Guidelines</p>
                  {[
                    'Keep this list updated with active medications',
                    'Scan new prescriptions to automatically check safety',
                    'Consult a physician for clinical decisions'
                  ].map((t, i) => (
                    <div key={i} className="ph-tip-item">
                      <span className="ph-tip-dot" style={{ background: '#06B6D4' }} />
                      {t}
                    </div>
                  ))}
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default PharmacyPage;

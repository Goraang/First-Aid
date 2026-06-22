import React, { useState, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

/* ── SVG Icons ────────────────────────────────────────────── */
const IconMicroscope = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 18H4a2 2 0 0 1-2-2v-1h20v1a2 2 0 0 1-2 2h-2"/>
    <path d="M6 18v3h12v-3"/>
    <path d="M15.5 8.5a2.5 2.5 0 1 0-5 0"/>
    <path d="M13 6V2"/><path d="M10 6V4"/><path d="M16 6V4"/>
    <path d="M9 13a3 3 0 0 0 6 0"/>
  </svg>
);
const IconUpload = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);
const IconCheck = () => (
  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
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
const IconShield = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>
);
const IconInfo = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
  </svg>
);
const IconPill = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/>
    <path d="m8.5 8.5 7 7"/>
  </svg>
);

/* ── Body part map (SVG body icons) ───────────────────────── */
const BODY_PARTS = [
  { id: 'face',  label: 'Face',  svgPath: 'M12 2a5 5 0 1 0 0 10A5 5 0 0 0 12 2zm0 12c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z' },
  { id: 'scalp', label: 'Scalp', svgPath: 'M12 1a9 9 0 0 1 9 9c0 3-1.5 5.5-4 7v3H7v-3c-2.5-1.5-4-4-4-7a9 9 0 0 1 9-9z' },
  { id: 'arms',  label: 'Arms',  svgPath: 'M6 3v12l-3 6h3l3-6V3zm12 0v12l3 6h-3l-3-6V3z' },
  { id: 'legs',  label: 'Legs',  svgPath: 'M8 2v12l-2 8h3l2-8 2 8h3l-2-8V2zm6 0v12l2 8h3l-2-8-2-8z' },
  { id: 'hands', label: 'Hands', svgPath: 'M7 8h2V4h2v4h2V4h2v6l-2 4v6H9v-6l-2-4z' },
  { id: 'feet',  label: 'Feet',  svgPath: 'M7 13h4v8H7zm6 0h4v6h-4zM5 11h6v3H5zm8 0h6v3h-6z' },
  { id: 'chest', label: 'Chest', svgPath: 'M5 5h14v9a7 7 0 0 1-14 0zm0 0V3h14v2' },
  { id: 'back',  label: 'Back',  svgPath: 'M5 5h14v14H5zM9 9h6m-6 4h6' },
  { id: 'other', label: 'Other', svgPath: 'M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 5v6m0 3v1' },
];

const SYMPTOMS = [
  'Itching', 'Redness', 'Swelling', 'Pain', 'Burning',
  'Dry / Flaky', 'Blistering', 'Oozing', 'Discoloration',
  'Raised bumps', 'Scaling', 'Cracking',
];

/* ── Circular confidence ring ─────────────────────────────── */
const ConfidenceRing = ({ value }) => {
  const pct = Math.round((value || 0) * 100);
  const r = 36, c = 2 * Math.PI * r;
  const dash = (pct / 100) * c;
  const color = pct >= 85 ? '#10B981' : pct >= 65 ? '#F59E0B' : '#EF4444';
  return (
    <div className="dr-conf-ring-wrap">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="8" />
        <circle
          cx="50" cy="50" r={r} fill="none"
          stroke={color} strokeWidth="8"
          strokeDasharray={`${dash} ${c - dash}`}
          strokeDashoffset={c * 0.25}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
      </svg>
      <div className="dr-conf-ring-text">
        <span style={{ color, fontSize: '1.3rem', fontWeight: 900 }}>{pct}%</span>
        <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>match</span>
      </div>
    </div>
  );
};

/* ── Severity badge ───────────────────────────────────────── */
const SeverityBadge = ({ severity }) => {
  const s = (severity || 'mild').toLowerCase();
  const map = {
    severe:   { bg: 'rgba(239,68,68,0.15)',  border: 'rgba(239,68,68,0.3)',  color: '#FCA5A5',  label: 'Severe' },
    moderate: { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', color: '#FCD34D',  label: 'Moderate' },
    mild:     { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)', color: '#6EE7B7',  label: 'Mild' },
  };
  const cfg = map[s] || map.mild;
  return (
    <span className="dr-severity-badge" style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color }}>
      {cfg.label} Severity
    </span>
  );
};

/* ── Main Component ───────────────────────────────────────── */
const DermatologyPage = () => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [bodyPart, setBodyPart] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileRef = useRef(null);

  const getAuthHeaders = () => ({
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  });

  const processFile = (file) => {
    if (!file) return;
    setImage(file); setResult(null); setError('');
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) processFile(f);
  }, []);
  const handleDragOver = useCallback((e) => { e.preventDefault(); setIsDragging(true); }, []);
  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  const toggleSymptom = (s) => setSelectedSymptoms(p =>
    p.includes(s) ? p.filter(x => x !== s) : [...p, s]
  );

  const handleAnalyze = async () => {
    if (!image) { setError('Please upload a skin image first'); return; }
    setIsLoading(true); setError('');
    try {
      const fd = new FormData();
      fd.append('image', image);
      fd.append('body_part', bodyPart || 'unknown');
      fd.append('symptom_text', selectedSymptoms.join(', '));
      fd.append('symptoms', JSON.stringify(selectedSymptoms));

      const res = await fetch(`${API_URL}/api/dermatology/analyze`, {
        method: 'POST', headers: getAuthHeaders(), body: fd
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Analysis failed');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally { setIsLoading(false); }
  };

  const handleReset = () => {
    setImage(null); setPreview(null); setBodyPart('');
    setSelectedSymptoms([]); setResult(null); setError('');
  };

  const disease = result?.disease?.disease || result?.disease || null;
  const confidence = result?.disease?.confidence || result?.confidence || 0;
  const alternatives = result?.disease?.top_alternatives || [];

  return (
    <div className="dr-page" id="dermatology-page">

      {/* ── HEADER ────────────────────────────────────────── */}
      <div className="dr-header">
        <div className="dr-header-bg" />
        <div className="dr-header-grid" />
        <div className="dr-header-orb dr-orb-1" />
        <div className="dr-header-orb dr-orb-2" />
        <div className="dr-header-content">
          <div className="dr-header-badge">
            <span className="badge-dot-live" style={{ background: '#EC4899' }} />
            <span>Dermatology Module</span>
          </div>
          <h1 className="dr-header-title">
            Skin <span className="text-gradient-pink">Analysis</span>
          </h1>
          <p className="dr-header-subtitle">
            Upload a photo of any skin condition for instant AI-powered analysis.
            Covers 20+ dermatological conditions with treatment recommendations.
          </p>
          <div className="dr-header-stats">
            {[
              { val: '20+',  label: 'Conditions' },
              { val: '94%',  label: 'Accuracy' },
              { val: 'Free', label: 'Always' },
            ].map((s, i) => (
              <div key={i} className="dr-header-stat">
                <span className="dr-stat-val">{s.val}</span>
                <span className="dr-stat-lbl">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── MAIN ──────────────────────────────────────────── */}
      <div className="dr-content">
        {!result ? (
          /* ── UPLOAD & CONFIGURE ─────────────────────────── */
          <div className="dr-configure-layout animate-fadeInUp">

            {/* Left: Upload */}
            <div className="dr-panel">
              <div className="dr-panel-header">
                <div className="dr-panel-icon">
                  <IconMicroscope />
                </div>
                <div>
                  <h3 className="dr-panel-title">Upload Skin Image</h3>
                  <p className="dr-panel-sub">Clear, well-lit photo of the affected area</p>
                </div>
              </div>

              <div
                className={`dr-dropzone ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => !preview && fileRef.current?.click()}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => processFile(e.target.files[0])}
                  id="skin-image-input"
                  style={{ display: 'none' }}
                />
                {preview ? (
                  <div className="dr-preview-wrap">
                    <img src={preview} alt="Skin condition" className="dr-preview-img" />
                    <div className="dr-preview-overlay">
                      <button className="dr-preview-change" onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}>
                        Change Image
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="dr-dropzone-empty">
                    <div className="dr-dropzone-icon"><IconUpload /></div>
                    <p className="dr-dropzone-title">Drop image here or click to upload</p>
                    <p className="dr-dropzone-hint">PNG, JPG, WEBP up to 10MB</p>
                  </div>
                )}
              </div>

              {/* Tips */}
              <div className="dr-tips">
                {['Good natural lighting', 'Keep camera steady', 'Capture the full affected area'].map((t, i) => (
                  <div key={i} className="dr-tip-item">
                    <span className="dr-tip-dot" />{t}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Body Part & Symptoms */}
            <div className="dr-panel">
              {/* Body Part */}
              <div className="dr-option-block">
                <h3 className="dr-option-title">Affected Area</h3>
                <p className="dr-option-sub">Where is the skin condition located?</p>
                <div className="dr-body-grid">
                  {BODY_PARTS.map(p => (
                    <button
                      key={p.id}
                      className={`dr-body-btn ${bodyPart === p.id ? 'active' : ''}`}
                      onClick={() => setBodyPart(p.id)}
                      id={`body-part-${p.id}`}
                    >
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d={p.svgPath} />
                      </svg>
                      <span>{p.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Symptoms */}
              <div className="dr-option-block">
                <h3 className="dr-option-title">Symptoms</h3>
                <p className="dr-option-sub">Select all that apply — improves AI accuracy</p>
                <div className="dr-symptom-wrap">
                  {SYMPTOMS.map(s => (
                    <button
                      key={s}
                      className={`dr-symptom-btn ${selectedSymptoms.includes(s) ? 'active' : ''}`}
                      onClick={() => toggleSymptom(s)}
                      id={`symptom-${s.toLowerCase().replace(/[^a-z]/g, '-')}`}
                    >
                      {selectedSymptoms.includes(s) && <span className="dr-check"><IconCheck /></span>}
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="dr-error">
                  <IconWarning /> {error}
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!image || isLoading}
                className="btn btn-derm btn-full btn-lg"
                id="analyze-btn"
                style={{ marginTop: '1rem' }}
              >
                {isLoading ? (
                  <><span className="ph-btn-spinner" /> Analyzing with AI...</>
                ) : (
                  <><IconMicroscope /> Analyze Skin Condition</>
                )}
              </button>

              {isLoading && (
                <div style={{ marginTop: '1.5rem' }}>
                  <LoadingSpinner message="Analyzing your skin condition with AI..." />
                </div>
              )}
            </div>
          </div>
        ) : (
          /* ── RESULTS ─────────────────────────────────────── */
          <div className="dr-results-layout animate-fadeInUp">

            {/* Results Header Card */}
            <div className="dr-result-hero">
              <div className="dr-result-hero-bg" />
              <div className="dr-result-hero-inner">
                <div className="dr-result-main-info">
                  <div className="dr-result-name-block">
                    <span className="dr-result-detected">AI Detected Condition</span>
                    <h2 className="dr-result-name">{disease?.name || 'Unknown Condition'}</h2>
                    {disease?.scientific_name && (
                      <p className="dr-result-sci">{disease.scientific_name}</p>
                    )}
                    <div className="dr-result-badges-row">
                      <SeverityBadge severity={disease?.severity} />
                      {disease?.india_prevalence && (
                        <span className="dr-prevalence-badge">
                          {disease.india_prevalence.replace('_', ' ')} prevalence
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Confidence ring */}
                  <ConfidenceRing value={confidence} />
                </div>

                {/* Preview thumbnail */}
                {preview && (
                  <div className="dr-result-thumb-wrap">
                    <img src={preview} alt="Analyzed skin" className="dr-result-thumb" />
                    <div className="dr-result-thumb-label">Analyzed Image</div>
                  </div>
                )}
              </div>
            </div>

            {/* Main results grid */}
            <div className="dr-results-grid">

              {/* Description */}
              <div className="dr-result-card dr-card-wide">
                <div className="dr-card-header">
                  <span className="dr-card-icon" style={{ background: 'rgba(139,92,246,0.15)', color: '#A78BFA' }}>
                    <IconInfo />
                  </span>
                  <h4>About this Condition</h4>
                </div>
                <p className="dr-card-body">{disease?.description}</p>
              </div>

              {/* Causes */}
              {disease?.causes?.length > 0 && (
                <div className="dr-result-card">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(245,158,11,0.15)', color: '#FCD34D' }}>
                      <IconInfo />
                    </span>
                    <h4>Causes</h4>
                  </div>
                  <div className="dr-tag-wrap">
                    {disease.causes.map((c, i) => (
                      <span key={i} className="dr-tag dr-tag-amber">{c}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Symptoms */}
              {disease?.symptoms?.length > 0 && (
                <div className="dr-result-card">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(6,182,212,0.15)', color: '#22D3EE' }}>
                      <IconInfo />
                    </span>
                    <h4>Common Symptoms</h4>
                  </div>
                  <ul className="dr-list">
                    {disease.symptoms.map((s, i) => (
                      <li key={i}>
                        <span className="dr-list-dot" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Treatments */}
              {disease?.treatments?.length > 0 && (
                <div className="dr-result-card dr-card-wide">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(16,185,129,0.15)', color: '#6EE7B7' }}>
                      <IconPill />
                    </span>
                    <h4>Recommended Treatments</h4>
                  </div>
                  <div className="dr-treatments-grid">
                    {disease.treatments.map((t, i) => (
                      <div key={i} className="dr-treatment-item">
                        <span className="dr-treatment-num">{i + 1}</span>
                        <span>{t}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Prevention */}
              {disease?.prevention?.length > 0 && (
                <div className="dr-result-card">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(16,185,129,0.15)', color: '#6EE7B7' }}>
                      <IconShield />
                    </span>
                    <h4>Prevention Tips</h4>
                  </div>
                  <ul className="dr-list">
                    {disease.prevention.map((p, i) => (
                      <li key={i}>
                        <span className="dr-list-dot" style={{ background: '#10B981' }} />
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Affected Areas */}
              {disease?.affected_areas?.length > 0 && (
                <div className="dr-result-card">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(236,72,153,0.15)', color: '#F472B6' }}>
                      <IconInfo />
                    </span>
                    <h4>Affected Areas</h4>
                  </div>
                  <div className="dr-tag-wrap">
                    {disease.affected_areas.map((a, i) => (
                      <span key={i} className="dr-tag dr-tag-pink">{a}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Alternatives */}
              {alternatives.length > 0 && (
                <div className="dr-result-card dr-card-wide">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(139,92,246,0.15)', color: '#A78BFA' }}>
                      <IconMicroscope />
                    </span>
                    <h4>Other Possible Conditions</h4>
                  </div>
                  <div className="dr-alt-grid">
                    {alternatives.map((alt, i) => (
                      <div key={i} className="dr-alt-item">
                        <span className="dr-alt-name">{alt.name}</span>
                        <div className="dr-alt-bar-wrap">
                          <div className="dr-alt-bar">
                            <div className="dr-alt-bar-fill" style={{ width: `${Math.round(alt.confidence * 100)}%` }} />
                          </div>
                          <span className="dr-alt-pct">{Math.round(alt.confidence * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Related Medicines */}
              {disease?.recommended_medicines?.length > 0 && (
                <div className="dr-result-card dr-card-wide">
                  <div className="dr-card-header">
                    <span className="dr-card-icon" style={{ background: 'rgba(6,182,212,0.15)', color: '#22D3EE' }}>
                      <IconPill />
                    </span>
                    <h4>Related Medicines</h4>
                  </div>
                  <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                    Commonly used medicines for this condition. Visit our pharmacy module for full details.
                  </p>
                  <Link to="/pharmacy" className="btn btn-pharmacy btn-sm">
                    Browse Pharmacy Module →
                  </Link>
                </div>
              )}
            </div>

            {/* Disclaimer */}
            <div className="dr-disclaimer">
              <IconWarning />
              <p><strong>Medical Disclaimer:</strong> This analysis is for informational purposes only and should not replace professional medical advice. Consult a qualified dermatologist for proper diagnosis and treatment.</p>
            </div>

            {/* Actions */}
            <div className="dr-result-actions">
              <button onClick={handleReset} className="btn btn-derm btn-lg" id="analyze-another-btn">
                <IconRefresh /> Analyze Another Image
              </button>
              <Link to="/profile" className="btn btn-outline btn-lg">
                View History
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DermatologyPage;

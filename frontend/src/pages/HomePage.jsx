import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

/* ─────────────────────────────────────────────────────────────
   SVG Icon Components
───────────────────────────────────────────────────────────── */
const IconMicroscope = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 18H4a2 2 0 0 1-2-2v-1h20v1a2 2 0 0 1-2 2h-2"/><path d="M6 18v3h12v-3"/>
    <path d="M15.5 8.5a2.5 2.5 0 1 0-5 0"/><path d="M13 6V2"/><path d="M10 6V4"/>
    <path d="M16 6V4"/><path d="M9 13a3 3 0 0 0 6 0"/>
  </svg>
);
const IconPill = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/>
    <path d="m8.5 8.5 7 7"/>
  </svg>
);
const IconBrain = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-4.66Z"/>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-4.66Z"/>
  </svg>
);
const IconShield = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>
  </svg>
);
const IconArrow = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M7 17l9.2-9.2M17 17V7H7"/>
  </svg>
);
const IconCheck = () => (
  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);
const IconScan = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/>
    <path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
    <line x1="7" y1="12" x2="17" y2="12"/>
  </svg>
);
const IconActivity = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
  </svg>
);
const IconGlobe = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <line x1="2" y1="12" x2="22" y2="12"/>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
);

/* ─────────────────────────────────────────────────────────────
   Particle Canvas Hook
───────────────────────────────────────────────────────────── */
function useParticles(canvasRef) {
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    const particles = [];
    const COLORS = ['rgba(139,92,246,', 'rgba(6,182,212,', 'rgba(236,72,153,'];

    const resize = () => {
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 70; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.8 + 0.4,
        dx: (Math.random() - 0.5) * 0.4,
        dy: (Math.random() - 0.5) * 0.4,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        alpha: Math.random() * 0.5 + 0.15,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color + p.alpha + ')';
        ctx.fill();
      });
      // Draw subtle connection lines
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(139,92,246,${0.06 * (1 - dist / 100)})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize); };
  }, [canvasRef]);
}

/* ─────────────────────────────────────────────────────────────
   Typewriter Hook
───────────────────────────────────────────────────────────── */
function useTypewriter(words, speed = 80, pauseMs = 1800) {
  const [display, setDisplay] = useState('');
  const [wordIdx, setWordIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = words[wordIdx % words.length];
    const delay = deleting ? speed / 2 : speed;
    const timer = setTimeout(() => {
      if (!deleting) {
        setDisplay(current.slice(0, charIdx + 1));
        if (charIdx + 1 === current.length) {
          setTimeout(() => setDeleting(true), pauseMs);
        } else {
          setCharIdx(c => c + 1);
        }
      } else {
        setDisplay(current.slice(0, charIdx - 1));
        if (charIdx - 1 === 0) {
          setDeleting(false);
          setWordIdx(w => w + 1);
          setCharIdx(0);
        } else {
          setCharIdx(c => c - 1);
        }
      }
    }, delay);
    return () => clearTimeout(timer);
  }, [charIdx, deleting, wordIdx, words, speed, pauseMs]);

  return display;
}

/* ─────────────────────────────────────────────────────────────
   Scroll-Reveal Hook
───────────────────────────────────────────────────────────── */
function useScrollReveal() {
  useEffect(() => {
    const targets = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
    const io = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
      { threshold: 0.12 }
    );
    targets.forEach(t => io.observe(t));
    return () => io.disconnect();
  }, []);
}

/* ─────────────────────────────────────────────────────────────
   Animated Counter Hook
───────────────────────────────────────────────────────────── */
function useCounter(target, duration = 1800, suffix = '') {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const start = performance.now();
        const num = parseInt(target.replace(/\D/g, ''), 10);
        const step = ts => {
          const elapsed = ts - start;
          const prog = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - prog, 3);
          setCount(Math.floor(eased * num));
          if (prog < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }
    }, { threshold: 0.5 });
    io.observe(el);
    return () => io.disconnect();
  }, [target, duration]);

  return { count, ref };
}

/* ─────────────────────────────────────────────────────────────
   Tilt Card Hook
───────────────────────────────────────────────────────────── */
function useTilt(ref) {
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handleMove = e => {
      const r = el.getBoundingClientRect();
      const x = e.clientX - r.left - r.width / 2;
      const y = e.clientY - r.top - r.height / 2;
      el.style.transform = `perspective(800px) rotateY(${x / 18}deg) rotateX(${-y / 18}deg) scale(1.02)`;
    };
    const handleLeave = () => { el.style.transform = 'perspective(800px) rotateY(0) rotateX(0) scale(1)'; };
    el.addEventListener('mousemove', handleMove);
    el.addEventListener('mouseleave', handleLeave);
    return () => { el.removeEventListener('mousemove', handleMove); el.removeEventListener('mouseleave', handleLeave); };
  }, [ref]);
}

/* ─────────────────────────────────────────────────────────────
   Stat Counter Component
───────────────────────────────────────────────────────────── */
function StatCounter({ value, label }) {
  const nonNum = value.replace(/\d/g, '');
  const { count, ref } = useCounter(value, 1600);
  return (
    <div className="stat-card reveal" ref={ref}>
      <div className="stat-number">
        <span className="stat-counter-num">{count}{nonNum}</span>
      </div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Feature Card with Tilt
───────────────────────────────────────────────────────────── */
function FeatureCard({ icon, title, desc, color, delay }) {
  const ref = useRef(null);
  useTilt(ref);
  return (
    <div ref={ref} className={`feature-card tilt-card reveal delay-${delay}`} style={{ '--card-accent': color }}>
      <div className="feature-card-icon" style={{ background: color + '18', border: `1px solid ${color}30` }}>
        <span style={{ color }}>{icon}</span>
      </div>
      <h3 className="feature-card-title">{title}</h3>
      <p className="feature-card-desc">{desc}</p>
      <div className="feature-card-arrow" style={{ color }}>
        <IconArrow />
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Main HomePage Component
───────────────────────────────────────────────────────────── */
const HomePage = () => {
  const canvasRef = useRef(null);
  const heroImgRef = useRef(null);
  const typed = useTypewriter(
    ['AI-Powered Medicine Scanner', 'Skin Disease Detection', 'Global Drug Database', 'Instant Health Insights'],
    75,
    2000
  );

  useParticles(canvasRef);
  useScrollReveal();

  // Parallax orb on mouse move
  useEffect(() => {
    const orb1 = document.getElementById('orb1');
    const orb2 = document.getElementById('orb2');
    const handle = e => {
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;
      if (orb1) orb1.style.transform = `translate(${x * 40}px, ${y * 30}px)`;
      if (orb2) orb2.style.transform = `translate(${-x * 30}px, ${-y * 20}px)`;
    };
    window.addEventListener('mousemove', handle);
    return () => window.removeEventListener('mousemove', handle);
  }, []);

  const FEATURES = [
    { icon: <IconScan />,       title: 'Medicine OCR Scanner',     desc: 'Point your camera at any medicine label — globally. AI extracts text and matches it against 500+ drugs instantly.', color: '#06B6D4', delay: '100' },
    { icon: <IconMicroscope />, title: 'Skin Condition Analysis',   desc: 'Upload a photo of your skin. Our model identifies 20+ dermatological conditions with confidence scores.', color: '#EC4899', delay: '200' },
    { icon: <IconBrain />,      title: 'AI-Driven Insights',        desc: 'Smart NLP extracts dosage, interactions, and warnings from chaotic OCR text with 96%+ accuracy.', color: '#8B5CF6', delay: '300' },
    { icon: <IconGlobe />,      title: 'Global Medicine Database',  desc: 'Covers brand names, generic equivalents, and trade names from India, US, UK, EU and beyond.', color: '#10B981', delay: '400' },
    { icon: <IconShield />,     title: 'Safety Warnings',           desc: 'Critical drug interactions, contraindications, and overdose warnings highlighted immediately.', color: '#F59E0B', delay: '500' },
    { icon: <IconActivity />,   title: 'Health History',            desc: 'All your scans and analyses saved securely. Track patterns and share with your doctor effortlessly.', color: '#3B82F6', delay: '600' },
  ];

  const MARQUEE_ITEMS = [
    'Medicine OCR', 'Skin Analysis', 'Drug Interactions', 'Global Coverage',
    'AI Diagnosis', 'Dosage Guidance', 'Real-time Results', 'Secure & Private',
    'Medicine OCR', 'Skin Analysis', 'Drug Interactions', 'Global Coverage',
    'AI Diagnosis', 'Dosage Guidance', 'Real-time Results', 'Secure & Private',
  ];

  return (
    <div className="home-page">

      {/* ── HERO ────────────────────────────────────────────── */}
      <section className="hero-section" id="hero">
        {/* Particle canvas */}
        <canvas ref={canvasRef} id="particle-canvas" />

        {/* Animated grid */}
        <div className="animated-grid" />

        {/* Drifting glow orbs */}
        <div id="orb1" className="hero-glow-1 orb-drift" />
        <div id="orb2" className="hero-glow-2" style={{ animationDelay: '-4s' }} />

        <div className="hero-inner">
          {/* Left: text */}
          <div className="hero-content">
            <div className="hero-eyebrow animate-fadeInUp stagger-1">
              <span className="hero-eyebrow-line" />
              AI-Powered Healthcare Platform
            </div>

            <h1 className="hero-title animate-fadeInUp stagger-2">
              <span className="text-highlight" style={{ display: 'block' }}>INTELLIGENT</span>
              <span className="hero-title-dim">FIRST AID</span>
              <span style={{ display: 'block', color: 'var(--color-white)', marginTop: '0.1em' }}>
                FOR ALL.
              </span>
            </h1>

            {/* Typewriter line */}
            <div className="hero-typewriter animate-fadeInUp stagger-3">
              <span className="hero-typewriter-text">{typed}</span>
              <span className="typed-cursor" />
            </div>

            <p className="hero-subtitle animate-fadeInUp stagger-4">
              Scan medicines, analyze skin conditions, and get instant treatment
              recommendations — all powered by advanced artificial intelligence.
            </p>

            <div className="hero-actions animate-fadeInUp stagger-5">
              <Link to="/register" className="btn btn-primary btn-lg pulse-glow" id="hero-cta-btn">
                Start Free Analysis
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg" id="hero-signin-btn">
                Sign In
              </Link>
            </div>

            {/* Trust bar */}
            <div className="hero-trust animate-fadeInUp stagger-6">
              <div className="hero-trust-avatars">
                {[
                  { bg: '#8B5CF6', l: 'A' }, { bg: '#06B6D4', l: 'M' },
                  { bg: '#EC4899', l: 'R' }, { bg: '#10B981', l: 'S' },
                ].map((a, i) => (
                  <div key={i} className="trust-avatar" style={{ background: a.bg }}>{a.l}</div>
                ))}
              </div>
              <p>Trusted by <strong>2,000+ professionals</strong> worldwide</p>
            </div>
          </div>

          {/* Right: floating product image */}
          <div className="hero-visual animate-fadeInUp stagger-3">
            <div className="hero-img-wrap float-anim-slow" ref={heroImgRef}>
              <img
                src="/hero-product.png"
                alt="AI Health Dashboard"
                className="hero-product-img"
                loading="eager"
              />
              {/* Glowing halo behind image */}
              <div className="hero-img-glow" />
            </div>

            {/* Floating badge 1 — accuracy */}
            <div className="hero-badge hero-badge-bottom animate-fadeInUp stagger-4"
              style={{ animation: 'float 5s ease-in-out infinite', animationDelay: '0.5s' }}>
              <div className="hero-badge-icon" style={{ background: 'rgba(139,92,246,0.2)' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <div>
                <div className="hero-badge-title">98% Accuracy</div>
                <div className="hero-badge-sub">AI-verified results</div>
              </div>
            </div>

            {/* Floating badge 2 — live */}
            <div className="hero-badge hero-badge-top animate-fadeInUp stagger-5"
              style={{ animation: 'float 6s ease-in-out infinite', animationDelay: '1.2s' }}>
              <div className="badge-dot-live" />
              <div>
                <div className="hero-badge-title">Live Analysis</div>
                <div className="hero-badge-sub">Processing now</div>
              </div>
            </div>

            {/* Floating chip: Global DB */}
            <div className="float-chip"
              style={{ top: '15%', left: '-10%', animation: 'floatX 4s ease-in-out infinite', animationDelay: '0.8s' }}>
              🌐 500+ Medicines
            </div>

            {/* Orbit ring */}
            <div className="orbit-ring"
              style={{ width: '480px', height: '480px', top: '50%', left: '50%',
                transform: 'translate(-50%,-50%)', animationDuration: '30s' }} />
            <div className="orbit-ring"
              style={{ width: '560px', height: '560px', top: '50%', left: '50%',
                transform: 'translate(-50%,-50%)', animationDuration: '45s',
                borderColor: 'rgba(6,182,212,0.1)', animationDirection: 'reverse' }} />
          </div>
        </div>
      </section>

      {/* ── MARQUEE ─────────────────────────────────────────── */}
      <div className="marquee-section">
        <div className="marquee-track">
          {MARQUEE_ITEMS.map((item, i) => (
            <div key={i} className="marquee-item">
              <span className="marquee-dot" />
              {item}
            </div>
          ))}
        </div>
      </div>

      {/* ── STATS ───────────────────────────────────────────── */}
      <section className="stats-section">
        <div className="glow-divider" style={{ marginBottom: '4rem' }} />
        <div className="stats-grid">
          <StatCounter value="10K+" label="SCANS COMPLETED" />
          <StatCounter value="98%" label="ACCURACY RATE" />
          <StatCounter value="500+" label="MEDICINES IN DB" />
          <StatCounter value="24/7" label="ALWAYS AVAILABLE" />
        </div>
        <div className="glow-divider" style={{ marginTop: '4rem' }} />
      </section>

      {/* ── FEATURES ────────────────────────────────────────── */}
      <section className="features-section" id="features">
        <div className="section-inner">
          <div className="section-header reveal">
            <h4>WHAT WE OFFER</h4>
            <h2>Everything you need for <span className="text-highlight">smart healthcare</span></h2>
            <p className="section-subtitle">
              From OCR medicine scanning to AI skin diagnosis — built for real people, powered by real AI.
            </p>
          </div>

          <div className="features-grid">
            {FEATURES.map((f, i) => (
              <FeatureCard key={i} {...f} />
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ────────────────────────────────────── */}
      <section className="process-section" id="how-it-works">
        <div className="section-inner">
          <div className="section-header reveal">
            <h4>HOW IT WORKS</h4>
            <h2>Three steps to <span className="text-highlight">instant answers</span></h2>
          </div>

          <div className="process-steps">
            {[
              {
                num: '01',
                title: 'Upload a Photo',
                desc: 'Take a picture of any medicine label or your skin condition. Works with any camera.',
                color: '#8B5CF6',
              },
              {
                num: '02',
                title: 'AI Processes It',
                desc: 'Our multi-pass OCR and keyword AI extracts and matches data in under 2 seconds.',
                color: '#06B6D4',
              },
              {
                num: '03',
                title: 'Get Your Results',
                desc: 'Receive detailed medicine info, interaction warnings, or skin condition analysis instantly.',
                color: '#EC4899',
              },
            ].map((step, i) => (
              <div key={i} className={`process-step reveal delay-${(i + 1) * 200}`}>
                <div className="process-step-num" style={{ color: step.color, borderColor: step.color + '30', background: step.color + '10' }}>
                  {step.num}
                </div>
                <div className="process-step-content">
                  <h3 style={{ color: 'var(--color-white)', marginBottom: '0.75rem' }}>{step.title}</h3>
                  <p>{step.desc}</p>
                </div>
                {i < 2 && (
                  <div className="process-connector">
                    <svg width="40" height="2" viewBox="0 0 40 2">
                      <line x1="0" y1="1" x2="40" y2="1" stroke="rgba(255,255,255,0.1)" strokeWidth="1" strokeDasharray="4 4" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PHARMACY MODULE ─────────────────────────────────── */}
      <section className="module-section" id="pharmacy">
        <div className="section-inner">
          <div className="module-card hover-lift border-beam reveal-left">
            <div className="module-content">
              <div className="module-badge" style={{ background: 'rgba(6,182,212,0.1)', borderColor: 'rgba(6,182,212,0.25)', color: '#22D3EE' }}>
                <IconPill /> Pharmacy Module
              </div>
              <h2>Scan <span style={{ color: '#06B6D4' }}>any medicine</span><br />in the world</h2>
              <p className="module-desc">
                Point your camera at a medicine strip, box, or label — in any language, any country.
                Our OCR extracts the text and matches it against our global database covering 500+
                medicines with dosage, interactions, and warnings.
              </p>
              <ul className="module-features-list">
                {[
                  'Multi-pass OCR with image enhancement',
                  'Global brand + generic name matching',
                  'Drug interaction & contraindication alerts',
                  'Dosage guidance for adults & children',
                  'Works offline with cached results',
                ].map((item, i) => (
                  <li key={i} className="module-feature-item">
                    <span className="module-check" style={{ background: 'rgba(6,182,212,0.15)', color: '#06B6D4' }}>
                      <IconCheck />
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register" className="btn btn-pharmacy btn-lg" id="pharmacy-cta-btn">
                Try Medicine Scanner
              </Link>
            </div>
            <div className="module-visual">
              <div className="module-img-wrap float-anim">
                <img src="/pharmacy-product.png" alt="Pharmacy AI Scanner" className="module-img" />
                <div className="module-img-glow" style={{ background: 'radial-gradient(circle, rgba(6,182,212,0.3) 0%, transparent 70%)' }} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── DERMATOLOGY MODULE ──────────────────────────────── */}
      <section className="module-section" id="dermatology">
        <div className="section-inner">
          <div className="module-card module-card-reverse hover-lift border-beam reveal-right">
            <div className="module-visual">
              <div className="module-img-wrap float-anim" style={{ animationDelay: '-2s' }}>
                <img src="/dermatology-product.png" alt="Skin Analysis AI" className="module-img" />
                <div className="module-img-glow" style={{ background: 'radial-gradient(circle, rgba(236,72,153,0.3) 0%, transparent 70%)' }} />
              </div>
            </div>
            <div className="module-content">
              <div className="module-badge" style={{ background: 'rgba(236,72,153,0.1)', borderColor: 'rgba(236,72,153,0.25)', color: '#F472B6' }}>
                <IconMicroscope /> Dermatology Module
              </div>
              <h2>Identify <span style={{ color: '#EC4899' }}>skin conditions</span><br />instantly</h2>
              <p className="module-desc">
                Upload a photo of your skin and our AI model analyzes color, texture, and patterns
                to identify from 20+ dermatological conditions — from common acne to rare autoimmune diseases.
              </p>
              <ul className="module-features-list">
                {[
                  '20+ skin conditions covered',
                  'Keyword & image feature matching',
                  'Severity classification (mild → severe)',
                  'Treatment recommendations with medicines',
                  'India-specific prevalence-weighted results',
                ].map((item, i) => (
                  <li key={i} className="module-feature-item">
                    <span className="module-check" style={{ background: 'rgba(236,72,153,0.15)', color: '#EC4899' }}>
                      <IconCheck />
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link to="/register" className="btn btn-derm btn-lg" id="derm-cta-btn">
                Try Skin Analysis
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ──────────────────────────────────────── */}
      <section className="cta-section">
        <div className="section-inner">
          <div className="cta-card reveal-scale">
            {/* Animated gradient background */}
            <div className="cta-bg gradient-anim"
              style={{ background: 'linear-gradient(135deg, #4C1D95, #1E3A5F, #701A41, #064E3B)' }} />
            <div className="cta-grid" />
            <div className="cta-content">
              <h4 style={{ color: 'rgba(167,139,250,0.8)' }}>GET STARTED TODAY</h4>
              <h2 style={{ fontSize: 'clamp(2rem, 4vw, 3.2rem)', marginBottom: '1.25rem' }}>
                Your personal <span className="text-highlight">AI health assistant</span><br />is waiting
              </h2>
              <p style={{ color: 'rgba(255,255,255,0.6)', maxWidth: '500px', margin: '0 auto 2.5rem' }}>
                Join thousands already using FirstAid to scan medicines, understand skin conditions,
                and make faster, smarter health decisions.
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link to="/register" className="btn btn-primary btn-lg pulse-glow" id="cta-register-btn">
                  Create Free Account
                </Link>
                <Link to="/login" className="btn btn-outline btn-lg" id="cta-login-btn">
                  Sign In
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default HomePage;

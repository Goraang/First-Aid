import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer" id="main-footer">
      <div className="footer-container" style={{ flexDirection: 'column', gap: 0 }}>
        {/* Top row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr 1fr',
          gap: 'var(--space-3xl)',
          paddingBottom: 'var(--space-2xl)',
          borderBottom: '1px solid var(--color-border)',
          flexWrap: 'wrap'
        }}>
          {/* Brand */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
            <Link to="/" className="footer-logo">
              <span className="logo-icon" style={{ width: 32, height: 32, borderRadius: 8, flexShrink: 0 }} aria-hidden="true" />
              <span style={{ fontFamily: 'var(--font-headline)', fontWeight: 800 }}>FirstAid</span>
            </Link>
            <p style={{ fontSize: '0.88rem', lineHeight: 1.75, maxWidth: 280 }}>
              AI-powered healthcare platform for instant skin analysis and medicine identification.
              Making quality healthcare accessible to everyone.
            </p>
            <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
              {['X', 'in', 'GH', '@'].map((social, i) => (
                <a
                  key={i}
                  href={`#${social}`}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'var(--color-bg-glass)',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-muted)',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    transition: 'var(--transition-fast)',
                    textDecoration: 'none'
                  }}
                  onMouseEnter={e => { e.target.style.borderColor = 'var(--color-border-accent)'; e.target.style.color = 'var(--color-text)'; }}
                  onMouseLeave={e => { e.target.style.borderColor = 'var(--color-border)'; e.target.style.color = 'var(--color-text-muted)'; }}
                >
                  {social}
                </a>
              ))}
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 style={{ marginBottom: 'var(--space-lg)', fontSize: '0.72rem', letterSpacing: '0.1em' }}>Product</h4>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {[
                { label: 'Skin Analysis', to: '/dermatology' },
                { label: 'Medicine Scanner', to: '/pharmacy' },
                { label: 'Health Profile', to: '/profile' },
                { label: 'Features', to: '/#features' },
              ].map((item, i) => (
                <li key={i}>
                  <Link to={item.to} className="footer-links" style={{ fontSize: '0.88rem', color: 'var(--color-text-muted)', transition: 'var(--transition-fast)' }}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 style={{ marginBottom: 'var(--space-lg)', fontSize: '0.72rem', letterSpacing: '0.1em' }}>Resources</h4>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {['Documentation', 'API Reference', 'Help Center', 'Health Blog'].map((item, i) => (
                <li key={i}>
                  <a href="#" style={{ fontSize: '0.88rem', color: 'var(--color-text-muted)', transition: 'var(--transition-fast)', textDecoration: 'none', display: 'block' }}>
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 style={{ marginBottom: 'var(--space-lg)', fontSize: '0.72rem', letterSpacing: '0.1em' }}>Legal</h4>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {['Privacy Policy', 'Terms of Service', 'HIPAA Compliance', 'Contact Us'].map((item, i) => (
                <li key={i}>
                  <a href="#" style={{ fontSize: '0.88rem', color: 'var(--color-text-muted)', transition: 'var(--transition-fast)', textDecoration: 'none', display: 'block' }}>
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom row */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: 'var(--space-lg)',
          flexWrap: 'wrap',
          gap: 'var(--space-sm)'
        }}>
          <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            &copy; {currentYear} FirstAid Platform. All rights reserved.
          </p>
          <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
            For informational purposes only. Always consult a qualified healthcare professional.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

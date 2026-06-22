import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();

  const getPasswordStrength = () => {
    if (!password) return { width: '0%', color: '#E5E7EB', label: '' };
    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 10) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    const levels = [
      { width: '20%', color: '#EF4444', label: 'Very weak' },
      { width: '40%', color: '#F59E0B', label: 'Weak' },
      { width: '60%', color: '#F59E0B', label: 'Fair' },
      { width: '80%', color: '#10B981', label: 'Good' },
      { width: '100%', color: '#10B981', label: 'Strong' },
    ];
    return levels[Math.min(score, 4)];
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (!agreedToTerms) {
      setError('Please agree to the Terms of Service');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, name);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container" id="register-page">
      {/* Left Visual Side */}
      <div className="auth-visual">
        <div className="auth-visual-content">
          <div className="auth-visual-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.44-4.66Z"/>
              <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.44-4.66Z"/>
            </svg>
          </div>
          <h2>Join FirstAid today</h2>
          <p>Get instant access to AI-powered skin analysis, medicine OCR scanning, and personalized health insights — all in one platform.</p>
          <div className="auth-visual-stats">
            <div className="auth-stat"><div className="auth-stat-value">10K+</div><div className="auth-stat-label">Scans done</div></div>
            <div className="auth-stat"><div className="auth-stat-value">98%</div><div className="auth-stat-label">Accuracy</div></div>
            <div className="auth-stat"><div className="auth-stat-value">Free</div><div className="auth-stat-label">To start</div></div>
          </div>
        </div>
      </div>

      {/* Right Form Side */}
      <div className="auth-form-side">
        <div className="auth-box">
          <h1>Create account</h1>
          <p className="auth-subtitle">Start your free health journey today</p>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="register-name">Full name</label>
              <input
                id="register-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="John Doe"
                autoComplete="name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-email">Email address</label>
              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="register-password">Password</label>
              <input
                id="register-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Create a strong password"
                autoComplete="new-password"
              />
              {password && (
                <>
                  <div className="password-strength">
                    <div
                      className="password-strength-bar"
                      style={{ width: strength.width, background: strength.color }}
                    ></div>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: strength.color, marginTop: '4px', fontWeight: 500 }}>
                    {strength.label}
                  </p>
                </>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="register-confirm-password">Confirm password</label>
              <input
                id="register-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="Confirm your password"
                autoComplete="new-password"
              />
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <input
                id="register-terms"
                type="checkbox"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                style={{ width: 'auto', marginTop: '3px' }}
              />
              <label htmlFor="register-terms" style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', fontWeight: 400, cursor: 'pointer' }}>
                I agree to the <a href="#terms" style={{ color: 'var(--color-primary-light)', fontWeight: 500 }}>Terms of Service</a> and <a href="#privacy" style={{ color: 'var(--color-primary-light)', fontWeight: 500 }}>Privacy Policy</a>
              </label>
            </div>

            <button type="submit" disabled={isLoading} id="register-submit-btn">
              {isLoading ? 'Creating account...' : 'Create free account'}
            </button>
          </form>

          <div className="auth-divider">or</div>

          <p className="auth-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

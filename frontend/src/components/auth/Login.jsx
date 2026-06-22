import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from './AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container" id="login-page">
      {/* Left Visual Side */}
      <div className="auth-visual">
        <div className="auth-visual-content">
          <div className="auth-visual-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <h2>Welcome back to FirstAid</h2>
          <p>Your AI-powered healthcare companion. Scan medicines, analyze skin conditions, and get instant medical insights.</p>
          <div className="auth-visual-stats">
            <div className="auth-stat"><div className="auth-stat-value">10K+</div><div className="auth-stat-label">Scans done</div></div>
            <div className="auth-stat"><div className="auth-stat-value">98%</div><div className="auth-stat-label">Accuracy</div></div>
            <div className="auth-stat"><div className="auth-stat-value">500+</div><div className="auth-stat-label">Medicines</div></div>
          </div>
        </div>
      </div>

      {/* Right Form Side */}
      <div className="auth-form-side">
        <div className="auth-box">
          <h1>Sign in</h1>
          <p className="auth-subtitle">Enter your credentials to access your account</p>

          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="login-email">Email address</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            <button type="submit" disabled={isLoading} id="login-submit-btn">
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="auth-divider">or</div>

          <p className="auth-link">
            Don't have an account? <Link to="/register">Create one free</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

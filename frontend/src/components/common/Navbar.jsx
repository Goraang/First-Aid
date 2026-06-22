import React, { useContext, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../auth/AuthContext';

const Navbar = () => {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link';
  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="navbar" id="main-navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          <span className="logo-icon" aria-hidden="true" />
          <span>
            FirstAid
            <span className="logo-sub">AI Platform</span>
          </span>
        </Link>

        {/* Mobile toggle */}
        <button
          className={`nav-toggle ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation menu"
          id="nav-toggle-btn"
        >
          <span />
          <span />
          <span />
        </button>

        {/* Nav menu */}
        <div className={`nav-menu ${menuOpen ? 'open' : ''}`}>
          {isAuthenticated ? (
            <>
              <Link to="/" className={isActive('/')} onClick={closeMenu}>Home</Link>
              <Link to="/dermatology" className={isActive('/dermatology')} onClick={closeMenu}>Dermatology</Link>
              <Link to="/pharmacy" className={isActive('/pharmacy')} onClick={closeMenu}>Pharmacy</Link>
              <Link to="/profile" className={isActive('/profile')} onClick={closeMenu}>Profile</Link>
              <button onClick={handleLogout} className="logout-btn" id="logout-btn">
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className={isActive('/login')} onClick={closeMenu}>Login</Link>
              <Link to="/register" className="register-btn" onClick={closeMenu} id="nav-register-btn">
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

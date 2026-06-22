import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './components/auth/AuthContext';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import ProtectedRoute from './components/common/ProtectedRoute';

// Pages
import HomePage from './pages/HomePage';
import DermatologyPage from './pages/DermatologyPage';
import PharmacyPage from './pages/PharmacyPage';
import ProfilePage from './pages/ProfilePage';

// Auth Pages
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Styles
import './styles/global.css';
import './styles/home.css';
import './styles/dermatology.css';
import './styles/pharmacy.css';
import './styles/profile.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              {/* Auth Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />

              {/* Protected Routes */}
              <Route
                path="/dermatology"
                element={
                  <ProtectedRoute>
                    <DermatologyPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/pharmacy"
                element={
                  <ProtectedRoute>
                    <PharmacyPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              {/* Catch all - redirect to home */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;

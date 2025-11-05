import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import './App.css';

// OAuth Callback Handler Component
function OAuthCallback() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(location.search);
      const sessionToken = params.get('session_token');
      
      if (sessionToken) {
        try {
          // Session token received from backend after OAuth
          // Store in sessionStorage
          sessionStorage.setItem('session_token', sessionToken);
          
          // Fetch user profile
          const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:7860';
          const response = await fetch(`${API_URL}/api/history?limit=1`, {
            headers: {
              'Authorization': `Bearer ${sessionToken}`
            }
          });
          
          if (response.ok) {
            // Successfully authenticated
            // Set a default user object (we'll get real profile from history)
            sessionStorage.setItem('user', JSON.stringify({ name: 'User' }));
            navigate('/dashboard', { replace: true });
          } else {
            console.error('Failed to verify session');
            navigate('/', { replace: true });
          }
        } catch (error) {
          console.error('OAuth callback error:', error);
          navigate('/', { replace: true });
        }
      } else {
        navigate('/', { replace: true });
      }
    };

    handleCallback();
  }, [location, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="loader mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (sessionStorage, not localStorage)
    const token = sessionStorage.getItem('session_token');
    const savedUser = sessionStorage.getItem('user');
    
    if (token && savedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(savedUser));
    }
    
    setLoading(false);
  }, []);

  const handleLogin = (userData, sessionToken) => {
    sessionStorage.setItem('session_token', sessionToken);
    sessionStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('session_token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('drive_folder_id');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/callback"
          element={<OAuthCallback />}
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <Dashboard user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

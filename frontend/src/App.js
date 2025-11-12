import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';
import Landing from '@/pages/Landing';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Onboarding from '@/pages/Onboarding';
import Home from '@/pages/Home';
import WorkoutPage from '@/pages/WorkoutPage';
import CompletionPage from '@/pages/CompletionPage';
import Profile from '@/pages/Profile';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Axios interceptor for auth token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState('dark'); // default to dark mode

  useEffect(() => {
    // Load theme from localStorage, default to dark mode
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  useEffect(() => {
    checkAuth();
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-[#1A1A1A] text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Home user={user} onLogout={handleLogout} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Landing theme={theme} onToggleTheme={toggleTheme} />
              )
            }
          />
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/home" />
              ) : (
                <Login onLogin={handleLogin} theme={theme} onToggleTheme={toggleTheme} />
              )
            }
          />
          <Route
            path="/register"
            element={
              isAuthenticated ? (
                <Navigate to="/onboarding" />
              ) : (
                <Register onRegister={handleLogin} theme={theme} onToggleTheme={toggleTheme} />
              )
            }
          />
          <Route
            path="/onboarding"
            element={
              isAuthenticated ? (
                <Onboarding user={user} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/home"
            element={
              isAuthenticated ? (
                <Home user={user} onLogout={handleLogout} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/workout/:id"
            element={
              isAuthenticated ? (
                <WorkoutPage user={user} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/workout/complete"
            element={
              isAuthenticated ? (
                <CompletionPage user={user} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/profile"
            element={
              isAuthenticated ? (
                <Profile user={user} onLogout={handleLogout} theme={theme} onToggleTheme={toggleTheme} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" />
    </div>
  );
}

export default App;
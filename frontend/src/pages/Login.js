import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Dumbbell, ArrowLeft } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Login = ({ onLogin, theme, onToggleTheme }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      onLogin(response.data.access_token, response.data.user);
      toast.success('Welcome back!');
      navigate('/home');
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <div
        className="w-full max-w-lg animate-fadeIn rounded-3xl transition-all duration-300"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: '2rem', // makes it extra round
        }}
      >
        <div className="flex items-center justify-between mb-6 px-8 pt-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 transition-colors"
            style={{ color: 'var(--text-secondary)' }}
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Home</span>
          </button>
          <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
        </div>

        <div className="text-center mb-8 px-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-[#D4AF37] rounded-full mb-4">
            <Dumbbell className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Welcome Back</h1>
          <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>Continue your fitness journey</p>
        </div>

        <div
          className="rounded-3xl p-10 premium-shadow border"
          style={{
            backgroundColor: 'var(--card-bg)',
            borderColor: 'var(--border-color)',
            boxShadow: 'var(--shadow-md)',
            margin: '0 2rem 2rem'
          }}
        >
          {/* form stays the same */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="email" className="mb-2 block font-medium" style={{ color: 'var(--text-primary)' }}>
                Email
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                data-testid="login-email-input"
                className="rounded-xl h-12"
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
                placeholder="your@email.com"
              />
            </div>

            <div>
              <Label htmlFor="password" className="mb-2 block font-medium" style={{ color: 'var(--text-primary)' }}>
                Password
              </Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                data-testid="login-password-input"
                className="rounded-xl h-12"
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
                placeholder="••••••••"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="login-submit-button"
              className="w-full bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-semibold h-12 rounded-xl text-lg"
            >
              {loading ? 'Logging in...' : 'Log In'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p style={{ color: 'var(--text-secondary)' }}>
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                data-testid="go-to-register-button"
                className="text-[#D4AF37] font-semibold hover:underline"
              >
                Sign Up
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>

  );
};

export default Login;
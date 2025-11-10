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

const Register = ({ onRegister, theme, onToggleTheme }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/register`, formData);
      onRegister(response.data.access_token, response.data.user);
      toast.success('Account created successfully!');
      navigate('/onboarding');
    } catch (error) {
      console.error('Registration error:', error);
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <div className="w-full max-w-md animate-fadeIn">
        <div className="flex items-center justify-between mb-6">
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

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#D4AF37] rounded-full mb-4">
            <Dumbbell className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Create Account</h1>
          <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>Start your fitness journey today</p>
        </div>

        <div className="rounded-3xl p-8 premium-shadow border" style={{ 
          backgroundColor: 'var(--card-bg)',
          borderColor: 'var(--border-color)',
          boxShadow: 'var(--shadow-md)'
        }}>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="name" className="mb-2 block font-medium" style={{ color: 'var(--text-primary)' }}>Name</Label>
              <Input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                data-testid="register-name-input"
                className="rounded-xl h-12"
                style={{ 
                  backgroundColor: 'var(--bg-secondary)',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
                placeholder="Your name"
              />
            </div>

            <div>
              <Label htmlFor="email" className="mb-2 block font-medium" style={{ color: 'var(--text-primary)' }}>Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                data-testid="register-email-input"
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
              <Label htmlFor="password" className="mb-2 block font-medium" style={{ color: 'var(--text-primary)' }}>Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                data-testid="register-password-input"
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
              data-testid="register-submit-button"
              className="w-full bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-semibold h-12 rounded-xl text-lg"
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p style={{ color: 'var(--text-secondary)' }}>
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                data-testid="go-to-login-button"
                className="text-[#D4AF37] font-semibold hover:underline"
              >
                Log In
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

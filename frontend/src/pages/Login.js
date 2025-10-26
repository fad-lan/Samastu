import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Dumbbell } from 'lucide-react';

const Login = ({ onLogin }) => {
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
      navigate('/');
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0D] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fadeIn">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#00FF88] rounded-full mb-4">
            <Dumbbell className="w-8 h-8 text-[#0D0D0D]" />
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-2">Samastu</h1>
          <p className="text-[#B0B0B0] text-lg">Fitness Made Fun</p>
        </div>

        <div className="bg-[#1a1a1a] rounded-3xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold text-white mb-6">Welcome Back</h2>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="email" className="text-white mb-2 block">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                data-testid="login-email-input"
                className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] focus:ring-[#00FF88] rounded-xl h-12"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-white mb-2 block">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                data-testid="login-password-input"
                className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] focus:ring-[#00FF88] rounded-xl h-12"
                placeholder="••••••••"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="login-submit-button"
              className="w-full bg-[#00FF88] hover:bg-[#00dd77] text-[#0D0D0D] font-semibold h-12 rounded-xl text-lg"
            >
              {loading ? 'Logging in...' : 'Log In'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-[#B0B0B0]">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                data-testid="go-to-register-button"
                className="text-[#00FF88] font-semibold hover:underline"
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
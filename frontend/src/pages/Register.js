import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Dumbbell, ArrowLeft } from 'lucide-react';

const Register = ({ onRegister }) => {
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
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fadeIn">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-[#1A1A1A] transition-colors mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#D4AF37] rounded-full mb-4">
            <Dumbbell className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-[#1A1A1A] mb-2">Create Account</h1>
          <p className="text-gray-600 text-lg">Start your fitness journey today</p>
        </div>

        <div className="bg-white rounded-3xl p-8 premium-shadow border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Label htmlFor="name" className="text-[#1A1A1A] mb-2 block font-medium">Name</Label>
              <Input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                data-testid="register-name-input"
                className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-12"
                placeholder="Your name"
              />
            </div>

            <div>
              <Label htmlFor="email" className="text-[#1A1A1A] mb-2 block font-medium">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                data-testid="register-email-input"
                className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-12"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-[#1A1A1A] mb-2 block font-medium">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                data-testid="register-password-input"
                className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-12"
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
            <p className="text-gray-600">
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
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Dumbbell, Zap, Target, Trophy, TrendingUp, Users, Star, CheckCircle } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Landing = ({ theme, onToggleTheme }) => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Target,
      title: 'Personalized Workout Plans',
      description: 'Customized routines based on your goals, equipment, and fitness level.'
    },
    {
      icon: Zap,
      title: 'Gamified XP & Streak System',
      description: 'Earn XP, level up, and maintain streaks just like your favorite apps.'
    },
    {
      icon: TrendingUp,
      title: 'Progress Visualization',
      description: 'Track your journey with beautiful charts and achievement badges.'
    },
    {
      icon: Trophy,
      title: 'Smart Reminders & Rewards',
      description: 'Stay motivated with daily challenges and milestone celebrations.'
    }
  ];

  const stats = [
    { label: 'Workouts Tracked', value: '10K+', icon: Dumbbell },
    { label: 'Completion Rate', value: '95%', icon: CheckCircle },
    { label: 'Active Users', value: '5K+', icon: Users },
    { label: 'Average Rating', value: '4.9', icon: Star }
  ];

  const testimonials = [
    {
      name: 'Sarah M.',
      avatar: 'SM',
      quote: 'Samastu made working out fun again. The gamification keeps me coming back every day!'
    },
    {
      name: 'Mike R.',
      avatar: 'MR',
      quote: 'Love the clean interface and the streak system. It\'s like Duolingo but for fitness!'
    },
    {
      name: 'Emma L.',
      avatar: 'EL',
      quote: 'Finally, a workout app that doesn\'t feel overwhelming. Simple, beautiful, effective.'
    }
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Navigation */}
      <nav className="fixed top-0 w-full backdrop-blur-md z-50 border-b" style={{ 
        backgroundColor: 'var(--card-bg)',
        borderColor: 'var(--border-color)'
      }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Dumbbell className="w-8 h-8 text-[#D4AF37]" />
            <span className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Samastu</span>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
            <Button
              onClick={() => navigate('/login')}
              data-testid="nav-login-button"
              className="border-2"
              style={{ 
                backgroundColor: 'var(--card-bg)',
                color: 'var(--text-primary)',
                borderColor: 'var(--border-color)'
              }}
            >
              Log In
            </Button>
            <Button
              onClick={() => navigate('/register')}
              data-testid="nav-signup-button"
              className="bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-semibold"
            >
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 bg-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fadeIn">
              <h1 className="text-5xl lg:text-7xl font-bold mb-6 leading-tight" style={{ color: 'var(--text-primary)' }}>
                Make Workouts
                <span className="block gradient-text">Fun Again.</span>
              </h1>
              <p className="text-xl mb-8 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                Samastu helps you build muscle, stay consistent, and enjoy the journey with gamified motivation.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button
                  onClick={() => navigate('/register')}
                  data-testid="hero-get-started-button"
                  className="bg-[#060736] hover:bg-[#c19b2e] text-white font-semibold h-14 px-8 text-lg rounded-xl"
                >
                  Get Started Free
                </Button>
                <Button
                  onClick={() => navigate('/register')}
                  data-testid="hero-view-demo-button"
                  className="bg-white hover:bg-gray-50 text-[#060736] border-2 border-gray-200 h-14 px-8 text-lg rounded-xl"
                >
                  View Demo
                </Button>
              </div>
            </div>
            
            <div className="relative animate-slideUp">
              <div className="bg-gradient-to-br from-[#D4AF37]/10 to-[#c19b2e]/5 rounded-3xl p-8 premium-shadow">
                <div className="bg-white rounded-2xl p-6 premium-shadow">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 bg-[#D4AF37] rounded-full flex items-center justify-center">
                      <Dumbbell className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Today's Workout</p>
                      <p className="font-bold text-[#060736]">Full Body Starter</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                      <span className="text-sm text-[#060736]">Push-ups</span>
                      <span className="text-xs text-gray-500">3 × 10</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                      <span className="text-sm text-[#060736]">Squats</span>
                      <span className="text-xs text-gray-500">3 × 15</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                      <span className="text-sm text-[#060736]">Plank</span>
                      <span className="text-xs text-gray-500">2 × 30s</span>
                    </div>
                  </div>
                  <Button               
                  onClick={() => navigate('/login')}
                  data-testid="nav-login-button" 
                  className="w-full mt-6 bg-[#060736] hover:bg-[#c19b2e] text-white font-semibold">
                    Start Workout
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-[#060736] mb-4">Everything You Need</h2>
            <p className="text-xl text-gray-600">Powerful features designed to keep you motivated</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="bg-white rounded-2xl p-8 card-hover premium-shadow animate-fadeIn"
                  style={{ animationDelay: `${idx * 0.1}s` }}
                >
                  <div className="w-14 h-14 bg-[#D4AF37]/10 rounded-xl flex items-center justify-center mb-6">
                    <Icon className="w-7 h-7 text-[#D4AF37]" />
                  </div>
                  <h3 className="text-xl font-bold text-[#060736] mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6 bg-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-br from-[#060736] to-[#c19b2e] rounded-3xl p-12 premium-shadow">
            <h2 className="text-4xl font-bold text-white text-center mb-12">Trusted by Thousands</h2>
            <div className="grid md:grid-cols-4 gap-8">
              {stats.map((stat, idx) => {
                const Icon = stat.icon;
                return (
                  <div key={idx} className="text-center animate-fadeIn" style={{ animationDelay: `${idx * 0.1}s` }}>
                    <Icon className="w-10 h-10 text-white mx-auto mb-4" />
                    <div className="text-5xl font-bold text-white mb-2">{stat.value}</div>
                    <div className="text-white/90">{stat.label}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-6 bg-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-[#060736] mb-4">What People Say</h2>
            <p className="text-xl text-gray-600">Join our growing community of fitness enthusiasts</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl p-8 premium-shadow animate-slideUp"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-14 h-14 bg-[#D4AF37] rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="font-bold text-[#060736]">{testimonial.name}</p>
                    <div className="flex gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 fill-[#D4AF37] text-[#D4AF37]" />
                      ))}
                    </div>
                  </div>
                </div>
                <p className="text-gray-600 italic leading-relaxed">"{testimonial.quote}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl lg:text-5xl font-bold text-[#060736] mb-6">
            Start Your Fitness Journey Today
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of users making workouts fun and consistent with Samastu.
          </p>
          <Button
            onClick={() => navigate('/register')}
            data-testid="cta-get-started-button"
            className="bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-bold h-14 px-12 text-lg rounded-xl"
          >
            Get Started Free
          </Button>
          <p className="text-sm text-gray-500 mt-4">No credit card required • Free forever</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#060736] text-white py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Dumbbell className="w-8 h-8 text-[#D4AF37]" />
            <span className="text-2xl font-bold">Samastu</span>
          </div>
          <p className="text-gray-400 mb-4">Make workouts fun again.</p>
          <p className="text-sm text-gray-500">© 2025 Samastu. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
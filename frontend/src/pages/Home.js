import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { User, Zap, Flame, Trophy, Calendar, RefreshCw, Sun, Moon } from 'lucide-react';
import WorkoutCalendar from '@/components/WorkoutCalendar';
import ThemeToggle from '@/components/ThemeToggle';

const Home = ({ user, onLogout, theme, onToggleTheme }) => {
  const navigate = useNavigate();
  const [journey, setJourney] = useState([]);
  const [progress, setProgress] = useState(null);
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('calendar'); // 'calendar' or 'journey'

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [journeyRes, progressRes, scheduleRes] = await Promise.all([
        axios.get(`${API}/workouts/journey`),
        axios.get(`${API}/progress`),
        axios.get(`${API}/schedule/calendar`),
      ]);
      setJourney(journeyRes.data);
      setProgress(progressRes.data);
      setSchedule(scheduleRes.data);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleResetSchedule = async () => {
    if (!window.confirm('Are you sure you want to reset your workout plan? Your current plan and AI-generated workouts will be deleted, and new AI workouts will be generated.')) {
      return;
    }
    
    try {
      toast.info('Resetting schedule and generating new AI workouts...');
      await axios.delete(`${API}/schedule/reset`);
      await axios.post(`${API}/schedule/generate`);
      toast.success('New AI-powered workout plan generated successfully!');
      
      // Refresh data
      const scheduleRes = await axios.get(`${API}/schedule/calendar`);
      setSchedule(scheduleRes.data);
    } catch (error) {
      console.error('Reset error:', error);
      toast.error('Failed to reset schedule');
    }
  };

  const handleWorkoutClick = (workout) => {
    if (workout.is_rest_day) {
      toast.info('This is a rest day. Take it easy! 😊');
      return;
    }
    
    if (workout.is_locked) {
      toast.error('This workout is scheduled for a future date. Come back on ' + new Date(workout.scheduled_date).toLocaleDateString());
      return;
    }
    
    if (workout.is_next || workout.is_completed || workout.scheduled_date) {
      navigate(`/workout/${workout.id}`);
    } else {
      toast.error('Complete previous workouts first!');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <div style={{ color: 'var(--text-primary)' }} className="text-xl">Loading...</div>
      </div>
    );
  }

  const xpProgress = progress ? (progress.total_xp % 500) / 500 * 100 : 0;

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Header */}
      <div className=" border-b style={{ borderColor: 'var(--border-color)' }} p-6 sticky top-0 z-10 premium-shadow" style={{ 
        backgroundColor: 'var(--card-bg)', 
        borderColor: 'var(--border-color)',
        boxShadow: 'var(--shadow-md)'
      }}>
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Samastu</h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Hey {user?.name}! 💪</p>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
            <button
              onClick={() => navigate('/profile')}
              data-testid="profile-nav-button"
              className="p-2 rounded-full bg-[#D4AF37] hover:bg-[#c19b2e] transition-colors"
            >
              <User className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-2xl p-4 text-center premium-shadow border" style={{ 
            backgroundColor: 'var(--card-bg)', 
            borderColor: 'var(--border-color)',
            boxShadow: 'var(--shadow-md)'
          }}>
            <div className="flex items-center justify-center gap-2 mb-1">
              <Trophy className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Level</span>
            </div>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="user-level">{progress?.level || 1}</p>
          </div>
          
          <div className="rounded-2xl p-4 text-center premium-shadow border" style={{ 
            backgroundColor: 'var(--card-bg)', 
            borderColor: 'var(--border-color)',
            boxShadow: 'var(--shadow-md)'
          }}>
            <div className="flex items-center justify-center gap-2 mb-1">
              <Zap className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>XP</span>
            </div>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="user-xp">{progress?.total_xp || 0}</p>
          </div>
          
          <div className="rounded-2xl p-4 text-center premium-shadow border" style={{ 
            backgroundColor: 'var(--card-bg)', 
            borderColor: 'var(--border-color)',
            boxShadow: 'var(--shadow-md)'
          }}>
            <div className="flex items-center justify-center gap-2 mb-1">
              <Flame className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Streak</span>
            </div>
            <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="user-streak">{progress?.streak || 0}</p>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="mt-6 rounded-2xl p-4 premium-shadow border" style={{ 
          backgroundColor: 'var(--card-bg)', 
          borderColor: 'var(--border-color)',
          boxShadow: 'var(--shadow-md)'
        }}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Next Level</span>
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{Math.floor(xpProgress)}%</span>
          </div>
          <div className="w-full h-3 rounded-full overflow-hidden" style={{ backgroundColor: '#F5F5F5' }}>
            <div
              className="h-full bg-gradient-to-r from-[#D4AF37] to-[#c19b2e] rounded-full transition-all duration-500"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Journey Path */}
      <div className="max-w-4xl mx-auto px-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            {view === 'calendar' ? 'Your Workout Schedule' : 'Your Workout Journey'}
          </h2>
          <div className="flex gap-2">
            <Button
              onClick={handleResetSchedule}
              data-testid="reset-schedule-button"
              className="border-2"
              style={{ 
                backgroundColor: 'var(--card-bg)',
                color: 'var(--text-primary)',
                borderColor: 'var(--border-color)'
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset Plan
            </Button>
            <Button
              onClick={() => setView(view === 'calendar' ? 'journey' : 'calendar')}
              data-testid="toggle-view-button"
              className="bg-[#D4AF37] hover:bg-[#c19b2e] text-white"
            >
              <Calendar className="w-4 h-4 mr-2" />
              {view === 'calendar' ? 'Journey View' : 'Calendar View'}
            </Button>
          </div>
        </div>
        
        {view === 'calendar' ? (
          schedule.length > 0 ? (
            <WorkoutCalendar schedule={schedule} />
          ) : (
            <div className="rounded-2xl p-12 text-center premium-shadow border style={{ borderColor: 'var(--border-color)' }}">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold style={{ color: 'var(--text-primary)' }} mb-2">No Schedule Yet</h3>
              <p className="style={{ color: 'var(--text-secondary)' }} mb-6">Complete your profile setup to generate a personalized workout schedule.</p>
              <Button
                onClick={() => navigate('/profile')}
                className="bg-[#D4AF37] hover:bg-[#c19b2e] text-white"
              >
                Go to Profile
              </Button>
            </div>
          )
        ) : (
          <div className="relative">
          {/* Connection Line */}
          <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-200" />
          
          <div className="space-y-6">
            {journey.map((workout, index) => {
              const isRestDay = workout.is_rest_day;
              const isLocked = workout.is_locked;
              
              return (
              <div key={workout.id || index} className="relative flex items-start animate-fadeIn" style={{ animationDelay: `${index * 0.1}s` }}>
                {/* Node Circle */}
                <div
                  className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                    isRestDay
                      ? 'bg-gray-200 border-4 border-white'
                      : workout.is_completed
                      ? 'bg-[#D4AF37] glow-effect'
                      : workout.is_next
                      ? 'bg-[#D4AF37] animate-pulse border-4 border-[#D4AF37]/30'
                      : isLocked
                      ? 'bg-gray-300 border-4 border-white'
                      : 'bg-gray-200 border-4 border-white'
                  }`}
                >
                  {isRestDay ? (
                    <div className="text-2xl">☕</div>
                  ) : workout.is_completed ? (
                    <div className="w-8 h-8 text-white flex items-center justify-center font-bold text-2xl">✓</div>
                  ) : isLocked ? (
                    <div className="text-2xl">🔒</div>
                  ) : (
                    <div className={`w-8 h-8 flex items-center justify-center font-bold ${
                      workout.is_next ? 'text-white' : 'text-gray-400'
                    }`}>{index + 1}</div>
                  )}
                </div>

                {/* Workout Card */}
                <div
                  onClick={() => handleWorkoutClick(workout)}
                  data-testid={`workout-card-${workout.id}`}
                  className={`ml-6 flex-1 bg-white rounded-2xl p-5 transition-all cursor-pointer premium-shadow border ${
                    isRestDay
                      ? 'cursor-default border-gray-100 bg-gray-50'
                      : isLocked
                      ? 'opacity-60 cursor-not-allowed border-gray-100'
                      : workout.is_next || workout.is_completed
                      ? 'hover:bg-gray-50 card-hover border-gray-100 cursor-pointer'
                      : 'opacity-50 cursor-not-allowed border-gray-100'
                  } ${
                    workout.is_next && !isRestDay && !isLocked ? 'gold-border' : ''
                  }`}
                  style={{ 
                    backgroundColor: isRestDay ? 'var(--bg-secondary)' : 'var(--card-bg)',
                    borderColor: 'var(--border-color)',
                    boxShadow: 'var(--shadow-md)'
                  }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>{workout.name}</h3>
                    <span className={`text-xs px-3 py-1 rounded-full font-semibold ${
                      isRestDay ? 'bg-gray-200' : 'bg-[#D4AF37]/10 text-[#D4AF37]'
                    }`} style={{ 
                      backgroundColor: isRestDay ? 'var(--bg-tertiary)' : undefined,
                      color: isRestDay ? 'var(--text-secondary)' : '#D4AF37'
                    }}>
                      {workout.difficulty}
                    </span>
                  </div>
                  
                  {workout.scheduled_date && (
                    <p className="text-xs mb-2" style={{ color: 'var(--text-tertiary)' }}>
                      Scheduled: {new Date(workout.scheduled_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </p>
                  )}
                  
                  <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>{workout.target_muscles}</p>
                  
                  {!isRestDay && (
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Zap className="w-4 h-4 text-[#D4AF37]" />
                        <span style={{ color: 'var(--text-secondary)' }}>+{workout.xp_reward} XP</span>
                      </div>
                      <div style={{ color: 'var(--text-secondary)' }}>• {workout.duration_minutes} min</div>
                      <div style={{ color: 'var(--text-secondary)' }}>• {workout.exercises?.length || 0} exercises</div>
                    </div>
                  )}
                  
                  {isLocked && (
                    <div className="mt-2 text-xs font-semibold" style={{ color: 'var(--text-tertiary)' }}>🔒 Unlocks on scheduled date</div>
                  )}
                </div>
              </div>
              );
            })}
          </div>
        </div>
        )}
      </div>
    </div>
  );
};

export default Home;
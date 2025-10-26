import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { User, Zap, Flame, Trophy, Calendar, RefreshCw } from 'lucide-react';
import WorkoutCalendar from '@/components/WorkoutCalendar';

const Home = ({ user, onLogout }) => {
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
    if (!window.confirm('Are you sure you want to delete your current workout plan? This cannot be undone.')) {
      return;
    }
    
    try {
      await axios.delete(`${API}/schedule/reset`);
      await axios.post(`${API}/schedule/generate`);
      toast.success('Schedule reset! Generating new plan...');
      
      // Refresh data
      const scheduleRes = await axios.get(`${API}/schedule/calendar`);
      setSchedule(scheduleRes.data);
    } catch (error) {
      console.error('Reset error:', error);
      toast.error('Failed to reset schedule');
    }
  };

  const handleWorkoutClick = (workout) => {
    if (workout.is_next || workout.is_completed) {
      navigate(`/workout/${workout.id}`);
    } else {
      toast.error('Complete previous workouts first!');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-[#1A1A1A] text-xl">Loading...</div>
      </div>
    );
  }

  const xpProgress = progress ? (progress.total_xp % 500) / 500 * 100 : 0;

  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 p-6 sticky top-0 z-10 premium-shadow">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[#1A1A1A]">Samastu</h1>
            <p className="text-gray-600 text-sm">Hey {user?.name}! 💪</p>
          </div>
          <div className="flex items-center gap-4">
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
          <div className="bg-white rounded-2xl p-4 text-center premium-shadow border border-gray-100">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Trophy className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-gray-600 text-sm">Level</span>
            </div>
            <p className="text-2xl font-bold text-[#1A1A1A]" data-testid="user-level">{progress?.level || 1}</p>
          </div>
          
          <div className="bg-white rounded-2xl p-4 text-center premium-shadow border border-gray-100">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Zap className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-gray-600 text-sm">XP</span>
            </div>
            <p className="text-2xl font-bold text-[#1A1A1A]" data-testid="user-xp">{progress?.total_xp || 0}</p>
          </div>
          
          <div className="bg-white rounded-2xl p-4 text-center premium-shadow border border-gray-100">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Flame className="w-5 h-5 text-[#D4AF37]" />
              <span className="text-gray-600 text-sm">Streak</span>
            </div>
            <p className="text-2xl font-bold text-[#1A1A1A]" data-testid="user-streak">{progress?.streak || 0}</p>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="mt-6 bg-white rounded-2xl p-4 premium-shadow border border-gray-100">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600 text-sm">Next Level</span>
            <span className="text-[#1A1A1A] text-sm font-semibold">{Math.floor(xpProgress)}%</span>
          </div>
          <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
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
          <h2 className="text-2xl font-bold text-[#1A1A1A]">
            {view === 'calendar' ? 'Your Workout Schedule' : 'Your Workout Journey'}
          </h2>
          <div className="flex gap-2">
            <Button
              onClick={handleResetSchedule}
              data-testid="reset-schedule-button"
              className="bg-white hover:bg-gray-50 text-[#1A1A1A] border-2 border-gray-200"
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
            <div className="bg-white rounded-2xl p-12 text-center premium-shadow border border-gray-100">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-[#1A1A1A] mb-2">No Schedule Yet</h3>
              <p className="text-gray-600 mb-6">Complete your profile setup to generate a personalized workout schedule.</p>
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
            {journey.map((workout, index) => (
              <div key={workout.id} className="relative flex items-start animate-fadeIn" style={{ animationDelay: `${index * 0.1}s` }}>
                {/* Node Circle */}
                <div
                  className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                    workout.is_completed
                      ? 'bg-[#D4AF37] glow-effect'
                      : workout.is_next
                      ? 'bg-[#D4AF37] animate-pulse border-4 border-[#D4AF37]/30'
                      : 'bg-gray-200 border-4 border-white'
                  }`}
                >
                  {workout.is_completed ? (
                    <div className="w-8 h-8 text-white flex items-center justify-center font-bold text-2xl">✓</div>
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
                    workout.is_next || workout.is_completed
                      ? 'hover:bg-gray-50 card-hover border-gray-100'
                      : 'opacity-50 cursor-not-allowed border-gray-100'
                  } ${
                    workout.is_next ? 'gold-border' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-[#1A1A1A]">{workout.name}</h3>
                    <span className="text-xs bg-[#D4AF37]/10 text-[#D4AF37] px-3 py-1 rounded-full font-semibold">
                      {workout.difficulty}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 text-sm mb-3">{workout.target_muscles}</p>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Zap className="w-4 h-4 text-[#D4AF37]" />
                      <span className="text-gray-600">+{workout.xp_reward} XP</span>
                    </div>
                    <div className="text-gray-600">• {workout.duration_minutes} min</div>
                    <div className="text-gray-600">• {workout.exercises.length} exercises</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        )}
      </div>
    </div>
  );
};

export default Home;
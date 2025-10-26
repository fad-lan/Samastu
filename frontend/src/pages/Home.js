import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { User, Zap, Flame, Trophy } from 'lucide-react';

const Home = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [journey, setJourney] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [journeyRes, progressRes] = await Promise.all([
        axios.get(`${API}/workouts/journey`),
        axios.get(`${API}/progress`),
      ]);
      setJourney(journeyRes.data);
      setProgress(progressRes.data);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
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
      <div className="min-h-screen bg-[#0D0D0D] flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  const xpProgress = progress ? (progress.total_xp % 500) / 500 * 100 : 0;

  return (
    <div className="min-h-screen bg-[#0D0D0D] pb-20">
      {/* Header */}
      <div className="bg-[#1a1a1a] p-6 sticky top-0 z-10 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Samastu</h1>
            <p className="text-[#B0B0B0] text-sm">Hey {user?.name}! 💪</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/profile')}
              data-testid="profile-nav-button"
              className="p-2 rounded-full bg-[#00FF88] hover:bg-[#00dd77] transition-colors"
            >
              <User className="w-5 h-5 text-[#0D0D0D]" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[#1a1a1a] rounded-2xl p-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Trophy className="w-5 h-5 text-[#00FF88]" />
              <span className="text-[#B0B0B0] text-sm">Level</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="user-level">{progress?.level || 1}</p>
          </div>
          
          <div className="bg-[#1a1a1a] rounded-2xl p-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Zap className="w-5 h-5 text-[#00FF88]" />
              <span className="text-[#B0B0B0] text-sm">XP</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="user-xp">{progress?.total_xp || 0}</p>
          </div>
          
          <div className="bg-[#1a1a1a] rounded-2xl p-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Flame className="w-5 h-5 text-[#00FF88]" />
              <span className="text-[#B0B0B0] text-sm">Streak</span>
            </div>
            <p className="text-2xl font-bold text-white" data-testid="user-streak">{progress?.streak || 0}</p>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="mt-6 bg-[#1a1a1a] rounded-2xl p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[#B0B0B0] text-sm">Next Level</span>
            <span className="text-white text-sm font-semibold">{Math.floor(xpProgress)}%</span>
          </div>
          <div className="w-full h-3 bg-[#0D0D0D] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#00FF88] rounded-full transition-all duration-500"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Journey Path */}
      <div className="max-w-4xl mx-auto px-6">
        <h2 className="text-2xl font-bold text-white mb-6">Your Workout Journey</h2>
        
        <div className="relative">
          {/* Connection Line */}
          <div className="absolute left-8 top-0 bottom-0 w-1 bg-[#333]" />
          
          <div className="space-y-6">
            {journey.map((workout, index) => (
              <div key={workout.id} className="relative flex items-start animate-fadeIn" style={{ animationDelay: `${index * 0.1}s` }}>
                {/* Node Circle */}
                <div
                  className={`relative z-10 flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                    workout.is_completed
                      ? 'bg-[#00FF88] glow-effect'
                      : workout.is_next
                      ? 'bg-[#00FF88] animate-pulse border-4 border-[#00FF88]/30'
                      : 'bg-[#333] border-4 border-[#1a1a1a]'
                  }`}
                >
                  {workout.is_completed ? (
                    <div className="w-8 h-8 text-[#0D0D0D] flex items-center justify-center font-bold text-2xl">✓</div>
                  ) : (
                    <div className="w-8 h-8 text-white flex items-center justify-center font-bold">{index + 1}</div>
                  )}
                </div>

                {/* Workout Card */}
                <div
                  onClick={() => handleWorkoutClick(workout)}
                  data-testid={`workout-card-${workout.id}`}
                  className={`ml-6 flex-1 bg-[#1a1a1a] rounded-2xl p-5 transition-all cursor-pointer ${
                    workout.is_next || workout.is_completed
                      ? 'hover:bg-[#222] card-hover'
                      : 'opacity-50 cursor-not-allowed'
                  } ${
                    workout.is_next ? 'neon-border' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-white">{workout.name}</h3>
                    <span className="text-xs bg-[#00FF88]/20 text-[#00FF88] px-3 py-1 rounded-full font-semibold">
                      {workout.difficulty}
                    </span>
                  </div>
                  
                  <p className="text-[#B0B0B0] text-sm mb-3">{workout.target_muscles}</p>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Zap className="w-4 h-4 text-[#00FF88]" />
                      <span className="text-[#B0B0B0]">+{workout.xp_reward} XP</span>
                    </div>
                    <div className="text-[#B0B0B0]">• {workout.duration_minutes} min</div>
                    <div className="text-[#B0B0B0]">• {workout.exercises.length} exercises</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
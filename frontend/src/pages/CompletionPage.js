import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Trophy, Zap, Flame, Award } from 'lucide-react';

const CompletionPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { result, workoutName } = location.state || {};

  useEffect(() => {
    if (!result) {
      navigate('/');
    }
  }, [result, navigate]);

  if (!result) {
    return null;
  }

  const motivationalMessages = [
    "🔥 You crushed it today!",
    "💪 Muscles loading... keep going!",
    "⚡ You did it again, legend!",
    "🏆 Another one in the books!",
    "🚀 You're unstoppable!",
    "🌟 Keep up the amazing work!",
  ];

  const randomMessage = motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-lg animate-fadeIn">
        {/* Success Animation */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-[#D4AF37] rounded-full mb-6 animate-pulse">
            <Trophy className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">Workout Complete!</h1>
          <p className="text-[#B0B0B0] text-lg mb-2">{workoutName}</p>
          <p className="text-2xl text-[#00FF88] font-semibold">{randomMessage}</p>
        </div>

        {/* Stats Cards */}
        <div className="space-y-4 mb-8">
          {/* XP Gained */}
          <div className="bg-[#1a1a1a] rounded-2xl p-6 flex items-center justify-between animate-slideUp">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-[#00FF88]/20 rounded-full flex items-center justify-center">
                <Zap className="w-6 h-6 text-[#00FF88]" />
              </div>
              <div>
                <p className="text-[#B0B0B0] text-sm">XP Earned</p>
                <p className="text-2xl font-bold text-white">+{result.xp_earned}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[#B0B0B0] text-sm">Total XP</p>
              <p className="text-xl font-bold text-[#00FF88]" data-testid="total-xp-display">{result.new_total_xp}</p>
            </div>
          </div>

          {/* Level */}
          <div className="bg-[#1a1a1a] rounded-2xl p-6 flex items-center gap-4 animate-slideUp" style={{ animationDelay: '0.1s' }}>
            <div className="w-12 h-12 bg-[#00FF88]/20 rounded-full flex items-center justify-center">
              <Trophy className="w-6 h-6 text-[#00FF88]" />
            </div>
            <div className="flex-1">
              <p className="text-[#B0B0B0] text-sm">Current Level</p>
              <p className="text-2xl font-bold text-white" data-testid="current-level-display">Level {result.new_level}</p>
            </div>
            {result.new_level > 1 && (
              <div className="text-[#00FF88] font-semibold">Level Up! 🎉</div>
            )}
          </div>

          {/* Streak */}
          <div className="bg-[#1a1a1a] rounded-2xl p-6 flex items-center gap-4 animate-slideUp" style={{ animationDelay: '0.2s' }}>
            <div className="w-12 h-12 bg-[#00FF88]/20 rounded-full flex items-center justify-center">
              <Flame className="w-6 h-6 text-[#00FF88]" />
            </div>
            <div>
              <p className="text-[#B0B0B0] text-sm">Current Streak</p>
              <p className="text-2xl font-bold text-white" data-testid="current-streak-display">{result.new_streak} {result.new_streak === 1 ? 'day' : 'days'}</p>
            </div>
          </div>

          {/* New Achievements */}
          {result.new_achievements && result.new_achievements.length > 0 && (
            <div className="bg-[#00FF88]/10 border-2 border-[#00FF88] rounded-2xl p-6 animate-slideUp" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center gap-3 mb-3">
                <Award className="w-6 h-6 text-[#00FF88]" />
                <p className="text-[#00FF88] font-bold text-lg">New Achievement Unlocked!</p>
              </div>
              <div className="space-y-2">
                {result.new_achievements.map((achievement, idx) => (
                  <div key={idx} className="text-white">
                    • {achievement.replace('_', ' ').toUpperCase()}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={() => navigate('/')}
            data-testid="back-to-journey-button"
            className="w-full bg-[#00FF88] hover:bg-[#00dd77] text-[#0D0D0D] font-bold h-12 rounded-xl text-lg"
          >
            Back to Journey
          </Button>
          
          <Button
            onClick={() => navigate('/profile')}
            data-testid="view-progress-button"
            className="w-full bg-[#1a1a1a] hover:bg-[#252525] text-white font-semibold h-12 rounded-xl border-2 border-[#333]"
          >
            View Full Progress
          </Button>
        </div>

        {/* Motivational Quote */}
        <div className="mt-8 text-center">
          <p className="text-[#B0B0B0] italic">“Don't break your streak now!”</p>
        </div>
      </div>
    </div>
  );
};

export default CompletionPage;
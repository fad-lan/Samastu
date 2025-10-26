import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { ArrowLeft, User, Trophy, Zap, Flame, Award, Edit2, LogOut } from 'lucide-react';

const Profile = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [totalWorkouts, setTotalWorkouts] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    height: user?.height || '',
    weight: user?.weight || '',
    goal: user?.goal || '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [progressRes, achievementsRes] = await Promise.all([
        axios.get(`${API}/progress`),
        axios.get(`${API}/achievements`),
      ]);
      setProgress(progressRes.data);
      setAchievements(achievementsRes.data.achievements);
      setTotalWorkouts(achievementsRes.data.total_workouts);
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSaveProfile = async () => {
    try {
      const updateData = {
        ...formData,
        height: formData.height ? parseFloat(formData.height) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
      };
      await axios.put(`${API}/user/profile`, updateData);
      toast.success('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleLogoutClick = () => {
    onLogout();
    navigate('/login');
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
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/')}
            data-testid="profile-back-button"
            className="flex items-center gap-2 text-[#B0B0B0] hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Journey</span>
          </button>
          
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-white">Profile</h1>
            <Button
              onClick={handleLogoutClick}
              data-testid="logout-button"
              className="bg-[#ff4444] hover:bg-[#dd3333] text-white"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* User Info Card */}
        <div className="bg-[#1a1a1a] rounded-3xl p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 bg-[#00FF88] rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-[#0D0D0D]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{user?.name}</h2>
                <p className="text-[#B0B0B0]">{user?.email}</p>
              </div>
            </div>
            
            {!isEditing && (
              <Button
                onClick={() => setIsEditing(true)}
                data-testid="edit-profile-button"
                className="bg-[#00FF88] hover:bg-[#00dd77] text-[#0D0D0D]"
              >
                <Edit2 className="w-4 h-4 mr-2" />
                Edit
              </Button>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-4 mt-6">
              <div>
                <Label className="text-white mb-2 block">Name</Label>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  data-testid="profile-name-input"
                  className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] rounded-xl"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-white mb-2 block">Height (cm)</Label>
                  <Input
                    name="height"
                    type="number"
                    value={formData.height}
                    onChange={handleInputChange}
                    data-testid="profile-height-input"
                    className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] rounded-xl"
                  />
                </div>
                
                <div>
                  <Label className="text-white mb-2 block">Weight (kg)</Label>
                  <Input
                    name="weight"
                    type="number"
                    value={formData.weight}
                    onChange={handleInputChange}
                    data-testid="profile-weight-input"
                    className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] rounded-xl"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={handleSaveProfile}
                  data-testid="save-profile-button"
                  className="flex-1 bg-[#00FF88] hover:bg-[#00dd77] text-[#0D0D0D] font-semibold"
                >
                  Save Changes
                </Button>
                <Button
                  onClick={() => setIsEditing(false)}
                  data-testid="cancel-edit-button"
                  className="flex-1 bg-[#333] hover:bg-[#444] text-white"
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="bg-[#0D0D0D] rounded-2xl p-4">
                <p className="text-[#B0B0B0] text-sm mb-1">Height</p>
                <p className="text-xl font-bold text-white">{user?.height ? `${user.height} cm` : 'Not set'}</p>
              </div>
              
              <div className="bg-[#0D0D0D] rounded-2xl p-4">
                <p className="text-[#B0B0B0] text-sm mb-1">Weight</p>
                <p className="text-xl font-bold text-white">{user?.weight ? `${user.weight} kg` : 'Not set'}</p>
              </div>
              
              <div className="bg-[#0D0D0D] rounded-2xl p-4">
                <p className="text-[#B0B0B0] text-sm mb-1">Goal</p>
                <p className="text-xl font-bold text-white capitalize">{user?.goal || 'Not set'}</p>
              </div>
              
              <div className="bg-[#0D0D0D] rounded-2xl p-4">
                <p className="text-[#B0B0B0] text-sm mb-1">Total Workouts</p>
                <p className="text-xl font-bold text-white" data-testid="total-workouts-display">{totalWorkouts}</p>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#1a1a1a] rounded-2xl p-6 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Trophy className="w-6 h-6 text-[#00FF88]" />
              <span className="text-[#B0B0B0]">Level</span>
            </div>
            <p className="text-3xl font-bold text-white" data-testid="profile-level-display">{progress?.level || 1}</p>
          </div>
          
          <div className="bg-[#1a1a1a] rounded-2xl p-6 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Zap className="w-6 h-6 text-[#00FF88]" />
              <span className="text-[#B0B0B0]">Total XP</span>
            </div>
            <p className="text-3xl font-bold text-white" data-testid="profile-xp-display">{progress?.total_xp || 0}</p>
          </div>
          
          <div className="bg-[#1a1a1a] rounded-2xl p-6 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Flame className="w-6 h-6 text-[#00FF88]" />
              <span className="text-[#B0B0B0]">Streak</span>
            </div>
            <p className="text-3xl font-bold text-white" data-testid="profile-streak-display">{progress?.streak || 0} days</p>
          </div>
        </div>

        {/* XP Progress */}
        <div className="bg-[#1a1a1a] rounded-2xl p-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-xl font-bold text-white">Level Progress</h3>
            <span className="text-[#00FF88] font-semibold">{Math.floor(xpProgress)}%</span>
          </div>
          <div className="w-full h-4 bg-[#0D0D0D] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#00FF88] rounded-full transition-all duration-500"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
          <p className="text-[#B0B0B0] text-sm mt-2">
            {500 - (progress?.total_xp % 500)} XP until Level {(progress?.level || 1) + 1}
          </p>
        </div>

        {/* Achievements */}
        <div className="bg-[#1a1a1a] rounded-3xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <Award className="w-6 h-6 text-[#00FF88]" />
            <h3 className="text-2xl font-bold text-white">Achievements</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                data-testid={`achievement-${achievement.id}`}
                className={`p-5 rounded-2xl border-2 transition-all ${
                  achievement.unlocked
                    ? 'bg-[#00FF88]/10 border-[#00FF88]'
                    : 'bg-[#0D0D0D] border-[#333] opacity-50'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    achievement.unlocked ? 'bg-[#00FF88]' : 'bg-[#333]'
                  }`}>
                    {achievement.unlocked ? (
                      <Award className="w-6 h-6 text-[#0D0D0D]" />
                    ) : (
                      <span className="text-2xl">🔒</span>
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <h4 className={`font-bold text-lg mb-1 ${
                      achievement.unlocked ? 'text-[#00FF88]' : 'text-[#B0B0B0]'
                    }`}>
                      {achievement.name}
                    </h4>
                    <p className="text-[#B0B0B0] text-sm">{achievement.description}</p>
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

export default Profile;
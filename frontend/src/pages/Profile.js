import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { ArrowLeft, User, Trophy, Zap, Flame, Award, Edit2, LogOut } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Profile = ({ user, onLogout, theme, onToggleTheme }) => {
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

  const handleDeleteAccount = async () => {
    if (!window.confirm('⚠️ Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently deleted.')) {
      return;
    }
    
    const confirmText = window.prompt('Type "DELETE" to confirm account deletion:');
    if (confirmText !== 'DELETE') {
      toast.error('Account deletion cancelled');
      return;
    }
    
    try {
      await axios.delete(`${API}/user/account`);
      toast.success('Account deleted successfully');
      onLogout();
      navigate('/');
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete account');
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
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Header */}
      <div className="border-b p-6 sticky top-0 z-10 premium-shadow" style={{ 
        backgroundColor: 'var(--card-bg)', 
        borderColor: 'var(--border-color)',
      }}>
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/home')}
            data-testid="profile-back-button"
            className="flex items-center gap-2 transition-colors mb-4"
            style={{ color: 'var(--text-secondary)' }}
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Journey</span>
          </button>
          
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Profile</h1>
            <div className="flex items-center gap-3">
              <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
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
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* User Info Card */}
        <div className="rounded-3xl p-8" 
          style={{ backgroundColor: 'var(--bg-secondary)',
          border: '1px solid #D4AF37'
          }} >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 bg-[#D4AF37] rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-[#0D0D0D]" />
              </div>
              <div>
                <h2 className="text-2xl font-bold " style={{ color: 'var(--text-primary)' }}>{user?.name}</h2>
                <p className="text-600" style={{ color: 'var(--text-primary)' }}>{user?.email}</p>
              </div>
            </div>
            
            {!isEditing && (
              <Button
                onClick={() => setIsEditing(true)}
                data-testid="edit-profile-button"
                className="bg-[#D4AF37] hover:bg-[#c19b2e] text-[#0D0D0D]"
              >
                <Edit2 className="w-4 h-4 mr-2" />
                Edit
              </Button>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-4 mt-6">
              <div>
                <Label className="text-[#1A1A1A] mb-2 block">Name</Label>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  data-testid="profile-name-input"
                  className="bg-white border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] rounded-xl"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-[#1A1A1A] mb-2 block">Height (cm)</Label>
                  <Input
                    name="height"
                    type="number"
                    value={formData.height}
                    onChange={handleInputChange}
                    data-testid="profile-height-input"
                    className="bg-white border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] rounded-xl"
                  />
                </div>
                
                <div>
                  <Label className="text-[#1A1A1A] mb-2 block">Weight (kg)</Label>
                  <Input
                    name="weight"
                    type="number"
                    value={formData.weight}
                    onChange={handleInputChange}
                    data-testid="profile-weight-input"
                    className="bg-white border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] rounded-xl"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  onClick={handleSaveProfile}
                  data-testid="save-profile-button"
                  className="flex-1 bg-[#D4AF37] hover:bg-[#c19b2e] text-[#0D0D0D] font-semibold"
                >
                  Save Changes
                </Button>
                <Button
                  onClick={() => setIsEditing(false)}
                  data-testid="cancel-edit-button"
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-[#1A1A1A]"
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="bg-white rounded-2xl p-4">
                <p className="text-gray-600 text-sm mb-1">Height</p>
                <p className="text-xl font-bold text-[#1A1A1A]">{user?.height ? `${user.height} cm` : 'Not set'}</p>
              </div>
              
              <div className="bg-white rounded-2xl p-4">
                <p className="text-gray-600 text-sm mb-1">Weight</p>
                <p className="text-xl font-bold text-[#1A1A1A]">{user?.weight ? `${user.weight} kg` : 'Not set'}</p>
              </div>
              
              <div className="bg-white rounded-2xl p-4">
                <p className="text-gray-600 text-sm mb-1">Goal</p>
                <p className="text-xl font-bold text-[#1A1A1A] capitalize">{user?.goal || 'Not set'}</p>
              </div>
              
              <div className="bg-white rounded-2xl p-4">
                <p className="text-gray-600 text-sm mb-1">Total Workouts</p>
                <p className="text-xl font-bold text-[#1A1A1A]" data-testid="total-workouts-display">{totalWorkouts}</p>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl p-6 text-center"           
          style={{ backgroundColor: 'var(--bg-secondary)',
          border: '1px solid #D4AF37'
          }}>
            <div className="flex items-center justify-center gap-2 mb-2">
              <Trophy className="w-6 h-6 text-[#D4AF37]" />
              <span className="text-600" style={{ color: 'var(--text-primary)' }}>Level</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="profile-level-display">{progress?.level || 1}</p>
          </div>
          
          <div className="rounded-2xl p-6 text-center"           
          style={{ backgroundColor: 'var(--bg-secondary)',
          border: '1px solid #D4AF37'
          }}>
            <div className="flex items-center justify-center gap-2 mb-2">
              <Zap className="w-6 h-6 text-[#D4AF37]" />
              <span className="text-600" style={{ color: 'var(--text-primary)' }}>Total XP</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="profile-xp-display">{progress?.total_xp || 0}</p>
          </div>
          
          <div className="rounded-2xl p-6 text-center"           
          style={{ backgroundColor: 'var(--bg-secondary)',
          border: '1px solid #D4AF37'
          }}>
            <div className="flex items-center justify-center gap-2 mb-2">
              <Flame className="w-6 h-6 text-[#D4AF37]" />
              <span className="text-600" style={{ color: 'var(--text-primary)' }}>Streak</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }} data-testid="profile-streak-display">{progress?.streak || 0} days</p>
          </div>
        </div>

        {/* XP Progress */}
        <div className="rounded-2xl p-6"           
        style={{ backgroundColor: 'var(--bg-secondary)',
        border: '1px solid #D4AF37'
          }}>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Level Progress</h3>
            <span className="text-[#D4AF37] font-semibold">{Math.floor(xpProgress)}%</span>
          </div>
          <div className="w-full h-4 bg-white rounded-full overflow-hidden">
            <div
              className="h-full bg-[#D4AF37] rounded-full transition-all duration-500"
              style={{ width: `${xpProgress}%` }}
            />
          </div>
          <p className="text-600 text-sm mt-2" style={{ color: 'var(--text-primary)' }}>
            {500 - (progress?.total_xp % 500)} XP until Level {(progress?.level || 1) + 1}
          </p>
        </div>

        {/* Achievements */}
        <div className="rounded-3xl p-8"         
        style={{ backgroundColor: 'var(--bg-secondary)',
        border: '1px solid #D4AF37'
          }}>
          <div className="flex items-center gap-3 mb-6">
            <Award className="w-6 h-6 text-[#D4AF37]" />
            <h3 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Achievements</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                data-testid={`achievement-${achievement.id}`}
                className={`p-5 rounded-2xl border-2 transition-all ${
                  achievement.unlocked
                    ? 'bg-[#D4AF37]/10 border-[#D4AF37]'
                    : 'bg-white border-gray-200 opacity-50'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    achievement.unlocked ? 'bg-[#D4AF37]' : 'bg-gray-200'
                  }`}>
                    {achievement.unlocked ? (
                      <Award className="w-6 h-6 text-[#0D0D0D]" />
                    ) : (
                      <span className="text-2xl">🔒</span>
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <h4 className={`font-bold text-lg mb-1 ${
                      achievement.unlocked ? 'text-[#D4AF37]' : 'text-gray-600'
                    }`}>
                      {achievement.name}
                    </h4>
                    <p className="text-gray-600 text-sm">{achievement.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Danger Zone */}
        <div className="rounded-3xl p-8 border-2 border-red-700" style={{ backgroundColor: 'var(--bg-secondary)'}}>
          <h3 className="text-xl font-bold text-red-600 mb-2">Danger Zone</h3>
          <p className="text-600 mb-4" style={{ color: 'var(--text-primary)' }}>Once you delete your account, there is no going back. Please be certain.</p>
          <Button
            onClick={handleDeleteAccount}
            data-testid="delete-account-button"
            className="bg-red-500 hover:bg-red-600 text-white font-semibold"
          >
            Delete My Account
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
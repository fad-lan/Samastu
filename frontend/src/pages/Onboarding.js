import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { ChevronRight } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const Onboarding = ({ user, theme, onToggleTheme }) => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    gender: '',
    height: '',
    weight: '',
    goal: '',
    equipment: [],
    experience_level: '',
    available_days: [], // [{day: "Monday", minutes: 30}]
    plan_duration: 4,
    plan_duration_unit: 'weeks',
  });

  const goals = [
    { id: 'lean', label: 'Lean & Toned', icon: '⚡' },
    { id: 'strong', label: 'Strong & Defined', icon: '💪' },
    { id: 'bulk', label: 'Bulk & Build', icon: '🏋️' },
    { id: 'active', label: 'Just Stay Active', icon: '🏃' },
  ];

  const experienceLevels = [
    { id: 'beginner', label: 'Beginner', description: 'New to working out' },
    { id: 'intermediate', label: 'Intermediate', description: '6+ months experience' },
    { id: 'advanced', label: 'Advanced', description: '2+ years experience' },
  ];

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const equipmentOptions = [
    { id: 'none', label: 'No Equipment' },
    { id: 'dumbbells', label: 'Dumbbells' },
    { id: 'resistance', label: 'Resistance Bands' },
    { id: 'pullup', label: 'Pull-up Bar' },
    { id: 'bench', label: 'Bench' },
  ];

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGoalSelect = (goalId) => {
    setFormData({ ...formData, goal: goalId });
  };

  const handleExperienceSelect = (levelId) => {
    setFormData({ ...formData, experience_level: levelId });
  };

  const handleDayToggle = (day) => {
    const current = formData.available_days;
    const existingIndex = current.findIndex(d => d.day === day);
    
    if (existingIndex !== -1) {
      // Remove the day
      setFormData({ 
        ...formData, 
        available_days: current.filter((_, idx) => idx !== existingIndex) 
      });
    } else {
      // Add the day with default 30 minutes
      setFormData({ 
        ...formData, 
        available_days: [...current, { day, minutes: 30 }] 
      });
    }
  };

  const handleTimeChange = (day, minutes) => {
    const current = formData.available_days;
    const updatedDays = current.map(d => 
      d.day === day ? { ...d, minutes: parseInt(minutes) || 0 } : d
    );
    setFormData({ ...formData, available_days: updatedDays });
  };

  const isDaySelected = (day) => {
    return formData.available_days.some(d => d.day === day);
  };

  const getDayMinutes = (day) => {
    const dayData = formData.available_days.find(d => d.day === day);
    return dayData ? dayData.minutes : 30;
  };

  const handleEquipmentToggle = (equipmentId) => {
    const current = formData.equipment;
    if (current.includes(equipmentId)) {
      setFormData({ ...formData, equipment: current.filter(e => e !== equipmentId) });
    } else {
      setFormData({ ...formData, equipment: [...current, equipmentId] });
    }
  };

  const handleNext = () => {
    if (step === 1 && !formData.gender) {
      toast.error('Please select your gender');
      return;
    }
    if (step === 2 && (!formData.height || !formData.weight)) {
      toast.error('Please enter your height and weight');
      return;
    }
    if (step === 3 && !formData.goal) {
      toast.error('Please select a goal');
      return;
    }
    if (step === 5 && !formData.experience_level) {
      toast.error('Please select your experience level');
      return;
    }
    if (step === 6 && formData.available_days.length === 0) {
      toast.error('Please select at least one day');
      return;
    }
    if (step === 7) {
      // Validate duration
      const duration = parseInt(formData.plan_duration);
      if (!duration || duration < 1) {
        toast.error('Please enter a valid duration');
        return;
      }
      
      // Validate max limits
      const unit = formData.plan_duration_unit;
      if ((unit === 'weeks' && duration > 156) || 
          (unit === 'months' && duration > 36) || 
          (unit === 'years' && duration > 3)) {
        toast.error('Maximum plan duration is 3 years');
        return;
      }
    }
    
    if (step < 7) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleComplete = async () => {
    try {
      const updateData = {
        ...formData,
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
      };
      await axios.put(`${API}/user/profile`, updateData);
      
      // Generate AI-powered workout schedule (may take 5-10 seconds)
      toast.info('Creating your personalized AI workout plan... This may take a moment.');
      await axios.post(`${API}/schedule/generate`);
      
      toast.success('✨ Your personalized AI workout plan is ready!');
      navigate('/home');
    } catch (error) {
      console.error('Update error:', error);
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <div className="w-full max-w-lg animate-fadeIn">
        <div className="flex justify-end mb-4">
          <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
        </div>
        
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            {[1, 2, 3, 4, 5, 6, 7].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 mx-1 rounded-full transition-all ${
                  s <= step ? 'bg-[#D4AF37]' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-center" style={{ color: 'var(--text-secondary)' }}>Step {step} of 7</p>
        </div>

        <div className="rounded-3xl p-8 premium-shadow border" style={{ 
          backgroundColor: 'var(--card-bg)',
          borderColor: 'var(--border-color)',
          boxShadow: 'var(--shadow-md)'
        }}>
          {step === 1 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Welcome, {user?.name}!</h2>
              <p className="text-gray-600 mb-6">Let's personalize your fitness journey</p>
              
              <Label className="text-[#1A1A1A] mb-3 block text-lg font-medium">Select Gender</Label>
              <div className="grid grid-cols-3 gap-3">
                {['Male', 'Female', 'Other'].map((g) => (
                  <button
                    key={g}
                    onClick={() => setFormData({ ...formData, gender: g })}
                    data-testid={`gender-${g.toLowerCase()}-button`}
                    className={`p-4 rounded-2xl border-2 font-medium transition-all ${
                      formData.gender === g
                        ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
                        : 'border-gray-200 text-gray-600 hover:border-[#D4AF37]/50'
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Your Stats</h2>
              <p className="text-gray-600 mb-6">Help us track your progress</p>
              
              <div className="space-y-5">
                <div>
                  <Label htmlFor="height" className="text-[#1A1A1A] mb-2 block font-medium">Height (cm)</Label>
                  <Input
                    id="height"
                    name="height"
                    type="number"
                    value={formData.height}
                    onChange={handleInputChange}
                    data-testid="height-input"
                    className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-12"
                    placeholder="170"
                  />
                </div>

                <div>
                  <Label htmlFor="weight" className="text-[#1A1A1A] mb-2 block font-medium">Weight (kg)</Label>
                  <Input
                    id="weight"
                    name="weight"
                    type="number"
                    value={formData.weight}
                    onChange={handleInputChange}
                    data-testid="weight-input"
                    className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-12"
                    placeholder="70"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Your Goal</h2>
              <p className="text-gray-600 mb-6">What do you want to achieve?</p>
              
              <div className="space-y-3">
                {goals.map((goal) => (
                  <button
                    key={goal.id}
                    onClick={() => handleGoalSelect(goal.id)}
                    data-testid={`goal-${goal.id}-button`}
                    className={`w-full p-5 rounded-2xl border-2 font-medium text-left transition-all flex items-center justify-between ${
                      formData.goal === goal.id
                        ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
                        : 'border-gray-200 text-[#1A1A1A] hover:border-[#D4AF37]/50'
                    }`}
                  >
                    <span className="flex items-center gap-3">
                      <span className="text-2xl">{goal.icon}</span>
                      <span className="text-lg">{goal.label}</span>
                    </span>
                    {formData.goal === goal.id && (
                      <div className="w-6 h-6 rounded-full bg-[#D4AF37] flex items-center justify-center">
                        <div className="w-3 h-3 bg-white rounded-full"></div>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Experience Level</h2>
              <p className="text-gray-600 mb-6">What's your workout experience?</p>
              
              <div className="space-y-3">
                {experienceLevels.map((level) => (
                  <button
                    key={level.id}
                    onClick={() => handleExperienceSelect(level.id)}
                    data-testid={`experience-${level.id}-button`}
                    className={`w-full p-5 rounded-2xl border-2 font-medium text-left transition-all ${
                      formData.experience_level === level.id
                        ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
                        : 'border-gray-200 text-[#1A1A1A] hover:border-[#D4AF37]/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-lg font-semibold">{level.label}</p>
                        <p className={`text-sm ${formData.experience_level === level.id ? 'text-[#D4AF37]' : 'text-gray-500'}`}>
                          {level.description}
                        </p>
                      </div>
                      {formData.experience_level === level.id && (
                        <div className="w-6 h-6 rounded-full bg-[#D4AF37] flex items-center justify-center">
                          <div className="w-3 h-3 bg-white rounded-full"></div>
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Available Days & Time</h2>
              <p className="text-gray-600 mb-6">Select days and set how much time you have each day</p>
              
              <div className="space-y-3">
                {daysOfWeek.map((day) => {
                  const isSelected = isDaySelected(day);
                  return (
                    <div key={day} className="space-y-2">
                      <button
                        onClick={() => handleDayToggle(day)}
                        data-testid={`day-${day.toLowerCase()}-button`}
                        className={`w-full p-4 rounded-2xl border-2 font-medium text-left transition-all flex items-center justify-between ${
                          isSelected
                            ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
                            : 'border-gray-200 text-[#1A1A1A] hover:border-[#D4AF37]/50'
                        }`}
                      >
                        {day}
                        {isSelected && (
                          <div className="w-6 h-6 rounded-full bg-[#D4AF37] flex items-center justify-center">
                            <div className="w-3 h-3 bg-white rounded-full"></div>
                          </div>
                        )}
                      </button>
                      
                      {isSelected && (
                        <div className="ml-4 animate-slideUp">
                          <Label className="text-[#1A1A1A] mb-2 block text-sm">Minutes available on {day}</Label>
                          <Input
                            type="number"
                            value={getDayMinutes(day)}
                            onChange={(e) => handleTimeChange(day, e.target.value)}
                            data-testid={`time-${day.toLowerCase()}-input`}
                            className="bg-gray-50 border-gray-200 text-[#1A1A1A] focus:border-[#D4AF37] focus:ring-[#D4AF37] rounded-xl h-10"
                            placeholder="30"
                            min="10"
                            max="120"
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              {formData.available_days.length > 0 && (
                <p className="mt-4 text-sm text-gray-600 text-center">
                  Selected {formData.available_days.length} day{formData.available_days.length > 1 ? 's' : ''} per week
                </p>
              )}
            </div>
          )}

          {step === 6 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Equipment</h2>
              <p className="text-gray-600 mb-6">What do you have access to?</p>
              
              <div className="space-y-3">
                {equipmentOptions.map((equipment) => (
                  <button
                    key={equipment.id}
                    onClick={() => handleEquipmentToggle(equipment.id)}
                    data-testid={`equipment-${equipment.id}-button`}
                    className={`w-full p-4 rounded-2xl border-2 font-medium text-left transition-all flex items-center justify-between ${
                      formData.equipment.includes(equipment.id)
                        ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
                        : 'border-gray-200 text-[#1A1A1A] hover:border-[#D4AF37]/50'
                    }`}
                  >
                    {equipment.label}
                    {formData.equipment.includes(equipment.id) && (
                      <div className="w-6 h-6 rounded-full bg-[#D4AF37] flex items-center justify-center">
                        <div className="w-3 h-3 bg-white rounded-full"></div>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          <Button
            onClick={handleNext}
            data-testid="onboarding-next-button"
            className="w-full mt-8 bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-semibold h-12 rounded-xl text-lg"
          >
            {step === 6 ? 'Generate My Schedule' : 'Continue'}
            <ChevronRight className="ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;

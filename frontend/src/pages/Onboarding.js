import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { ChevronRight } from 'lucide-react';

const Onboarding = ({ user }) => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    gender: '',
    height: '',
    weight: '',
    goal: '',
    equipment: [],
  });

  const goals = [
    { id: 'lean', label: 'Lean & Toned', icon: '⚡' },
    { id: 'strong', label: 'Strong & Defined', icon: '💪' },
    { id: 'bulk', label: 'Bulk & Build', icon: '🏋️' },
    { id: 'active', label: 'Just Stay Active', icon: '🏃' },
  ];

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
    
    if (step < 4) {
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
      toast.success('Profile setup complete!');
      navigate('/');
    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update profile');
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-lg animate-fadeIn">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 mx-1 rounded-full transition-all ${
                  s <= step ? 'bg-[#D4AF37]' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-gray-600 text-center">Step {step} of 4</p>
        </div>

        <div className="bg-white rounded-3xl p-8 premium-shadow border border-gray-100">
          {step === 1 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-white mb-2">Welcome, {user?.name}!</h2>
              <p className="text-[#B0B0B0] mb-6">Let's personalize your fitness journey</p>
              
              <Label className="text-white mb-3 block text-lg">Select Gender</Label>
              <div className="grid grid-cols-3 gap-3">
                {['Male', 'Female', 'Other'].map((g) => (
                  <button
                    key={g}
                    onClick={() => setFormData({ ...formData, gender: g })}
                    data-testid={`gender-${g.toLowerCase()}-button`}
                    className={`p-4 rounded-2xl border-2 font-medium transition-all ${
                      formData.gender === g
                        ? 'border-[#00FF88] bg-[#00FF88]/10 text-[#00FF88]'
                        : 'border-[#333] text-[#B0B0B0] hover:border-[#00FF88]/50'
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
              <h2 className="text-3xl font-bold text-white mb-2">Your Stats</h2>
              <p className="text-[#B0B0B0] mb-6">Help us track your progress</p>
              
              <div className="space-y-5">
                <div>
                  <Label htmlFor="height" className="text-white mb-2 block">Height (cm)</Label>
                  <Input
                    id="height"
                    name="height"
                    type="number"
                    value={formData.height}
                    onChange={handleInputChange}
                    data-testid="height-input"
                    className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] focus:ring-[#00FF88] rounded-xl h-12"
                    placeholder="170"
                  />
                </div>

                <div>
                  <Label htmlFor="weight" className="text-white mb-2 block">Weight (kg)</Label>
                  <Input
                    id="weight"
                    name="weight"
                    type="number"
                    value={formData.weight}
                    onChange={handleInputChange}
                    data-testid="weight-input"
                    className="bg-[#0D0D0D] border-[#333] text-white focus:border-[#00FF88] focus:ring-[#00FF88] rounded-xl h-12"
                    placeholder="70"
                  />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-white mb-2">Your Goal</h2>
              <p className="text-[#B0B0B0] mb-6">What do you want to achieve?</p>
              
              <div className="space-y-3">
                {goals.map((goal) => (
                  <button
                    key={goal.id}
                    onClick={() => handleGoalSelect(goal.id)}
                    data-testid={`goal-${goal.id}-button`}
                    className={`w-full p-5 rounded-2xl border-2 font-medium text-left transition-all flex items-center justify-between ${
                      formData.goal === goal.id
                        ? 'border-[#00FF88] bg-[#00FF88]/10 text-[#00FF88]'
                        : 'border-[#333] text-white hover:border-[#00FF88]/50'
                    }`}
                  >
                    <span className="flex items-center gap-3">
                      <span className="text-2xl">{goal.icon}</span>
                      <span className="text-lg">{goal.label}</span>
                    </span>
                    {formData.goal === goal.id && (
                      <div className="w-6 h-6 rounded-full bg-[#00FF88] flex items-center justify-center">
                        <div className="w-3 h-3 bg-[#0D0D0D] rounded-full"></div>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="animate-slideUp">
              <h2 className="text-3xl font-bold text-white mb-2">Equipment</h2>
              <p className="text-[#B0B0B0] mb-6">What do you have access to?</p>
              
              <div className="space-y-3">
                {equipmentOptions.map((equipment) => (
                  <button
                    key={equipment.id}
                    onClick={() => handleEquipmentToggle(equipment.id)}
                    data-testid={`equipment-${equipment.id}-button`}
                    className={`w-full p-4 rounded-2xl border-2 font-medium text-left transition-all flex items-center justify-between ${
                      formData.equipment.includes(equipment.id)
                        ? 'border-[#00FF88] bg-[#00FF88]/10 text-[#00FF88]'
                        : 'border-[#333] text-white hover:border-[#00FF88]/50'
                    }`}
                  >
                    {equipment.label}
                    {formData.equipment.includes(equipment.id) && (
                      <div className="w-6 h-6 rounded-full bg-[#00FF88] flex items-center justify-center">
                        <div className="w-3 h-3 bg-[#0D0D0D] rounded-full"></div>
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
            className="w-full mt-8 bg-[#00FF88] hover:bg-[#00dd77] text-[#0D0D0D] font-semibold h-12 rounded-xl text-lg"
          >
            {step === 4 ? 'Start Your Journey' : 'Continue'}
            <ChevronRight className="ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Play, Pause, ArrowLeft, Check } from 'lucide-react';
import * as LucideIcons from 'lucide-react';

const WorkoutPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workout, setWorkout] = useState(null);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [restTimer, setRestTimer] = useState(0);
  const [completedExercises, setCompletedExercises] = useState([]);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    fetchWorkout();
  }, [id]);

  useEffect(() => {
    let interval;
    if (isResting && restTimer > 0) {
      interval = setInterval(() => {
        setRestTimer((prev) => {
          if (prev <= 1) {
            setIsResting(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isResting, restTimer]);

  // Handle automatic exercise transition after rest
  useEffect(() => {
    if (!isResting && restTimer === 0 && completedExercises.length > 0 && currentExercise < workout?.exercises.length - 1) {
      const lastCompleted = completedExercises[completedExercises.length - 1];
      if (lastCompleted === currentExercise) {
        setCurrentExercise(currentExercise + 1);
      }
    }
  }, [isResting, restTimer, completedExercises, currentExercise, workout]);

  const fetchWorkout = async () => {
    try {
      const response = await axios.get(`${API}/workouts/plans`);
      const found = response.data.find((w) => w.id === id);
      if (found) {
        setWorkout(found);
      } else {
        toast.error('Workout not found');
        navigate('/home');
      }
    } catch (error) {
      console.error('Fetch error:', error);
      toast.error('Failed to load workout');
      navigate('/home');
    }
  };

  const handleCompleteExercise = () => {
    const exercise = workout.exercises[currentExercise];
    
    if (!completedExercises.includes(currentExercise)) {
      setCompletedExercises([...completedExercises, currentExercise]);
    }

    if (currentExercise < workout.exercises.length - 1) {
      // Start rest timer
      setRestTimer(exercise.rest_seconds);
      setIsResting(true);
    } else {
      // All exercises completed
      handleCompleteWorkout();
    }
  };

  const handleCompleteWorkout = async () => {
    const durationMinutes = Math.round((Date.now() - startTime) / 60000);
    
    try {
      const response = await axios.post(`${API}/workouts/complete`, {
        workout_plan_id: workout.id,
        duration_minutes: durationMinutes,
      });
      
      navigate('/workout/complete', { 
        state: { 
          result: response.data,
          workoutName: workout.name 
        } 
      });
    } catch (error) {
      console.error('Complete error:', error);
      toast.error('Failed to complete workout');
    }
  };

  const getIcon = (iconName) => {
    const IconComponent = LucideIcons[iconName.split('-').map((word, i) => 
      i === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1)
    ).join('').replace(/^(.)/, (match) => match.toUpperCase())];
    
    return IconComponent || LucideIcons.Circle;
  };

  if (!workout) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-[#1A1A1A] text-xl">Loading workout...</div>
      </div>
    );
  }

  const exercise = workout.exercises[currentExercise];
  const Icon = getIcon(exercise.icon);
  const progressPercent = ((currentExercise + 1) / workout.exercises.length) * 100;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 p-6 sticky top-0 z-10 premium-shadow">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/home')}
            data-testid="workout-back-button"
            className="flex items-center gap-2 text-gray-600 hover:text-[#1A1A1A] transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Journey</span>
          </button>
          
          <h1 className="text-2xl font-bold text-[#1A1A1A] mb-2">{workout.name}</h1>
          
          {/* Progress Bar */}
          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#D4AF37] to-[#c19b2e] rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className="text-gray-600 text-sm mt-2">
            Exercise {currentExercise + 1} of {workout.exercises.length}
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {isResting ? (
          <div className="animate-fadeIn text-center">
            <div className="bg-white rounded-3xl p-12 mb-6 premium-shadow border border-gray-100">
              <Pause className="w-16 h-16 text-[#D4AF37] mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-[#1A1A1A] mb-2">Rest Time</h2>
              <p className="text-gray-600 mb-6">Get ready for the next exercise</p>
              
              <div className="text-7xl font-bold text-[#D4AF37] mb-4">{restTimer}</div>
              <p className="text-gray-600">seconds</p>
            </div>
          </div>
        ) : (
          <div className="animate-fadeIn">
            {/* Exercise Card */}
            <div className="bg-white rounded-3xl p-8 mb-6 premium-shadow border border-gray-100">
              <div className="flex items-center justify-center w-20 h-20 bg-[#D4AF37]/10 rounded-full mx-auto mb-6">
                <Icon className="w-10 h-10 text-[#D4AF37]" />
              </div>
              
              <h2 className="text-3xl font-bold text-[#1A1A1A] text-center mb-4">{exercise.name}</h2>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-2xl p-4 text-center border border-gray-100">
                  <p className="text-gray-600 text-sm mb-1">Reps</p>
                  <p className="text-2xl font-bold text-[#1A1A1A]">{exercise.reps}</p>
                </div>
                
                <div className="bg-gray-50 rounded-2xl p-4 text-center border border-gray-100">
                  <p className="text-gray-600 text-sm mb-1">Sets</p>
                  <p className="text-2xl font-bold text-[#1A1A1A]">{exercise.sets}</p>
                </div>
              </div>

              <div className="bg-[#D4AF37]/10 border-2 border-[#D4AF37] rounded-2xl p-4 text-center">
                <p className="text-[#D4AF37] font-semibold">Rest: {exercise.rest_seconds}s after completion</p>
              </div>
            </div>

            {/* Complete Button */}
            <Button
              onClick={handleCompleteExercise}
              data-testid="complete-exercise-button"
              className="w-full bg-[#D4AF37] hover:bg-[#c19b2e] text-white font-bold h-14 rounded-xl text-lg"
            >
              {currentExercise < workout.exercises.length - 1 ? (
                <>
                  <Check className="mr-2" />
                  Complete Exercise
                </>
              ) : (
                <>
                  <Check className="mr-2" />
                  Finish Workout
                </>
              )}
            </Button>

            {/* Exercise List */}
            <div className="mt-8">
              <h3 className="text-xl font-bold text-[#1A1A1A] mb-4">All Exercises</h3>
              <div className="space-y-3">
                {workout.exercises.map((ex, idx) => {
                  const ExIcon = getIcon(ex.icon);
                  return (
                    <div
                      key={idx}
                      className={`flex items-center gap-4 p-4 rounded-2xl transition-all border ${
                        idx === currentExercise
                          ? 'bg-[#D4AF37]/10 border-[#D4AF37]'
                          : completedExercises.includes(idx)
                          ? 'bg-gray-50 opacity-60 border-gray-100'
                          : 'bg-white border-gray-100'
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        completedExercises.includes(idx) ? 'bg-[#D4AF37]' : 'bg-gray-200'
                      }`}>
                        {completedExercises.includes(idx) ? (
                          <Check className="w-5 h-5 text-white" />
                        ) : (
                          <ExIcon className={`w-5 h-5 ${idx === currentExercise ? 'text-[#D4AF37]' : 'text-gray-400'}`} />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <p className="text-[#1A1A1A] font-semibold">{ex.name}</p>
                        <p className="text-gray-600 text-sm">{ex.reps} × {ex.sets} sets</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkoutPage;
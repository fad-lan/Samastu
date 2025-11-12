import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API } from '@/App';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Play, Pause, ArrowLeft, Check } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const WorkoutPage = ({ theme, onToggleTheme }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workout, setWorkout] = useState(null);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [restTimer, setRestTimer] = useState(0);
  const [completedExercises, setCompletedExercises] = useState([]);
  const [startTime] = useState(Date.now());

  // Fetch workout when page loads
  useEffect(() => {
    const fetchWorkout = async () => {
      try {
        const response = await axios.get(`${API}/workouts/plans`);
        const found = response.data.find((w) => String(w.id) === String(id));
        if (found) {
          setWorkout({ ...found, exercises: found.exercises || [] });
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
    fetchWorkout();
  }, [id, navigate]);

  // Rest timer
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

  // Auto move to next exercise after rest
  useEffect(() => {
    if (
      !isResting &&
      restTimer === 0 &&
      completedExercises.length > 0 &&
      currentExercise < workout?.exercises.length - 1
    ) {
      const lastCompleted = completedExercises[completedExercises.length - 1];
      if (lastCompleted === currentExercise) {
        setCurrentExercise(currentExercise + 1);
      }
    }
  }, [isResting, restTimer, completedExercises, currentExercise, workout]);

  const handleCompleteExercise = () => {
    const exercise = workout.exercises[currentExercise];

    if (!completedExercises.includes(currentExercise)) {
      setCompletedExercises([...completedExercises, currentExercise]);
    }

    if (currentExercise < workout.exercises.length - 1) {
      const restTime = exercise.rest_seconds || 30;
      setRestTimer(restTime);
      setIsResting(true);
    } else {
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
          workoutName: workout.name,
        },
      });
    } catch (error) {
      console.error('Complete error:', error);
      toast.error('Failed to complete workout');
    }
  };

  const getIcon = (iconName) => {
    const IconComponent =
      LucideIcons[
        iconName
          .split('-')
          .map((word, i) =>
            i === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1)
          )
          .join('')
          .replace(/^(.)/, (match) => match.toUpperCase())
      ];
    return IconComponent || LucideIcons.Circle;
  };

  if (!workout) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg-primary)' }}
      >
        <div style={{ color: 'var(--text-primary)' }} className="text-xl">
          Loading workout...
        </div>
      </div>
    );
  }

  const exercise = workout.exercises[currentExercise];
  const Icon = getIcon(exercise.icon);
  const progressPercent = ((currentExercise + 1) / workout.exercises.length) * 100;

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Header */}
      <div
        className="border-b p-6 sticky top-0 z-10 premium-shadow"
        style={{
          backgroundColor: 'var(--card-bg)',
          borderColor: 'var(--border-color)',
        }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/home')}
              data-testid="workout-back-button"
              className="flex items-center gap-2 transition-colors"
              style={{ color: 'var(--text-secondary)' }}
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Journey</span>
            </button>
            <ThemeToggle theme={theme} onToggleTheme={onToggleTheme} />
          </div>

          <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
            {workout.name.replace('Week', 'Day')}
          </h1>

          {/* Progress Bar */}
          <div
            className="w-full h-2 rounded-full overflow-hidden"
            style={{ backgroundColor: 'var(--border-color)' }}
          >
            <div
              className="h-full bg-gradient-to-r from-[#D4AF37] to-[#c19b2e] rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
            Exercise {currentExercise + 1} of {workout.exercises.length}
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {isResting ? (
          <div className="animate-fadeIn text-center">
            <div
              className="rounded-3xl p-12 mb-6 premium-shadow border"
              style={{
                backgroundColor: 'var(--card-bg)',
                borderColor: 'var(--border-color)',
              }}
            >
              <Pause className="w-16 h-16 text-[#D4AF37] mx-auto mb-4" />
              <h2 className="text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                Rest Time
              </h2>
              <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
                Get ready for the next exercise
              </p>

              <div className="text-7xl font-bold text-[#D4AF37] mb-4">{restTimer}</div>
              <p style={{ color: 'var(--text-secondary)' }}>seconds</p>
            </div>
          </div>
        ) : (
          <div className="animate-fadeIn">
            {/* Current Exercise Card */}
            <div
              className="rounded-3xl p-8 mb-6 premium-shadow border"
              style={{
                backgroundColor: 'var(--card-bg)',
                borderColor: 'var(--border-color)',
              }}
            >
              <div className="flex items-center justify-center w-20 h-20 bg-[#D4AF37]/10 rounded-full mx-auto mb-6">
                <Icon className="w-10 h-10 text-[#D4AF37]" />
              </div>

              <h2 className="text-3xl font-bold text-center mb-4" style={{ color: 'var(--text-primary)' }}>
                {exercise.name}
              </h2>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div
                  className="rounded-2xl p-4 text-center border"
                  style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}
                >
                  <p className="text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>
                    Reps
                  </p>
                  <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                    {exercise.reps}
                  </p>
                </div>
                <div
                  className="rounded-2xl p-4 text-center border"
                  style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}
                >
                  <p className="text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>
                    Sets
                  </p>
                  <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                    {exercise.sets}
                  </p>
                </div>
              </div>

              <div className="bg-[#D4AF37]/10 border-2 border-[#D4AF37] rounded-2xl p-4 text-center">
                <p className="text-[#D4AF37] font-semibold">
                  Rest: {exercise.rest_seconds || 30}s after completion
                </p>
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

            {/* All Exercises List */}
            <div className="mt-8">
              <h3 className="text-xl font-bold mb-4">All Exercises</h3>
              <div className="space-y-3">
                {workout.exercises.map((ex, idx) => {
                  const ExIcon = getIcon(ex.icon);

                  return (
                    <div
                      key={idx}
                      className={`flex items-center gap-4 p-4 rounded-2xl transition-all border ${
                        idx === currentExercise
                          ? 'bg-[#fcf7eb] border-4 border-[#D4AF37]'
                          : completedExercises.includes(idx)
                          ? 'bg-gray-50 opacity-60 border-gray-100'
                          : 'bg-white border-gray-100'
                      }`}
                    >
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          completedExercises.includes(idx) ? 'bg-[#D4AF37]' : 'bg-gray-200'
                        }`}
                      >
                        {completedExercises.includes(idx) ? (
                          <Check className="w-5 h-5 text-white" />
                        ) : (
                          <ExIcon
                            className={`w-5 h-5 ${
                              idx === currentExercise ? 'text-[#D4AF37]' : 'text-gray-400'
                            }`}
                          />
                        )}
                      </div>

                      <div className="flex-1">
                        <p className="text-[#1A1A1A] font-semibold">{ex.name}</p>
                        <p className="text-gray-600 text-sm">
                          {ex.reps} × {ex.sets} sets
                        </p>
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

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Dumbbell, Coffee, CheckCircle } from 'lucide-react';

const WorkoutCalendar = ({ schedule }) => {
  const navigate = useNavigate();

  // Group by week
  const groupByWeek = (items) => {
    const weeks = {};
    items.forEach(item => {
      const date = new Date(item.scheduled_date);
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay()); // Start of week (Sunday)
      const weekKey = weekStart.toISOString().split('T')[0];
      
      if (!weeks[weekKey]) {
        weeks[weekKey] = [];
      }
      weeks[weekKey].push(item);
    });
    return weeks;
  };

  const weeks = schedule ? groupByWeek(schedule) : {};
  const weekKeys = Object.keys(weeks).sort();

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const handleWorkoutClick = (item) => {
    if (item.is_rest_day) {
      return; // Can't click on rest days
    }
    if (!item.is_completed) {
      navigate(`/workout/${item.workout_plan_id}`);
    }
  };

  const isToday = (dateStr) => {
    const today = new Date().toISOString().split('T')[0];
    return dateStr === today;
  };

  const isPast = (dateStr) => {
    const today = new Date().toISOString().split('T')[0];
    return dateStr < today;
  };

  return (
    <div className="space-y-6">
      {weekKeys.slice(0, 4).map((weekKey, weekIdx) => (
        <div key={weekKey} className="bg-white rounded-2xl p-6 premium-shadow border border-gray-100">
          <h3 className="text-lg font-bold text-[#1A1A1A] mb-4">
            Week {weekIdx + 1} - Starting {formatDate(weekKey)}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-7 gap-3">
            {weeks[weekKey].map((item, idx) => {
              const details = item.workout_details;
              const today = isToday(item.scheduled_date);
              const past = isPast(item.scheduled_date);
              
              return (
                <div
                  key={idx}
                  onClick={() => handleWorkoutClick(item)}
                  data-testid={`calendar-item-${item.id}`}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    item.is_rest_day
                      ? 'border-gray-200 bg-gray-50 cursor-default'
                      : item.is_completed
                      ? 'border-[#D4AF37] bg-[#D4AF37]/10 cursor-default'
                      : today
                      ? 'border-[#D4AF37] bg-[#D4AF37]/5 cursor-pointer hover:bg-[#D4AF37]/15 gold-border'
                      : past && !item.is_completed
                      ? 'border-red-300 bg-red-50 cursor-pointer hover:bg-red-100'
                      : 'border-gray-200 bg-white cursor-pointer hover:border-[#D4AF37]/50 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-xs font-semibold text-gray-500 uppercase">
                      {item.day_of_week.substring(0, 3)}
                    </p>
                    {item.is_rest_day ? (
                      <Coffee className="w-5 h-5 text-gray-400" />
                    ) : item.is_completed ? (
                      <CheckCircle className="w-5 h-5 text-[#D4AF37]" />
                    ) : (
                      <Dumbbell className={`w-5 h-5 ${today ? 'text-[#D4AF37]' : 'text-gray-400'}`} />
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-500 mb-1">{formatDate(item.scheduled_date)}</p>
                  
                  {details && (
                    <>
                      <p className={`font-semibold text-sm mb-1 ${
                        item.is_rest_day ? 'text-gray-600' : today ? 'text-[#D4AF37]' : 'text-[#1A1A1A]'
                      }`}>
                        {details.name}
                      </p>
                      {!item.is_rest_day && (
                        <p className="text-xs text-gray-500">
                          {details.duration_minutes} min • {details.difficulty}
                        </p>
                      )}
                    </>
                  )}
                  
                  {today && !item.is_completed && !item.is_rest_day && (
                    <div className="mt-2 text-xs font-semibold text-[#D4AF37]">Today's Workout</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default WorkoutCalendar;

#!/usr/bin/env python3

from datetime import date, timedelta

def debug_schedule_generation(available_days, total_weeks=2):
    """Debug the schedule generation logic"""
    print(f"Available days: {available_days}")
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    available_day_names = available_days
    
    # Smart rest day logic - check if user has consecutive workout days
    day_indices = {day: days_of_week.index(day) for day in available_day_names}
    sorted_indices = sorted(day_indices.values())
    
    # Check for consecutive days - find max consecutive count
    has_consecutive = False
    max_consecutive_count = 1
    current_consecutive = 1
    
    for i in range(1, len(sorted_indices)):
        if sorted_indices[i] == sorted_indices[i-1] + 1:
            current_consecutive += 1
            has_consecutive = True
            max_consecutive_count = max(max_consecutive_count, current_consecutive)
        else:
            current_consecutive = 1
    
    # Only add rest days if user has 2+ consecutive workout days
    should_add_rest_days = has_consecutive and max_consecutive_count >= 2
    # Set rest frequency based on max consecutive count to ensure rest days are added within consecutive pairs
    rest_frequency = max_consecutive_count if max_consecutive_count >= 2 else 2
    
    print(f"Algorithm results:")
    print(f"  has_consecutive: {has_consecutive}")
    print(f"  max_consecutive_count: {max_consecutive_count}")
    print(f"  should_add_rest_days: {should_add_rest_days}")
    print(f"  rest_frequency: {rest_frequency}")
    
    # Simulate schedule generation
    today = date.today()
    days_until_monday = (today.weekday() - 0) % 7
    if days_until_monday > 0:
        start_date = today - timedelta(days=days_until_monday)
    else:
        start_date = today
    
    print(f"\nSchedule generation simulation:")
    print(f"  start_date: {start_date}")
    
    schedule = []
    workout_index = 0
    consecutive_workout_count = 0
    
    for week in range(total_weeks):
        print(f"\n  Week {week + 1}:")
        for day_offset in range(7):
            schedule_date = start_date + timedelta(days=week * 7 + day_offset)
            day_name = days_of_week[schedule_date.weekday()]
            
            # Check if user is available on this day
            if day_name in available_day_names:
                # Check if it should be a rest day
                is_rest = should_add_rest_days and (consecutive_workout_count > 0 and consecutive_workout_count % rest_frequency == 0)
                
                if is_rest:
                    print(f"    {schedule_date} ({day_name}): REST DAY (after {consecutive_workout_count} consecutive workouts)")
                    schedule.append({
                        'date': schedule_date,
                        'day': day_name,
                        'type': 'rest',
                        'consecutive_count': consecutive_workout_count
                    })
                    consecutive_workout_count = 0  # Reset counter after rest
                else:
                    print(f"    {schedule_date} ({day_name}): WORKOUT (consecutive_count: {consecutive_workout_count + 1})")
                    schedule.append({
                        'date': schedule_date,
                        'day': day_name,
                        'type': 'workout',
                        'consecutive_count': consecutive_workout_count + 1
                    })
                    workout_index += 1
                    consecutive_workout_count += 1  # Increment consecutive counter
            else:
                # Day not available for user - natural rest day, reset consecutive counter
                print(f"    {schedule_date} ({day_name}): NATURAL GAP (resetting consecutive_count)")
                consecutive_workout_count = 0
    
    print(f"\nFinal schedule summary:")
    workouts = [item for item in schedule if item['type'] == 'workout']
    rest_days = [item for item in schedule if item['type'] == 'rest']
    print(f"  Total workouts: {len(workouts)}")
    print(f"  Total rest days: {len(rest_days)}")
    
    return schedule

# Test the problematic case
print("=" * 80)
print("DEBUGGING MON/TUE/THU/FRI SCHEDULE GENERATION")
print("=" * 80)

schedule = debug_schedule_generation(["Monday", "Tuesday", "Thursday", "Friday"])
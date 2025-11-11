#!/usr/bin/env python3

def debug_consecutive_logic(available_days):
    """Debug the consecutive day detection logic"""
    print(f"Available days: {available_days}")
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create day indices
    day_indices = {day: days_of_week.index(day) for day in available_days}
    print(f"Day indices: {day_indices}")
    
    sorted_indices = sorted(day_indices.values())
    print(f"Sorted indices: {sorted_indices}")
    
    # Check for consecutive days - find max consecutive count
    has_consecutive = False
    max_consecutive_count = 1
    current_consecutive = 1
    
    print(f"\nAnalyzing consecutive patterns:")
    for i in range(1, len(sorted_indices)):
        prev_idx = sorted_indices[i-1]
        curr_idx = sorted_indices[i]
        
        if curr_idx == prev_idx + 1:
            current_consecutive += 1
            has_consecutive = True
            max_consecutive_count = max(max_consecutive_count, current_consecutive)
            print(f"  {days_of_week[prev_idx]} -> {days_of_week[curr_idx]}: consecutive! current_consecutive={current_consecutive}")
        else:
            print(f"  {days_of_week[prev_idx]} -> {days_of_week[curr_idx]}: gap, resetting current_consecutive to 1")
            current_consecutive = 1
    
    print(f"\nResults:")
    print(f"  has_consecutive: {has_consecutive}")
    print(f"  max_consecutive_count: {max_consecutive_count}")
    
    should_add_rest_days = has_consecutive and max_consecutive_count >= 2
    print(f"  should_add_rest_days: {should_add_rest_days}")
    
    return should_add_rest_days, max_consecutive_count

# Test cases
print("=" * 60)
print("TESTING CONSECUTIVE DAY DETECTION LOGIC")
print("=" * 60)

test_cases = [
    ["Monday", "Tuesday", "Wednesday"],  # 3 consecutive
    ["Monday", "Tuesday", "Thursday", "Friday"],  # Two pairs: Mon-Tue, Thu-Fri
    ["Monday", "Wednesday", "Friday"],  # No consecutive
    ["Monday", "Tuesday"],  # 2 consecutive
    ["Thursday", "Friday", "Saturday"],  # 3 consecutive
]

for i, days in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    print("-" * 40)
    should_add, max_count = debug_consecutive_logic(days)
    print(f"Expected behavior: {'Add rest days' if should_add else 'No rest days'}")
    print()
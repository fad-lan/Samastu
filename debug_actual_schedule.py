import requests
import json
from datetime import datetime

def test_mon_tue_thu_fri():
    """Test the actual API to see what schedule is generated"""
    base_url = "https://fitgame-app-1.preview.emergentagent.com"
    
    # Create test user
    timestamp = datetime.now().strftime('%H%M%S')
    user_data = {
        "email": f"debug_test_{timestamp}@example.com",
        "password": "TestPass123!",
        "name": f"Debug Test User {timestamp}"
    }
    
    # Register
    response = requests.post(f"{base_url}/api/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Registration failed: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Set profile with Mon/Tue/Thu/Fri
    profile_data = {
        "experience_level": "intermediate",
        "goal": "muscle_building",
        "equipment": ["dumbbells"],
        "available_days": [
            {"day": "Monday", "minutes": 45},
            {"day": "Tuesday", "minutes": 45},
            {"day": "Thursday", "minutes": 45},
            {"day": "Friday", "minutes": 45}
        ],
        "plan_duration": 2,
        "plan_duration_unit": "weeks"
    }
    
    response = requests.put(f"{base_url}/api/user/profile", json=profile_data, headers=headers)
    if response.status_code != 200:
        print(f"Profile update failed: {response.status_code}")
        return
    
    # Generate schedule
    response = requests.post(f"{base_url}/api/schedule/generate", headers=headers, timeout=60)
    if response.status_code != 200:
        print(f"Schedule generation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print(f"Schedule generation response: {response.json()}")
    
    # Get schedule
    response = requests.get(f"{base_url}/api/schedule/calendar", headers=headers)
    if response.status_code != 200:
        print(f"Get schedule failed: {response.status_code}")
        return
    
    schedule = response.json()
    print(f"\nGenerated schedule ({len(schedule)} items):")
    
    for item in schedule:
        rest_indicator = "REST" if item.get('is_rest_day', False) else "WORKOUT"
        print(f"  {item['scheduled_date']} ({item['day_of_week']}): {rest_indicator}")
    
    # Analyze
    rest_days = [item for item in schedule if item.get('is_rest_day', False)]
    workout_days = [item for item in schedule if not item.get('is_rest_day', False)]
    
    print(f"\nAnalysis:")
    print(f"  Total items: {len(schedule)}")
    print(f"  Workout days: {len(workout_days)}")
    print(f"  Rest days: {len(rest_days)}")
    
    if len(rest_days) > 0:
        print(f"  Rest day dates: {[item['scheduled_date'] for item in rest_days]}")

if __name__ == "__main__":
    test_mon_tue_thu_fri()
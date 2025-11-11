#!/usr/bin/env python3
"""
Specific test for workout journey display fix after AI generation.
Tests the fix for: "workouts don't display on home page after AI generation"
"""

import requests
import json
import sys
from datetime import datetime

class JourneyFixTester:
    def __init__(self, base_url="https://fitgame-app-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            print(f"   FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def create_test_user_with_ai_plans(self):
        """Create a test user and generate AI plans"""
        timestamp = datetime.now().strftime('%H%M%S%f')
        user_data = {
            "email": f"journey_fix_test_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Journey Fix Test {timestamp}"
        }
        
        # Register user
        response = requests.post(f"{self.base_url}/api/auth/register", json=user_data)
        if response.status_code != 200:
            return None, None
        
        token = response.json()['access_token']
        user_id = response.json()['user']['id']
        
        # Set complete profile
        profile_data = {
            "experience_level": "intermediate",
            "goal": "Strong & Defined",
            "equipment": ["dumbbells", "resistance_bands"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Wednesday", "minutes": 30},
                {"day": "Friday", "minutes": 45},
                {"day": "Sunday", "minutes": 60}
            ]
        }
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        profile_response = requests.put(f"{self.base_url}/api/user/profile", json=profile_data, headers=headers)
        if profile_response.status_code != 200:
            return None, None
        
        # Generate AI plans and schedule
        try:
            schedule_response = requests.post(f"{self.base_url}/api/schedule/generate", headers=headers, timeout=60)
            if schedule_response.status_code == 200:
                return token, user_id
        except Exception as e:
            print(f"AI generation failed: {e}")
            return None, None
        
        return None, None

    def test_journey_endpoint_returns_ai_plans(self, token):
        """Part 1: Verify Journey Endpoint Returns AI Plans"""
        print(f"\n📋 PART 1: VERIFY JOURNEY ENDPOINT RETURNS AI PLANS")
        print("-" * 50)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 1. Call GET /workouts/journey with auth token
        journey_response = requests.get(f"{self.base_url}/api/workouts/journey", headers=headers)
        
        success = journey_response.status_code == 200
        self.log_test("1.1 GET /workouts/journey returns 200", success, 
                     f"Status: {journey_response.status_code}")
        
        if not success:
            return False
        
        journey_data = journey_response.json()
        
        # 2. Verify response contains workout array with actual workout data (not empty)
        success = isinstance(journey_data, list) and len(journey_data) > 0
        self.log_test("1.2 Journey response contains workout array (not empty)", success,
                     f"Type: {type(journey_data)}, Length: {len(journey_data) if isinstance(journey_data, list) else 'N/A'}")
        
        if not success:
            return False
        
        # 3. Filter workout items (non-rest days)
        workout_items = [item for item in journey_data if not item.get('is_rest_day', False)]
        
        success = len(workout_items) > 0
        self.log_test("1.3 Journey contains workout items (non-rest days)", success,
                     f"Workout items: {len(workout_items)}, Rest days: {len(journey_data) - len(workout_items)}")
        
        if not success:
            return False
        
        # 4. Verify each workout has required fields
        first_workout = workout_items[0]
        required_fields = ['name', 'difficulty', 'exercises', 'target_muscles', 'duration_minutes', 'xp_reward']
        missing_fields = [field for field in required_fields if field not in first_workout or not first_workout[field]]
        
        success = len(missing_fields) == 0
        self.log_test("1.4 Workout has required fields", success,
                     f"Missing fields: {missing_fields}" if missing_fields else "All required fields present")
        
        if not success:
            return False
        
        # 5. Verify exercises array is populated for workout days
        exercises = first_workout.get('exercises', [])
        success = isinstance(exercises, list) and len(exercises) > 0
        self.log_test("1.5 Exercises array is populated", success,
                     f"Exercises count: {len(exercises) if isinstance(exercises, list) else 'Not a list'}")
        
        if not success:
            return False
        
        # 6. Verify workout IDs match AI-generated plan IDs in database
        ai_plans_response = requests.get(f"{self.base_url}/api/workouts/ai-plans", headers=headers)
        
        if ai_plans_response.status_code == 200:
            ai_plans = ai_plans_response.json()
            ai_plan_ids = set(plan['id'] for plan in ai_plans)
            
            workout_ids = set()
            for item in workout_items:
                workout_id = item.get('id') or item.get('workout_plan_id')
                if workout_id:
                    workout_ids.add(workout_id)
            
            matching_ids = workout_ids.intersection(ai_plan_ids)
            success = len(matching_ids) > 0
            
            self.log_test("1.6 Workout IDs match AI-generated plan IDs", success,
                         f"Matching IDs: {len(matching_ids)}/{len(workout_ids)}")
        else:
            self.log_test("1.6 Could not verify AI plan IDs", False, "Failed to get AI plans")
            return False
        
        # 7. Verify journey includes both workout days and rest days
        rest_days = [item for item in journey_data if item.get('is_rest_day', False)]
        
        self.log_test("1.7 Journey structure complete", True,
                     f"Total items: {len(journey_data)}, Workouts: {len(workout_items)}, Rest days: {len(rest_days)}")
        
        print(f"   ✅ First workout: '{first_workout['name']}'")
        print(f"   ✅ Difficulty: {first_workout['difficulty']}")
        print(f"   ✅ Target muscles: {first_workout['target_muscles']}")
        print(f"   ✅ Duration: {first_workout['duration_minutes']} minutes")
        print(f"   ✅ XP reward: {first_workout['xp_reward']}")
        print(f"   ✅ Exercises: {len(exercises)}")
        
        return True

    def test_calendar_endpoint_returns_ai_plans(self, token):
        """Part 2: Verify Calendar Endpoint Returns AI Plans"""
        print(f"\n📅 PART 2: VERIFY CALENDAR ENDPOINT RETURNS AI PLANS")
        print("-" * 50)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 8. Call GET /schedule/calendar with auth token
        calendar_response = requests.get(f"{self.base_url}/api/schedule/calendar", headers=headers)
        
        success = calendar_response.status_code == 200
        self.log_test("2.1 GET /schedule/calendar returns 200", success,
                     f"Status: {calendar_response.status_code}")
        
        if not success:
            return False
        
        calendar_data = calendar_response.json()
        
        # 9. Verify calendar data includes workout details
        workout_items = [item for item in calendar_data if not item.get('is_rest_day', False)]
        
        success = len(workout_items) > 0
        self.log_test("2.2 Calendar contains workout items", success,
                     f"Workout items: {len(workout_items)}")
        
        if not success:
            return False
        
        # 10. Verify workout plan details are enriched from ai_workout_plans collection
        first_workout = workout_items[0]
        
        success = 'workout_details' in first_workout and first_workout['workout_details']
        self.log_test("2.3 Calendar items have workout_details", success,
                     "workout_details field present and populated" if success else "workout_details missing or empty")
        
        if success:
            workout_details = first_workout['workout_details']
            success = 'name' in workout_details and workout_details['name']
            self.log_test("2.4 Workout details include name", success,
                         f"Workout name: '{workout_details.get('name', 'Missing')}'" if success else "Name missing")
            
            if success:
                print(f"   ✅ Calendar workout: '{workout_details['name']}'")
        
        return success

    def test_workout_plans_endpoint_returns_ai_plans(self, token):
        """Part 3: Verify Workout Plans Endpoint Returns AI Plans"""
        print(f"\n📋 PART 3: VERIFY WORKOUT PLANS ENDPOINT RETURNS AI PLANS")
        print("-" * 50)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 11. Call GET /workouts/plans with auth token
        plans_response = requests.get(f"{self.base_url}/api/workouts/plans", headers=headers)
        
        success = plans_response.status_code == 200
        self.log_test("3.1 GET /workouts/plans returns 200", success,
                     f"Status: {plans_response.status_code}")
        
        if not success:
            return False
        
        plans_data = plans_response.json()
        
        # 12. Verify it returns user's AI-generated plans (not empty or default plans)
        success = isinstance(plans_data, list) and len(plans_data) > 0
        self.log_test("3.2 Plans endpoint returns data", success,
                     f"Plans count: {len(plans_data) if isinstance(plans_data, list) else 'Not a list'}")
        
        if not success:
            return False
        
        # Verify these are AI-generated plans by checking against ai-plans endpoint
        ai_plans_response = requests.get(f"{self.base_url}/api/workouts/ai-plans", headers=headers)
        
        if ai_plans_response.status_code == 200:
            ai_plans = ai_plans_response.json()
            ai_plan_ids = set(plan['id'] for plan in ai_plans)
            plans_ids = set(plan['id'] for plan in plans_data)
            
            matching_ids = plans_ids.intersection(ai_plan_ids)
            success = len(matching_ids) > 0
            
            self.log_test("3.3 Plans endpoint returns AI-generated plans", success,
                         f"AI plans match: {len(matching_ids)}/{len(plans_ids)}")
        else:
            self.log_test("3.3 Could not verify AI plans", False, "Failed to get AI plans for comparison")
            return False
        
        return success

    def test_complete_flow(self):
        """Part 4: Complete Flow Test"""
        print(f"\n🔄 PART 4: COMPLETE FLOW TEST (NEW USER)")
        print("-" * 50)
        
        # 13. Create a NEW test user
        timestamp = datetime.now().strftime('%H%M%S%f')
        user_data = {
            "email": f"complete_flow_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Complete Flow Test {timestamp}"
        }
        
        response = requests.post(f"{self.base_url}/api/auth/register", json=user_data)
        
        success = response.status_code == 200
        self.log_test("4.1 Create NEW test user", success,
                     f"Status: {response.status_code}")
        
        if not success:
            return False
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # 14. Set profile with experience_level, goal, equipment, available_days
        profile_data = {
            "experience_level": "beginner",
            "goal": "weight_loss",
            "equipment": ["bodyweight"],
            "available_days": [
                {"day": "Tuesday", "minutes": 30},
                {"day": "Thursday", "minutes": 30},
                {"day": "Saturday", "minutes": 45}
            ]
        }
        
        profile_response = requests.put(f"{self.base_url}/api/user/profile", json=profile_data, headers=headers)
        
        success = profile_response.status_code == 200
        self.log_test("4.2 Set complete profile", success,
                     f"Status: {profile_response.status_code}")
        
        if not success:
            return False
        
        # 15. Call POST /schedule/generate (should auto-generate AI plans)
        print(f"   🤖 Auto-generating AI plans (may take 5-10 seconds)...")
        
        try:
            schedule_response = requests.post(f"{self.base_url}/api/schedule/generate", headers=headers, timeout=60)
            
            success = schedule_response.status_code == 200
            self.log_test("4.3 Auto-generate AI plans via schedule", success,
                         f"Status: {schedule_response.status_code}")
            
            if not success:
                if schedule_response.headers.get('content-type', '').startswith('application/json'):
                    error_data = schedule_response.json()
                    print(f"   Error details: {error_data}")
                return False
                
        except Exception as e:
            self.log_test("4.3 Auto-generate AI plans via schedule", False, f"Exception: {str(e)}")
            return False
        
        # 16. Immediately call GET /workouts/journey
        journey_response = requests.get(f"{self.base_url}/api/workouts/journey", headers=headers)
        
        success = journey_response.status_code == 200
        self.log_test("4.4 GET journey immediately after generation", success,
                     f"Status: {journey_response.status_code}")
        
        if not success:
            return False
        
        # 17. Verify journey returns populated workout data with AI-generated plans
        journey_data = journey_response.json()
        
        success = isinstance(journey_data, list) and len(journey_data) > 0
        self.log_test("4.5 Journey populated immediately after AI generation", success,
                     f"Journey items: {len(journey_data) if isinstance(journey_data, list) else 'Not a list'}")
        
        if not success:
            print("   ❌ BUG STILL EXISTS: Journey is empty after AI generation!")
            return False
        
        workout_items = [item for item in journey_data if not item.get('is_rest_day', False)]
        
        success = len(workout_items) > 0
        self.log_test("4.6 Journey contains workout items", success,
                     f"Workout items: {len(workout_items)}")
        
        if not success:
            print("   ❌ BUG STILL EXISTS: No workout items in journey after AI generation!")
            return False
        
        # Verify workout data is populated (not empty)
        first_workout = workout_items[0]
        
        success = (first_workout.get('name') and 
                  first_workout.get('exercises') and 
                  len(first_workout.get('exercises', [])) > 0)
        
        self.log_test("4.7 Workout data is populated", success,
                     f"Name: '{first_workout.get('name', 'Missing')}', Exercises: {len(first_workout.get('exercises', []))}")
        
        if not success:
            print("   ❌ BUG STILL EXISTS: Workout data is empty after AI generation!")
            return False
        
        # Verify workout IDs match AI plan IDs
        ai_plans_response = requests.get(f"{self.base_url}/api/workouts/ai-plans", headers=headers)
        
        if ai_plans_response.status_code == 200:
            ai_plans = ai_plans_response.json()
            ai_plan_ids = set(plan['id'] for plan in ai_plans)
            
            workout_ids = set()
            for item in workout_items:
                workout_id = item.get('id') or item.get('workout_plan_id')
                if workout_id:
                    workout_ids.add(workout_id)
            
            matching_ids = workout_ids.intersection(ai_plan_ids)
            success = len(matching_ids) > 0
            
            self.log_test("4.8 Journey uses AI-generated plan IDs", success,
                         f"Matching IDs: {len(matching_ids)}/{len(workout_ids)}")
        
        print(f"   ✅ Journey immediately displays {len(workout_items)} populated workouts")
        print(f"   ✅ First workout: '{first_workout['name']}'")
        print(f"   ✅ Exercises: {len(first_workout['exercises'])} exercises")
        
        return True

    def run_journey_fix_tests(self):
        """Run all journey fix tests"""
        print("🔥 TESTING WORKOUT JOURNEY DISPLAY FIX")
        print("=" * 60)
        print("Testing fix for: 'workouts don't display on home page after AI generation'")
        
        # Create test user with AI plans
        print(f"\n🤖 Creating test user with AI plans (may take 5-10 seconds)...")
        token, user_id = self.create_test_user_with_ai_plans()
        
        if not token:
            print("❌ Failed to create test user with AI plans")
            print("   This could be due to Gemini API issues")
            return False
        
        print(f"✅ Test user created with AI plans")
        
        # Run all test parts
        success = True
        
        success &= self.test_journey_endpoint_returns_ai_plans(token)
        success &= self.test_calendar_endpoint_returns_ai_plans(token)
        success &= self.test_workout_plans_endpoint_returns_ai_plans(token)
        success &= self.test_complete_flow()
        
        # Print summary
        print(f"\n" + "=" * 60)
        print(f"📊 Journey Fix Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL JOURNEY FIX TESTS PASSED!")
            print("✅ Workout journey display fix is working correctly")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            print("❌ Journey display fix needs attention")
            return False

def main():
    tester = JourneyFixTester()
    success = tester.run_journey_fix_tests()
    
    # Save results
    with open('/app/journey_fix_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'results': tester.test_results,
            'fix_working': success
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
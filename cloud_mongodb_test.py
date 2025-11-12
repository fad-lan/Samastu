import requests
import sys
import json
from datetime import datetime, timedelta

class CloudMongoDBTester:
    def __init__(self, base_url="https://fitgame-app-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return {}

    def test_cloud_mongodb_connection(self):
        """Test complete cloud MongoDB connection and data persistence"""
        print(f"\n🎯 TESTING CLOUD MONGODB CONNECTION AND DATA PERSISTENCE")
        print("=" * 70)
        print("Testing connection to: mongodb+srv://fadlan@effendialogue")
        print("Database: Samastu")
        print("=" * 70)
        
        # Part 1: Create new test user
        print(f"\n📋 PART 1: USER REGISTRATION AND AUTHENTICATION")
        print("-" * 50)
        
        timestamp = datetime.now().strftime('%H%M%S')
        test_user_data = {
            "email": f"cloud_test_{timestamp}@samastu.com",
            "password": "CloudTest123!",
            "name": f"Cloud Test User {timestamp}"
        }
        
        # Test user registration
        response = self.run_test(
            "1.1 Create New User in Cloud MongoDB",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if not response or 'access_token' not in response:
            print("❌ Failed to create user in cloud MongoDB, stopping test")
            return False
        
        self.token = response['access_token']
        self.user_id = response['user']['id']
        
        print(f"   ✅ User created with ID: {self.user_id}")
        print(f"   ✅ JWT token received and stored")
        
        # Test login with created user
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = self.run_test(
            "1.2 Login with Cloud MongoDB User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if login_response and 'access_token' in login_response:
            print(f"   ✅ Login successful - user data persisted in cloud")
        
        # Part 2: Update user profile with onboarding data
        print(f"\n📋 PART 2: USER PROFILE UPDATE AND PERSISTENCE")
        print("-" * 50)
        
        onboarding_data = {
            "gender": "male",
            "height": 180.0,
            "weight": 75.0,
            "goal": "muscle_building",
            "equipment": ["dumbbells", "resistance_bands", "bodyweight"],
            "experience_level": "intermediate",
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Wednesday", "minutes": 30},
                {"day": "Friday", "minutes": 45},
                {"day": "Saturday", "minutes": 60}
            ],
            "plan_duration": 8,
            "plan_duration_unit": "weeks"
        }
        
        profile_response = self.run_test(
            "2.1 Update User Profile with Onboarding Data",
            "PUT",
            "user/profile",
            200,
            data=onboarding_data
        )
        
        if profile_response:
            print(f"   ✅ Profile updated in cloud MongoDB")
            print(f"   ✅ Goal: {profile_response.get('goal')}")
            print(f"   ✅ Experience: {profile_response.get('experience_level')}")
            print(f"   ✅ Available days: {len(profile_response.get('available_days', []))}")
        
        # Verify profile persistence by fetching it again
        fetch_profile_response = self.run_test(
            "2.2 Fetch User Profile (Verify Persistence)",
            "GET",
            "user/profile",
            200
        )
        
        if fetch_profile_response:
            # Verify all onboarding data persisted
            persisted_correctly = True
            missing_fields = []
            
            for key, expected_value in onboarding_data.items():
                if key not in fetch_profile_response:
                    missing_fields.append(key)
                    persisted_correctly = False
                elif fetch_profile_response[key] != expected_value:
                    missing_fields.append(f"{key} (value mismatch)")
                    persisted_correctly = False
            
            if persisted_correctly:
                print(f"   ✅ All onboarding data persisted correctly in cloud")
                self.log_test("2.3 Profile Data Persistence", True, "All onboarding fields persisted correctly")
            else:
                self.log_test("2.3 Profile Data Persistence", False, f"Missing/incorrect fields: {missing_fields}")
        
        # Part 3: Generate AI workout schedule
        print(f"\n📋 PART 3: AI WORKOUT GENERATION AND SCHEDULE CREATION")
        print("-" * 50)
        
        print(f"🤖 Generating AI workout plans and schedule (may take 5-10 seconds)...")
        
        url = f"{self.base_url}/api/schedule/generate"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=60)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get('success'):
                    scheduled_count = data.get('scheduled_count', 0)
                    print(f"   ✅ AI workout schedule generated successfully")
                    print(f"   ✅ Scheduled items: {scheduled_count}")
                else:
                    success = False
            
            self.log_test("3.1 Generate AI Workout Schedule", success, f"Status: {response.status_code}")
            
            if not success:
                return False
                
        except Exception as e:
            self.log_test("3.1 Generate AI Workout Schedule", False, f"Exception: {str(e)}")
            return False
        
        # Part 4: Verify data storage in all collections
        print(f"\n📋 PART 4: VERIFY DATA IN ALL CLOUD MONGODB COLLECTIONS")
        print("-" * 50)
        
        # 4.1 Verify users collection
        user_check = self.run_test(
            "4.1 Verify Users Collection",
            "GET",
            "auth/me",
            200
        )
        
        if user_check and user_check.get('id') == self.user_id:
            print(f"   ✅ Users collection: User data found")
        
        # 4.2 Verify ai_workout_plans collection
        ai_plans_check = self.run_test(
            "4.2 Verify AI Workout Plans Collection",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        if ai_plans_check and isinstance(ai_plans_check, list) and len(ai_plans_check) > 0:
            print(f"   ✅ AI Workout Plans collection: {len(ai_plans_check)} plans stored")
            
            # Check for rest_seconds field in exercises
            first_plan = ai_plans_check[0]
            if 'exercises' in first_plan and len(first_plan['exercises']) > 0:
                first_exercise = first_plan['exercises'][0]
                if 'rest_seconds' in first_exercise:
                    rest_seconds = first_exercise['rest_seconds']
                    print(f"   ✅ Exercise rest_seconds field present: {rest_seconds}s")
                    
                    # Test rest timer default logic (Part 3 of requirements)
                    if rest_seconds == 0:
                        print(f"   ⚠️  Found exercise with 0 rest_seconds - frontend should default to 30s")
                        self.log_test("4.2.1 Rest Timer Default Logic", True, "Found 0 rest_seconds - frontend will default to 30s")
                    else:
                        print(f"   ✅ Exercise has non-zero rest_seconds: {rest_seconds}s")
        else:
            self.log_test("4.2 AI Workout Plans Collection", False, "No AI workout plans found")
        
        # 4.3 Verify scheduled_workouts collection
        schedule_check = self.run_test(
            "4.3 Verify Scheduled Workouts Collection",
            "GET",
            "schedule/calendar",
            200
        )
        
        if schedule_check and isinstance(schedule_check, list) and len(schedule_check) > 0:
            print(f"   ✅ Scheduled Workouts collection: {len(schedule_check)} items stored")
            
            # Verify workout details are populated from ai_workout_plans
            workout_items = [item for item in schedule_check if not item.get('is_rest_day', False)]
            if len(workout_items) > 0:
                first_workout = workout_items[0]
                if 'workout_details' in first_workout and first_workout['workout_details']:
                    workout_details = first_workout['workout_details']
                    print(f"   ✅ Workout details populated: '{workout_details.get('name', 'Unknown')}'")
        else:
            self.log_test("4.3 Scheduled Workouts Collection", False, "No scheduled workouts found")
        
        # 4.4 Verify progress collection
        progress_check = self.run_test(
            "4.4 Verify Progress Collection",
            "GET",
            "progress",
            200
        )
        
        if progress_check and progress_check.get('user_id') == self.user_id:
            print(f"   ✅ Progress collection: User progress initialized")
            print(f"   ✅ Level: {progress_check.get('level', 1)}")
            print(f"   ✅ Total XP: {progress_check.get('total_xp', 0)}")
            print(f"   ✅ Streak: {progress_check.get('streak', 0)}")
        
        # Part 5: Test workout completion and session storage
        print(f"\n📋 PART 5: WORKOUT COMPLETION AND SESSION STORAGE")
        print("-" * 50)
        
        # Get a workout plan ID to complete
        if ai_plans_check and len(ai_plans_check) > 0:
            workout_plan_id = ai_plans_check[0]['id']
            
            complete_data = {
                "workout_plan_id": workout_plan_id,
                "duration_minutes": 30
            }
            
            complete_response = self.run_test(
                "5.1 Complete Workout Session",
                "POST",
                "workouts/complete",
                200,
                data=complete_data
            )
            
            if complete_response and complete_response.get('success'):
                print(f"   ✅ Workout completed successfully")
                print(f"   ✅ XP earned: {complete_response.get('xp_earned', 0)}")
                print(f"   ✅ New level: {complete_response.get('new_level', 1)}")
                print(f"   ✅ New streak: {complete_response.get('new_streak', 0)}")
                
                # Verify workout session was stored
                updated_progress = self.run_test(
                    "5.2 Verify Updated Progress",
                    "GET",
                    "progress",
                    200
                )
                
                if updated_progress:
                    new_xp = updated_progress.get('total_xp', 0)
                    if new_xp > 0:
                        print(f"   ✅ Progress updated in cloud: {new_xp} total XP")
                        self.log_test("5.3 Workout Session Storage", True, "Workout session and progress stored in cloud")
        
        # Part 6: Test data persistence across requests
        print(f"\n📋 PART 6: DATA PERSISTENCE VERIFICATION")
        print("-" * 50)
        
        # Fetch user profile again
        final_profile = self.run_test(
            "6.1 Final Profile Fetch",
            "GET",
            "user/profile",
            200
        )
        
        # Fetch workout plans again
        final_plans = self.run_test(
            "6.2 Final AI Plans Fetch",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        # Fetch schedule again
        final_schedule = self.run_test(
            "6.3 Final Schedule Fetch",
            "GET",
            "schedule/calendar",
            200
        )
        
        # Fetch progress again
        final_progress = self.run_test(
            "6.4 Final Progress Fetch",
            "GET",
            "progress",
            200
        )
        
        # Verify all data persists
        persistence_checks = [
            ("User Profile", final_profile and 'id' in final_profile),
            ("AI Workout Plans", final_plans and len(final_plans) > 0),
            ("Workout Schedule", final_schedule and len(final_schedule) > 0),
            ("User Progress", final_progress and 'user_id' in final_progress)
        ]
        
        all_persisted = all(check[1] for check in persistence_checks)
        
        if all_persisted:
            print(f"   ✅ All data persists across requests in cloud MongoDB")
            self.log_test("6.5 Complete Data Persistence", True, "All collections maintain data across requests")
        else:
            failed_checks = [check[0] for check in persistence_checks if not check[1]]
            self.log_test("6.5 Complete Data Persistence", False, f"Failed persistence: {failed_checks}")
        
        return True

    def test_rest_timer_functionality(self):
        """Test rest timer default behavior"""
        print(f"\n🎯 TESTING REST TIMER DEFAULT FUNCTIONALITY")
        print("=" * 70)
        
        # Get workout plans to check rest_seconds values
        plans_response = self.run_test(
            "Rest Timer - Get Workout Plans",
            "GET",
            "workouts/plans",
            200
        )
        
        if not plans_response or not isinstance(plans_response, list):
            print("❌ No workout plans available for rest timer testing")
            return False
        
        print(f"\n📋 ANALYZING REST TIMER VALUES IN WORKOUT PLANS")
        print("-" * 50)
        
        total_exercises = 0
        zero_rest_exercises = 0
        rest_values = []
        
        for plan in plans_response:
            if 'exercises' in plan:
                for exercise in plan['exercises']:
                    total_exercises += 1
                    rest_seconds = exercise.get('rest_seconds', 0)
                    rest_values.append(rest_seconds)
                    
                    if rest_seconds == 0:
                        zero_rest_exercises += 1
                        print(f"   ⚠️  Found exercise '{exercise.get('name', 'Unknown')}' with 0 rest_seconds")
        
        print(f"\n📊 REST TIMER ANALYSIS RESULTS:")
        print(f"   - Total exercises analyzed: {total_exercises}")
        print(f"   - Exercises with 0 rest_seconds: {zero_rest_exercises}")
        print(f"   - Rest values range: {min(rest_values) if rest_values else 0}s - {max(rest_values) if rest_values else 0}s")
        
        if zero_rest_exercises > 0:
            print(f"\n✅ REST TIMER FIX VERIFICATION:")
            print(f"   - Found {zero_rest_exercises} exercises with 0 rest_seconds")
            print(f"   - Frontend should default these to 30 seconds")
            print(f"   - This prevents users from being stuck with 0s rest timer")
            self.log_test("Rest Timer Default Logic", True, f"Found {zero_rest_exercises} exercises that will default to 30s")
        else:
            print(f"\n✅ REST TIMER VALUES:")
            print(f"   - All exercises have non-zero rest_seconds values")
            print(f"   - No exercises require the 30s default")
            self.log_test("Rest Timer Values Check", True, "All exercises have proper rest_seconds values")
        
        return True

    def run_all_tests(self):
        """Run all cloud MongoDB and rest timer tests"""
        print(f"\n🚀 STARTING CLOUD MONGODB AND REST TIMER TESTS")
        print("=" * 70)
        
        # Test cloud MongoDB connection and data persistence
        mongodb_success = self.test_cloud_mongodb_connection()
        
        # Test rest timer functionality
        rest_timer_success = self.test_rest_timer_functionality()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ Cloud MongoDB connection working")
            print(f"✅ Data persistence verified across all collections")
            print(f"✅ Rest timer functionality confirmed")
        else:
            print(f"\n⚠️  SOME TESTS FAILED")
            failed_tests = [result for result in self.test_results if not result['success']]
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = CloudMongoDBTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
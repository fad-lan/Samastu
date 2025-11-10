import requests
import sys
import json
from datetime import datetime

class SamastuAPITester:
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
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)

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

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Test User {timestamp}"
        }
        
        response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        timestamp = datetime.now().strftime('%H%M%S')
        register_data = {
            "email": f"login_test_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Login Test {timestamp}"
        }
        
        # Register first
        self.run_test(
            "Pre-Login Registration",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        
        # Now test login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_auth_me(self):
        """Test getting current user info"""
        response = self.run_test(
            "Get Current User (/auth/me)",
            "GET",
            "auth/me",
            200
        )
        return bool(response and 'id' in response)

    def test_get_workout_plans(self):
        """Test getting workout plans"""
        response = self.run_test(
            "Get Workout Plans",
            "GET",
            "workouts/plans",
            200
        )
        
        if response and isinstance(response, list) and len(response) > 0:
            print(f"   Found {len(response)} workout plans")
            return response[0]['id']  # Return first workout ID for later tests
        return None

    def test_get_workout_journey(self):
        """Test getting workout journey"""
        response = self.run_test(
            "Get Workout Journey",
            "GET",
            "workouts/journey",
            200
        )
        
        if response and isinstance(response, list):
            print(f"   Found {len(response)} journey items")
            return True
        return False

    def test_complete_workout(self, workout_id):
        """Test completing a workout"""
        if not workout_id:
            self.log_test("Complete Workout", False, "No workout ID available")
            return False
            
        complete_data = {
            "workout_plan_id": workout_id,
            "duration_minutes": 25
        }
        
        response = self.run_test(
            "Complete Workout",
            "POST",
            "workouts/complete",
            200,
            data=complete_data
        )
        
        if response and 'success' in response and response['success']:
            print(f"   XP Earned: {response.get('xp_earned', 0)}")
            print(f"   New Level: {response.get('new_level', 1)}")
            print(f"   New Streak: {response.get('new_streak', 0)}")
            return True
        return False

    def test_get_progress(self):
        """Test getting user progress"""
        response = self.run_test(
            "Get User Progress",
            "GET",
            "progress",
            200
        )
        
        if response and 'user_id' in response:
            print(f"   Level: {response.get('level', 1)}")
            print(f"   Total XP: {response.get('total_xp', 0)}")
            print(f"   Streak: {response.get('streak', 0)}")
            return True
        return False

    def test_get_achievements(self):
        """Test getting achievements"""
        response = self.run_test(
            "Get Achievements",
            "GET",
            "achievements",
            200
        )
        
        if response and 'achievements' in response:
            achievements = response['achievements']
            unlocked = [a for a in achievements if a.get('unlocked', False)]
            print(f"   Total achievements: {len(achievements)}")
            print(f"   Unlocked: {len(unlocked)}")
            return True
        return False

    def test_update_profile(self):
        """Test updating user profile"""
        update_data = {
            "height": 175.0,
            "weight": 70.0,
            "goal": "strong",
            "equipment": ["dumbbells", "resistance"]
        }
        
        response = self.run_test(
            "Update User Profile",
            "PUT",
            "user/profile",
            200,
            data=update_data
        )
        
        if response and 'id' in response:
            print(f"   Updated profile for user: {response.get('name', 'Unknown')}")
            return True
        return False

    def test_get_profile(self):
        """Test getting user profile"""
        response = self.run_test(
            "Get User Profile",
            "GET",
            "user/profile",
            200
        )
        
        if response and 'id' in response:
            print(f"   Profile: {response.get('name', 'Unknown')}")
            print(f"   Height: {response.get('height', 'Not set')}")
            print(f"   Weight: {response.get('weight', 'Not set')}")
            return True
        return False

    def test_ai_workout_generation(self):
        """Test AI workout generation endpoint"""
        print(f"\n🤖 Testing AI Workout Generation...")
        print("   This may take 5-10 seconds due to Gemini AI processing...")
        
        # First ensure user has complete profile data
        profile_data = {
            "experience_level": "intermediate",
            "goal": "muscle_building",
            "equipment": ["dumbbells", "resistance_bands"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Wednesday", "minutes": 30},
                {"day": "Friday", "minutes": 45}
            ]
        }
        
        # Update profile first
        self.run_test(
            "Update Profile for AI Test",
            "PUT",
            "user/profile",
            200,
            data=profile_data
        )
        
        # Test AI workout generation
        url = f"{self.base_url}/api/workouts/generate-ai"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)  # Longer timeout for AI
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    data = response.json()
                    
                    # Verify response structure
                    if not isinstance(data, dict):
                        success = False
                        details += ", Response is not a dict"
                    elif 'success' not in data or not data['success']:
                        success = False
                        details += f", Success field missing or false: {data.get('success')}"
                    elif 'plans' not in data:
                        success = False
                        details += ", Plans field missing"
                    elif not isinstance(data['plans'], list):
                        success = False
                        details += ", Plans is not a list"
                    elif len(data['plans']) == 0:
                        success = False
                        details += ", No plans generated"
                    else:
                        # Verify plan structure
                        plan = data['plans'][0]
                        required_fields = ['id', 'name', 'difficulty', 'target_muscles', 'duration_minutes', 'xp_reward', 'exercises']
                        missing_fields = [field for field in required_fields if field not in plan]
                        
                        if missing_fields:
                            success = False
                            details += f", Missing plan fields: {missing_fields}"
                        elif not isinstance(plan['exercises'], list) or len(plan['exercises']) == 0:
                            success = False
                            details += ", No exercises in plan"
                        else:
                            # Verify exercise structure
                            exercise = plan['exercises'][0]
                            required_ex_fields = ['name', 'reps', 'sets', 'rest_seconds', 'icon']
                            missing_ex_fields = [field for field in required_ex_fields if field not in exercise]
                            
                            if missing_ex_fields:
                                success = False
                                details += f", Missing exercise fields: {missing_ex_fields}"
                            else:
                                # Check for MongoDB ObjectId (should not be present)
                                if '_id' in plan or any('_id' in ex for ex in plan['exercises']):
                                    success = False
                                    details += ", MongoDB _id found in response (serialization issue)"
                                else:
                                    details += f", Generated {len(data['plans'])} plans with {len(plan['exercises'])} exercises each"
                                    print(f"   ✅ Generated {len(data['plans'])} AI workout plans")
                                    print(f"   ✅ First plan: {plan['name']} ({plan['difficulty']})")
                                    print(f"   ✅ Target muscles: {plan['target_muscles']}")
                                    print(f"   ✅ Duration: {plan['duration_minutes']} minutes")
                                    print(f"   ✅ Exercises: {len(plan['exercises'])}")
                                    print(f"   ✅ No MongoDB ObjectId in response")
                
                except json.JSONDecodeError as e:
                    success = False
                    details += f", JSON decode error: {str(e)}"
                except Exception as e:
                    success = False
                    details += f", Response parsing error: {str(e)}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("AI Workout Generation", success, details)
            return success
            
        except requests.exceptions.Timeout:
            self.log_test("AI Workout Generation", False, "Request timeout (>30s)")
            return False
        except Exception as e:
            self.log_test("AI Workout Generation", False, f"Exception: {str(e)}")
            return False

    def test_get_ai_plans(self):
        """Test getting AI-generated workout plans"""
        response = self.run_test(
            "Get AI Workout Plans",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        if response and isinstance(response, list):
            print(f"   Found {len(response)} AI-generated plans in database")
            if len(response) > 0:
                plan = response[0]
                print(f"   First plan: {plan.get('name', 'Unknown')}")
                # Verify no MongoDB _id in stored plans
                if '_id' in plan:
                    self.log_test("AI Plans Storage Check", False, "MongoDB _id found in stored plans")
                    return False
                else:
                    print(f"   ✅ No MongoDB _id in stored plans")
            return True
        return False

    def test_integrated_ai_schedule_flow(self):
        """Test the complete integrated AI workout generation flow in schedule creation"""
        print(f"\n🎯 TESTING INTEGRATED AI SCHEDULE FLOW")
        print("=" * 60)
        
        # Part 1: New User Onboarding Flow
        print(f"\n📋 PART 1: NEW USER ONBOARDING FLOW")
        print("-" * 40)
        
        # Create a new test user with complete profile
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"ai_schedule_test_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"AI Schedule Test User {timestamp}"
        }
        
        # Register new user
        response = self.run_test(
            "1.1 Create New Test User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not response or 'access_token' not in response:
            print("❌ Failed to create test user, stopping AI schedule flow test")
            return False
        
        # Store token for this test user
        test_token = response['access_token']
        test_user_id = response['user']['id']
        
        # Update profile with complete onboarding data
        profile_data = {
            "experience_level": "intermediate",
            "goal": "muscle_building",
            "equipment": ["dumbbells", "resistance_bands", "bodyweight"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Wednesday", "minutes": 30},
                {"day": "Friday", "minutes": 45},
                {"day": "Saturday", "minutes": 60}
            ]
        }
        
        # Temporarily switch to test user token
        original_token = self.token
        self.token = test_token
        
        response = self.run_test(
            "1.2 Update Profile with Complete Data",
            "PUT",
            "user/profile",
            200,
            data=profile_data
        )
        
        if not response:
            self.token = original_token
            return False
        
        # Call POST /schedule/generate (should auto-generate AI plans)
        print(f"\n🤖 Calling /schedule/generate (may take 5-10 seconds for AI generation)...")
        
        url = f"{self.base_url}/api/schedule/generate"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {test_token}'
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=60)  # Long timeout for AI
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if data.get('success') and 'scheduled_count' in data:
                    scheduled_count = data['scheduled_count']
                    print(f"   ✅ Schedule generated with {scheduled_count} items")
                    details += f", Scheduled {scheduled_count} items"
                else:
                    success = False
                    details += f", Invalid response: {data}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("1.3 Generate Schedule with Auto AI Plans", success, details)
            
            if not success:
                self.token = original_token
                return False
                
        except Exception as e:
            self.log_test("1.3 Generate Schedule with Auto AI Plans", False, f"Exception: {str(e)}")
            self.token = original_token
            return False
        
        # Verify AI plans were auto-generated
        ai_plans_response = self.run_test(
            "1.4 Verify AI Plans Auto-Generated",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        if not ai_plans_response or not isinstance(ai_plans_response, list) or len(ai_plans_response) == 0:
            self.log_test("1.4 AI Plans Verification", False, "No AI plans found after schedule generation")
            self.token = original_token
            return False
        
        ai_plan_ids = [plan['id'] for plan in ai_plans_response]
        print(f"   ✅ Found {len(ai_plans_response)} AI-generated plans")
        
        # Verify scheduled workouts were created
        schedule_response = self.run_test(
            "1.5 Verify Scheduled Workouts Created",
            "GET",
            "schedule/calendar",
            200
        )
        
        if not schedule_response or not isinstance(schedule_response, list) or len(schedule_response) == 0:
            self.log_test("1.5 Schedule Verification", False, "No scheduled workouts found")
            self.token = original_token
            return False
        
        # Verify scheduled workouts reference AI-generated plan IDs
        workout_plan_ids = [item['workout_plan_id'] for item in schedule_response if not item.get('is_rest_day', False)]
        ai_plans_referenced = any(plan_id in ai_plan_ids for plan_id in workout_plan_ids)
        
        if not ai_plans_referenced:
            self.log_test("1.6 AI Plans Referenced in Schedule", False, "Scheduled workouts don't reference AI-generated plans")
            self.token = original_token
            return False
        
        print(f"   ✅ Scheduled workouts reference AI-generated plans")
        self.log_test("1.6 AI Plans Referenced in Schedule", True, f"AI plans properly referenced in {len(schedule_response)} scheduled items")
        
        # Part 2: Schedule Reuse (AI plans NOT regenerated)
        print(f"\n🔄 PART 2: SCHEDULE REUSE TEST")
        print("-" * 40)
        
        # Store original AI plan creation timestamps
        original_timestamps = {plan['id']: plan.get('created_at') for plan in ai_plans_response}
        
        # Call POST /schedule/generate again
        try:
            response = requests.post(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Second schedule generation successful")
                else:
                    success = False
            
            self.log_test("2.1 Generate Schedule Again", success, f"Status: {response.status_code}")
            
            if not success:
                self.token = original_token
                return False
                
        except Exception as e:
            self.log_test("2.1 Generate Schedule Again", False, f"Exception: {str(e)}")
            self.token = original_token
            return False
        
        # Verify AI plans were reused (same IDs and timestamps)
        new_ai_plans_response = self.run_test(
            "2.2 Verify AI Plans Reused",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        if not new_ai_plans_response:
            self.token = original_token
            return False
        
        new_timestamps = {plan['id']: plan.get('created_at') for plan in new_ai_plans_response}
        
        # Check if plans were reused (same IDs and timestamps)
        plans_reused = (set(original_timestamps.keys()) == set(new_timestamps.keys()) and 
                       all(original_timestamps[plan_id] == new_timestamps[plan_id] 
                           for plan_id in original_timestamps.keys()))
        
        if plans_reused:
            print(f"   ✅ AI plans were reused (same IDs and timestamps)")
            self.log_test("2.3 AI Plans Reuse Verification", True, "AI plans properly reused")
        else:
            self.log_test("2.3 AI Plans Reuse Verification", False, "AI plans were regenerated instead of reused")
        
        # Part 3: Reset and Regenerate
        print(f"\n🔄 PART 3: RESET AND REGENERATE TEST")
        print("-" * 40)
        
        # Call DELETE /schedule/reset
        reset_url = f"{self.base_url}/api/schedule/reset"
        try:
            response = requests.delete(reset_url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if data.get('success'):
                    deleted_schedule = data.get('deleted_schedule_count', 0)
                    deleted_ai_plans = data.get('deleted_ai_plans_count', 0)
                    print(f"   ✅ Reset successful: {deleted_schedule} schedule items, {deleted_ai_plans} AI plans deleted")
                    details += f", Deleted {deleted_schedule} schedule + {deleted_ai_plans} AI plans"
                else:
                    success = False
                    details += f", Reset failed: {data}"
            else:
                try:
                    error_data = response.json()
                    details += f", Error: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("3.1 Reset Schedule and AI Plans", success, details)
            
            if not success:
                self.token = original_token
                return False
                
        except Exception as e:
            self.log_test("3.1 Reset Schedule and AI Plans", False, f"Exception: {str(e)}")
            self.token = original_token
            return False
        
        # Verify both schedule and AI plans were deleted
        empty_schedule = self.run_test(
            "3.2 Verify Schedule Deleted",
            "GET",
            "schedule/calendar",
            200
        )
        
        empty_ai_plans = self.run_test(
            "3.3 Verify AI Plans Deleted",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        schedule_deleted = not empty_schedule or len(empty_schedule) == 0
        ai_plans_deleted = not empty_ai_plans or len(empty_ai_plans) == 0
        
        if not schedule_deleted:
            self.log_test("3.2 Schedule Deletion Verification", False, f"Schedule still has {len(empty_schedule)} items")
        else:
            print(f"   ✅ Schedule properly deleted")
            
        if not ai_plans_deleted:
            self.log_test("3.3 AI Plans Deletion Verification", False, f"AI plans still has {len(empty_ai_plans)} items")
        else:
            print(f"   ✅ AI plans properly deleted")
        
        # Call POST /schedule/generate again to verify NEW AI plans are generated
        print(f"\n🤖 Regenerating after reset (may take 5-10 seconds)...")
        
        try:
            response = requests.post(url, headers=headers, timeout=60)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ Post-reset schedule generation successful")
                else:
                    success = False
            
            self.log_test("3.4 Generate Schedule After Reset", success, f"Status: {response.status_code}")
            
            if not success:
                self.token = original_token
                return False
                
        except Exception as e:
            self.log_test("3.4 Generate Schedule After Reset", False, f"Exception: {str(e)}")
            self.token = original_token
            return False
        
        # Verify NEW AI plans are generated (different plan IDs)
        final_ai_plans = self.run_test(
            "3.5 Verify NEW AI Plans Generated",
            "GET",
            "workouts/ai-plans",
            200
        )
        
        if not final_ai_plans or len(final_ai_plans) == 0:
            self.log_test("3.5 New AI Plans Verification", False, "No AI plans found after reset and regeneration")
            self.token = original_token
            return False
        
        final_plan_ids = set(plan['id'] for plan in final_ai_plans)
        original_plan_ids = set(original_timestamps.keys())
        
        new_plans_generated = not final_plan_ids.intersection(original_plan_ids)
        
        if new_plans_generated:
            print(f"   ✅ NEW AI plans generated (different IDs than before)")
            self.log_test("3.6 New AI Plans ID Verification", True, f"Generated {len(final_ai_plans)} new AI plans with different IDs")
        else:
            self.log_test("3.6 New AI Plans ID Verification", False, "AI plans have same IDs as before reset")
        
        # Verify new schedule uses new AI plan IDs
        final_schedule = self.run_test(
            "3.7 Verify New Schedule with New AI Plans",
            "GET",
            "schedule/calendar",
            200
        )
        
        if final_schedule and len(final_schedule) > 0:
            final_workout_plan_ids = [item['workout_plan_id'] for item in final_schedule if not item.get('is_rest_day', False)]
            new_ai_plans_used = any(plan_id in final_plan_ids for plan_id in final_workout_plan_ids)
            
            if new_ai_plans_used:
                print(f"   ✅ New schedule uses new AI plan IDs")
                self.log_test("3.8 New Schedule Uses New AI Plans", True, "Schedule properly references new AI plans")
            else:
                self.log_test("3.8 New Schedule Uses New AI Plans", False, "Schedule doesn't reference new AI plans")
        
        # Restore original token
        self.token = original_token
        
        print(f"\n🎯 INTEGRATED AI SCHEDULE FLOW TEST COMPLETED")
        print("=" * 60)
        
        return True

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Samastu API Tests")
        print("=" * 50)
        
        # Test authentication flow
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False
            
        self.test_auth_me()
        
        # Test login with different user
        self.test_user_login()
        
        # Test workout-related endpoints
        workout_id = self.test_get_workout_plans()
        self.test_get_workout_journey()
        
        # Test completing a workout (this will affect progress)
        self.test_complete_workout(workout_id)
        
        # Test progress and achievements
        self.test_get_progress()
        self.test_get_achievements()
        
        # Test profile management
        self.test_update_profile()
        self.test_get_profile()
        
        # Test AI workout generation (main focus)
        print("\n" + "🎯" * 25)
        print("🎯 MAIN FOCUS: AI WORKOUT GENERATION TESTS")
        print("🎯" * 25)
        self.test_ai_workout_generation()
        self.test_get_ai_plans()
        
        # Test integrated AI schedule flow (NEW MAIN FOCUS)
        print("\n" + "🚀" * 30)
        print("🚀 NEW MAIN FOCUS: INTEGRATED AI SCHEDULE FLOW")
        print("🚀" * 30)
        self.test_integrated_ai_schedule_flow()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = SamastuAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': tester.tests_run,
            'passed_tests': tester.tests_passed,
            'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
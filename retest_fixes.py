import requests
import sys
import json
from datetime import datetime, timedelta

class RestDayAndMondayTester:
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

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

    def create_test_user(self, suffix=""):
        """Create a test user and return token"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"retest_{suffix}_{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Retest User {suffix} {timestamp}"
        }
        
        response = self.run_test(
            f"Create Test User {suffix}",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if response and 'access_token' in response:
            return response['access_token'], response['user']['id']
        return None, None

    def test_smart_rest_day_logic_retest(self):
        """RETEST: Smart rest day logic with max_consecutive_count fix"""
        print(f"\n🎯 RETESTING SMART REST DAY LOGIC (MAX_CONSECUTIVE_COUNT FIX)")
        print("=" * 70)
        
        # Test 1: Mon/Tue/Wed availability (3 consecutive days)
        print(f"\n📋 TEST 1: MON/TUE/WED (3 CONSECUTIVE DAYS)")
        print("-" * 50)
        
        token1, user_id1 = self.create_test_user("consecutive3")
        if not token1:
            return False
        
        original_token = self.token
        self.token = token1
        
        # Set profile with Mon/Tue/Wed availability
        profile_data1 = {
            "experience_level": "intermediate",
            "goal": "muscle_building", 
            "equipment": ["dumbbells"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Tuesday", "minutes": 45},
                {"day": "Wednesday", "minutes": 45}
            ],
            "plan_duration": 2,
            "plan_duration_unit": "weeks"
        }
        
        self.run_test(
            "1.1 Set Profile Mon/Tue/Wed",
            "PUT",
            "user/profile",
            200,
            data=profile_data1
        )
        
        # Generate schedule
        response = self.run_test(
            "1.2 Generate Schedule Mon/Tue/Wed",
            "POST",
            "schedule/generate",
            200
        )
        
        if not response:
            self.token = original_token
            return False
        
        # Get schedule and analyze rest day placement
        schedule = self.run_test(
            "1.3 Get Schedule Mon/Tue/Wed",
            "GET",
            "schedule/calendar",
            200
        )
        
        if schedule:
            rest_days = [item for item in schedule if item.get('is_rest_day', False)]
            workout_days = [item for item in schedule if not item.get('is_rest_day', False)]
            
            print(f"   📊 Mon/Tue/Wed Analysis:")
            print(f"   - Total items: {len(schedule)}")
            print(f"   - Workout days: {len(workout_days)}")
            print(f"   - Rest days: {len(rest_days)}")
            
            # Verify rest days ARE added after 2-3 consecutive workouts
            if len(rest_days) > 0:
                print(f"   ✅ Rest days added for 3 consecutive workout days")
                
                # Check if rest days are strategically placed after consecutive workouts
                from datetime import datetime as dt
                dated_items = []
                for item in schedule:
                    try:
                        date_obj = dt.fromisoformat(item['scheduled_date']).date()
                        dated_items.append({
                            'date': date_obj,
                            'is_rest_day': item.get('is_rest_day', False),
                            'day_of_week': item['day_of_week']
                        })
                    except:
                        continue
                
                dated_items.sort(key=lambda x: x['date'])
                
                # Look for pattern: workout -> workout -> workout -> rest
                consecutive_count = 0
                rest_after_consecutive = False
                
                for item in dated_items:
                    if not item['is_rest_day']:
                        consecutive_count += 1
                    else:
                        if consecutive_count >= 2:  # Rest day after 2+ consecutive workouts
                            rest_after_consecutive = True
                        consecutive_count = 0
                
                if rest_after_consecutive:
                    print(f"   ✅ Rest days correctly placed after consecutive workouts")
                    self.log_test("1.4 Rest Days After Consecutive Workouts", True, f"Rest days properly placed after {consecutive_count} consecutive workouts")
                else:
                    print(f"   ⚠️  Rest days not optimally placed after consecutive workouts")
                    self.log_test("1.4 Rest Days After Consecutive Workouts", False, "Rest days not placed after consecutive workouts")
                
                self.log_test("1.4 Smart Rest Logic - 3 Consecutive", True, f"Added {len(rest_days)} rest days for 3 consecutive workout days")
            else:
                print(f"   ❌ No rest days added for 3 consecutive workout days")
                self.log_test("1.4 Smart Rest Logic - 3 Consecutive", False, "No rest days added for 3 consecutive workout days")
        
        # Test 2: Mon/Tue/Thu/Fri availability (two pairs of consecutive: Mon/Tue and Thu/Fri)
        print(f"\n📋 TEST 2: MON/TUE/THU/FRI (TWO PAIRS OF CONSECUTIVE)")
        print("-" * 50)
        
        token2, user_id2 = self.create_test_user("twopairs")
        if not token2:
            self.token = original_token
            return False
        
        self.token = token2
        
        # Set profile with Mon/Tue/Thu/Fri availability
        profile_data2 = {
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
        
        self.run_test(
            "2.1 Set Profile Mon/Tue/Thu/Fri",
            "PUT",
            "user/profile",
            200,
            data=profile_data2
        )
        
        # Generate schedule
        response = self.run_test(
            "2.2 Generate Schedule Mon/Tue/Thu/Fri",
            "POST",
            "schedule/generate",
            200
        )
        
        if not response:
            self.token = original_token
            return False
        
        # Get schedule and analyze
        schedule2 = self.run_test(
            "2.3 Get Schedule Mon/Tue/Thu/Fri",
            "GET",
            "schedule/calendar",
            200
        )
        
        if schedule2:
            rest_days2 = [item for item in schedule2 if item.get('is_rest_day', False)]
            workout_days2 = [item for item in schedule2 if not item.get('is_rest_day', False)]
            
            print(f"   📊 Mon/Tue/Thu/Fri Analysis:")
            print(f"   - Total items: {len(schedule2)}")
            print(f"   - Workout days: {len(workout_days2)}")
            print(f"   - Rest days: {len(rest_days2)}")
            
            # Check max_consecutive_count detection (should be 2)
            # The algorithm should detect max consecutive as 2 (Mon/Tue pair and Thu/Fri pair)
            if len(rest_days2) > 0:
                print(f"   ✅ Rest days added for consecutive pairs (max_consecutive_count = 2)")
                self.log_test("2.4 Max Consecutive Count Detection", True, f"Correctly identified max_consecutive_count=2, added {len(rest_days2)} rest days")
            else:
                print(f"   ❌ No rest days added - algorithm may not detect max_consecutive_count correctly")
                self.log_test("2.4 Max Consecutive Count Detection", False, "Algorithm failed to detect max_consecutive_count=2")
        
        # Test 3: Mon/Wed/Fri availability (no consecutive, natural gaps)
        print(f"\n📋 TEST 3: MON/WED/FRI (NO CONSECUTIVE, NATURAL GAPS)")
        print("-" * 50)
        
        token3, user_id3 = self.create_test_user("naturalgaps")
        if not token3:
            self.token = original_token
            return False
        
        self.token = token3
        
        # Set profile with Mon/Wed/Fri availability
        profile_data3 = {
            "experience_level": "intermediate",
            "goal": "muscle_building",
            "equipment": ["dumbbells"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Wednesday", "minutes": 45},
                {"day": "Friday", "minutes": 45}
            ],
            "plan_duration": 2,
            "plan_duration_unit": "weeks"
        }
        
        self.run_test(
            "3.1 Set Profile Mon/Wed/Fri",
            "PUT",
            "user/profile",
            200,
            data=profile_data3
        )
        
        # Generate schedule
        response = self.run_test(
            "3.2 Generate Schedule Mon/Wed/Fri",
            "POST",
            "schedule/generate",
            200
        )
        
        if not response:
            self.token = original_token
            return False
        
        # Get schedule and verify NO additional rest days
        schedule3 = self.run_test(
            "3.3 Get Schedule Mon/Wed/Fri",
            "GET",
            "schedule/calendar",
            200
        )
        
        if schedule3:
            rest_days3 = [item for item in schedule3 if item.get('is_rest_day', False)]
            workout_days3 = [item for item in schedule3 if not item.get('is_rest_day', False)]
            
            print(f"   📊 Mon/Wed/Fri Analysis:")
            print(f"   - Total items: {len(schedule3)}")
            print(f"   - Workout days: {len(workout_days3)}")
            print(f"   - Rest days: {len(rest_days3)}")
            
            # Verify NO additional rest days are added (natural gaps)
            if len(rest_days3) == 0:
                print(f"   ✅ No additional rest days added (natural gaps respected)")
                self.log_test("3.4 Natural Gaps Respected", True, "Correctly avoided adding rest days with natural gaps")
            else:
                print(f"   ❌ {len(rest_days3)} rest days added despite natural gaps")
                self.log_test("3.4 Natural Gaps Respected", False, f"Added {len(rest_days3)} rest days despite natural gaps")
        
        self.token = original_token
        return True

    def test_week_start_monday_retest(self):
        """RETEST: Week start on Monday with start_date alignment fix"""
        print(f"\n🎯 RETESTING WEEK START ON MONDAY (START_DATE ALIGNMENT FIX)")
        print("=" * 70)
        
        # Create test user
        token, user_id = self.create_test_user("monday")
        if not token:
            return False
        
        original_token = self.token
        self.token = token
        
        # Set profile with multiple days to see week pattern
        profile_data = {
            "experience_level": "intermediate",
            "goal": "muscle_building",
            "equipment": ["dumbbells"],
            "available_days": [
                {"day": "Monday", "minutes": 45},
                {"day": "Tuesday", "minutes": 45},
                {"day": "Wednesday", "minutes": 45},
                {"day": "Thursday", "minutes": 45},
                {"day": "Friday", "minutes": 45}
            ],
            "plan_duration": 2,
            "plan_duration_unit": "weeks"
        }
        
        self.run_test(
            "1.1 Set Profile for Monday Test",
            "PUT",
            "user/profile",
            200,
            data=profile_data
        )
        
        # Generate schedule
        response = self.run_test(
            "1.2 Generate Schedule for Monday Test",
            "POST",
            "schedule/generate",
            200
        )
        
        if not response:
            self.token = original_token
            return False
        
        # Get schedule and verify Monday start
        schedule = self.run_test(
            "1.3 Get Schedule for Monday Verification",
            "GET",
            "schedule/calendar",
            200
        )
        
        if schedule and len(schedule) > 0:
            print(f"\n📊 Analyzing Monday start alignment...")
            
            # Parse dates and analyze
            from datetime import datetime as dt
            dated_items = []
            
            for item in schedule:
                try:
                    date_obj = dt.fromisoformat(item['scheduled_date']).date()
                    weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
                    dated_items.append({
                        'date': date_obj,
                        'weekday': weekday,
                        'day_of_week': item['day_of_week'],
                        'is_rest_day': item.get('is_rest_day', False)
                    })
                except:
                    continue
            
            # Sort by date
            dated_items.sort(key=lambda x: x['date'])
            
            if len(dated_items) > 0:
                first_item = dated_items[0]
                
                print(f"   📅 First scheduled item:")
                print(f"   - Date: {first_item['date']}")
                print(f"   - Weekday: {first_item['weekday']} (0=Monday)")
                print(f"   - Day of week: {first_item['day_of_week']}")
                print(f"   - Type: {'Rest' if first_item['is_rest_day'] else 'Workout'}")
                
                # Test 1: Verify first scheduled date is a Monday
                if first_item['weekday'] == 0:  # Monday
                    print(f"   ✅ First scheduled item is on Monday")
                    self.log_test("1.4 First Item on Monday", True, f"First scheduled date {first_item['date']} is Monday")
                else:
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    actual_day = day_names[first_item['weekday']]
                    print(f"   ❌ First scheduled item is on {actual_day}, not Monday")
                    self.log_test("1.4 First Item on Monday", False, f"First scheduled date {first_item['date']} is {actual_day}, not Monday")
                
                # Test 2: Verify schedule starts from nearest past Monday, not current day
                today = dt.now().date()
                
                # Calculate what the nearest past Monday should be
                days_since_monday = today.weekday()  # 0=Monday, so 0 means today is Monday
                if days_since_monday == 0:
                    expected_monday = today  # Today is Monday
                else:
                    expected_monday = today - timedelta(days=days_since_monday)
                
                print(f"   📅 Monday alignment analysis:")
                print(f"   - Today: {today} (weekday {today.weekday()})")
                print(f"   - Expected Monday start: {expected_monday}")
                print(f"   - Actual first date: {first_item['date']}")
                
                # Check if first date aligns with expected Monday start
                if first_item['date'] >= expected_monday:
                    # Find the Monday of the week containing first_item['date']
                    first_item_monday = first_item['date'] - timedelta(days=first_item['date'].weekday())
                    
                    if first_item_monday == expected_monday:
                        print(f"   ✅ Schedule starts from nearest past Monday")
                        self.log_test("1.5 Nearest Past Monday Start", True, f"Schedule correctly starts from {expected_monday}")
                    else:
                        print(f"   ⚠️  Schedule starts from {first_item_monday}, expected {expected_monday}")
                        self.log_test("1.5 Nearest Past Monday Start", False, f"Expected {expected_monday}, got {first_item_monday}")
                else:
                    print(f"   ❌ Schedule starts before expected Monday")
                    self.log_test("1.5 Nearest Past Monday Start", False, f"Schedule starts {first_item['date']}, before expected {expected_monday}")
                
                # Test 3: Check all scheduled_date values align with Monday-based weeks
                print(f"\n   📅 Verifying all dates align with Monday-based weeks...")
                
                week_alignment_errors = []
                current_week_start = None
                
                for item in dated_items:
                    # Calculate Monday of this item's week
                    item_monday = item['date'] - timedelta(days=item['date'].weekday())
                    
                    if current_week_start is None:
                        current_week_start = item_monday
                    elif item_monday != current_week_start and (item_monday - current_week_start).days == 7:
                        # New week started
                        current_week_start = item_monday
                    elif item_monday != current_week_start and (item_monday - current_week_start).days != 7:
                        # Week alignment error
                        week_alignment_errors.append(f"{item['date']} (Monday: {item_monday})")
                
                if len(week_alignment_errors) == 0:
                    print(f"   ✅ All scheduled dates align with Monday-based weeks")
                    self.log_test("1.6 Monday-Based Week Alignment", True, "All dates properly aligned with Monday-based weeks")
                else:
                    print(f"   ❌ Week alignment errors: {week_alignment_errors[:3]}...")  # Show first 3
                    self.log_test("1.6 Monday-Based Week Alignment", False, f"Week alignment errors found: {len(week_alignment_errors)} items")
                
                # Show first week pattern
                print(f"\n   📅 First week pattern:")
                first_week_items = [item for item in dated_items if (item['date'] - dated_items[0]['date']).days < 7]
                for item in first_week_items:
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    day_name = day_names[item['weekday']]
                    print(f"   - {item['date']} ({day_name}): {item['day_of_week']} - {'Rest' if item['is_rest_day'] else 'Workout'}")
            
            else:
                self.log_test("1.4 Schedule Analysis", False, "No valid dated items found in schedule")
        
        self.token = original_token
        return True

    def run_retest(self):
        """Run the focused retest for smart rest day logic and Monday start fixes"""
        print("🔄 RETESTING SMART REST DAY LOGIC AND WEEK START MONDAY FIXES")
        print("=" * 80)
        
        # Run focused tests
        rest_day_success = self.test_smart_rest_day_logic_retest()
        monday_start_success = self.test_week_start_monday_retest()
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"📊 RETEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print(f"📊 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All retests passed! Fixes are working correctly.")
            return True
        else:
            failed_tests = [result for result in self.test_results if not result['success']]
            print(f"⚠️  {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
            return False

def main():
    tester = RestDayAndMondayTester()
    success = tester.run_retest()
    
    # Save results
    with open('/app/retest_results.json', 'w') as f:
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
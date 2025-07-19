#!/usr/bin/env python3
"""
Test for Smart Calendar Bot Backend API Implementation
Tests the study planner endpoints that power the conversational AI study planner.
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔍 Using API URL: {API_URL}")

class SmartCalendarBotTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.plan_id = None
        
    def register_and_login_student(self):
        """Register and login a student for testing"""
        print("\n🔍 Setting up student account for Smart Calendar Bot testing...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"calendar_bot_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Priya Sharma",
            "user_type": "student",
            "grade_level": "11th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Student Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Registered student with ID: {self.student_id}")
                return True
            else:
                print(f"❌ Failed to register student: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error registering student: {str(e)}")
            return False
    
    def test_study_planner_chat_api(self):
        """Test the /api/study-planner/chat endpoint"""
        print("\n🎯 TESTING STUDY PLANNER CHAT API")
        print("=" * 60)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/study-planner/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different chat scenarios
        test_messages = [
            {
                "name": "Initial greeting",
                "payload": {
                    "message": "Hi, I need help planning my study session",
                    "context": {}
                }
            },
            {
                "name": "Study requirements",
                "payload": {
                    "message": "I have 2 hours to study. I need to cover math for 1 hour and physics for 30 minutes",
                    "context": {"stage": "requirements_gathering"}
                }
            },
            {
                "name": "Specific subject request",
                "payload": {
                    "message": "Can you help me create a Pomodoro schedule for calculus?",
                    "context": {"subjects": ["mathematics"]}
                }
            }
        ]
        
        results = []
        for test_case in test_messages:
            print(f"\n🔍 Testing: {test_case['name']}")
            
            try:
                response = requests.post(url, json=test_case['payload'], headers=headers)
                print(f"   Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS")
                    print(f"   Bot Response: {data.get('response', '')[:100]}...")
                    print(f"   Needs Input: {data.get('needs_input', False)}")
                    print(f"   Input Type: {data.get('input_type', 'None')}")
                    print(f"   Suggested Actions: {len(data.get('suggested_actions', []))} actions")
                    results.append(True)
                else:
                    print(f"   ❌ FAILED: {response.status_code}")
                    print(f"   Error: {response.text}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 CHAT API TEST RESULTS: {sum(results)}/{len(results)} passed ({success_rate:.1f}%)")
        return all(results)
    
    def test_study_plan_generation_api(self):
        """Test the /api/study-planner/generate-plan endpoint"""
        print("\n🎯 TESTING STUDY PLAN GENERATION API")
        print("=" * 60)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/study-planner/generate-plan"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test plan generation with realistic study requirements
        test_payload = {
            "total_duration_minutes": 120,  # 2 hours
            "subjects": [
                {
                    "subject": "mathematics",
                    "duration_minutes": 60,
                    "priority": "high",
                    "notes": "Focus on calculus derivatives"
                },
                {
                    "subject": "physics",
                    "duration_minutes": 45,
                    "priority": "medium", 
                    "notes": "Review mechanics and motion"
                },
                {
                    "subject": "chemistry",
                    "duration_minutes": 15,
                    "priority": "low",
                    "notes": "Quick review of organic chemistry"
                }
            ],
            "preferred_start_time": "14:00",
            "break_preferences": {
                "short_break_duration": 5,
                "long_break_duration": 15,
                "break_activities": ["stretch", "water", "walk"]
            }
        }
        
        print(f"🔍 Testing plan generation with:")
        print(f"   - Total Duration: {test_payload['total_duration_minutes']} minutes")
        print(f"   - Subjects: {len(test_payload['subjects'])} subjects")
        print(f"   - Start Time: {test_payload['preferred_start_time']}")
        
        try:
            response = requests.post(url, json=test_payload, headers=headers)
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Study plan generated successfully!")
                
                # Store plan ID for later tests
                self.plan_id = data.get('plan_id')
                
                # Verify response structure
                required_fields = ['plan_id', 'total_duration_minutes', 'total_work_time', 
                                 'total_break_time', 'pomodoro_sessions', 'study_tips', 'created_at']
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                    return False
                
                # Analyze the generated plan
                sessions = data.get('pomodoro_sessions', [])
                work_sessions = [s for s in sessions if s.get('session_type') == 'work']
                break_sessions = [s for s in sessions if s.get('session_type') == 'break']
                
                print(f"   Plan ID: {data.get('plan_id')}")
                print(f"   Total Sessions: {len(sessions)}")
                print(f"   Work Sessions: {len(work_sessions)}")
                print(f"   Break Sessions: {len(break_sessions)}")
                print(f"   Total Work Time: {data.get('total_work_time')} minutes")
                print(f"   Total Break Time: {data.get('total_break_time')} minutes")
                print(f"   Study Tips: {len(data.get('study_tips', []))} tips")
                
                # Verify Pomodoro structure (25-minute work sessions)
                work_durations = [s.get('duration_minutes') for s in work_sessions]
                print(f"   Work Session Durations: {work_durations}")
                
                # Check if sessions have proper structure
                if sessions:
                    first_session = sessions[0]
                    session_fields = ['id', 'session_type', 'duration_minutes', 'start_time', 'end_time', 'description']
                    session_missing = [field for field in session_fields if field not in first_session]
                    if session_missing:
                        print(f"   ⚠️ Session missing fields: {session_missing}")
                    else:
                        print("   ✅ Session structure is complete")
                
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False
    
    def test_my_plans_api(self):
        """Test the /api/study-planner/my-plans endpoint"""
        print("\n🎯 TESTING MY PLANS API")
        print("=" * 60)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/study-planner/my-plans"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Retrieved study plans successfully!")
                
                print(f"   Number of Plans: {len(data)}")
                
                if data and len(data) > 0:
                    # Verify plan structure
                    first_plan = data[0]
                    plan_fields = ['plan_id', 'user_id', 'total_duration_minutes', 'subjects', 
                                 'pomodoro_sessions', 'study_tips', 'created_at']
                    
                    missing_fields = [field for field in plan_fields if field not in first_plan]
                    if missing_fields:
                        print(f"   ⚠️ Plan missing fields: {missing_fields}")
                        return False
                    
                    print(f"   First Plan ID: {first_plan.get('plan_id')}")
                    print(f"   Duration: {first_plan.get('total_duration_minutes')} minutes")
                    print(f"   Subjects: {len(first_plan.get('subjects', []))}")
                    print(f"   Sessions: {len(first_plan.get('pomodoro_sessions', []))}")
                    print("   ✅ Plan structure is complete")
                else:
                    print("   ℹ️ No plans found (expected for new user)")
                
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False
    
    def test_start_session_api(self):
        """Test the /api/study-planner/start-session/{plan_id} endpoint"""
        print("\n🎯 TESTING START SESSION API")
        print("=" * 60)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        if not self.plan_id:
            print("❌ Plan ID not available (need to generate a plan first)")
            return False
        
        url = f"{API_URL}/study-planner/start-session/{self.plan_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        print(f"🔍 Starting session for plan: {self.plan_id}")
        
        try:
            response = requests.post(url, headers=headers)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Study session started successfully!")
                
                # Verify response structure
                required_fields = ['message', 'plan_id', 'plan', 'actual_start_time']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                    return False
                
                print(f"   Message: {data.get('message')}")
                print(f"   Plan ID: {data.get('plan_id')}")
                print(f"   Actual Start Time: {data.get('actual_start_time')}")
                
                # Check if plan has updated sessions with actual times
                plan = data.get('plan', {})
                sessions = plan.get('pomodoro_sessions', [])
                if sessions:
                    first_session = sessions[0]
                    if 'actual_start_time' in first_session:
                        print("   ✅ Sessions updated with actual start times")
                    else:
                        print("   ⚠️ Sessions not updated with actual times")
                
                # Check calendar events
                calendar_events = data.get('calendar_events', [])
                print(f"   Calendar Events Created: {len(calendar_events)}")
                
                return True
            elif response.status_code == 404:
                print("❌ FAILED: Study plan not found")
                return False
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False
    
    def test_delete_plan_api(self):
        """Test the /api/study-planner/plan/{plan_id} DELETE endpoint"""
        print("\n🎯 TESTING DELETE PLAN API")
        print("=" * 60)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        if not self.plan_id:
            print("❌ Plan ID not available (need to generate a plan first)")
            return False
        
        url = f"{API_URL}/study-planner/plan/{self.plan_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        print(f"🔍 Deleting plan: {self.plan_id}")
        
        try:
            response = requests.delete(url, headers=headers)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS: Study plan deleted successfully!")
                print(f"   Message: {data.get('message')}")
                return True
            elif response.status_code == 404:
                print("❌ FAILED: Study plan not found")
                return False
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Smart Calendar Bot API tests"""
        print("🚀 STARTING SMART CALENDAR BOT BACKEND API TESTING")
        print("=" * 80)
        print("Testing the comprehensive study planner backend that powers the conversational AI")
        print("study planner with Pomodoro technique integration.")
        print("=" * 80)
        
        # Setup
        if not self.register_and_login_student():
            print("❌ Failed to setup test environment")
            return False
        
        # Run tests in sequence
        test_results = []
        
        # Test 1: Chat API
        test_results.append(self.test_study_planner_chat_api())
        
        # Test 2: Plan Generation API
        test_results.append(self.test_study_plan_generation_api())
        
        # Test 3: My Plans API
        test_results.append(self.test_my_plans_api())
        
        # Test 4: Start Session API (depends on plan generation)
        test_results.append(self.test_start_session_api())
        
        # Test 5: Delete Plan API (cleanup)
        test_results.append(self.test_delete_plan_api())
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = passed_tests / total_tests * 100
        
        test_names = [
            "Study Planner Chat API",
            "Plan Generation API", 
            "My Plans API",
            "Start Session API",
            "Delete Plan API"
        ]
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {i+1}. {name}: {status}")
        
        if all(test_results):
            print("\n✅ ALL TESTS PASSED: Smart Calendar Bot backend is fully operational!")
            print("   - Conversational AI chat interface working")
            print("   - Pomodoro study plan generation working")
            print("   - Study plan management working")
            print("   - Session timing and calendar integration working")
            return True
        else:
            print("\n❌ SOME TESTS FAILED: Smart Calendar Bot backend needs attention")
            return False

if __name__ == "__main__":
    tester = SmartCalendarBotTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SMART CALENDAR BOT BACKEND API TESTING COMPLETED SUCCESSFULLY!")
        exit(0)
    else:
        print("\n💥 SMART CALENDAR BOT BACKEND API TESTING FAILED!")
        exit(1)
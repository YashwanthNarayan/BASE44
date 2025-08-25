#!/usr/bin/env python3
"""
Focused test for Smart Calendar Bot Backend API Implementation
Tests all study planner endpoints comprehensively
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 Testing Smart Calendar Bot Backend API at: {API_URL}")

class StudyPlannerTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.plan_id = None
        self.test_results = []

    def log_result(self, test_name, success, message="", details=None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if details and not success:
            print(f"    Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })

    def setup_student_account(self):
        """Register a student account for testing"""
        print("\n🔍 Setting up student account for study planner testing...")
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"study_planner_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Patel",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(url, json=payload)
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

    def test_study_planner_chat(self):
        """Test POST /api/study-planner/chat endpoint"""
        print("\n🔍 Testing Study Planner Chat API...")
        
        if not self.student_token:
            self.log_result("Study Planner Chat API", False, "No student token available")
            return False
        
        url = f"{API_URL}/study-planner/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different chat scenarios
        test_scenarios = [
            {
                "name": "Initial greeting",
                "payload": {
                    "message": "Hi, I need help creating a study plan",
                    "context": {}
                }
            },
            {
                "name": "Study requirements",
                "payload": {
                    "message": "I need to study math and physics for 2 hours total",
                    "context": {"stage": "requirements"}
                }
            },
            {
                "name": "Specific subjects",
                "payload": {
                    "message": "I want to focus on algebra and mechanics",
                    "context": {"subjects": ["math", "physics"], "duration": 120}
                }
            }
        ]
        
        success_count = 0
        for scenario in test_scenarios:
            try:
                response = requests.post(url, json=scenario["payload"], headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_fields = ["response", "needs_input", "suggested_actions"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        success_count += 1
                        print(f"  ✅ {scenario['name']}: {data.get('response', '')[:100]}...")
                    else:
                        print(f"  ❌ {scenario['name']}: Missing fields {missing_fields}")
                else:
                    print(f"  ❌ {scenario['name']}: Status {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"  ❌ {scenario['name']}: Exception {str(e)}")
        
        success = success_count == len(test_scenarios)
        self.log_result(
            "Study Planner Chat API", 
            success, 
            f"Passed {success_count}/{len(test_scenarios)} chat scenarios",
            f"Chat API working correctly with proper response structure" if success else "Some chat scenarios failed"
        )
        return success

    def test_generate_study_plan(self):
        """Test POST /api/study-planner/generate-plan endpoint"""
        print("\n🔍 Testing Generate Study Plan API...")
        
        if not self.student_token:
            self.log_result("Generate Study Plan API", False, "No student token available")
            return False
        
        url = f"{API_URL}/study-planner/generate-plan"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test plan generation with realistic data
        payload = {
            "total_duration_minutes": 120,
            "subjects": [
                {
                    "subject": "mathematics",
                    "duration_minutes": 50,
                    "priority": "high",
                    "notes": "Focus on algebra and calculus"
                },
                {
                    "subject": "physics",
                    "duration_minutes": 40,
                    "priority": "medium",
                    "notes": "Mechanics and thermodynamics"
                },
                {
                    "subject": "chemistry",
                    "duration_minutes": 30,
                    "priority": "low",
                    "notes": "Organic chemistry basics"
                }
            ],
            "preferred_start_time": "14:00",
            "break_preferences": {
                "short_break_duration": 5,
                "long_break_duration": 15
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = [
                    "plan_id", "total_duration_minutes", "total_work_time", 
                    "total_break_time", "pomodoro_sessions", "study_tips", "created_at"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.plan_id = data.get("plan_id")  # Save for later tests
                    sessions = data.get("pomodoro_sessions", [])
                    work_sessions = [s for s in sessions if s.get("session_type") == "work"]
                    break_sessions = [s for s in sessions if s.get("session_type") == "break"]
                    
                    self.log_result(
                        "Generate Study Plan API", 
                        True, 
                        f"Generated plan with {len(sessions)} total sessions ({len(work_sessions)} work + {len(break_sessions)} break)",
                        f"Plan ID: {self.plan_id}, Total duration: {data.get('total_duration_minutes')} min"
                    )
                    return True
                else:
                    self.log_result(
                        "Generate Study Plan API", 
                        False, 
                        f"Missing required fields: {missing_fields}",
                        response.text
                    )
                    return False
            else:
                self.log_result(
                    "Generate Study Plan API", 
                    False, 
                    f"Status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Generate Study Plan API", False, f"Exception: {str(e)}")
            return False

    def test_get_my_plans(self):
        """Test GET /api/study-planner/my-plans endpoint"""
        print("\n🔍 Testing Get My Plans API...")
        
        if not self.student_token:
            self.log_result("Get My Plans API", False, "No student token available")
            return False
        
        url = f"{API_URL}/study-planner/my-plans"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Verify structure of first plan
                        first_plan = data[0]
                        required_fields = ["plan_id", "user_id", "total_duration_minutes", "subjects", "pomodoro_sessions"]
                        missing_fields = [field for field in required_fields if field not in first_plan]
                        
                        if not missing_fields:
                            self.log_result(
                                "Get My Plans API", 
                                True, 
                                f"Retrieved {len(data)} study plans",
                                f"Plans contain all required fields"
                            )
                            return True
                        else:
                            self.log_result(
                                "Get My Plans API", 
                                False, 
                                f"Plan missing fields: {missing_fields}",
                                json.dumps(first_plan, indent=2)
                            )
                            return False
                    else:
                        self.log_result(
                            "Get My Plans API", 
                            True, 
                            "No plans found (empty list - valid response)",
                            "User has no study plans yet"
                        )
                        return True
                else:
                    self.log_result(
                        "Get My Plans API", 
                        False, 
                        "Response is not a list",
                        f"Response type: {type(data)}"
                    )
                    return False
            else:
                self.log_result(
                    "Get My Plans API", 
                    False, 
                    f"Status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Get My Plans API", False, f"Exception: {str(e)}")
            return False

    def test_start_study_session(self):
        """Test POST /api/study-planner/start-session/{plan_id} endpoint"""
        print("\n🔍 Testing Start Study Session API...")
        
        if not self.student_token:
            self.log_result("Start Study Session API", False, "No student token available")
            return False
        
        if not self.plan_id:
            self.log_result("Start Study Session API", False, "No plan ID available (generate plan first)")
            return False
        
        url = f"{API_URL}/study-planner/start-session/{self.plan_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["message", "plan_id", "plan", "actual_start_time"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    plan_data = data.get("plan", {})
                    calendar_events = data.get("calendar_events", [])
                    
                    self.log_result(
                        "Start Study Session API", 
                        True, 
                        f"Started session for plan {data.get('plan_id')}",
                        f"Created {len(calendar_events)} calendar events, Start time: {data.get('actual_start_time')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Start Study Session API", 
                        False, 
                        f"Missing required fields: {missing_fields}",
                        response.text
                    )
                    return False
            else:
                self.log_result(
                    "Start Study Session API", 
                    False, 
                    f"Status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Start Study Session API", False, f"Exception: {str(e)}")
            return False

    def test_delete_study_plan(self):
        """Test DELETE /api/study-planner/plan/{plan_id} endpoint"""
        print("\n🔍 Testing Delete Study Plan API...")
        
        if not self.student_token:
            self.log_result("Delete Study Plan API", False, "No student token available")
            return False
        
        if not self.plan_id:
            self.log_result("Delete Study Plan API", False, "No plan ID available")
            return False
        
        url = f"{API_URL}/study-planner/plan/{self.plan_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data:
                    self.log_result(
                        "Delete Study Plan API", 
                        True, 
                        f"Successfully deleted plan {self.plan_id}",
                        data.get("message")
                    )
                    return True
                else:
                    self.log_result(
                        "Delete Study Plan API", 
                        False, 
                        "No message in response",
                        response.text
                    )
                    return False
            else:
                self.log_result(
                    "Delete Study Plan API", 
                    False, 
                    f"Status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Delete Study Plan API", False, f"Exception: {str(e)}")
            return False

    def test_authentication_requirements(self):
        """Test that all endpoints require proper authentication"""
        print("\n🔍 Testing Authentication Requirements...")
        
        endpoints = [
            ("POST", "/study-planner/chat", {"message": "test"}),
            ("POST", "/study-planner/generate-plan", {"total_duration_minutes": 60, "subjects": []}),
            ("GET", "/study-planner/my-plans", None),
            ("POST", "/study-planner/start-session/test-id", None),
            ("DELETE", "/study-planner/plan/test-id", None)
        ]
        
        success_count = 0
        for method, endpoint, payload in endpoints:
            try:
                url = f"{API_URL}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url)
                elif method == "POST":
                    response = requests.post(url, json=payload)
                elif method == "DELETE":
                    response = requests.delete(url)
                
                # Should return 401 or 403 for missing authentication
                if response.status_code in [401, 403]:
                    success_count += 1
                    print(f"  ✅ {method} {endpoint}: Correctly requires authentication ({response.status_code})")
                else:
                    print(f"  ❌ {method} {endpoint}: Should require auth but returned {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {method} {endpoint}: Exception {str(e)}")
        
        success = success_count == len(endpoints)
        self.log_result(
            "Authentication Requirements", 
            success, 
            f"Passed {success_count}/{len(endpoints)} authentication checks",
            "All endpoints properly require authentication" if success else "Some endpoints don't require authentication"
        )
        return success

    def run_comprehensive_test(self):
        """Run all study planner tests"""
        print("\n" + "="*80)
        print("🎯 SMART CALENDAR BOT BACKEND API COMPREHENSIVE TESTING")
        print("="*80)
        
        # Setup
        if not self.setup_student_account():
            print("❌ Failed to setup student account - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = []
        test_results.append(self.test_authentication_requirements())
        test_results.append(self.test_study_planner_chat())
        test_results.append(self.test_generate_study_plan())
        test_results.append(self.test_get_my_plans())
        test_results.append(self.test_start_study_session())
        test_results.append(self.test_delete_study_plan())
        
        # Summary
        print("\n" + "="*80)
        print("📊 SMART CALENDAR BOT BACKEND API TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result["message"]:
                print(f"    {result['message']}")
        
        if passed == total:
            print("\n🎉 ALL SMART CALENDAR BOT BACKEND API TESTS PASSED!")
            print("✅ The Smart Calendar Bot Backend API is fully operational and ready for frontend integration.")
        else:
            print(f"\n⚠️  {total-passed} tests failed - Issues found in Smart Calendar Bot Backend API")
            
        return passed == total

if __name__ == "__main__":
    tester = StudyPlannerTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
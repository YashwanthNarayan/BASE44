#!/usr/bin/env python3
"""
Modern UI Components API Testing
Tests specific API endpoints used by modern UI components that are showing "failed to load data" messages
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

print(f"🎯 MODERN UI COMPONENTS API TESTING")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class ModernUIAPITester:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.session_id = None
        self.note_id = None
        self.test_results = []

    def log_result(self, test_name, success, message="", details=None):
        """Log test result with details"""
        status = "✅ WORKING" if success else "❌ FAILING"
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

    def setup_accounts(self):
        """Setup student and teacher accounts for testing"""
        print("\n🔧 SETTING UP TEST ACCOUNTS...")
        
        # Register student
        student_payload = {
            "email": f"modern_ui_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Modern UI Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(f"{API_URL}/auth/register", json=student_payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student account created: {self.student_id}")
            else:
                print(f"❌ Failed to create student account: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating student account: {str(e)}")
            return False
        
        # Register teacher
        teacher_payload = {
            "email": f"modern_ui_teacher_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Modern UI Test Teacher",
            "user_type": "teacher",
            "school_name": "Modern UI Test School"
        }
        
        try:
            response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"✅ Teacher account created: {self.teacher_id}")
                return True
            else:
                print(f"❌ Failed to create teacher account: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating teacher account: {str(e)}")
            return False

    def test_student_dashboard_apis(self):
        """Test Student Dashboard APIs"""
        print("\n1️⃣ TESTING STUDENT DASHBOARD APIs...")
        
        if not self.student_token:
            self.log_result("Student Dashboard APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/student/dashboard (for dashboard data)
        try:
            response = requests.get(f"{API_URL}/dashboard", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "profile" in data and "total_xp" in data:
                    self.log_result("Student Dashboard API (/api/dashboard)", True, "Dashboard data loaded successfully")
                else:
                    self.log_result("Student Dashboard API (/api/dashboard)", False, "Missing expected fields in dashboard response")
            else:
                self.log_result("Student Dashboard API (/api/dashboard)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Student Dashboard API (/api/dashboard)", False, f"Exception: {str(e)}")
        
        # Test /api/student/progress (for XP, tests, scores) - This endpoint doesn't exist, testing alternatives
        try:
            response = requests.get(f"{API_URL}/student/profile", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "total_xp" in data or "level" in data:
                    self.log_result("Student Progress API (/api/student/profile)", True, "Student progress data available")
                else:
                    self.log_result("Student Progress API (/api/student/profile)", False, "Missing progress fields in profile")
            else:
                self.log_result("Student Progress API (/api/student/profile)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Student Progress API (/api/student/profile)", False, f"Exception: {str(e)}")

    def test_progress_component_apis(self):
        """Test Progress Component APIs"""
        print("\n2️⃣ TESTING PROGRESS COMPONENT APIs...")
        
        if not self.student_token:
            self.log_result("Progress Component APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/student/progress (for overall progress) - Alternative: /api/practice/results
        try:
            response = requests.get(f"{API_URL}/practice/results", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Progress Component API (/api/practice/results)", True, f"Retrieved {len(data)} practice results")
            else:
                self.log_result("Progress Component API (/api/practice/results)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Progress Component API (/api/practice/results)", False, f"Exception: {str(e)}")
        
        # Test /api/student/test-results (for recent test results) - Alternative: /api/practice/stats/{subject}
        try:
            response = requests.get(f"{API_URL}/practice/stats/math", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "total_tests" in data and "average_score" in data:
                    self.log_result("Test Results API (/api/practice/stats/math)", True, f"Math stats: {data.get('total_tests', 0)} tests, avg: {data.get('average_score', 0)}%")
                else:
                    self.log_result("Test Results API (/api/practice/stats/math)", False, "Missing expected stats fields")
            else:
                self.log_result("Test Results API (/api/practice/stats/math)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test Results API (/api/practice/stats/math)", False, f"Exception: {str(e)}")

    def test_notes_component_apis(self):
        """Test Notes Component APIs"""
        print("\n3️⃣ TESTING NOTES COMPONENT APIs...")
        
        if not self.student_token:
            self.log_result("Notes Component APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/notes/user (for loading user notes) - Alternative: /api/notes/
        try:
            response = requests.get(f"{API_URL}/notes/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Notes Load API (/api/notes/)", True, f"Retrieved {len(data)} notes")
            else:
                self.log_result("Notes Load API (/api/notes/)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Notes Load API (/api/notes/)", False, f"Exception: {str(e)}")
        
        # Test /api/notes/create (for creating notes) - Alternative: /api/notes/generate
        try:
            create_payload = {
                "subject": "math",
                "topic": "Quadratic Equations",
                "grade_level": "10th"
            }
            response = requests.post(f"{API_URL}/notes/generate", json=create_payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.note_id = data.get("note_id")
                self.log_result("Notes Create API (/api/notes/generate)", True, f"Created note: {self.note_id}")
            else:
                self.log_result("Notes Create API (/api/notes/generate)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Notes Create API (/api/notes/generate)", False, f"Exception: {str(e)}")
        
        # Test /api/notes/update/{id} (for updating notes) - Alternative: /api/notes/{id}/favorite
        if self.note_id:
            try:
                response = requests.put(f"{API_URL}/notes/{self.note_id}/favorite", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Notes Update API (/api/notes/{id}/favorite)", True, f"Updated note favorite status")
                else:
                    self.log_result("Notes Update API (/api/notes/{id}/favorite)", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Notes Update API (/api/notes/{id}/favorite)", False, f"Exception: {str(e)}")
        
        # Test /api/notes/delete/{id} (for deleting notes)
        if self.note_id:
            try:
                response = requests.delete(f"{API_URL}/notes/{self.note_id}/delete", headers=headers)
                if response.status_code == 200:
                    self.log_result("Notes Delete API (/api/notes/{id}/delete)", True, "Note deleted successfully")
                else:
                    self.log_result("Notes Delete API (/api/notes/{id}/delete)", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Notes Delete API (/api/notes/{id}/delete)", False, f"Exception: {str(e)}")

    def test_scheduled_tests_apis(self):
        """Test Scheduled Tests APIs"""
        print("\n4️⃣ TESTING SCHEDULED TESTS APIs...")
        
        if not self.student_token:
            self.log_result("Scheduled Tests APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/practice-scheduler/scheduled-tests (for loading scheduled tests) - Alternative: /api/practice-scheduler/upcoming-tests
        try:
            response = requests.get(f"{API_URL}/practice-scheduler/upcoming-tests", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total_tests = sum(len(tests) for tests in data.values()) if isinstance(data, dict) else len(data)
                self.log_result("Scheduled Tests Load API (/api/practice-scheduler/upcoming-tests)", True, f"Retrieved {total_tests} scheduled tests")
            else:
                self.log_result("Scheduled Tests Load API (/api/practice-scheduler/upcoming-tests)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Scheduled Tests Load API (/api/practice-scheduler/upcoming-tests)", False, f"Exception: {str(e)}")
        
        # Test /api/practice-scheduler/complete-scheduled-test/{test_id} (for completing tests)
        # First create a scheduled test to complete
        try:
            schedule_payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "original_score": 75.0,
                "question_count": 3
            }
            response = requests.post(f"{API_URL}/practice-scheduler/schedule-review", json=schedule_payload, headers=headers)
            if response.status_code == 200:
                self.log_result("Schedule Test Creation", True, "Test scheduled for completion testing")
            else:
                self.log_result("Schedule Test Creation", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Schedule Test Creation", False, f"Exception: {str(e)}")

    def test_analytics_apis(self):
        """Test Analytics APIs"""
        print("\n5️⃣ TESTING ANALYTICS APIs...")
        
        if not self.student_token:
            self.log_result("Analytics APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/student-analytics/strengths (for strengths data)
        try:
            response = requests.get(f"{API_URL}/student/analytics/strengths-weaknesses", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "strengths" in data or "weaknesses" in data:
                    self.log_result("Analytics Strengths API (/api/student/analytics/strengths-weaknesses)", True, "Strengths/weaknesses data available")
                else:
                    self.log_result("Analytics Strengths API (/api/student/analytics/strengths-weaknesses)", False, "Missing strengths/weaknesses in response")
            else:
                self.log_result("Analytics Strengths API (/api/student/analytics/strengths-weaknesses)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Analytics Strengths API (/api/student/analytics/strengths-weaknesses)", False, f"Exception: {str(e)}")
        
        # Test /api/student-analytics/performance-trends (for trends)
        try:
            response = requests.get(f"{API_URL}/student/analytics/performance-trends?days=7", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Analytics Performance Trends API", True, "Performance trends data available")
            else:
                self.log_result("Analytics Performance Trends API", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Analytics Performance Trends API", False, f"Exception: {str(e)}")
        
        # Test /api/student-analytics/subject-breakdown (for subject data)
        try:
            response = requests.get(f"{API_URL}/student/analytics/subject-breakdown", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "subject_breakdown" in data:
                    self.log_result("Analytics Subject Breakdown API", True, f"Subject breakdown with {len(data.get('subject_breakdown', []))} subjects")
                else:
                    self.log_result("Analytics Subject Breakdown API", False, "Missing subject_breakdown in response")
            else:
                self.log_result("Analytics Subject Breakdown API", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Analytics Subject Breakdown API", False, f"Exception: {str(e)}")
        
        # Test /api/student-analytics/learning-insights (for insights)
        try:
            response = requests.get(f"{API_URL}/student/analytics/learning-insights", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "insights" in data:
                    self.log_result("Analytics Learning Insights API", True, f"Learning insights with {len(data.get('insights', []))} insights")
                else:
                    self.log_result("Analytics Learning Insights API", False, "Missing insights in response")
            else:
                self.log_result("Analytics Learning Insights API", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Analytics Learning Insights API", False, f"Exception: {str(e)}")

    def test_tutor_component_apis(self):
        """Test Tutor Component APIs"""
        print("\n6️⃣ TESTING TUTOR COMPONENT APIs...")
        
        if not self.student_token:
            self.log_result("Tutor Component APIs", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test /api/tutor/chat (for AI chat functionality)
        # First create a session
        try:
            session_payload = {"subject": "math", "session_type": "tutoring"}
            response = requests.post(f"{API_URL}/tutor/session", json=session_payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                self.log_result("Tutor Session Creation", True, f"Created session: {self.session_id}")
            else:
                self.log_result("Tutor Session Creation", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Tutor Session Creation", False, f"Exception: {str(e)}")
        
        # Test chat functionality
        if self.session_id:
            try:
                chat_payload = {
                    "message": "Can you help me with quadratic equations?",
                    "subject": "math",
                    "session_id": self.session_id
                }
                response = requests.post(f"{API_URL}/tutor/chat", json=chat_payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data:
                        self.log_result("Tutor Chat API (/api/tutor/chat)", True, "AI chat response received")
                    else:
                        self.log_result("Tutor Chat API (/api/tutor/chat)", False, "Missing response in chat data")
                else:
                    self.log_result("Tutor Chat API (/api/tutor/chat)", False, f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Tutor Chat API (/api/tutor/chat)", False, f"Exception: {str(e)}")

    def create_test_data(self):
        """Create some test data to make the APIs return meaningful results"""
        print("\n📊 CREATING TEST DATA FOR BETTER API TESTING...")
        
        if not self.student_token:
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Generate and submit a practice test to create data for progress/analytics APIs
        try:
            # Generate test
            gen_payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 3
            }
            
            gen_response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                questions = gen_data.get("questions", [])
                
                if questions:
                    # Submit test with correct answers
                    student_answers = {}
                    question_ids = []
                    for question in questions:
                        question_id = question.get("id")
                        question_ids.append(question_id)
                        student_answers[question_id] = question.get("correct_answer")
                    
                    submit_payload = {
                        "questions": question_ids,
                        "student_answers": student_answers,
                        "subject": "math",
                        "time_taken": 300
                    }
                    
                    submit_response = requests.post(f"{API_URL}/practice/submit", json=submit_payload, headers=headers)
                    if submit_response.status_code == 200:
                        print("✅ Created test data: Practice test completed")
                    else:
                        print(f"❌ Failed to submit test data: {submit_response.status_code}")
                else:
                    print("❌ No questions generated for test data")
            else:
                print(f"❌ Failed to generate test data: {gen_response.status_code}")
        except Exception as e:
            print(f"❌ Error creating test data: {str(e)}")

    def run_comprehensive_test(self):
        """Run all comprehensive tests for modern UI components"""
        print("🚀 STARTING MODERN UI COMPONENTS API TESTING")
        
        # Setup
        if not self.setup_accounts():
            print("❌ Failed to setup accounts - cannot proceed")
            return False
        
        # Create test data first
        self.create_test_data()
        
        # Run all API tests
        test_functions = [
            self.test_student_dashboard_apis,
            self.test_progress_component_apis,
            self.test_notes_component_apis,
            self.test_scheduled_tests_apis,
            self.test_analytics_apis,
            self.test_tutor_component_apis
        ]
        
        for test_func in test_functions:
            test_func()
        
        # Summary
        print("\n" + "="*80)
        print("📊 MODERN UI COMPONENTS API TEST SUMMARY")
        print("="*80)
        
        working_apis = [result for result in self.test_results if result["success"]]
        failing_apis = [result for result in self.test_results if not result["success"]]
        
        print(f"\n✅ WORKING APIs ({len(working_apis)}):")
        for result in working_apis:
            print(f"   • {result['test']}: {result['message']}")
        
        if failing_apis:
            print(f"\n❌ FAILING APIs ({len(failing_apis)}):")
            for result in failing_apis:
                print(f"   • {result['test']}: {result['message']}")
                if result.get('details'):
                    print(f"     Details: {result['details'][:200]}...")
        
        success_rate = (len(working_apis) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n📈 SUCCESS RATE: {success_rate:.1f}% ({len(working_apis)}/{len(self.test_results)} APIs working)")
        
        if success_rate >= 80:
            print("\n🎉 MODERN UI COMPONENTS APIs ARE MOSTLY WORKING!")
            print("✅ Most critical APIs are operational")
        else:
            print("\n⚠️ MODERN UI COMPONENTS HAVE SIGNIFICANT API ISSUES")
            print("❌ Multiple APIs are failing - this explains the 'failed to load data' messages")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ModernUIAPITester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
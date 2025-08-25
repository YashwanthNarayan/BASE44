#!/usr/bin/env python3
"""
Comprehensive Backend Test for Critical Pre-Demo Verification
Tests all major backend endpoints and features as requested in the review
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

print(f"🎯 CRITICAL PRE-DEMO VERIFICATION")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class ComprehensiveBackendTester:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        self.session_id = None
        self.plan_id = None
        self.test_results = []

    def log_result(self, test_name, success, message="", details=None):
        """Log test result with details"""
        status = "✅ WORKING" if success else "❌ BROKEN"
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
        """Setup student and teacher accounts"""
        print("\n🔧 SETTING UP TEST ACCOUNTS...")
        
        # Register student
        student_payload = {
            "email": f"demo_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Demo Student",
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
                print(f"❌ Failed to create student account: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating student account: {str(e)}")
            return False
        
        # Register teacher
        teacher_payload = {
            "email": f"demo_teacher_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Demo Teacher",
            "user_type": "teacher",
            "school_name": "Demo School"
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
                print(f"❌ Failed to create teacher account: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating teacher account: {str(e)}")
            return False

    def test_authentication_system(self):
        """Test 1: Authentication System"""
        print("\n1️⃣ TESTING AUTHENTICATION SYSTEM...")
        
        # Test login
        login_payload = {
            "email": "demo_student_test@example.com",
            "password": "SecurePass123!"
        }
        
        # First register the account
        register_payload = {
            "email": "demo_student_test@example.com",
            "password": "SecurePass123!",
            "name": "Login Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            # Register
            register_response = requests.post(f"{API_URL}/auth/register", json=register_payload)
            if register_response.status_code != 200:
                self.log_result("Authentication System", False, "Registration failed", register_response.text)
                return False
            
            # Login
            login_response = requests.post(f"{API_URL}/auth/login", json=login_payload)
            if login_response.status_code == 200:
                login_data = login_response.json()
                if login_data.get("access_token"):
                    self.log_result("Authentication System", True, "Registration, login, JWT tokens working")
                    return True
                else:
                    self.log_result("Authentication System", False, "No access token in login response")
                    return False
            else:
                self.log_result("Authentication System", False, f"Login failed: {login_response.status_code}", login_response.text)
                return False
        except Exception as e:
            self.log_result("Authentication System", False, f"Exception: {str(e)}")
            return False

    def test_practice_tests(self):
        """Test 2: Practice Tests"""
        print("\n2️⃣ TESTING PRACTICE TESTS...")
        
        if not self.student_token:
            self.log_result("Practice Tests", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test generation
        gen_payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        try:
            # Generate test
            gen_response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
            if gen_response.status_code != 200:
                self.log_result("Practice Tests", False, f"Generation failed: {gen_response.status_code}", gen_response.text)
                return False
            
            gen_data = gen_response.json()
            questions = gen_data.get("questions", [])
            test_id = gen_data.get("test_id")
            
            if not questions or not test_id:
                self.log_result("Practice Tests", False, "No questions or test_id in response")
                return False
            
            # Test submission
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
                submit_data = submit_response.json()
                score = submit_data.get("score", 0)
                self.log_result("Practice Tests", True, f"Generation, submission, scoring working (Score: {score}%)")
                return True
            else:
                self.log_result("Practice Tests", False, f"Submission failed: {submit_response.status_code}", submit_response.text)
                return False
                
        except Exception as e:
            self.log_result("Practice Tests", False, f"Exception: {str(e)}")
            return False

    def test_ai_tutor(self):
        """Test 3: AI Tutor"""
        print("\n3️⃣ TESTING AI TUTOR...")
        
        if not self.student_token:
            self.log_result("AI Tutor", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Create session
            session_payload = {"subject": "math"}
            session_response = requests.post(f"{API_URL}/tutor/session", json=session_payload, headers=headers)
            
            if session_response.status_code != 200:
                self.log_result("AI Tutor", False, f"Session creation failed: {session_response.status_code}", session_response.text)
                return False
            
            session_data = session_response.json()
            self.session_id = session_data.get("session_id")
            
            # Send chat message
            chat_payload = {
                "session_id": self.session_id,
                "message": "Can you help me with quadratic equations?",
                "subject": "math"
            }
            
            chat_response = requests.post(f"{API_URL}/tutor/chat", json=chat_payload, headers=headers)
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                if chat_data.get("response"):
                    self.log_result("AI Tutor", True, "Chat sessions, AI responses, conversation history working")
                    return True
                else:
                    self.log_result("AI Tutor", False, "No response in chat data")
                    return False
            else:
                self.log_result("AI Tutor", False, f"Chat failed: {chat_response.status_code}", chat_response.text)
                return False
                
        except Exception as e:
            self.log_result("AI Tutor", False, f"Exception: {str(e)}")
            return False

    def test_study_planner(self):
        """Test 4: Study Planner"""
        print("\n4️⃣ TESTING STUDY PLANNER...")
        
        if not self.student_token:
            self.log_result("Study Planner", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test chat
            chat_payload = {
                "message": "I need help creating a study plan for 2 hours",
                "context": {}
            }
            
            chat_response = requests.post(f"{API_URL}/study-planner/chat", json=chat_payload, headers=headers)
            if chat_response.status_code != 200:
                self.log_result("Study Planner", False, f"Chat failed: {chat_response.status_code}", chat_response.text)
                return False
            
            # Test plan generation
            plan_payload = {
                "total_duration_minutes": 120,
                "subjects": [
                    {"subject": "math", "duration_minutes": 60, "priority": "high"},
                    {"subject": "physics", "duration_minutes": 60, "priority": "medium"}
                ]
            }
            
            plan_response = requests.post(f"{API_URL}/study-planner/generate-plan", json=plan_payload, headers=headers)
            if plan_response.status_code == 200:
                plan_data = plan_response.json()
                self.plan_id = plan_data.get("plan_id")
                sessions = plan_data.get("pomodoro_sessions", [])
                self.log_result("Study Planner", True, f"Smart calendar bot, Pomodoro planning working ({len(sessions)} sessions)")
                return True
            else:
                self.log_result("Study Planner", False, f"Plan generation failed: {plan_response.status_code}", plan_response.text)
                return False
                
        except Exception as e:
            self.log_result("Study Planner", False, f"Exception: {str(e)}")
            return False

    def test_notes_system(self):
        """Test 5: Notes System"""
        print("\n5️⃣ TESTING NOTES SYSTEM...")
        
        if not self.student_token:
            self.log_result("Notes System", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test notes generation
            notes_payload = {
                "subject": "math",
                "topic": "Quadratic Equations",
                "content": "Key concepts about solving quadratic equations using factoring and quadratic formula"
            }
            
            notes_response = requests.post(f"{API_URL}/notes/generate", json=notes_payload, headers=headers)
            if notes_response.status_code == 200:
                # Test getting notes
                get_response = requests.get(f"{API_URL}/notes", headers=headers)
                if get_response.status_code == 200:
                    self.log_result("Notes System", True, "AI note generation, storage, retrieval working")
                    return True
                else:
                    self.log_result("Notes System", False, f"Get notes failed: {get_response.status_code}")
                    return False
            else:
                self.log_result("Notes System", False, f"Notes generation failed: {notes_response.status_code}", notes_response.text)
                return False
                
        except Exception as e:
            self.log_result("Notes System", False, f"Exception: {str(e)}")
            return False

    def test_scheduled_tests(self):
        """Test 6: Scheduled Tests"""
        print("\n6️⃣ TESTING SCHEDULED TESTS...")
        
        if not self.student_token:
            self.log_result("Scheduled Tests", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test creating scheduled test
            schedule_payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 3,
                "scheduled_for": "2025-08-26T10:00:00Z"
            }
            
            schedule_response = requests.post(f"{API_URL}/practice-scheduler/schedule", json=schedule_payload, headers=headers)
            if schedule_response.status_code == 200:
                # Test getting scheduled tests
                get_response = requests.get(f"{API_URL}/practice-scheduler/my-tests", headers=headers)
                if get_response.status_code == 200:
                    self.log_result("Scheduled Tests", True, "Spaced repetition system, test scheduling working")
                    return True
                else:
                    self.log_result("Scheduled Tests", False, f"Get scheduled tests failed: {get_response.status_code}")
                    return False
            else:
                self.log_result("Scheduled Tests", False, f"Schedule test failed: {schedule_response.status_code}", schedule_response.text)
                return False
                
        except Exception as e:
            self.log_result("Scheduled Tests", False, f"Exception: {str(e)}")
            return False

    def test_student_analytics(self):
        """Test 7: Student Analytics"""
        print("\n7️⃣ TESTING STUDENT ANALYTICS...")
        
        if not self.student_token:
            self.log_result("Student Analytics", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test strengths/weaknesses
            strengths_response = requests.get(f"{API_URL}/student/analytics/strengths-weaknesses", headers=headers)
            if strengths_response.status_code != 200:
                self.log_result("Student Analytics", False, f"Strengths analysis failed: {strengths_response.status_code}")
                return False
            
            # Test performance trends
            trends_response = requests.get(f"{API_URL}/student/analytics/performance-trends?days=7", headers=headers)
            if trends_response.status_code != 200:
                self.log_result("Student Analytics", False, f"Performance trends failed: {trends_response.status_code}")
                return False
            
            # Test subject breakdown
            breakdown_response = requests.get(f"{API_URL}/student/analytics/subject-breakdown", headers=headers)
            if breakdown_response.status_code == 200:
                self.log_result("Student Analytics", True, "Strengths/weaknesses analysis, performance trends working")
                return True
            else:
                self.log_result("Student Analytics", False, f"Subject breakdown failed: {breakdown_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Student Analytics", False, f"Exception: {str(e)}")
            return False

    def test_teacher_features(self):
        """Test 8: Teacher Features"""
        print("\n8️⃣ TESTING TEACHER FEATURES...")
        
        if not self.teacher_token:
            self.log_result("Teacher Features", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # Test class creation
            class_payload = {
                "subject": "math",
                "class_name": "Demo Math Class",
                "grade_level": "10th",
                "description": "Demo class for testing"
            }
            
            class_response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
            if class_response.status_code != 200:
                self.log_result("Teacher Features", False, f"Class creation failed: {class_response.status_code}", class_response.text)
                return False
            
            class_data = class_response.json()
            self.class_id = class_data.get("class_id")
            
            # Test analytics overview
            analytics_response = requests.get(f"{API_URL}/teacher/analytics/overview", headers=headers)
            if analytics_response.status_code == 200:
                self.log_result("Teacher Features", True, "Analytics dashboard, class management working")
                return True
            else:
                self.log_result("Teacher Features", False, f"Analytics overview failed: {analytics_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Teacher Features", False, f"Exception: {str(e)}")
            return False

    def test_progress_tracking(self):
        """Test 9: Progress Tracking"""
        print("\n9️⃣ TESTING PROGRESS TRACKING...")
        
        if not self.student_token:
            self.log_result("Progress Tracking", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test getting practice results
            results_response = requests.get(f"{API_URL}/practice/results", headers=headers)
            if results_response.status_code != 200:
                self.log_result("Progress Tracking", False, f"Practice results failed: {results_response.status_code}")
                return False
            
            # Test getting stats
            stats_response = requests.get(f"{API_URL}/practice/stats/math", headers=headers)
            if stats_response.status_code == 200:
                self.log_result("Progress Tracking", True, "Practice test history, statistics working")
                return True
            else:
                self.log_result("Progress Tracking", False, f"Practice stats failed: {stats_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Progress Tracking", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING FOR DEMO")
        
        # Setup
        if not self.setup_accounts():
            print("❌ Failed to setup accounts - cannot proceed")
            return False
        
        # Run all critical tests
        test_functions = [
            self.test_authentication_system,
            self.test_practice_tests,
            self.test_ai_tutor,
            self.test_study_planner,
            self.test_notes_system,
            self.test_scheduled_tests,
            self.test_student_analytics,
            self.test_teacher_features,
            self.test_progress_tracking
        ]
        
        for test_func in test_functions:
            test_func()
        
        # Summary
        print("\n" + "="*80)
        print("📊 CRITICAL PRE-DEMO VERIFICATION SUMMARY")
        print("="*80)
        
        working_features = [result for result in self.test_results if result["success"]]
        broken_features = [result for result in self.test_results if not result["success"]]
        
        print(f"\n✅ WORKING FEATURES ({len(working_features)}):")
        for result in working_features:
            print(f"   • {result['test']}: {result['message']}")
        
        if broken_features:
            print(f"\n❌ BROKEN FEATURES ({len(broken_features)}):")
            for result in broken_features:
                print(f"   • {result['test']}: {result['message']}")
        
        success_rate = (len(working_features) / len(self.test_results)) * 100
        print(f"\n📈 SUCCESS RATE: {success_rate:.1f}% ({len(working_features)}/{len(self.test_results)} features working)")
        
        if success_rate >= 80:
            print("\n🎉 BACKEND IS DEMO-READY!")
            print("✅ Most critical features are operational")
        else:
            print("\n⚠️ BACKEND NEEDS FIXES BEFORE DEMO")
            print("❌ Too many critical features are broken")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
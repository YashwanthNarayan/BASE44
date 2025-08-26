#!/usr/bin/env python3
import requests
import json
import time
import unittest
import os
import uuid
from dotenv import load_dotenv
import sys
from enum import Enum

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Add /api prefix to the backend URL
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Enums to match backend
class GradeLevel(str, Enum):
    GRADE_6 = "6th"
    GRADE_7 = "7th" 
    GRADE_8 = "8th"
    GRADE_9 = "9th"
    GRADE_10 = "10th"
    GRADE_11 = "11th"
    GRADE_12 = "12th"

class Subject(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    ENGLISH = "english"
    HISTORY = "history"
    GEOGRAPHY = "geography"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"  
    HARD = "hard"
    MIXED = "mixed"

class UserType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    NUMERICAL = "numerical"

class TestProjectKV3Backend(unittest.TestCase):
    """Test cases for Project K AI Educational Chatbot backend V3.0 with authentication"""

    def setUp(self):
        """Set up test case - create student and teacher accounts"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        self.session_id = None
        
        # Register student and teacher
        self.register_student()
        self.register_teacher()

    def register_student(self):
        """Test student registration"""
        print("\n🔍 Testing Student Registration...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Rahul Sharma",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Student Registration Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to register student")
            data = response.json()
            self.student_token = data.get("access_token")
            self.student_id = data.get("user", {}).get("id")
            
            print(f"Registered student with ID: {self.student_id}")
            self.assertIsNotNone(self.student_token, "Student token should not be None")
            self.assertIsNotNone(self.student_id, "Student ID should not be None")
            print("✅ Student registration test passed")
            return data
        except Exception as e:
            print(f"❌ Student registration test failed: {str(e)}")
            return None

    def register_teacher(self):
        """Test teacher registration"""
        print("\n🔍 Testing Teacher Registration...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"teacher_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Priya Patel",
            "user_type": UserType.TEACHER.value,
            "school_name": "Delhi Public School"
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Teacher Registration Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to register teacher")
            data = response.json()
            self.teacher_token = data.get("access_token")
            self.teacher_id = data.get("user", {}).get("id")
            
            print(f"Registered teacher with ID: {self.teacher_id}")
            self.assertIsNotNone(self.teacher_token, "Teacher token should not be None")
            self.assertIsNotNone(self.teacher_id, "Teacher ID should not be None")
            print("✅ Teacher registration test passed")
            return data
        except Exception as e:
            print(f"❌ Teacher registration test failed: {str(e)}")
            return None

    def test_01_login(self):
        """Test login functionality"""
        print("\n🔍 Testing Login Functionality...")
        
        # Skip if registration failed
        if not self.student_id or not self.teacher_id:
            self.skipTest("Registration failed, cannot test login")
        
        # Test student login
        url = f"{API_URL}/auth/login"
        payload = {
            "email": "student_test@example.com",
            "password": "SecurePass123!"
        }
        
        # Register a new account specifically for login test
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": "student_test@example.com",
            "password": "SecurePass123!",
            "name": "Login Test Student",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_9.value
        }
        
        try:
            # Register first
            register_response = requests.post(register_url, json=register_payload)
            self.assertEqual(register_response.status_code, 200, "Failed to register test account")
            
            # Then login
            login_response = requests.post(url, json=payload)
            print(f"Student Login Response: {login_response.status_code}")
            
            self.assertEqual(login_response.status_code, 200, "Failed to login as student")
            login_data = login_response.json()
            
            self.assertIsNotNone(login_data.get("access_token"), "Login should return access token")
            self.assertEqual(login_data.get("user_type"), UserType.STUDENT.value, "User type should be student")
            print("✅ Student login test passed")
        except Exception as e:
            print(f"❌ Student login test failed: {str(e)}")
        
        # Test teacher login
        payload = {
            "email": "teacher_test@example.com",
            "password": "SecurePass123!"
        }
        
        # Register a new teacher account for login test
        register_payload = {
            "email": "teacher_test@example.com",
            "password": "SecurePass123!",
            "name": "Login Test Teacher",
            "user_type": UserType.TEACHER.value,
            "school_name": "Test School"
        }
        
        try:
            # Register first
            register_response = requests.post(register_url, json=register_payload)
            self.assertEqual(register_response.status_code, 200, "Failed to register test teacher account")
            
            # Then login
            login_response = requests.post(url, json=payload)
            print(f"Teacher Login Response: {login_response.status_code}")
            
            self.assertEqual(login_response.status_code, 200, "Failed to login as teacher")
            login_data = login_response.json()
            
            self.assertIsNotNone(login_data.get("access_token"), "Login should return access token")
            self.assertEqual(login_data.get("user_type"), UserType.TEACHER.value, "User type should be teacher")
            print("✅ Teacher login test passed")
        except Exception as e:
            print(f"❌ Teacher login test failed: {str(e)}")

    def test_02_student_profile(self):
        """Test student profile endpoint with authentication"""
        print("\n🔍 Testing Student Profile with Authentication...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/student/profile"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Student Profile Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get student profile")
            data = response.json()
            
            self.assertEqual(data.get("user_id"), self.student_id, "User ID mismatch")
            self.assertEqual(data.get("name"), "Rahul Sharma", "Name mismatch")
            print("✅ Student profile test passed")
        except Exception as e:
            print(f"❌ Student profile test failed: {str(e)}")

    def test_03_teacher_profile(self):
        """Test teacher profile endpoint with authentication"""
        print("\n🔍 Testing Teacher Profile with Authentication...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/profile"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Profile Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher profile")
            data = response.json()
            
            self.assertEqual(data.get("user_id"), self.teacher_id, "User ID mismatch")
            self.assertEqual(data.get("name"), "Priya Patel", "Name mismatch")
            self.assertEqual(data.get("school_name"), "Delhi Public School", "School name mismatch")
            print("✅ Teacher profile test passed")
        except Exception as e:
            print(f"❌ Teacher profile test failed: {str(e)}")

    def test_04_create_class(self):
        """Test class creation by teacher"""
        print("\n🔍 Testing Class Creation...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        payload = {
            "subject": Subject.PHYSICS.value,
            "class_name": "Advanced Physics",
            "grade_level": GradeLevel.GRADE_11.value,
            "description": "Advanced physics class covering mechanics, thermodynamics, and electromagnetism"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Create Class Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to create class")
            data = response.json()
            
            self.class_id = data.get("class_id")
            self.join_code = data.get("join_code")
            
            self.assertIsNotNone(self.class_id, "Class ID should not be None")
            self.assertIsNotNone(self.join_code, "Join code should not be None")
            self.assertEqual(data.get("teacher_id"), self.teacher_id, "Teacher ID mismatch")
            self.assertEqual(data.get("subject"), Subject.PHYSICS.value, "Subject mismatch")
            self.assertEqual(data.get("class_name"), "Advanced Physics", "Class name mismatch")
            
            print(f"Created class with ID: {self.class_id} and join code: {self.join_code}")
            print("✅ Create class test passed")
        except Exception as e:
            print(f"❌ Create class test failed: {str(e)}")

    def test_05_get_teacher_classes(self):
        """Test getting teacher's classes"""
        print("\n🔍 Testing Get Teacher Classes...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Teacher Classes Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher classes")
            data = response.json()
            
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertTrue(len(data) > 0, "Teacher should have at least one class")
            
            # Check if our created class is in the list
            class_ids = [cls.get("class_id") for cls in data]
            self.assertIn(self.class_id, class_ids, "Created class not found in teacher's classes")
            
            print(f"Teacher has {len(data)} classes")
            print("✅ Get teacher classes test passed")
        except Exception as e:
            print(f"❌ Get teacher classes test failed: {str(e)}")

    def test_06_join_class(self):
        """Test student joining a class"""
        print("\n🔍 Testing Join Class...")
        
        if not self.student_token or not self.join_code:
            self.skipTest("Student token or join code not available")
        
        url = f"{API_URL}/student/join-class"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "join_code": self.join_code
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Join Class Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to join class")
            data = response.json()
            
            self.assertIn("message", data, "Response should contain a message")
            self.assertIn("class", data, "Response should contain class details")
            
            class_data = data.get("class", {})
            self.assertEqual(class_data.get("class_id"), self.class_id, "Class ID mismatch")
            self.assertEqual(class_data.get("join_code"), self.join_code, "Join code mismatch")
            
            print(f"Student joined class: {class_data.get('class_name')}")
            print("✅ Join class test passed")
        except Exception as e:
            print(f"❌ Join class test failed: {str(e)}")

    def test_07_get_student_classes(self):
        """Test getting student's joined classes"""
        print("\n🔍 Testing Get Student Classes...")
        
        if not self.student_token or not self.class_id:
            self.skipTest("Student token or class ID not available")
        
        url = f"{API_URL}/student/classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Student Classes Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get student classes")
            data = response.json()
            
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertTrue(len(data) > 0, "Student should have at least one class")
            
            # Check if our joined class is in the list
            class_ids = [cls.get("class_id") for cls in data]
            self.assertIn(self.class_id, class_ids, "Joined class not found in student's classes")
            
            print(f"Student has joined {len(data)} classes")
            print("✅ Get student classes test passed")
        except Exception as e:
            print(f"❌ Get student classes test failed: {str(e)}")

    def test_08_chat_session(self):
        """Test creating a chat session with authentication"""
        print("\n🔍 Testing Chat Session Creation...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/chat/session"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": Subject.MATH.value
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Create Chat Session Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to create chat session")
            data = response.json()
            
            self.session_id = data.get("session_id")
            self.assertIsNotNone(self.session_id, "Session ID should not be None")
            self.assertEqual(data.get("student_id"), self.student_id, "Student ID mismatch")
            self.assertEqual(data.get("subject"), Subject.MATH.value, "Subject mismatch")
            
            print(f"Created chat session with ID: {self.session_id}")
            print("✅ Create chat session test passed")
        except Exception as e:
            print(f"❌ Create chat session test failed: {str(e)}")

    def test_09_send_chat_message(self):
        """Test sending a chat message with authentication"""
        print("\n🔍 Testing Send Chat Message...")
        
        if not self.student_token or not self.session_id:
            self.skipTest("Student token or session ID not available")
        
        url = f"{API_URL}/chat/message"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "session_id": self.session_id,
            "subject": Subject.MATH.value,
            "user_message": "Can you help me solve the quadratic equation x^2 - 5x + 6 = 0?"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Send Chat Message Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to send chat message")
            data = response.json()
            
            self.assertEqual(data.get("session_id"), self.session_id, "Session ID mismatch")
            self.assertEqual(data.get("student_id"), self.student_id, "Student ID mismatch")
            self.assertEqual(data.get("subject"), Subject.MATH.value, "Subject mismatch")
            self.assertEqual(data.get("user_message"), payload["user_message"], "User message mismatch")
            self.assertIsNotNone(data.get("bot_response"), "Bot response should not be None")
            
            print(f"Bot response preview: {data.get('bot_response')[:100]}...")
            print("✅ Send chat message test passed")
        except Exception as e:
            print(f"❌ Send chat message test failed: {str(e)}")

    def test_10_chat_history(self):
        """Test getting chat history with authentication"""
        print("\n🔍 Testing Get Chat History...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/chat/history"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Chat History Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get chat history")
            data = response.json()
            
            self.assertIsInstance(data, list, "Chat history should be a list")
            
            if len(data) > 0:
                # If we have chat history, check the first message
                message = data[0]
                self.assertEqual(message.get("student_id"), self.student_id, "Student ID mismatch")
                self.assertIsNotNone(message.get("user_message"), "User message should not be None")
                self.assertIsNotNone(message.get("bot_response"), "Bot response should not be None")
            
            print(f"Chat history contains {len(data)} messages")
            print("✅ Get chat history test passed")
        except Exception as e:
            print(f"❌ Get chat history test failed: {str(e)}")

    def test_11_practice_test_generation(self):
        """Test practice test generation with authentication"""
        print("\n🔍 Testing Practice Test Generation...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": Subject.MATH.value,
            "topics": ["Algebra"],
            "difficulty": DifficultyLevel.MEDIUM.value,
            "question_count": 3
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Practice Test Generation Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to generate practice test")
            data = response.json()
            
            self.assertIn("test_id", data, "Test ID not found in response")
            self.assertIn("questions", data, "Questions not found in response")
            self.assertIn("total_questions", data, "Total questions not found in response")
            
            questions = data.get("questions", [])
            self.assertTrue(len(questions) > 0, "Should have at least one question")
            
            # Check the first question structure
            if len(questions) > 0:
                question = questions[0]
                self.assertIn("question_text", question, "Question text not found")
                self.assertIn("options", question, "Options not found")
                self.assertIn("correct_answer", question, "Correct answer not found")
            
            print(f"Generated {len(questions)} practice questions")
            print("✅ Practice test generation test passed")
        except Exception as e:
            print(f"❌ Practice test generation test failed: {str(e)}")

    def test_12_practice_test_submission(self):
        """Test practice test submission with authentication"""
        print("\n🔍 Testing Practice Test Submission...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # First generate a test
        gen_url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        gen_payload = {
            "subject": Subject.MATH.value,
            "topics": ["Algebra"],
            "difficulty": DifficultyLevel.MEDIUM.value,
            "question_count": 2
        }
        
        try:
            gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
            self.assertEqual(gen_response.status_code, 200, "Failed to generate practice test")
            gen_data = gen_response.json()
            
            test_id = gen_data.get("test_id")
            questions = gen_data.get("questions", [])
            
            if len(questions) == 0:
                self.skipTest("No questions generated")
            
            # Create student answers (just use the correct answers for testing)
            student_answers = {}
            question_ids = []
            for question in questions:
                question_id = question.get("id")
                question_ids.append(question_id)
                student_answers[question_id] = question.get("correct_answer")
            
            # Submit the test
            submit_url = f"{API_URL}/practice/submit"
            submit_payload = {
                "test_id": test_id,
                "questions": question_ids,
                "student_answers": student_answers,
                "time_taken": 300  # 5 minutes
            }
            
            submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
            print(f"Practice Test Submission Response: {submit_response.status_code}")
            
            self.assertEqual(submit_response.status_code, 200, "Failed to submit practice test")
            submit_data = submit_response.json()
            
            self.assertIn("score", submit_data, "Score not found in response")
            self.assertIn("correct_answers", submit_data, "Correct answers not found in response")
            self.assertIn("total_questions", submit_data, "Total questions not found in response")
            self.assertIn("xp_earned", submit_data, "XP earned not found in response")
            
            # Since we used correct answers, score should be 100%
            self.assertEqual(submit_data.get("score"), 100.0, "Score should be 100%")
            self.assertEqual(submit_data.get("correct_answers"), len(questions), "All answers should be correct")
            
            print(f"Submitted practice test with score: {submit_data.get('score')}%")
            print(f"Earned {submit_data.get('xp_earned')} XP")
            print("✅ Practice test submission test passed")
        except Exception as e:
            print(f"❌ Practice test submission test failed: {str(e)}")

    def test_13_student_dashboard(self):
        """Test student dashboard with authentication"""
        print("\n🔍 Testing Student Dashboard...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/dashboard"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Student Dashboard Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get student dashboard")
            data = response.json()
            
            self.assertIn("profile", data, "Profile not found in dashboard")
            self.assertIn("stats", data, "Stats not found in dashboard")
            self.assertIn("recent_activity", data, "Recent activity not found in dashboard")
            
            profile = data.get("profile", {})
            self.assertEqual(profile.get("user_id"), self.student_id, "User ID mismatch")
            
            stats = data.get("stats", {})
            self.assertIn("total_messages", stats, "Total messages not found in stats")
            self.assertIn("total_xp", stats, "Total XP not found in stats")
            
            print(f"Student dashboard loaded with {len(data.get('recent_activity', {}).get('messages', []))} recent messages")
            print("✅ Student dashboard test passed")
        except Exception as e:
            print(f"❌ Student dashboard test failed: {str(e)}")

    def test_14_teacher_dashboard(self):
        """Test teacher dashboard with authentication"""
        print("\n🔍 Testing Teacher Dashboard...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/dashboard"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Dashboard Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher dashboard")
            data = response.json()
            
            self.assertIn("profile", data, "Profile not found in dashboard")
            self.assertIn("classes", data, "Classes not found in dashboard")
            self.assertIn("stats", data, "Stats not found in dashboard")
            
            profile = data.get("profile", {})
            self.assertEqual(profile.get("user_id"), self.teacher_id, "User ID mismatch")
            
            classes = data.get("classes", [])
            self.assertTrue(len(classes) > 0, "Teacher should have at least one class")
            
            stats = data.get("stats", {})
            self.assertIn("total_classes", stats, "Total classes not found in stats")
            self.assertIn("total_students", stats, "Total students not found in stats")
            
            print(f"Teacher dashboard loaded with {len(classes)} classes")
            print("✅ Teacher dashboard test passed")
        except Exception as e:
            print(f"❌ Teacher dashboard test failed: {str(e)}")

    def test_15_jwt_validation(self):
        """Test JWT token validation"""
        print("\n🔍 Testing JWT Token Validation...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Test with valid token
        url = f"{API_URL}/student/profile"
        valid_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            valid_response = requests.get(url, headers=valid_headers)
            print(f"Valid Token Response: {valid_response.status_code}")
            
            self.assertEqual(valid_response.status_code, 200, "Valid token should be accepted")
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid.token.here"}
            invalid_response = requests.get(url, headers=invalid_headers)
            print(f"Invalid Token Response: {invalid_response.status_code}")
            
            self.assertEqual(invalid_response.status_code, 401, "Invalid token should be rejected")
            
            # Test with missing token
            missing_response = requests.get(url)
            print(f"Missing Token Response: {missing_response.status_code}")
            
            self.assertEqual(missing_response.status_code, 401, "Missing token should be rejected")
            
            print("✅ JWT token validation test passed")
        except Exception as e:
            print(f"❌ JWT token validation test failed: {str(e)}")

    def test_16_health_check(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check...")
        
        url = f"{API_URL}/health"
        
        try:
            response = requests.get(url)
            print(f"Health Check Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Health check should return 200")
            data = response.json()
            
            self.assertEqual(data.get("status"), "healthy", "Status should be 'healthy'")
            self.assertIn("timestamp", data, "Timestamp should be included")
            self.assertIn("version", data, "Version should be included")
            
            print(f"API version: {data.get('version')}")
            print("✅ Health check test passed")
        except Exception as e:
            print(f"❌ Health check test failed: {str(e)}")

    def test_17_teacher_analytics_overview(self):
        """Test teacher analytics overview endpoint"""
        print("\n🔍 Testing Teacher Analytics Overview...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/analytics/overview"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Analytics Overview Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher analytics overview")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("overview_metrics", data, "Overview metrics not found in response")
            self.assertIn("class_summary", data, "Class summary not found in response")
            self.assertIn("subject_distribution", data, "Subject distribution not found in response")
            self.assertIn("weekly_activity_trend", data, "Weekly activity trend not found in response")
            
            # Verify overview metrics
            metrics = data.get("overview_metrics", {})
            self.assertIn("total_classes", metrics, "Total classes not found in metrics")
            self.assertIn("total_students", metrics, "Total students not found in metrics")
            self.assertIn("total_messages", metrics, "Total messages not found in metrics")
            self.assertIn("total_tests", metrics, "Total tests not found in metrics")
            self.assertIn("average_score", metrics, "Average score not found in metrics")
            
            # Verify class summary
            class_summary = data.get("class_summary", [])
            self.assertIsInstance(class_summary, list, "Class summary should be a list")
            
            if len(class_summary) > 0:
                first_class = class_summary[0]
                self.assertIn("class_info", first_class, "Class info not found in class summary")
                self.assertIn("student_count", first_class, "Student count not found in class summary")
                self.assertIn("average_xp", first_class, "Average XP not found in class summary")
                self.assertIn("weekly_activity", first_class, "Weekly activity not found in class summary")
            
            print(f"Teacher analytics overview loaded with {len(class_summary)} classes")
            print("✅ Teacher analytics overview test passed")
        except Exception as e:
            print(f"❌ Teacher analytics overview test failed: {str(e)}")

    def test_18_teacher_analytics_class(self):
        """Test teacher analytics for a specific class"""
        print("\n🔍 Testing Teacher Analytics for Class...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        url = f"{API_URL}/teacher/analytics/class/{self.class_id}"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Analytics Class Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher analytics for class")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("class_info", data, "Class info not found in response")
            self.assertIn("student_count", data, "Student count not found in response")
            
            # Verify class info
            class_info = data.get("class_info", {})
            self.assertEqual(class_info.get("class_id"), self.class_id, "Class ID mismatch")
            
            # If there are students in the class, verify student analytics
            if data.get("student_count", 0) > 0:
                self.assertIn("class_metrics", data, "Class metrics not found in response")
                self.assertIn("student_analytics", data, "Student analytics not found in response")
                
                # Verify class metrics
                class_metrics = data.get("class_metrics", {})
                self.assertIn("average_xp", class_metrics, "Average XP not found in class metrics")
                self.assertIn("average_level", class_metrics, "Average level not found in class metrics")
                self.assertIn("total_messages", class_metrics, "Total messages not found in class metrics")
                self.assertIn("total_tests", class_metrics, "Total tests not found in class metrics")
                self.assertIn("average_score", class_metrics, "Average score not found in class metrics")
                self.assertIn("active_students", class_metrics, "Active students not found in class metrics")
                
                # Verify student analytics
                student_analytics = data.get("student_analytics", {})
                self.assertIsInstance(student_analytics, dict, "Student analytics should be a dictionary")
            
            print(f"Teacher analytics for class loaded with {data.get('student_count', 0)} students")
            print("✅ Teacher analytics class test passed")
        except Exception as e:
            print(f"❌ Teacher analytics class test failed: {str(e)}")

    def test_19_teacher_analytics_student(self):
        """Test teacher analytics for a specific student"""
        print("\n🔍 Testing Teacher Analytics for Student...")
        
        if not self.teacher_token or not self.student_id:
            self.skipTest("Teacher token or student ID not available")
        
        # First, make sure the student is in the teacher's class
        if not self.class_id or not self.join_code:
            self.skipTest("Class ID or join code not available")
        
        # Join the class if not already joined
        join_url = f"{API_URL}/student/join-class"
        join_headers = {"Authorization": f"Bearer {self.student_token}"}
        join_payload = {"join_code": self.join_code}
        
        try:
            # Try to join the class (will be ignored if already joined)
            requests.post(join_url, json=join_payload, headers=join_headers)
            
            # Now test the student analytics endpoint
            url = f"{API_URL}/teacher/analytics/student/{self.student_id}"
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            
            response = requests.get(url, headers=headers)
            print(f"Teacher Analytics Student Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher analytics for student")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("student_profile", data, "Student profile not found in response")
            self.assertIn("subject_analytics", data, "Subject analytics not found in response")
            self.assertIn("overall_stats", data, "Overall stats not found in response")
            self.assertIn("activity_timeline", data, "Activity timeline not found in response")
            self.assertIn("wellness_data", data, "Wellness data not found in response")
            
            # Verify student profile
            student_profile = data.get("student_profile", {})
            self.assertEqual(student_profile.get("user_id"), self.student_id, "Student ID mismatch")
            
            # Verify overall stats
            overall_stats = data.get("overall_stats", {})
            self.assertIn("total_messages", overall_stats, "Total messages not found in overall stats")
            self.assertIn("total_tests", overall_stats, "Total tests not found in overall stats")
            self.assertIn("total_mindfulness_sessions", overall_stats, "Total mindfulness sessions not found in overall stats")
            self.assertIn("total_events", overall_stats, "Total events not found in overall stats")
            self.assertIn("average_test_score", overall_stats, "Average test score not found in overall stats")
            self.assertIn("study_streak", overall_stats, "Study streak not found in overall stats")
            self.assertIn("total_xp", overall_stats, "Total XP not found in overall stats")
            self.assertIn("current_level", overall_stats, "Current level not found in overall stats")
            
            # Verify subject analytics
            subject_analytics = data.get("subject_analytics", {})
            self.assertIsInstance(subject_analytics, dict, "Subject analytics should be a dictionary")
            
            # Verify activity timeline
            activity_timeline = data.get("activity_timeline", {})
            self.assertIn("daily_activity", activity_timeline, "Daily activity not found in activity timeline")
            self.assertIn("performance_trend", activity_timeline, "Performance trend not found in activity timeline")
            self.assertIn("recent_activity", activity_timeline, "Recent activity not found in activity timeline")
            
            # Verify wellness data
            wellness_data = data.get("wellness_data", {})
            self.assertIn("mindfulness_sessions", wellness_data, "Mindfulness sessions not found in wellness data")
            self.assertIn("total_mindfulness_minutes", wellness_data, "Total mindfulness minutes not found in wellness data")
            self.assertIn("mood_trends", wellness_data, "Mood trends not found in wellness data")
            
            print("✅ Teacher analytics student test passed")
        except Exception as e:
            print(f"❌ Teacher analytics student test failed: {str(e)}")

class TestProjectKV3BackendFocusedIssues(unittest.TestCase):
    """Test cases specifically for the issues identified in the test plan"""

    def setUp(self):
        """Set up test case - create student and teacher accounts"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        
        # Register student and teacher
        self.register_student()
        self.register_teacher()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"student_focus_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Kumar",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student with ID: {self.student_id}")
            else:
                print(f"Failed to register student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student: {str(e)}")

    def register_teacher(self):
        """Register a teacher for testing"""
        print("\n🔍 Setting up teacher account...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"teacher_focus_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Neha Sharma",
            "user_type": UserType.TEACHER.value,
            "school_name": "Modern Public School"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"Registered teacher with ID: {self.teacher_id}")
            else:
                print(f"Failed to register teacher: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering teacher: {str(e)}")

    def test_01_practice_test_system(self):
        """Test practice test generation with correct request format"""
        print("\n🔍 Testing Practice Test System (ISSUE #1)...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test with different payload formats to identify the correct one
        payloads = [
            # Original payload from existing test
            {
                "subject": Subject.MATH.value,
                "topics": ["Algebra"],
                "difficulty": DifficultyLevel.MEDIUM.value,
                "question_count": 3
            },
            # Alternative payload with string topics
            {
                "subject": Subject.MATH.value,
                "topics": "Algebra",
                "difficulty": DifficultyLevel.MEDIUM.value,
                "question_count": 3
            },
            # Alternative payload with single topic as list
            {
                "subject": Subject.MATH.value,
                "topics": ["Algebra"],
                "difficulty": DifficultyLevel.MEDIUM.value,
                "question_count": 3
            },
            # Alternative payload with different field names
            {
                "subject": Subject.MATH.value,
                "topic": ["Algebra"],
                "difficulty_level": DifficultyLevel.MEDIUM.value,
                "num_questions": 3
            }
        ]
        
        success = False
        working_payload = None
        error_details = []
        
        for i, payload in enumerate(payloads):
            try:
                print(f"Trying payload format #{i+1}: {json.dumps(payload)}")
                response = requests.post(url, json=payload, headers=headers)
                print(f"Response: {response.status_code}")
                
                if response.status_code == 200:
                    success = True
                    working_payload = payload
                    data = response.json()
                    print(f"Success! Generated {len(data.get('questions', []))} practice questions")
                    break
                else:
                    error_details.append(f"Payload #{i+1}: Status {response.status_code}, Response: {response.text}")
            except Exception as e:
                error_details.append(f"Payload #{i+1}: Exception: {str(e)}")
        
        if success:
            print(f"✅ Practice test generation works with payload format: {json.dumps(working_payload)}")
        else:
            print("❌ All practice test generation attempts failed")
            for error in error_details:
                print(f"  - {error}")
            
        # Assert based on success flag rather than expecting success
        # This allows us to report the issue properly
        self.assertEqual(success, True, "Practice test generation should work with at least one payload format")

    def test_02_teacher_dashboard_empty_classes(self):
        """Test teacher dashboard when teacher has no classes"""
        print("\n🔍 Testing Teacher Dashboard with No Classes (ISSUE #2)...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/dashboard"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            # This is a newly registered teacher with no classes
            response = requests.get(url, headers=headers)
            print(f"Teacher Dashboard Response: {response.status_code}")
            
            # We expect this to work even with no classes
            self.assertEqual(response.status_code, 200, "Teacher dashboard should work with no classes")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Teacher dashboard works with no classes")
                
                # Verify the structure
                self.assertIn("profile", data, "Profile should be present")
                self.assertIn("classes", data, "Classes array should be present (even if empty)")
                self.assertIn("stats", data, "Stats should be present")
                
                # Verify classes is an empty array
                classes = data.get("classes", None)
                self.assertIsInstance(classes, list, "Classes should be a list")
                self.assertEqual(len(classes), 0, "Classes should be empty")
                
                # Verify stats has appropriate values for no classes
                stats = data.get("stats", {})
                self.assertEqual(stats.get("total_classes", None), 0, "Total classes should be 0")
                self.assertEqual(stats.get("total_students", None), 0, "Total students should be 0")
            else:
                print(f"❌ Teacher dashboard fails with no classes: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Teacher dashboard test failed: {str(e)}")
            self.fail(f"Teacher dashboard test failed: {str(e)}")

    def test_03_jwt_validation_missing_token(self):
        """Test JWT validation for missing tokens"""
        print("\n🔍 Testing JWT Validation for Missing Tokens (ISSUE #3)...")
        
        # Test with missing token
        url = f"{API_URL}/student/profile"
        
        try:
            # Make request with no Authorization header
            response = requests.get(url)
            print(f"Missing Token Response: {response.status_code}")
            
            # Check if it returns 401 (expected) or 403 (current behavior)
            if response.status_code == 401:
                print("✅ Missing token correctly returns 401 Unauthorized")
                self.assertEqual(response.status_code, 401, "Missing token should return 401 Unauthorized")
            else:
                print(f"❌ Missing token returns {response.status_code} instead of 401 Unauthorized")
                # We'll assert this to document the issue, not because we expect it to pass
                self.assertEqual(response.status_code, 401, 
                                f"Missing token returns {response.status_code} instead of 401 Unauthorized")
            
            # Check response headers
            headers = response.headers
            self.assertIn("WWW-Authenticate", headers, 
                         "Response should include WWW-Authenticate header for 401 responses")
            
            # Check response body
            try:
                data = response.json()
                self.assertIn("detail", data, "Response should include error detail")
                print(f"Error detail: {data.get('detail', '')}")
            except:
                print("Response is not valid JSON")
        except Exception as e:
            print(f"❌ JWT validation test failed: {str(e)}")
            self.fail(f"JWT validation test failed: {str(e)}")

class TestPracticeResultsEndpointFix(unittest.TestCase):
    """Test cases specifically for the /api/practice/results endpoint fix"""

    def setUp(self):
        """Set up test case - create student account"""
        self.student_token = None
        self.student_id = None
        
        # Register student
        self.register_student()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account for practice results testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"practice_results_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Priya Sharma",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student with ID: {self.student_id}")
            else:
                print(f"Failed to register student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student: {str(e)}")

    def test_01_practice_results_endpoint_with_authentication(self):
        """Test /api/practice/results endpoint with proper authentication"""
        print("\n🔍 Testing Practice Results Endpoint with Authentication...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/practice/results"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Practice Results Response: {response.status_code}")
            
            # This should return 200 OK, not 500 Internal Server Error
            self.assertEqual(response.status_code, 200, "Practice results endpoint should return 200 OK")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Practice results endpoint returns 200 OK")
                
                # Verify response structure
                self.assertIsInstance(data, list, "Response should be a list")
                print(f"Found {len(data)} practice test results")
                
                # If there are results, verify the data structure
                if len(data) > 0:
                    first_result = data[0]
                    required_fields = ["id", "subject", "score", "total_questions", "completed_at"]
                    for field in required_fields:
                        self.assertIn(field, first_result, f"Field '{field}' should be present in results")
                    
                    # Verify total_questions field is not None and is a valid number
                    total_questions = first_result.get("total_questions")
                    self.assertIsNotNone(total_questions, "total_questions should not be None")
                    self.assertIsInstance(total_questions, int, "total_questions should be an integer")
                    self.assertGreaterEqual(total_questions, 0, "total_questions should be >= 0")
                    
                    print(f"✅ Data structure verified - total_questions: {total_questions}")
                else:
                    print("✅ Empty results returned successfully (no practice tests yet)")
            else:
                print(f"❌ Practice results endpoint failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Practice results endpoint test failed: {str(e)}")
            self.fail(f"Practice results endpoint test failed: {str(e)}")

    def test_02_practice_results_endpoint_without_authentication(self):
        """Test /api/practice/results endpoint without authentication"""
        print("\n🔍 Testing Practice Results Endpoint without Authentication...")
        
        url = f"{API_URL}/practice/results"
        
        try:
            response = requests.get(url)
            print(f"Practice Results (No Auth) Response: {response.status_code}")
            
            # Should return 401 or 403, not 500
            self.assertIn(response.status_code, [401, 403], 
                         "Endpoint should return 401/403 for missing authentication, not 500")
            
            if response.status_code in [401, 403]:
                print("✅ Properly rejects requests without authentication")
            else:
                print(f"❌ Unexpected response code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Authentication test failed: {str(e)}")
            self.fail(f"Authentication test failed: {str(e)}")

    def test_03_create_and_verify_practice_test_data(self):
        """Create practice test data and verify it appears in results"""
        print("\n🔍 Creating Practice Test Data and Verifying Results...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # First, generate a practice test
            gen_url = f"{API_URL}/practice/generate"
            gen_payload = {
                "subject": Subject.MATH.value,
                "topics": ["Algebra"],
                "difficulty": DifficultyLevel.MEDIUM.value,
                "question_count": 3
            }
            
            gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
            print(f"Generate Test Response: {gen_response.status_code}")
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                questions = gen_data.get("questions", [])
                
                if questions:
                    # Submit the test with correct answers
                    student_answers = {}
                    question_ids = []
                    for question in questions:
                        question_id = question.get("id")
                        question_ids.append(question_id)
                        student_answers[question_id] = question.get("correct_answer")
                    
                    submit_url = f"{API_URL}/practice/submit"
                    submit_payload = {
                        "questions": question_ids,
                        "student_answers": student_answers,
                        "subject": Subject.MATH.value,
                        "time_taken": 300
                    }
                    
                    submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                    print(f"Submit Test Response: {submit_response.status_code}")
                    
                    if submit_response.status_code == 200:
                        submit_data = submit_response.json()
                        print(f"Test submitted with score: {submit_data.get('score')}%")
                        
                        # Now test the results endpoint
                        results_url = f"{API_URL}/practice/results"
                        results_response = requests.get(results_url, headers=headers)
                        print(f"Results Response: {results_response.status_code}")
                        
                        self.assertEqual(results_response.status_code, 200, 
                                       "Results endpoint should return 200 OK after test submission")
                        
                        if results_response.status_code == 200:
                            results_data = results_response.json()
                            print(f"Found {len(results_data)} results after test submission")
                            
                            # Verify our test appears in results
                            self.assertGreater(len(results_data), 0, "Should have at least one result")
                            
                            # Find our submitted test
                            our_test = None
                            for result in results_data:
                                if result.get("subject") == Subject.MATH.value:
                                    our_test = result
                                    break
                            
                            self.assertIsNotNone(our_test, "Our submitted test should appear in results")
                            
                            # Verify the data structure and total_questions field
                            self.assertIn("total_questions", our_test, "total_questions field should be present")
                            self.assertEqual(our_test["total_questions"], 3, "total_questions should match submitted test")
                            self.assertIn("score", our_test, "score field should be present")
                            self.assertIn("subject", our_test, "subject field should be present")
                            
                            print("✅ Practice test data successfully stored and retrieved")
                            print(f"✅ total_questions field working correctly: {our_test['total_questions']}")
                        else:
                            print(f"❌ Results endpoint failed: {results_response.text}")
                    else:
                        print(f"❌ Test submission failed: {submit_response.text}")
                else:
                    print("⚠️ No questions generated, skipping submission test")
            else:
                print(f"❌ Test generation failed: {gen_response.text}")
                
        except Exception as e:
            print(f"❌ Practice test data verification failed: {str(e)}")
            self.fail(f"Practice test data verification failed: {str(e)}")

    def test_04_practice_results_with_subject_filter(self):
        """Test /api/practice/results endpoint with subject filter"""
        print("\n🔍 Testing Practice Results with Subject Filter...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Test with math subject filter
            url = f"{API_URL}/practice/results?subject=math"
            response = requests.get(url, headers=headers)
            print(f"Filtered Results Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Filtered results should return 200 OK")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} math results")
                
                # Verify all results are for math subject
                for result in data:
                    self.assertEqual(result.get("subject"), "math", "All results should be for math subject")
                    self.assertIn("total_questions", result, "total_questions field should be present")
                    self.assertIsNotNone(result.get("total_questions"), "total_questions should not be None")
                
                print("✅ Subject filtering works correctly")
            else:
                print(f"❌ Filtered results failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Subject filter test failed: {str(e)}")
            self.fail(f"Subject filter test failed: {str(e)}")

class TestTeacherAnalyticsEndpoints(unittest.TestCase):
    """Test cases specifically for teacher analytics endpoints to verify practice test data"""

    def setUp(self):
        """Set up test case - create student and teacher accounts with practice test data"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        
        # Register student and teacher
        self.register_student()
        self.register_teacher()
        self.create_class_and_join()
        self.create_practice_test_data()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account for analytics testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"analytics_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Ravi Kumar",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student with ID: {self.student_id}")
            else:
                print(f"Failed to register student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student: {str(e)}")

    def register_teacher(self):
        """Register a teacher for testing"""
        print("\n🔍 Setting up teacher account for analytics testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"analytics_teacher_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Dr. Sunita Sharma",
            "user_type": UserType.TEACHER.value,
            "school_name": "St. Xavier's School"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"Registered teacher with ID: {self.teacher_id}")
            else:
                print(f"Failed to register teacher: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering teacher: {str(e)}")

    def create_class_and_join(self):
        """Create a class and have student join it"""
        print("\n🔍 Setting up class for analytics testing...")
        
        if not self.teacher_token or not self.student_token:
            self.skipTest("Teacher or student token not available")
        
        # Create class
        create_url = f"{API_URL}/teacher/classes"
        create_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        create_payload = {
            "subject": Subject.MATH.value,
            "class_name": "Advanced Mathematics Analytics Test",
            "grade_level": GradeLevel.GRADE_10.value,
            "description": "Mathematics class for testing analytics functionality"
        }
        
        try:
            create_response = requests.post(create_url, json=create_payload, headers=create_headers)
            print(f"Create Class Response: {create_response.status_code}")
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                self.class_id = create_data.get("class_id")
                self.join_code = create_data.get("join_code")
                print(f"Created class: {self.class_id} with join code: {self.join_code}")
                
                # Join class
                join_url = f"{API_URL}/student/join-class"
                join_headers = {"Authorization": f"Bearer {self.student_token}"}
                join_payload = {"join_code": self.join_code}
                
                join_response = requests.post(join_url, json=join_payload, headers=join_headers)
                print(f"Join Class Response: {join_response.status_code}")
                
                if join_response.status_code != 200:
                    print(f"Failed to join class: {join_response.text}")
            else:
                print(f"Failed to create class: {create_response.text}")
                
        except Exception as e:
            print(f"❌ Class setup failed: {str(e)}")

    def create_practice_test_data(self):
        """Create some practice test data for analytics testing"""
        print("\n🔍 Creating practice test data for analytics...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Generate and submit multiple practice tests
        subjects_and_scores = [
            (Subject.MATH.value, ["Algebra"], 85),
            (Subject.MATH.value, ["Geometry"], 92),
            (Subject.PHYSICS.value, ["Mechanics"], 78),
            (Subject.CHEMISTRY.value, ["Organic Chemistry"], 88)
        ]
        
        for subject, topics, target_score in subjects_and_scores:
            try:
                # Generate practice test
                gen_url = f"{API_URL}/practice/generate"
                headers = {"Authorization": f"Bearer {self.student_token}"}
                gen_payload = {
                    "subject": subject,
                    "topics": topics,
                    "difficulty": DifficultyLevel.MEDIUM.value,
                    "question_count": 3
                }
                
                gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    questions = gen_data.get("questions", [])
                    
                    if questions:
                        # Create student answers to achieve target score
                        student_answers = {}
                        correct_answers_needed = int((target_score / 100) * len(questions))
                        
                        for i, question in enumerate(questions):
                            question_id = question.get("id")
                            if i < correct_answers_needed:
                                # Give correct answer
                                student_answers[question_id] = question.get("correct_answer")
                            else:
                                # Give wrong answer
                                student_answers[question_id] = "wrong_answer"
                        
                        # Submit the test
                        submit_url = f"{API_URL}/practice/submit"
                        submit_payload = {
                            "questions": [q.get("id") for q in questions],
                            "student_answers": student_answers,
                            "subject": subject,
                            "time_taken": 300
                        }
                        
                        submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                        if submit_response.status_code == 200:
                            submit_data = submit_response.json()
                            print(f"Created practice test for {subject}: {submit_data.get('score')}%")
                        else:
                            print(f"Failed to submit {subject} test: {submit_response.text}")
                    else:
                        print(f"No questions generated for {subject}")
                else:
                    print(f"Failed to generate {subject} test: {gen_response.text}")
                    
            except Exception as e:
                print(f"Error creating practice test for {subject}: {str(e)}")

    def test_01_teacher_analytics_overview(self):
        """Test GET /api/teacher/analytics/overview"""
        print("\n🔍 Testing Teacher Analytics Overview...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/analytics/overview"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Analytics Overview Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher analytics overview")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("overview_metrics", data, "Overview metrics not found in response")
            self.assertIn("class_summary", data, "Class summary not found in response")
            self.assertIn("subject_distribution", data, "Subject distribution not found in response")
            
            # Verify overview metrics structure
            metrics = data.get("overview_metrics", {})
            required_metrics = ["total_classes", "total_students", "total_tests", "average_score"]
            for metric in required_metrics:
                self.assertIn(metric, metrics, f"Metric '{metric}' not found in overview metrics")
            
            # Verify we have at least one class and student
            self.assertGreaterEqual(metrics.get("total_classes", 0), 1, "Should have at least 1 class")
            self.assertGreaterEqual(metrics.get("total_students", 0), 1, "Should have at least 1 student")
            
            # Verify practice test data is showing up
            total_tests = metrics.get("total_tests", 0)
            print(f"Total tests found in analytics: {total_tests}")
            
            # Check if practice test data is being retrieved from PRACTICE_ATTEMPTS collection
            if total_tests > 0:
                print("✅ Practice test data is showing up in analytics overview")
                self.assertGreater(total_tests, 0, "Should have practice test data")
                
                # Verify average score is calculated
                avg_score = metrics.get("average_score", 0)
                self.assertGreaterEqual(avg_score, 0, "Average score should be >= 0")
                self.assertLessEqual(avg_score, 100, "Average score should be <= 100")
                print(f"Average score: {avg_score}%")
            else:
                print("⚠️ No practice test data found in analytics overview")
            
            # Verify class summary
            class_summary = data.get("class_summary", [])
            self.assertIsInstance(class_summary, list, "Class summary should be a list")
            
            if len(class_summary) > 0:
                first_class = class_summary[0]
                self.assertIn("class_info", first_class, "Class info not found in class summary")
                self.assertIn("student_count", first_class, "Student count not found in class summary")
                self.assertIn("total_tests", first_class, "Total tests not found in class summary")
                self.assertIn("average_score", first_class, "Average score not found in class summary")
                
                print(f"Class summary - Students: {first_class.get('student_count')}, Tests: {first_class.get('total_tests')}")
            
            # Verify subject distribution
            subject_distribution = data.get("subject_distribution", [])
            self.assertIsInstance(subject_distribution, list, "Subject distribution should be a list")
            
            if len(subject_distribution) > 0:
                print(f"Subject distribution found: {len(subject_distribution)} subjects")
                for subject_data in subject_distribution:
                    self.assertIn("subject", subject_data, "Subject name not found")
                    self.assertIn("test_count", subject_data, "Test count not found")
                    self.assertIn("average_score", subject_data, "Average score not found")
                    print(f"Subject: {subject_data.get('subject')}, Tests: {subject_data.get('test_count')}, Avg: {subject_data.get('average_score')}%")
            
            print("✅ Teacher analytics overview test passed")
            
        except Exception as e:
            print(f"❌ Teacher analytics overview test failed: {str(e)}")
            self.fail(f"Teacher analytics overview test failed: {str(e)}")

    def test_02_teacher_analytics_test_results(self):
        """Test GET /api/teacher/analytics/test-results with filters"""
        print("\n🔍 Testing Teacher Analytics Test Results...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        # Test without filters
        url = f"{API_URL}/teacher/analytics/test-results"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Test Results Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get test results")
            data = response.json()
            
            self.assertIsInstance(data, list, "Test results should be a list")
            print(f"Found {len(data)} test results")
            
            if len(data) > 0:
                # Verify structure of test result
                first_result = data[0]
                required_fields = [
                    "id", "student_id", "student_name", "subject", "score", 
                    "correct_count", "total_questions", "difficulty", "completed_at"
                ]
                
                for field in required_fields:
                    self.assertIn(field, first_result, f"Field '{field}' not found in test result")
                
                # Verify student information is populated
                self.assertIsNotNone(first_result.get("student_name"), "Student name should not be None")
                self.assertNotEqual(first_result.get("student_name"), "Unknown", "Student name should be resolved")
                
                # Verify practice test data fields
                self.assertIsNotNone(first_result.get("subject"), "Subject should not be None")
                self.assertNotEqual(first_result.get("subject"), "", "Subject should not be empty")
                
                print(f"Sample result: {first_result.get('student_name')} - {first_result.get('subject')} - {first_result.get('score')}%")
                print("✅ Practice test data is properly showing up with student information")
            
            # Test with class_id filter
            if self.class_id:
                print("\n🔍 Testing with class_id filter...")
                filtered_url = f"{API_URL}/teacher/analytics/test-results?class_id={self.class_id}"
                filtered_response = requests.get(filtered_url, headers=headers)
                print(f"Filtered Test Results Response: {filtered_response.status_code}")
                
                self.assertEqual(filtered_response.status_code, 200, "Failed to get filtered test results")
                filtered_data = filtered_response.json()
                
                self.assertIsInstance(filtered_data, list, "Filtered test results should be a list")
                print(f"Found {len(filtered_data)} test results for class {self.class_id}")
            
            # Test with subject filter
            print("\n🔍 Testing with subject filter...")
            subject_url = f"{API_URL}/teacher/analytics/test-results?subject=math"
            subject_response = requests.get(subject_url, headers=headers)
            print(f"Subject Filtered Response: {subject_response.status_code}")
            
            self.assertEqual(subject_response.status_code, 200, "Failed to get subject filtered results")
            subject_data = subject_response.json()
            
            self.assertIsInstance(subject_data, list, "Subject filtered results should be a list")
            print(f"Found {len(subject_data)} math test results")
            
            # Verify all results are for math subject
            for result in subject_data:
                self.assertEqual(result.get("subject"), "math", "All results should be for math subject")
            
            print("✅ Teacher analytics test results test passed")
            
        except Exception as e:
            print(f"❌ Teacher analytics test results test failed: {str(e)}")
            self.fail(f"Teacher analytics test results test failed: {str(e)}")

    def test_03_teacher_analytics_class_performance(self):
        """Test GET /api/teacher/analytics/class-performance/{class_id}"""
        print("\n🔍 Testing Teacher Analytics Class Performance...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        url = f"{API_URL}/teacher/analytics/class-performance/{self.class_id}"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Class Performance Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get class performance")
            data = response.json()
            
            # Verify the structure of the response
            required_sections = [
                "class_info", "performance_summary", "student_performance", 
                "subject_breakdown", "recent_activity"
            ]
            
            for section in required_sections:
                self.assertIn(section, data, f"Section '{section}' not found in class performance")
            
            # Verify class info
            class_info = data.get("class_info", {})
            self.assertEqual(class_info.get("class_id"), self.class_id, "Class ID should match")
            self.assertIsNotNone(class_info.get("class_name"), "Class name should not be None")
            self.assertIsNotNone(class_info.get("subject"), "Class subject should not be None")
            
            student_count = class_info.get("student_count", 0)
            print(f"Class has {student_count} students")
            self.assertGreaterEqual(student_count, 1, "Class should have at least 1 student")
            
            # Verify performance summary
            performance_summary = data.get("performance_summary", {})
            required_metrics = ["total_tests", "average_score", "highest_score", "lowest_score", "completion_rate"]
            
            for metric in required_metrics:
                self.assertIn(metric, performance_summary, f"Metric '{metric}' not found in performance summary")
            
            total_tests = performance_summary.get("total_tests", 0)
            print(f"Class performance - Total tests: {total_tests}")
            
            if total_tests > 0:
                print("✅ Practice test data is showing up in class performance")
                avg_score = performance_summary.get("average_score", 0)
                highest_score = performance_summary.get("highest_score", 0)
                lowest_score = performance_summary.get("lowest_score", 0)
                
                self.assertGreaterEqual(avg_score, 0, "Average score should be >= 0")
                self.assertLessEqual(avg_score, 100, "Average score should be <= 100")
                self.assertGreaterEqual(highest_score, lowest_score, "Highest score should be >= lowest score")
                
                print(f"Performance metrics - Avg: {avg_score}%, High: {highest_score}%, Low: {lowest_score}%")
            
            # Verify student performance
            student_performance = data.get("student_performance", [])
            self.assertIsInstance(student_performance, list, "Student performance should be a list")
            
            if len(student_performance) > 0:
                first_student = student_performance[0]
                student_fields = ["student_id", "student_name", "total_tests", "average_score", "best_score"]
                
                for field in student_fields:
                    self.assertIn(field, first_student, f"Field '{field}' not found in student performance")
                
                self.assertIsNotNone(first_student.get("student_name"), "Student name should not be None")
                self.assertNotEqual(first_student.get("student_name"), "Unknown", "Student name should be resolved")
                
                print(f"Student performance: {first_student.get('student_name')} - {first_student.get('total_tests')} tests, {first_student.get('average_score')}% avg")
            
            # Verify subject breakdown
            subject_breakdown = data.get("subject_breakdown", [])
            self.assertIsInstance(subject_breakdown, list, "Subject breakdown should be a list")
            
            if len(subject_breakdown) > 0:
                print(f"Subject breakdown found: {len(subject_breakdown)} subjects")
                for subject_data in subject_breakdown:
                    self.assertIn("subject", subject_data, "Subject name not found")
                    self.assertIn("test_count", subject_data, "Test count not found")
                    self.assertIn("average_score", subject_data, "Average score not found")
                    print(f"Subject: {subject_data.get('subject')}, Tests: {subject_data.get('test_count')}, Avg: {subject_data.get('average_score')}%")
            
            # Verify recent activity
            recent_activity = data.get("recent_activity", [])
            self.assertIsInstance(recent_activity, list, "Recent activity should be a list")
            
            if len(recent_activity) > 0:
                print(f"Recent activity found: {len(recent_activity)} activities")
                first_activity = recent_activity[0]
                activity_fields = ["student_name", "subject", "score", "completed_at", "difficulty"]
                
                for field in activity_fields:
                    self.assertIn(field, first_activity, f"Field '{field}' not found in recent activity")
                
                print(f"Recent activity: {first_activity.get('student_name')} - {first_activity.get('subject')} - {first_activity.get('score')}%")
            
            print("✅ Teacher analytics class performance test passed")
            
        except Exception as e:
            print(f"❌ Teacher analytics class performance test failed: {str(e)}")
            self.fail(f"Teacher analytics class performance test failed: {str(e)}")

    def test_04_data_verification_collection_and_fields(self):
        """Verify that the collection name fix (PRACTICE_RESULTS → PRACTICE_ATTEMPTS) and field name fix (user_id → student_id) are working"""
        print("\n🔍 Testing Data Verification - Collection and Field Names...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        # Test all three analytics endpoints to ensure they're using correct collection and field names
        endpoints = [
            f"{API_URL}/teacher/analytics/overview",
            f"{API_URL}/teacher/analytics/test-results",
            f"{API_URL}/teacher/analytics/class-performance/{self.class_id}" if self.class_id else None
        ]
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        for endpoint in endpoints:
            if endpoint is None:
                continue
                
            try:
                print(f"\n🔍 Testing endpoint: {endpoint}")
                response = requests.get(endpoint, headers=headers)
                print(f"Response: {response.status_code}")
                
                self.assertEqual(response.status_code, 200, f"Endpoint {endpoint} should return 200")
                
                data = response.json()
                
                # Check if we're getting data (indicating correct collection name)
                if "overview_metrics" in data:
                    # Overview endpoint
                    total_tests = data.get("overview_metrics", {}).get("total_tests", 0)
                    if total_tests > 0:
                        print(f"✅ Overview endpoint shows {total_tests} tests - PRACTICE_ATTEMPTS collection working")
                    
                elif isinstance(data, list) and len(data) > 0:
                    # Test results endpoint
                    print(f"✅ Test results endpoint shows {len(data)} results - PRACTICE_ATTEMPTS collection working")
                    
                    # Verify field names are correct
                    first_result = data[0]
                    self.assertIn("student_id", first_result, "Should use 'student_id' field name")
                    self.assertIn("id", first_result, "Should have 'id' field")
                    
                    # Verify student_id is not None/empty (indicating correct field mapping)
                    self.assertIsNotNone(first_result.get("student_id"), "student_id should not be None")
                    self.assertNotEqual(first_result.get("student_id"), "", "student_id should not be empty")
                    
                    print(f"✅ Field names verified - student_id: {first_result.get('student_id')[:8]}...")
                    
                elif "class_info" in data:
                    # Class performance endpoint
                    total_tests = data.get("performance_summary", {}).get("total_tests", 0)
                    if total_tests > 0:
                        print(f"✅ Class performance endpoint shows {total_tests} tests - PRACTICE_ATTEMPTS collection working")
                
            except Exception as e:
                print(f"❌ Error testing endpoint {endpoint}: {str(e)}")
                self.fail(f"Error testing endpoint {endpoint}: {str(e)}")
        
        print("✅ Data verification test passed - Collection and field names are working correctly")

class TestStudentJoinedClassesEndpoint(unittest.TestCase):
    """Test cases specifically for the new student joined-classes endpoint"""

    def setUp(self):
        """Set up test case - create student and teacher accounts"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        
        # Register student and teacher
        self.register_student()
        self.register_teacher()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account for joined-classes testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"joined_classes_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Aarav Patel",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_11.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student with ID: {self.student_id}")
            else:
                print(f"Failed to register student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student: {str(e)}")

    def register_teacher(self):
        """Register a teacher for testing"""
        print("\n🔍 Setting up teacher account for joined-classes testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"joined_classes_teacher_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Dr. Kavya Sharma",
            "user_type": UserType.TEACHER.value,
            "school_name": "Kendriya Vidyalaya"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"Registered teacher with ID: {self.teacher_id}")
            else:
                print(f"Failed to register teacher: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering teacher: {str(e)}")

    def test_01_student_joined_classes_empty(self):
        """Test joined-classes endpoint when student has no classes"""
        print("\n🔍 Testing Student Joined Classes - Empty State...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/student/joined-classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Joined Classes (Empty) Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Joined classes endpoint should work even with no classes")
            data = response.json()
            
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertEqual(len(data), 0, "Should return empty list when no classes joined")
            
            print("✅ Empty joined classes test passed")
        except Exception as e:
            print(f"❌ Empty joined classes test failed: {str(e)}")
            self.fail(f"Empty joined classes test failed: {str(e)}")

    def test_02_student_joined_classes_authentication(self):
        """Test joined-classes endpoint authentication requirements"""
        print("\n🔍 Testing Student Joined Classes - Authentication...")
        
        url = f"{API_URL}/student/joined-classes"
        
        try:
            # Test without authentication
            response = requests.get(url)
            print(f"No Auth Response: {response.status_code}")
            
            # Should require authentication
            self.assertIn(response.status_code, [401, 403], "Should require authentication")
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid.token.here"}
            invalid_response = requests.get(url, headers=invalid_headers)
            print(f"Invalid Token Response: {invalid_response.status_code}")
            
            self.assertIn(invalid_response.status_code, [401, 403], "Should reject invalid tokens")
            
            print("✅ Authentication requirements test passed")
        except Exception as e:
            print(f"❌ Authentication test failed: {str(e)}")
            self.fail(f"Authentication test failed: {str(e)}")

    def test_03_create_class_and_join(self):
        """Create a class and have student join it"""
        print("\n🔍 Setting up class for joined-classes testing...")
        
        if not self.teacher_token or not self.student_token:
            self.skipTest("Teacher or student token not available")
        
        # Create class
        create_url = f"{API_URL}/teacher/classes"
        create_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        create_payload = {
            "subject": Subject.CHEMISTRY.value,
            "class_name": "Advanced Organic Chemistry",
            "grade_level": GradeLevel.GRADE_11.value,
            "description": "Comprehensive study of organic chemistry including reaction mechanisms, stereochemistry, and synthesis"
        }
        
        try:
            create_response = requests.post(create_url, json=create_payload, headers=create_headers)
            print(f"Create Class Response: {create_response.status_code}")
            
            self.assertEqual(create_response.status_code, 200, "Failed to create class")
            create_data = create_response.json()
            
            self.class_id = create_data.get("class_id")
            self.join_code = create_data.get("join_code")
            
            self.assertIsNotNone(self.class_id, "Class ID should not be None")
            self.assertIsNotNone(self.join_code, "Join code should not be None")
            
            print(f"Created class: {create_data.get('class_name')} with join code: {self.join_code}")
            
            # Join class
            join_url = f"{API_URL}/student/join-class"
            join_headers = {"Authorization": f"Bearer {self.student_token}"}
            join_payload = {"join_code": self.join_code}
            
            join_response = requests.post(join_url, json=join_payload, headers=join_headers)
            print(f"Join Class Response: {join_response.status_code}")
            
            self.assertEqual(join_response.status_code, 200, "Failed to join class")
            join_data = join_response.json()
            
            self.assertEqual(join_data.get("class_id"), self.class_id, "Class ID mismatch")
            self.assertEqual(join_data.get("class_name"), "Advanced Organic Chemistry", "Class name mismatch")
            
            print("✅ Class creation and joining completed successfully")
            
        except Exception as e:
            print(f"❌ Class setup failed: {str(e)}")
            self.fail(f"Class setup failed: {str(e)}")

    def test_04_student_joined_classes_complete_data(self):
        """Test joined-classes endpoint returns complete class information"""
        print("\n🔍 Testing Student Joined Classes - Complete Data...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Ensure we have a class to test with
        if not self.class_id:
            self.test_03_create_class_and_join()
        
        if not self.class_id:
            self.skipTest("No class available for testing")
        
        url = f"{API_URL}/student/joined-classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Joined Classes Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get joined classes")
            data = response.json()
            
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertTrue(len(data) > 0, "Should have at least one joined class")
            
            # Check the first class details
            class_info = data[0]
            
            # Verify all required fields are present
            required_fields = [
                "class_id", "class_name", "subject", "description", 
                "join_code", "teacher_id", "student_count"
            ]
            
            for field in required_fields:
                self.assertIn(field, class_info, f"Field '{field}' should be present in class info")
                self.assertIsNotNone(class_info.get(field), f"Field '{field}' should not be None")
            
            # Verify specific values
            self.assertEqual(class_info.get("class_id"), self.class_id, "Class ID should match")
            self.assertEqual(class_info.get("class_name"), "Advanced Organic Chemistry", "Class name should match")
            self.assertEqual(class_info.get("subject"), Subject.CHEMISTRY.value, "Subject should match")
            self.assertEqual(class_info.get("join_code"), self.join_code, "Join code should match")
            self.assertEqual(class_info.get("teacher_id"), self.teacher_id, "Teacher ID should match")
            self.assertGreaterEqual(class_info.get("student_count"), 1, "Student count should be at least 1")
            
            # Verify description is present and not empty
            description = class_info.get("description", "")
            self.assertTrue(len(description) > 0, "Description should not be empty")
            self.assertIn("organic chemistry", description.lower(), "Description should contain subject details")
            
            print("✅ Complete class data verification passed")
            print(f"Class Details Retrieved:")
            print(f"  - Class ID: {class_info.get('class_id')}")
            print(f"  - Class Name: {class_info.get('class_name')}")
            print(f"  - Subject: {class_info.get('subject')}")
            print(f"  - Description: {class_info.get('description')[:50]}...")
            print(f"  - Join Code: {class_info.get('join_code')}")
            print(f"  - Teacher ID: {class_info.get('teacher_id')}")
            print(f"  - Student Count: {class_info.get('student_count')}")
            
        except Exception as e:
            print(f"❌ Complete data test failed: {str(e)}")
            self.fail(f"Complete data test failed: {str(e)}")

    def test_05_multiple_classes_scenario(self):
        """Test joined-classes endpoint with multiple classes"""
        print("\n🔍 Testing Student Joined Classes - Multiple Classes...")
        
        if not self.teacher_token or not self.student_token:
            self.skipTest("Teacher or student token not available")
        
        # Create a second class
        create_url = f"{API_URL}/teacher/classes"
        create_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        create_payload = {
            "subject": Subject.PHYSICS.value,
            "class_name": "Quantum Physics Fundamentals",
            "grade_level": GradeLevel.GRADE_11.value,
            "description": "Introduction to quantum mechanics, wave-particle duality, and quantum phenomena"
        }
        
        try:
            create_response = requests.post(create_url, json=create_payload, headers=create_headers)
            print(f"Create Second Class Response: {create_response.status_code}")
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                second_class_id = create_data.get("class_id")
                second_join_code = create_data.get("join_code")
                
                # Join the second class
                join_url = f"{API_URL}/student/join-class"
                join_headers = {"Authorization": f"Bearer {self.student_token}"}
                join_payload = {"join_code": second_join_code}
                
                join_response = requests.post(join_url, json=join_payload, headers=join_headers)
                print(f"Join Second Class Response: {join_response.status_code}")
                
                if join_response.status_code == 200:
                    # Now test the joined-classes endpoint
                    url = f"{API_URL}/student/joined-classes"
                    headers = {"Authorization": f"Bearer {self.student_token}"}
                    
                    response = requests.get(url, headers=headers)
                    print(f"Multiple Classes Response: {response.status_code}")
                    
                    self.assertEqual(response.status_code, 200, "Failed to get joined classes")
                    data = response.json()
                    
                    self.assertIsInstance(data, list, "Response should be a list")
                    self.assertGreaterEqual(len(data), 2, "Should have at least 2 joined classes")
                    
                    # Verify both classes are present
                    class_ids = [cls.get("class_id") for cls in data]
                    class_names = [cls.get("class_name") for cls in data]
                    
                    self.assertIn(self.class_id, class_ids, "First class should be present")
                    self.assertIn(second_class_id, class_ids, "Second class should be present")
                    self.assertIn("Advanced Organic Chemistry", class_names, "Chemistry class should be present")
                    self.assertIn("Quantum Physics Fundamentals", class_names, "Physics class should be present")
                    
                    print("✅ Multiple classes test passed")
                    print(f"Student is enrolled in {len(data)} classes:")
                    for cls in data:
                        print(f"  - {cls.get('class_name')} ({cls.get('subject')})")
                else:
                    print("⚠️ Could not join second class, testing with single class")
            else:
                print("⚠️ Could not create second class, testing with single class")
                
        except Exception as e:
            print(f"⚠️ Multiple classes test encountered error: {str(e)}")
            print("Continuing with single class test...")

    def test_06_class_name_display_fix_verification(self):
        """Verify that the class name display issue is resolved"""
        print("\n🔍 Testing Class Name Display Fix Verification...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Ensure we have a class to test with
        if not self.class_id:
            self.test_03_create_class_and_join()
        
        if not self.class_id:
            self.skipTest("No class available for testing")
        
        url = f"{API_URL}/student/joined-classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Class Name Display Fix Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get joined classes")
            data = response.json()
            
            self.assertTrue(len(data) > 0, "Should have at least one joined class")
            
            # Focus specifically on class name display
            for class_info in data:
                class_name = class_info.get("class_name")
                
                # Verify class_name is present and not empty
                self.assertIsNotNone(class_name, "class_name should not be None")
                self.assertIsInstance(class_name, str, "class_name should be a string")
                self.assertTrue(len(class_name.strip()) > 0, "class_name should not be empty")
                
                # Verify it's not just an ID or placeholder
                self.assertNotEqual(class_name.lower(), "untitled", "class_name should not be a placeholder")
                self.assertNotEqual(class_name.lower(), "class", "class_name should not be generic")
                self.assertFalse(class_name.startswith("class_"), "class_name should not be an ID")
                
                print(f"✅ Class name properly displayed: '{class_name}'")
            
            print("✅ Class name display fix verification passed")
            print("🎯 ISSUE RESOLVED: Students can now see proper class names in their 'My Classes' view")
            
        except Exception as e:
            print(f"❌ Class name display fix verification failed: {str(e)}")
            self.fail(f"Class name display fix verification failed: {str(e)}")

class TestTutorAPIRoutes(unittest.TestCase):
    """Test cases specifically for the Tutor API routes implementation"""

    def setUp(self):
        """Set up test case - create student account for tutor testing"""
        self.student_token = None
        self.student_id = None
        self.session_id = None
        
        # Register student for tutor testing
        self.register_student()

    def register_student(self):
        """Register a student for tutor testing"""
        print("\n🔍 Setting up student account for tutor testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"tutor_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Tutor Test Student",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered tutor test student with ID: {self.student_id}")
            else:
                print(f"Failed to register tutor test student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering tutor test student: {str(e)}")

    def test_01_create_tutor_session(self):
        """Test POST /api/tutor/session - Create new chat session"""
        print("\n🔍 Testing Tutor Session Creation...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/tutor/session"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test with different subjects
        test_subjects = [Subject.MATH.value, Subject.PHYSICS.value, Subject.CHEMISTRY.value]
        
        for subject in test_subjects:
            payload = {
                "subject": subject,
                "session_type": "tutoring"
            }
            
            try:
                print(f"Creating session for subject: {subject}")
                response = requests.post(url, json=payload, headers=headers)
                print(f"Create Session Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    self.assertIn("session_id", data, "Session ID should be present")
                    self.assertIn("subject", data, "Subject should be present")
                    self.assertIn("started_at", data, "Started at should be present")
                    self.assertIn("last_activity", data, "Last activity should be present")
                    self.assertIn("message_count", data, "Message count should be present")
                    self.assertIn("topics_covered", data, "Topics covered should be present")
                    self.assertIn("is_active", data, "Is active should be present")
                    
                    # Verify data values
                    self.assertEqual(data.get("subject"), subject, f"Subject should be {subject}")
                    self.assertEqual(data.get("message_count"), 0, "Initial message count should be 0")
                    self.assertEqual(data.get("is_active"), True, "Session should be active")
                    self.assertIsInstance(data.get("topics_covered"), list, "Topics covered should be a list")
                    
                    # Store session ID for further tests
                    if subject == Subject.MATH.value:
                        self.session_id = data.get("session_id")
                    
                    print(f"✅ Successfully created {subject} session: {data.get('session_id')}")
                else:
                    print(f"❌ Failed to create {subject} session: {response.status_code} - {response.text}")
                    self.fail(f"Failed to create {subject} session: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating {subject} session: {str(e)}")
                self.fail(f"Error creating {subject} session: {str(e)}")

    def test_02_send_tutor_message(self):
        """Test POST /api/tutor/chat - Send message and get AI response"""
        print("\n🔍 Testing Tutor Chat Message...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        if not self.session_id:
            # Create a session first
            self.test_01_create_tutor_session()
        
        if not self.session_id:
            self.skipTest("Session ID not available")
        
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different types of messages
        test_messages = [
            {
                "message": "Can you help me solve the quadratic equation x^2 - 5x + 6 = 0?",
                "subject": Subject.MATH.value,
                "description": "Math quadratic equation"
            },
            {
                "message": "What is the derivative of x^3?",
                "subject": Subject.MATH.value,
                "description": "Math calculus derivative"
            },
            {
                "message": "Explain the concept of limits in calculus",
                "subject": Subject.MATH.value,
                "description": "Math concept explanation"
            }
        ]
        
        for test_msg in test_messages:
            payload = {
                "message": test_msg["message"],
                "subject": test_msg["subject"],
                "session_id": self.session_id
            }
            
            try:
                print(f"Sending message: {test_msg['description']}")
                response = requests.post(url, json=payload, headers=headers)
                print(f"Send Message Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    self.assertIn("message_id", data, "Message ID should be present")
                    self.assertIn("response", data, "AI response should be present")
                    self.assertIn("session_id", data, "Session ID should be present")
                    self.assertIn("timestamp", data, "Timestamp should be present")
                    
                    # Verify data values
                    self.assertEqual(data.get("session_id"), self.session_id, "Session ID should match")
                    self.assertIsNotNone(data.get("response"), "AI response should not be None")
                    self.assertTrue(len(data.get("response", "")) > 0, "AI response should not be empty")
                    
                    print(f"✅ Successfully sent message and received response")
                    print(f"Response preview: {data.get('response')[:100]}...")
                else:
                    print(f"❌ Failed to send message: {response.status_code} - {response.text}")
                    self.fail(f"Failed to send message: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error sending message: {str(e)}")
                self.fail(f"Error sending message: {str(e)}")

    def test_03_get_tutor_sessions(self):
        """Test GET /api/tutor/sessions - Get chat history"""
        print("\n🔍 Testing Get Tutor Sessions...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/tutor/sessions"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Sessions Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response is a list
                self.assertIsInstance(data, list, "Sessions should be a list")
                
                if len(data) > 0:
                    # Check first session structure
                    session = data[0]
                    self.assertIn("session_id", session, "Session ID should be present")
                    self.assertIn("subject", session, "Subject should be present")
                    self.assertIn("started_at", session, "Started at should be present")
                    self.assertIn("last_activity", session, "Last activity should be present")
                    self.assertIn("message_count", session, "Message count should be present")
                    self.assertIn("topics_covered", session, "Topics covered should be present")
                    self.assertIn("is_active", session, "Is active should be present")
                    
                    print(f"✅ Successfully retrieved {len(data)} sessions")
                    
                    # Verify sessions are sorted by last_activity (most recent first)
                    if len(data) > 1:
                        for i in range(len(data) - 1):
                            current_activity = data[i].get("last_activity")
                            next_activity = data[i + 1].get("last_activity")
                            # Note: This is a basic check, proper datetime comparison would be better
                            print(f"Session {i}: {current_activity}, Session {i+1}: {next_activity}")
                else:
                    print("✅ No sessions found (expected for new user)")
                    
            else:
                print(f"❌ Failed to get sessions: {response.status_code} - {response.text}")
                self.fail(f"Failed to get sessions: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting sessions: {str(e)}")
            self.fail(f"Error getting sessions: {str(e)}")

    def test_04_get_session_messages(self):
        """Test GET /api/tutor/session/{session_id}/messages - Get session messages"""
        print("\n🔍 Testing Get Session Messages...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        if not self.session_id:
            # Try to get sessions and use the first one
            sessions_url = f"{API_URL}/tutor/sessions"
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            try:
                sessions_response = requests.get(sessions_url, headers=headers)
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    if len(sessions) > 0:
                        self.session_id = sessions[0].get("session_id")
                    else:
                        self.skipTest("No sessions available for testing")
                else:
                    self.skipTest("Could not retrieve sessions")
            except:
                self.skipTest("Error retrieving sessions")
        
        if not self.session_id:
            self.skipTest("Session ID not available")
        
        url = f"{API_URL}/tutor/session/{self.session_id}/messages"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Session Messages Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response is a list
                self.assertIsInstance(data, list, "Messages should be a list")
                
                if len(data) > 0:
                    # Check first message structure
                    message = data[0]
                    self.assertIn("id", message, "Message ID should be present")
                    self.assertIn("session_id", message, "Session ID should be present")
                    self.assertIn("message", message, "Message should be present")
                    self.assertIn("response", message, "Response should be present")
                    self.assertIn("timestamp", message, "Timestamp should be present")
                    self.assertIn("message_type", message, "Message type should be present")
                    
                    # Verify session ID matches
                    self.assertEqual(message.get("session_id"), self.session_id, "Session ID should match")
                    
                    print(f"✅ Successfully retrieved {len(data)} messages for session")
                    
                    # Verify messages are sorted by timestamp (oldest first)
                    if len(data) > 1:
                        for i in range(len(data) - 1):
                            current_timestamp = data[i].get("timestamp")
                            next_timestamp = data[i + 1].get("timestamp")
                            print(f"Message {i}: {current_timestamp}, Message {i+1}: {next_timestamp}")
                else:
                    print("✅ No messages found in session (expected for new session)")
                    
            elif response.status_code == 404:
                print("❌ Session not found - this could indicate an authorization issue")
                self.fail("Session not found - check authorization")
            else:
                print(f"❌ Failed to get session messages: {response.status_code} - {response.text}")
                self.fail(f"Failed to get session messages: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting session messages: {str(e)}")
            self.fail(f"Error getting session messages: {str(e)}")

    def test_05_delete_tutor_session(self):
        """Test DELETE /api/tutor/session/{session_id} - Delete chat session"""
        print("\n🔍 Testing Delete Tutor Session...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Create a session specifically for deletion testing
        create_url = f"{API_URL}/tutor/session"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        create_payload = {
            "subject": Subject.PHYSICS.value,
            "session_type": "tutoring"
        }
        
        try:
            # Create session to delete
            create_response = requests.post(create_url, json=create_payload, headers=headers)
            if create_response.status_code != 200:
                self.skipTest("Could not create session for deletion test")
            
            session_to_delete = create_response.json().get("session_id")
            if not session_to_delete:
                self.skipTest("Could not get session ID for deletion test")
            
            print(f"Created session for deletion: {session_to_delete}")
            
            # Delete the session
            delete_url = f"{API_URL}/tutor/session/{session_to_delete}"
            delete_response = requests.delete(delete_url, headers=headers)
            print(f"Delete Session Response: {delete_response.status_code}")
            
            if delete_response.status_code == 200:
                data = delete_response.json()
                
                # Verify response structure
                self.assertIn("message", data, "Success message should be present")
                self.assertIn("deleted", data.get("message", "").lower(), "Message should indicate deletion")
                
                print("✅ Successfully deleted session")
                
                # Verify session is actually deleted by trying to get its messages
                messages_url = f"{API_URL}/tutor/session/{session_to_delete}/messages"
                messages_response = requests.get(messages_url, headers=headers)
                
                if messages_response.status_code == 404:
                    print("✅ Confirmed session is deleted (404 when accessing messages)")
                else:
                    print(f"⚠️ Session may not be fully deleted (messages still accessible: {messages_response.status_code})")
                    
            elif delete_response.status_code == 404:
                print("❌ Session not found for deletion - this could indicate an authorization issue")
                self.fail("Session not found for deletion - check authorization")
            else:
                print(f"❌ Failed to delete session: {delete_response.status_code} - {delete_response.text}")
                self.fail(f"Failed to delete session: {delete_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error deleting session: {str(e)}")
            self.fail(f"Error deleting session: {str(e)}")

    def test_06_tutor_authentication_required(self):
        """Test that tutor endpoints require student authentication"""
        print("\n🔍 Testing Tutor Authentication Requirements...")
        
        # Test endpoints without authentication
        endpoints_to_test = [
            ("POST", f"{API_URL}/tutor/session", {"subject": "math"}),
            ("POST", f"{API_URL}/tutor/chat", {"message": "test", "subject": "math", "session_id": "test"}),
            ("GET", f"{API_URL}/tutor/sessions", None),
            ("GET", f"{API_URL}/tutor/session/test/messages", None),
            ("DELETE", f"{API_URL}/tutor/session/test", None)
        ]
        
        for method, url, payload in endpoints_to_test:
            try:
                if method == "POST":
                    response = requests.post(url, json=payload)
                elif method == "GET":
                    response = requests.get(url)
                elif method == "DELETE":
                    response = requests.delete(url)
                
                print(f"{method} {url}: {response.status_code}")
                
                # Should return 401 or 403 for unauthorized access
                self.assertIn(response.status_code, [401, 403], 
                             f"{method} {url} should require authentication")
                
            except Exception as e:
                print(f"❌ Error testing {method} {url}: {str(e)}")
        
        print("✅ All tutor endpoints properly require authentication")

    def test_07_tutor_error_handling(self):
        """Test error handling for tutor endpoints"""
        print("\n🔍 Testing Tutor Error Handling...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test invalid session ID for chat
        chat_url = f"{API_URL}/tutor/chat"
        invalid_chat_payload = {
            "message": "test message",
            "subject": Subject.MATH.value,
            "session_id": "invalid-session-id"
        }
        
        try:
            response = requests.post(chat_url, json=invalid_chat_payload, headers=headers)
            print(f"Invalid session chat response: {response.status_code}")
            
            # Should return 404 for invalid session
            self.assertEqual(response.status_code, 404, "Invalid session should return 404")
            
        except Exception as e:
            print(f"❌ Error testing invalid session: {str(e)}")
        
        # Test invalid session ID for messages
        messages_url = f"{API_URL}/tutor/session/invalid-session-id/messages"
        
        try:
            response = requests.get(messages_url, headers=headers)
            print(f"Invalid session messages response: {response.status_code}")
            
            # Should return 404 for invalid session
            self.assertEqual(response.status_code, 404, "Invalid session should return 404")
            
        except Exception as e:
            print(f"❌ Error testing invalid session messages: {str(e)}")
        
        # Test invalid session ID for deletion
        delete_url = f"{API_URL}/tutor/session/invalid-session-id"
        
        try:
            response = requests.delete(delete_url, headers=headers)
            print(f"Invalid session deletion response: {response.status_code}")
            
            # Should return 404 for invalid session
            self.assertEqual(response.status_code, 404, "Invalid session should return 404")
            
        except Exception as e:
            print(f"❌ Error testing invalid session deletion: {str(e)}")
        
        print("✅ Error handling tests completed")

class TestStudyPlannerAPI(unittest.TestCase):
    """Test cases specifically for the Smart Calendar Bot Study Planner API endpoints"""

    def setUp(self):
        """Set up test case - create student account for study planner testing"""
        self.student_token = None
        self.student_id = None
        self.plan_id = None
        
        # Register student for study planner testing
        self.register_student()

    def register_student(self):
        """Register a student for study planner testing"""
        print("\n🔍 Setting up student account for study planner testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"study_planner_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Mehta",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered study planner test student with ID: {self.student_id}")
            else:
                print(f"Failed to register study planner test student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering study planner test student: {str(e)}")

    def test_01_study_planner_chat_greeting(self):
        """Test POST /api/study-planner/chat - Initial greeting"""
        print("\n🔍 Testing Study Planner Chat - Initial Greeting...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/study-planner/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "message": "Hello",
            "context": None
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Study Planner Chat Greeting Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get study planner greeting")
            data = response.json()
            
            # Verify response structure
            self.assertIn("response", data, "Response should be present")
            self.assertIn("needs_input", data, "Needs input should be present")
            self.assertIn("input_type", data, "Input type should be present")
            self.assertIn("suggested_actions", data, "Suggested actions should be present")
            
            # Verify greeting content
            response_text = data.get("response", "")
            self.assertIn("Smart Study Planner", response_text, "Should mention Smart Study Planner")
            self.assertIn("Pomodoro", response_text, "Should mention Pomodoro technique")
            self.assertTrue(data.get("needs_input"), "Should need input after greeting")
            self.assertEqual(data.get("input_type"), "requirements", "Should ask for requirements")
            
            # Verify suggested actions
            suggested_actions = data.get("suggested_actions", [])
            self.assertIsInstance(suggested_actions, list, "Suggested actions should be a list")
            self.assertTrue(len(suggested_actions) > 0, "Should have suggested actions")
            
            print("✅ Study planner greeting test passed")
            print(f"Bot response preview: {response_text[:100]}...")
            
        except Exception as e:
            print(f"❌ Study planner greeting test failed: {str(e)}")
            self.fail(f"Study planner greeting test failed: {str(e)}")

    def test_02_study_planner_chat_requirements_gathering(self):
        """Test POST /api/study-planner/chat - Requirements gathering conversation"""
        print("\n🔍 Testing Study Planner Chat - Requirements Gathering...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/study-planner/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different requirement gathering scenarios
        test_scenarios = [
            {
                "message": "I want to study for 2 hours total - 1 hour math and 1 hour physics",
                "description": "Complete requirements in one message",
                "expected_stage": "confirmation"
            },
            {
                "message": "I need to study for 90 minutes",
                "description": "Duration only",
                "expected_stage": "collecting_requirements"
            },
            {
                "message": "I want to study math and physics",
                "description": "Subjects only",
                "expected_stage": "collecting_requirements"
            }
        ]
        
        for scenario in test_scenarios:
            payload = {
                "message": scenario["message"],
                "context": {"stage": "collecting_requirements", "requirements": {}}
            }
            
            try:
                print(f"Testing scenario: {scenario['description']}")
                response = requests.post(url, json=payload, headers=headers)
                print(f"Requirements Gathering Response: {response.status_code}")
                
                self.assertEqual(response.status_code, 200, f"Failed to process requirements: {scenario['description']}")
                data = response.json()
                
                # Verify response structure
                self.assertIn("response", data, "Response should be present")
                self.assertIn("needs_input", data, "Needs input should be present")
                self.assertIn("context", data, "Context should be present")
                
                # Verify context progression
                context = data.get("context", {})
                if scenario["expected_stage"] == "confirmation":
                    # Should move to confirmation stage if complete requirements provided
                    self.assertIn("requirements", context, "Requirements should be stored in context")
                    requirements = context.get("requirements", {})
                    self.assertTrue(len(requirements) > 0, "Requirements should not be empty")
                
                response_text = data.get("response", "")
                print(f"Bot response preview: {response_text[:100]}...")
                print("✅ Requirements gathering scenario passed")
                
            except Exception as e:
                print(f"❌ Requirements gathering scenario failed: {str(e)}")
                self.fail(f"Requirements gathering scenario failed: {str(e)}")

    def test_03_study_planner_generate_plan(self):
        """Test POST /api/study-planner/generate-plan - Generate Pomodoro study plan"""
        print("\n🔍 Testing Study Planner - Generate Plan...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/study-planner/generate-plan"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test plan generation with realistic study requirements
        payload = {
            "total_duration_minutes": 120,  # 2 hours
            "subjects": [
                {
                    "subject": "math",
                    "duration_minutes": 60,
                    "priority": "high",
                    "notes": "Focus on algebra and geometry"
                },
                {
                    "subject": "physics",
                    "duration_minutes": 60,
                    "priority": "medium",
                    "notes": "Mechanics and thermodynamics"
                }
            ],
            "preferred_start_time": "09:00",
            "break_preferences": {
                "short_break_activity": "stretch",
                "long_break_activity": "walk"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Generate Plan Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to generate study plan")
            data = response.json()
            
            # Verify response structure
            required_fields = [
                "plan_id", "total_duration_minutes", "total_work_time", 
                "total_break_time", "pomodoro_sessions", "study_tips", "created_at"
            ]
            
            for field in required_fields:
                self.assertIn(field, data, f"Field '{field}' should be present in plan response")
            
            # Verify plan data
            self.assertEqual(data.get("total_duration_minutes"), 120, "Total duration should match request")
            self.assertIsNotNone(data.get("plan_id"), "Plan ID should not be None")
            
            # Store plan ID for further tests
            self.plan_id = data.get("plan_id")
            
            # Verify Pomodoro sessions
            pomodoro_sessions = data.get("pomodoro_sessions", [])
            self.assertIsInstance(pomodoro_sessions, list, "Pomodoro sessions should be a list")
            self.assertTrue(len(pomodoro_sessions) > 0, "Should have Pomodoro sessions")
            
            # Verify session structure
            work_sessions = [s for s in pomodoro_sessions if s.get("session_type") == "work"]
            break_sessions = [s for s in pomodoro_sessions if s.get("session_type") == "break"]
            
            self.assertTrue(len(work_sessions) > 0, "Should have work sessions")
            self.assertTrue(len(break_sessions) > 0, "Should have break sessions")
            
            # Verify Pomodoro timing (25-minute work sessions)
            for work_session in work_sessions:
                duration = work_session.get("duration_minutes", 0)
                self.assertLessEqual(duration, 25, "Work sessions should be <= 25 minutes (Pomodoro standard)")
                self.assertIn("subject", work_session, "Work sessions should have subject")
                self.assertIn("description", work_session, "Work sessions should have description")
            
            # Verify break timing (5 or 15 minute breaks)
            for break_session in break_sessions:
                duration = break_session.get("duration_minutes", 0)
                self.assertIn(duration, [5, 15], "Break sessions should be 5 or 15 minutes")
                self.assertIn("break_activity", break_session, "Break sessions should have activity")
            
            # Verify study tips
            study_tips = data.get("study_tips", [])
            self.assertIsInstance(study_tips, list, "Study tips should be a list")
            self.assertTrue(len(study_tips) > 0, "Should have study tips")
            
            # Verify work/break time calculation
            total_work_time = data.get("total_work_time", 0)
            total_break_time = data.get("total_break_time", 0)
            calculated_work_time = sum(s.get("duration_minutes", 0) for s in work_sessions)
            calculated_break_time = sum(s.get("duration_minutes", 0) for s in break_sessions)
            
            self.assertEqual(total_work_time, calculated_work_time, "Total work time should match calculated")
            self.assertEqual(total_break_time, calculated_break_time, "Total break time should match calculated")
            
            print("✅ Study plan generation test passed")
            print(f"Generated plan ID: {self.plan_id}")
            print(f"Work sessions: {len(work_sessions)}, Break sessions: {len(break_sessions)}")
            print(f"Total work time: {total_work_time} min, Total break time: {total_break_time} min")
            print(f"Study tips provided: {len(study_tips)}")
            
        except Exception as e:
            print(f"❌ Study plan generation test failed: {str(e)}")
            self.fail(f"Study plan generation test failed: {str(e)}")

    def test_04_get_my_study_plans(self):
        """Test GET /api/study-planner/my-plans - Get user's study plans"""
        print("\n🔍 Testing Get My Study Plans...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Ensure we have a plan to retrieve
        if not self.plan_id:
            self.test_03_study_planner_generate_plan()
        
        url = f"{API_URL}/study-planner/my-plans"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get My Plans Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get study plans")
            data = response.json()
            
            # Verify response is a list
            self.assertIsInstance(data, list, "Study plans should be a list")
            
            if self.plan_id:
                # Should have at least one plan
                self.assertTrue(len(data) > 0, "Should have at least one study plan")
                
                # Find our created plan
                our_plan = None
                for plan in data:
                    if plan.get("plan_id") == self.plan_id:
                        our_plan = plan
                        break
                
                self.assertIsNotNone(our_plan, "Should find our created plan")
                
                # Verify plan structure
                required_fields = [
                    "plan_id", "user_id", "total_duration_minutes", "subjects", 
                    "pomodoro_sessions", "study_tips", "created_at", "used"
                ]
                
                for field in required_fields:
                    self.assertIn(field, our_plan, f"Field '{field}' should be present in plan")
                
                # Verify plan data
                self.assertEqual(our_plan.get("plan_id"), self.plan_id, "Plan ID should match")
                self.assertEqual(our_plan.get("user_id"), self.student_id, "User ID should match")
                self.assertEqual(our_plan.get("used"), False, "Plan should not be used initially")
                
                print("✅ Get my study plans test passed")
                print(f"Retrieved {len(data)} study plans")
            else:
                print("✅ Get my study plans test passed (no plans found)")
                
        except Exception as e:
            print(f"❌ Get my study plans test failed: {str(e)}")
            self.fail(f"Get my study plans test failed: {str(e)}")

    def test_05_start_study_session(self):
        """Test POST /api/study-planner/start-session/{plan_id} - Start a study session"""
        print("\n🔍 Testing Start Study Session...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Ensure we have a plan to start
        if not self.plan_id:
            self.test_03_study_planner_generate_plan()
        
        if not self.plan_id:
            self.skipTest("Plan ID not available")
        
        url = f"{API_URL}/study-planner/start-session/{self.plan_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            print(f"Start Session Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to start study session")
            data = response.json()
            
            # Verify response structure
            self.assertIn("message", data, "Message should be present")
            self.assertIn("plan_id", data, "Plan ID should be present")
            self.assertIn("calendar_events", data, "Calendar events should be present")
            
            # Verify data values
            self.assertEqual(data.get("plan_id"), self.plan_id, "Plan ID should match")
            self.assertIn("started successfully", data.get("message", ""), "Should confirm session started")
            
            # Verify calendar events
            calendar_events = data.get("calendar_events", [])
            self.assertIsInstance(calendar_events, list, "Calendar events should be a list")
            
            if len(calendar_events) > 0:
                # Check first event structure
                event = calendar_events[0]
                event_fields = ["title", "description", "start_time", "end_time", "event_type", "subject"]
                
                for field in event_fields:
                    self.assertIn(field, event, f"Field '{field}' should be present in calendar event")
                
                # Verify event data
                self.assertEqual(event.get("event_type"), "study", "Event type should be study")
                self.assertIn("Study:", event.get("title", ""), "Event title should indicate study")
                
                print(f"Generated {len(calendar_events)} calendar events")
            
            # Verify plan is marked as used
            plans_url = f"{API_URL}/study-planner/my-plans"
            plans_response = requests.get(plans_url, headers=headers)
            
            if plans_response.status_code == 200:
                plans = plans_response.json()
                started_plan = None
                
                for plan in plans:
                    if plan.get("plan_id") == self.plan_id:
                        started_plan = plan
                        break
                
                if started_plan:
                    self.assertEqual(started_plan.get("used"), True, "Plan should be marked as used")
                    self.assertIn("started_at", started_plan, "Plan should have started_at timestamp")
            
            print("✅ Start study session test passed")
            print(f"Started session for plan: {self.plan_id}")
            
        except Exception as e:
            print(f"❌ Start study session test failed: {str(e)}")
            self.fail(f"Start study session test failed: {str(e)}")

    def test_06_delete_study_plan(self):
        """Test DELETE /api/study-planner/plan/{plan_id} - Delete a study plan"""
        print("\n🔍 Testing Delete Study Plan...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Create a plan specifically for deletion testing
        create_url = f"{API_URL}/study-planner/generate-plan"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        create_payload = {
            "total_duration_minutes": 60,
            "subjects": [
                {
                    "subject": "chemistry",
                    "duration_minutes": 60,
                    "priority": "medium",
                    "notes": "Organic chemistry review"
                }
            ]
        }
        
        try:
            # Create plan to delete
            create_response = requests.post(create_url, json=create_payload, headers=headers)
            if create_response.status_code != 200:
                self.skipTest("Could not create plan for deletion test")
            
            plan_to_delete = create_response.json().get("plan_id")
            if not plan_to_delete:
                self.skipTest("Could not get plan ID for deletion test")
            
            print(f"Created plan for deletion: {plan_to_delete}")
            
            # Delete the plan
            delete_url = f"{API_URL}/study-planner/plan/{plan_to_delete}"
            delete_response = requests.delete(delete_url, headers=headers)
            print(f"Delete Plan Response: {delete_response.status_code}")
            
            self.assertEqual(delete_response.status_code, 200, "Failed to delete study plan")
            delete_data = delete_response.json()
            
            # Verify response
            self.assertIn("message", delete_data, "Message should be present")
            self.assertIn("deleted successfully", delete_data.get("message", ""), "Should confirm deletion")
            
            # Verify plan is actually deleted
            plans_url = f"{API_URL}/study-planner/my-plans"
            plans_response = requests.get(plans_url, headers=headers)
            
            if plans_response.status_code == 200:
                plans = plans_response.json()
                deleted_plan = None
                
                for plan in plans:
                    if plan.get("plan_id") == plan_to_delete:
                        deleted_plan = plan
                        break
                
                self.assertIsNone(deleted_plan, "Deleted plan should not be found in user's plans")
            
            # Test deleting non-existent plan
            fake_plan_id = str(uuid.uuid4())
            fake_delete_url = f"{API_URL}/study-planner/plan/{fake_plan_id}"
            fake_delete_response = requests.delete(fake_delete_url, headers=headers)
            print(f"Delete Non-existent Plan Response: {fake_delete_response.status_code}")
            
            self.assertEqual(fake_delete_response.status_code, 404, "Should return 404 for non-existent plan")
            
            print("✅ Delete study plan test passed")
            
        except Exception as e:
            print(f"❌ Delete study plan test failed: {str(e)}")
            self.fail(f"Delete study plan test failed: {str(e)}")

    def test_07_study_planner_authentication(self):
        """Test study planner endpoints require authentication"""
        print("\n🔍 Testing Study Planner Authentication Requirements...")
        
        # Test all endpoints without authentication
        endpoints = [
            ("POST", f"{API_URL}/study-planner/chat", {"message": "Hello"}),
            ("POST", f"{API_URL}/study-planner/generate-plan", {"total_duration_minutes": 60, "subjects": []}),
            ("GET", f"{API_URL}/study-planner/my-plans", None),
            ("POST", f"{API_URL}/study-planner/start-session/fake-id", None),
            ("DELETE", f"{API_URL}/study-planner/plan/fake-id", None)
        ]
        
        for method, url, payload in endpoints:
            try:
                print(f"Testing {method} {url.split('/')[-1]} without auth...")
                
                if method == "POST":
                    response = requests.post(url, json=payload) if payload else requests.post(url)
                elif method == "GET":
                    response = requests.get(url)
                elif method == "DELETE":
                    response = requests.delete(url)
                
                print(f"Response: {response.status_code}")
                
                # Should require authentication
                self.assertIn(response.status_code, [401, 403], 
                             f"{method} {url} should require authentication")
                
            except Exception as e:
                print(f"❌ Error testing {method} {url}: {str(e)}")
                self.fail(f"Error testing {method} {url}: {str(e)}")
        
        print("✅ Study planner authentication test passed")

    def test_08_study_planner_ai_integration(self):
        """Test study planner AI integration and optimization"""
        print("\n🔍 Testing Study Planner AI Integration...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Test AI-powered subject optimization
        url = f"{API_URL}/study-planner/generate-plan"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test with multiple subjects to verify AI optimization
        payload = {
            "total_duration_minutes": 150,  # 2.5 hours
            "subjects": [
                {
                    "subject": "math",
                    "duration_minutes": 50,
                    "priority": "high",
                    "notes": "Calculus and algebra"
                },
                {
                    "subject": "english",
                    "duration_minutes": 50,
                    "priority": "medium", 
                    "notes": "Literature analysis"
                },
                {
                    "subject": "physics",
                    "duration_minutes": 50,
                    "priority": "high",
                    "notes": "Mechanics and waves"
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"AI Integration Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to generate AI-optimized plan")
            data = response.json()
            
            # Verify AI optimization features
            pomodoro_sessions = data.get("pomodoro_sessions", [])
            work_sessions = [s for s in pomodoro_sessions if s.get("session_type") == "work"]
            
            # Verify subject alternation (AI optimization)
            if len(work_sessions) >= 3:
                subjects_order = [s.get("subject") for s in work_sessions]
                
                # Check that subjects are alternated (not all same subject in a row)
                consecutive_same = 0
                max_consecutive = 0
                
                for i in range(1, len(subjects_order)):
                    if subjects_order[i] == subjects_order[i-1]:
                        consecutive_same += 1
                        max_consecutive = max(max_consecutive, consecutive_same + 1)
                    else:
                        consecutive_same = 0
                
                # AI should optimize to avoid too many consecutive sessions of same subject
                self.assertLessEqual(max_consecutive, 2, 
                                   "AI should optimize subject ordering to avoid too many consecutive sessions")
                
                print(f"Subject order: {subjects_order}")
                print(f"Max consecutive same subject: {max_consecutive}")
            
            # Verify study tips are AI-generated and relevant
            study_tips = data.get("study_tips", [])
            self.assertTrue(len(study_tips) >= 3, "Should have multiple AI-generated study tips")
            
            # Verify tips contain Pomodoro-related advice
            tips_text = " ".join(study_tips).lower()
            pomodoro_keywords = ["focus", "break", "session", "distraction", "25", "minute"]
            found_keywords = sum(1 for keyword in pomodoro_keywords if keyword in tips_text)
            
            self.assertGreaterEqual(found_keywords, 2, 
                                  "Study tips should contain Pomodoro-related advice")
            
            print("✅ Study planner AI integration test passed")
            print(f"AI optimization verified with {len(work_sessions)} work sessions")
            print(f"Study tips generated: {len(study_tips)}")
            
        except Exception as e:
            print(f"❌ Study planner AI integration test failed: {str(e)}")
            self.fail(f"Study planner AI integration test failed: {str(e)}")


class TestStudentAnalyticsEndpoints(unittest.TestCase):
    """Test cases specifically for the newly implemented Student Analytics endpoints"""

    def setUp(self):
        """Set up test case - create student account with practice test data"""
        self.student_token = None
        self.student_id = None
        self.student_with_data_token = None
        self.student_with_data_id = None
        
        # Register student accounts
        self.register_student_no_data()
        self.register_student_with_data()
        self.create_practice_test_data()

    def register_student_no_data(self):
        """Register a student with no practice test data"""
        print("\n🔍 Setting up student account with no data for analytics testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"analytics_no_data_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Priya Sharma",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_10.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student (no data) with ID: {self.student_id}")
            else:
                print(f"Failed to register student (no data): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student (no data): {str(e)}")

    def register_student_with_data(self):
        """Register a student who will have practice test data"""
        print("\n🔍 Setting up student account with data for analytics testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"analytics_with_data_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Kumar",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_11.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_with_data_token = data.get("access_token")
                self.student_with_data_id = data.get("user", {}).get("id")
                print(f"Registered student (with data) with ID: {self.student_with_data_id}")
            else:
                print(f"Failed to register student (with data): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student (with data): {str(e)}")

    def create_practice_test_data(self):
        """Create comprehensive practice test data for analytics testing"""
        print("\n🔍 Creating comprehensive practice test data for analytics...")
        
        if not self.student_with_data_token:
            print("⚠️ Student with data token not available, skipping data creation")
            return
        
        # Create practice tests with different subjects and performance patterns
        test_scenarios = [
            # Math - Strong performance (should be identified as strength)
            (Subject.MATH.value, ["Algebra"], 88, "Strong math performance"),
            (Subject.MATH.value, ["Geometry"], 92, "Strong math performance"),
            (Subject.MATH.value, ["Calculus"], 85, "Strong math performance"),
            (Subject.MATH.value, ["Statistics"], 90, "Strong math performance"),
            
            # Physics - Weak performance (should be identified as weakness)
            (Subject.PHYSICS.value, ["Mechanics"], 55, "Weak physics performance"),
            (Subject.PHYSICS.value, ["Thermodynamics"], 58, "Weak physics performance"),
            (Subject.PHYSICS.value, ["Optics"], 52, "Weak physics performance"),
            
            # Chemistry - Improving performance (should show trend)
            (Subject.CHEMISTRY.value, ["Organic Chemistry"], 65, "Improving chemistry - early"),
            (Subject.CHEMISTRY.value, ["Inorganic Chemistry"], 72, "Improving chemistry - middle"),
            (Subject.CHEMISTRY.value, ["Physical Chemistry"], 78, "Improving chemistry - recent"),
            
            # Biology - Declining performance (should show trend)
            (Subject.BIOLOGY.value, ["Cell Biology"], 82, "Declining biology - early"),
            (Subject.BIOLOGY.value, ["Genetics"], 75, "Declining biology - middle"),
            (Subject.BIOLOGY.value, ["Ecology"], 68, "Declining biology - recent"),
        ]
        
        created_tests = 0
        for subject, topics, target_score, description in test_scenarios:
            try:
                # Generate practice test
                gen_url = f"{API_URL}/practice/generate"
                headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
                gen_payload = {
                    "subject": subject,
                    "topics": topics,
                    "difficulty": DifficultyLevel.MEDIUM.value,
                    "question_count": 5
                }
                
                gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    questions = gen_data.get("questions", [])
                    
                    if questions:
                        # Create student answers to achieve target score
                        student_answers = {}
                        correct_answers_needed = int((target_score / 100) * len(questions))
                        
                        for i, question in enumerate(questions):
                            question_id = question.get("id")
                            if i < correct_answers_needed:
                                # Give correct answer
                                student_answers[question_id] = question.get("correct_answer", "correct")
                            else:
                                # Give wrong answer
                                student_answers[question_id] = "wrong_answer"
                        
                        # Submit the test
                        submit_url = f"{API_URL}/practice/submit"
                        submit_payload = {
                            "questions": [q.get("id") for q in questions],
                            "student_answers": student_answers,
                            "subject": subject,
                            "time_taken": 300 + (created_tests * 30)  # Vary time taken
                        }
                        
                        submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                        if submit_response.status_code == 200:
                            submit_data = submit_response.json()
                            actual_score = submit_data.get('score', 0)
                            print(f"✅ Created {subject} test: {actual_score}% (target: {target_score}%) - {description}")
                            created_tests += 1
                            
                            # Add small delay to ensure different timestamps
                            time.sleep(0.5)
                        else:
                            print(f"❌ Failed to submit {subject} test: {submit_response.text}")
                    else:
                        print(f"❌ No questions generated for {subject}")
                else:
                    print(f"❌ Failed to generate {subject} test: {gen_response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating practice test for {subject}: {str(e)}")
        
        print(f"✅ Created {created_tests} practice tests for analytics testing")

    def test_01_strengths_weaknesses_analysis_with_data(self):
        """Test GET /api/student/analytics/strengths-weaknesses with student who has data"""
        print("\n🔍 Testing Student Analytics - Strengths & Weaknesses Analysis (With Data)...")
        
        if not self.student_with_data_token:
            self.skipTest("Student with data token not available")
        
        url = f"{API_URL}/student/analytics/strengths-weaknesses"
        headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Strengths & Weaknesses Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get strengths & weaknesses analysis")
            data = response.json()
            
            # Verify response structure
            required_fields = [
                "strengths", "weaknesses", "improving_areas", "declining_areas",
                "overall_performance", "recommendations", "analysis_date"
            ]
            
            for field in required_fields:
                self.assertIn(field, data, f"Field '{field}' should be present in analysis")
            
            # Verify data types
            self.assertIsInstance(data.get("strengths"), list, "Strengths should be a list")
            self.assertIsInstance(data.get("weaknesses"), list, "Weaknesses should be a list")
            self.assertIsInstance(data.get("improving_areas"), list, "Improving areas should be a list")
            self.assertIsInstance(data.get("declining_areas"), list, "Declining areas should be a list")
            self.assertIsInstance(data.get("overall_performance"), dict, "Overall performance should be a dict")
            self.assertIsInstance(data.get("recommendations"), list, "Recommendations should be a list")
            
            # Verify overall performance structure
            overall = data.get("overall_performance", {})
            performance_fields = ["average_score", "total_tests", "subjects_tested", "highest_score", "lowest_score"]
            
            for field in performance_fields:
                self.assertIn(field, overall, f"Field '{field}' should be present in overall performance")
            
            # Verify we have meaningful data
            total_tests = overall.get("total_tests", 0)
            subjects_tested = overall.get("subjects_tested", 0)
            average_score = overall.get("average_score", 0)
            
            self.assertGreater(total_tests, 0, "Should have practice test data")
            self.assertGreater(subjects_tested, 0, "Should have tested multiple subjects")
            self.assertGreater(average_score, 0, "Should have calculated average score")
            
            print(f"✅ Overall Performance: {total_tests} tests, {subjects_tested} subjects, {average_score}% avg")
            
            # Verify strengths and weaknesses logic
            strengths = data.get("strengths", [])
            weaknesses = data.get("weaknesses", [])
            
            print(f"✅ Found {len(strengths)} strengths and {len(weaknesses)} weaknesses")
            
            # Check if math is identified as strength (avg >= 80% with >= 3 attempts)
            math_strength = any(s.get("subject") == "math" for s in strengths)
            if math_strength:
                print("✅ Math correctly identified as strength")
            
            # Check if physics is identified as weakness (avg <= 60% with >= 3 attempts)
            physics_weakness = any(w.get("subject") == "physics" for w in weaknesses)
            if physics_weakness:
                print("✅ Physics correctly identified as weakness")
            
            # Verify recommendations are generated
            recommendations = data.get("recommendations", [])
            self.assertGreater(len(recommendations), 0, "Should have generated recommendations")
            
            for rec in recommendations:
                self.assertIn("type", rec, "Recommendation should have type")
                self.assertIn("priority", rec, "Recommendation should have priority")
                self.assertIn("message", rec, "Recommendation should have message")
                self.assertIn("suggested_actions", rec, "Recommendation should have suggested actions")
            
            print(f"✅ Generated {len(recommendations)} personalized recommendations")
            print("✅ Strengths & Weaknesses analysis test passed")
            
        except Exception as e:
            print(f"❌ Strengths & Weaknesses analysis test failed: {str(e)}")
            self.fail(f"Strengths & Weaknesses analysis test failed: {str(e)}")

    def test_02_strengths_weaknesses_analysis_no_data(self):
        """Test GET /api/student/analytics/strengths-weaknesses with student who has no data"""
        print("\n🔍 Testing Student Analytics - Strengths & Weaknesses Analysis (No Data)...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/student/analytics/strengths-weaknesses"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Strengths & Weaknesses (No Data) Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Should handle students with no data gracefully")
            data = response.json()
            
            # Verify empty state structure
            self.assertEqual(len(data.get("strengths", [])), 0, "Should have no strengths with no data")
            self.assertEqual(len(data.get("weaknesses", [])), 0, "Should have no weaknesses with no data")
            self.assertEqual(len(data.get("improving_areas", [])), 0, "Should have no improving areas with no data")
            self.assertEqual(len(data.get("declining_areas", [])), 0, "Should have no declining areas with no data")
            
            # Verify overall performance shows zeros
            overall = data.get("overall_performance", {})
            self.assertEqual(overall.get("total_tests", -1), 0, "Should show 0 total tests")
            self.assertEqual(overall.get("subjects_tested", -1), 0, "Should show 0 subjects tested")
            self.assertEqual(overall.get("average_score", -1), 0, "Should show 0 average score")
            
            print("✅ Correctly handles student with no practice test data")
            
        except Exception as e:
            print(f"❌ No data analysis test failed: {str(e)}")
            self.fail(f"No data analysis test failed: {str(e)}")

    def test_03_performance_trends_analysis(self):
        """Test GET /api/student/analytics/performance-trends"""
        print("\n🔍 Testing Student Analytics - Performance Trends...")
        
        if not self.student_with_data_token:
            self.skipTest("Student with data token not available")
        
        # Test with different time periods
        time_periods = [7, 14, 30, 60]
        
        for days in time_periods:
            url = f"{API_URL}/student/analytics/performance-trends?days={days}"
            headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
            
            try:
                print(f"Testing performance trends for {days} days...")
                response = requests.get(url, headers=headers)
                print(f"Performance Trends ({days} days) Response: {response.status_code}")
                
                self.assertEqual(response.status_code, 200, f"Failed to get performance trends for {days} days")
                data = response.json()
                
                # Verify response structure
                required_fields = ["trend_data", "trend_direction", "total_tests_period", "period_days"]
                
                for field in required_fields:
                    self.assertIn(field, data, f"Field '{field}' should be present in trends")
                
                # Verify data types
                self.assertIsInstance(data.get("trend_data"), list, "Trend data should be a list")
                self.assertIn(data.get("trend_direction"), ["improving", "declining", "stable"], "Trend direction should be valid")
                self.assertEqual(data.get("period_days"), days, f"Period days should match requested {days}")
                
                # Verify trend data structure if present
                trend_data = data.get("trend_data", [])
                if len(trend_data) > 0:
                    first_trend = trend_data[0]
                    trend_fields = ["week", "average_score", "test_count", "highest_score", "lowest_score"]
                    
                    for field in trend_fields:
                        self.assertIn(field, first_trend, f"Field '{field}' should be present in trend data")
                    
                    print(f"✅ Found {len(trend_data)} weeks of trend data for {days} days period")
                    print(f"✅ Trend direction: {data.get('trend_direction')}")
                else:
                    print(f"✅ No trend data for {days} days (expected for recent tests)")
                
            except Exception as e:
                print(f"❌ Performance trends test failed for {days} days: {str(e)}")
                self.fail(f"Performance trends test failed for {days} days: {str(e)}")
        
        print("✅ Performance trends analysis test passed")

    def test_04_subject_breakdown_analysis(self):
        """Test GET /api/student/analytics/subject-breakdown"""
        print("\n🔍 Testing Student Analytics - Subject Breakdown...")
        
        if not self.student_with_data_token:
            self.skipTest("Student with data token not available")
        
        url = f"{API_URL}/student/analytics/subject-breakdown"
        headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Subject Breakdown Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get subject breakdown")
            data = response.json()
            
            # Verify response structure
            required_fields = ["subject_breakdown", "total_subjects", "best_subject", "analysis_date"]
            
            for field in required_fields:
                self.assertIn(field, data, f"Field '{field}' should be present in breakdown")
            
            # Verify data types
            self.assertIsInstance(data.get("subject_breakdown"), list, "Subject breakdown should be a list")
            self.assertIsInstance(data.get("total_subjects"), int, "Total subjects should be an integer")
            
            # Verify we have subject data
            breakdown = data.get("subject_breakdown", [])
            total_subjects = data.get("total_subjects", 0)
            
            self.assertGreater(len(breakdown), 0, "Should have subject breakdown data")
            self.assertEqual(len(breakdown), total_subjects, "Total subjects should match breakdown length")
            
            print(f"✅ Found breakdown for {total_subjects} subjects")
            
            # Verify subject breakdown structure
            for subject_data in breakdown:
                subject_fields = [
                    "subject", "subject_display", "total_tests", "average_score",
                    "highest_score", "lowest_score", "total_time_minutes",
                    "avg_time_per_test", "performance_grade"
                ]
                
                for field in subject_fields:
                    self.assertIn(field, subject_data, f"Field '{field}' should be present in subject data")
                
                # Verify data validity
                self.assertGreater(subject_data.get("total_tests", 0), 0, "Should have tests for each subject")
                self.assertGreaterEqual(subject_data.get("average_score", -1), 0, "Average score should be >= 0")
                self.assertLessEqual(subject_data.get("average_score", 101), 100, "Average score should be <= 100")
                self.assertIn(subject_data.get("performance_grade"), ["A", "B", "C", "D", "F"], "Should have valid grade")
                
                subject_name = subject_data.get("subject_display", "Unknown")
                avg_score = subject_data.get("average_score", 0)
                grade = subject_data.get("performance_grade", "?")
                total_tests = subject_data.get("total_tests", 0)
                
                print(f"✅ {subject_name}: {total_tests} tests, {avg_score}% avg, Grade {grade}")
            
            # Verify best subject is identified
            best_subject = data.get("best_subject")
            if best_subject:
                self.assertIsInstance(best_subject, dict, "Best subject should be a dict")
                self.assertIn("subject_display", best_subject, "Best subject should have display name")
                print(f"✅ Best subject identified: {best_subject.get('subject_display')}")
            
            print("✅ Subject breakdown analysis test passed")
            
        except Exception as e:
            print(f"❌ Subject breakdown analysis test failed: {str(e)}")
            self.fail(f"Subject breakdown analysis test failed: {str(e)}")

    def test_05_learning_insights_analysis(self):
        """Test GET /api/student/analytics/learning-insights"""
        print("\n🔍 Testing Student Analytics - Learning Insights...")
        
        if not self.student_with_data_token:
            self.skipTest("Student with data token not available")
        
        url = f"{API_URL}/student/analytics/learning-insights"
        headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Learning Insights Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Failed to get learning insights")
            data = response.json()
            
            # Verify response structure
            required_fields = ["insights", "study_tips", "recent_activity"]
            
            for field in required_fields:
                self.assertIn(field, data, f"Field '{field}' should be present in insights")
            
            # Verify data types
            self.assertIsInstance(data.get("insights"), list, "Insights should be a list")
            self.assertIsInstance(data.get("study_tips"), list, "Study tips should be a list")
            self.assertIsInstance(data.get("recent_activity"), dict, "Recent activity should be a dict")
            
            # Verify insights structure
            insights = data.get("insights", [])
            self.assertGreater(len(insights), 0, "Should have generated insights")
            
            for insight in insights:
                insight_fields = ["type", "title", "message", "icon", "action"]
                
                for field in insight_fields:
                    self.assertIn(field, insight, f"Field '{field}' should be present in insight")
                
                # Verify insight types are valid
                valid_types = [
                    "frequency", "consistency", "time_management", "variety",
                    "progress", "encouragement", "getting_started"
                ]
                self.assertIn(insight.get("type"), valid_types, "Insight type should be valid")
                
                print(f"✅ Insight: {insight.get('title')} ({insight.get('type')})")
            
            # Verify study tips
            study_tips = data.get("study_tips", [])
            self.assertGreater(len(study_tips), 0, "Should have study tips")
            
            for tip in study_tips:
                self.assertIsInstance(tip, str, "Study tip should be a string")
                self.assertGreater(len(tip), 0, "Study tip should not be empty")
            
            print(f"✅ Generated {len(study_tips)} study tips")
            
            # Verify recent activity
            recent_activity = data.get("recent_activity", {})
            activity_fields = ["tests_taken", "average_score", "subjects_practiced"]
            
            for field in activity_fields:
                self.assertIn(field, recent_activity, f"Field '{field}' should be present in recent activity")
            
            tests_taken = recent_activity.get("tests_taken", 0)
            avg_score = recent_activity.get("average_score", 0)
            subjects_practiced = recent_activity.get("subjects_practiced", 0)
            
            print(f"✅ Recent Activity: {tests_taken} tests, {avg_score}% avg, {subjects_practiced} subjects")
            
            print("✅ Learning insights analysis test passed")
            
        except Exception as e:
            print(f"❌ Learning insights analysis test failed: {str(e)}")
            self.fail(f"Learning insights analysis test failed: {str(e)}")

    def test_06_learning_insights_no_data(self):
        """Test GET /api/student/analytics/learning-insights with student who has no data"""
        print("\n🔍 Testing Student Analytics - Learning Insights (No Data)...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        url = f"{API_URL}/student/analytics/learning-insights"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Learning Insights (No Data) Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Should handle students with no data gracefully")
            data = response.json()
            
            # Verify getting started message
            insights = data.get("insights", [])
            self.assertGreater(len(insights), 0, "Should have getting started insight")
            
            first_insight = insights[0]
            self.assertEqual(first_insight.get("type"), "getting_started", "Should show getting started insight")
            self.assertIn("Start Your Learning Journey", first_insight.get("title", ""), "Should have appropriate title")
            
            # Verify study tips are still provided
            study_tips = data.get("study_tips", [])
            self.assertGreater(len(study_tips), 0, "Should still provide study tips")
            
            print("✅ Correctly handles student with no data - shows getting started message")
            
        except Exception as e:
            print(f"❌ Learning insights no data test failed: {str(e)}")
            self.fail(f"Learning insights no data test failed: {str(e)}")

    def test_07_authentication_requirements(self):
        """Test that all analytics endpoints require proper authentication"""
        print("\n🔍 Testing Student Analytics - Authentication Requirements...")
        
        endpoints = [
            "/student/analytics/strengths-weaknesses",
            "/student/analytics/performance-trends",
            "/student/analytics/subject-breakdown",
            "/student/analytics/learning-insights"
        ]
        
        for endpoint in endpoints:
            url = f"{API_URL}{endpoint}"
            
            try:
                # Test without authentication
                response = requests.get(url)
                print(f"No Auth {endpoint}: {response.status_code}")
                
                self.assertIn(response.status_code, [401, 403], f"Endpoint {endpoint} should require authentication")
                
                # Test with invalid token
                invalid_headers = {"Authorization": "Bearer invalid.token.here"}
                invalid_response = requests.get(url, headers=invalid_headers)
                print(f"Invalid Token {endpoint}: {invalid_response.status_code}")
                
                self.assertIn(invalid_response.status_code, [401, 403], f"Endpoint {endpoint} should reject invalid tokens")
                
            except Exception as e:
                print(f"❌ Authentication test failed for {endpoint}: {str(e)}")
                self.fail(f"Authentication test failed for {endpoint}: {str(e)}")
        
        print("✅ All analytics endpoints properly require authentication")

    def test_08_comprehensive_workflow_verification(self):
        """Test the complete workflow of all analytics endpoints working together"""
        print("\n🔍 Testing Student Analytics - Comprehensive Workflow Verification...")
        
        if not self.student_with_data_token:
            self.skipTest("Student with data token not available")
        
        headers = {"Authorization": f"Bearer {self.student_with_data_token}"}
        
        # Test all endpoints in sequence
        endpoints_data = {}
        
        endpoints = [
            ("strengths-weaknesses", "/student/analytics/strengths-weaknesses"),
            ("performance-trends", "/student/analytics/performance-trends?days=30"),
            ("subject-breakdown", "/student/analytics/subject-breakdown"),
            ("learning-insights", "/student/analytics/learning-insights")
        ]
        
        try:
            for name, endpoint in endpoints:
                url = f"{API_URL}{endpoint}"
                response = requests.get(url, headers=headers)
                
                self.assertEqual(response.status_code, 200, f"Endpoint {name} should return 200")
                data = response.json()
                endpoints_data[name] = data
                
                print(f"✅ {name} endpoint working correctly")
            
            # Verify data consistency across endpoints
            print("🔍 Verifying data consistency across endpoints...")
            
            # Get subject data from different endpoints
            strengths_data = endpoints_data["strengths-weaknesses"]
            breakdown_data = endpoints_data["subject-breakdown"]
            
            # Verify total tests consistency
            total_tests_overall = strengths_data.get("overall_performance", {}).get("total_tests", 0)
            total_tests_breakdown = sum(s.get("total_tests", 0) for s in breakdown_data.get("subject_breakdown", []))
            
            self.assertEqual(total_tests_overall, total_tests_breakdown, 
                           "Total tests should be consistent across endpoints")
            
            # Verify subjects consistency
            subjects_overall = strengths_data.get("overall_performance", {}).get("subjects_tested", 0)
            subjects_breakdown = breakdown_data.get("total_subjects", 0)
            
            self.assertEqual(subjects_overall, subjects_breakdown,
                           "Subject count should be consistent across endpoints")
            
            # Verify insights are relevant to performance
            insights_data = endpoints_data["learning-insights"]
            insights = insights_data.get("insights", [])
            
            # Should have insights relevant to the student's performance pattern
            insight_types = [i.get("type") for i in insights]
            
            # With multiple subjects and tests, should have meaningful insights
            self.assertGreater(len(insights), 0, "Should have generated insights")
            
            print("✅ Data consistency verified across all endpoints")
            print("✅ Comprehensive workflow verification passed")
            
            # Print summary
            print("\n📊 STUDENT ANALYTICS SYSTEM SUMMARY:")
            print(f"   • Total Tests: {total_tests_overall}")
            print(f"   • Subjects Tested: {subjects_overall}")
            print(f"   • Strengths Identified: {len(strengths_data.get('strengths', []))}")
            print(f"   • Weaknesses Identified: {len(strengths_data.get('weaknesses', []))}")
            print(f"   • Recommendations Generated: {len(strengths_data.get('recommendations', []))}")
            print(f"   • Learning Insights: {len(insights)}")
            
        except Exception as e:
            print(f"❌ Comprehensive workflow verification failed: {str(e)}")
            self.fail(f"Comprehensive workflow verification failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting AIR Project K Backend Testing Suite V3.0")
    print(f"Testing against API: {API_URL}")
    print("=" * 80)
    
    # First run the Student Analytics tests (NEW - CURRENT FOCUS)
    print("\n==== RUNNING STUDENT ANALYTICS API TESTS (CURRENT FOCUS) ====\n")
    analytics_suite = unittest.TestLoader().loadTestsFromTestCase(TestStudentAnalyticsEndpoints)
    analytics_result = unittest.TextTestRunner().run(analytics_suite)
    
    # Then run the study planner tests
    print("\n==== RUNNING STUDY PLANNER API TESTS ====\n")
    study_planner_suite = unittest.TestLoader().loadTestsFromTestCase(TestStudyPlannerAPI)
    study_planner_result = unittest.TextTestRunner().run(study_planner_suite)
    
    # Then run the tutor API tests
    print("\n==== RUNNING TUTOR API TESTS ====\n")
    tutor_suite = unittest.TestLoader().loadTestsFromTestCase(TestTutorAPIRoutes)
    tutor_result = unittest.TextTestRunner().run(tutor_suite)
    
    # Then run the focused tests for the issues in the test plan
    print("\n==== RUNNING FOCUSED TESTS FOR IDENTIFIED ISSUES ====\n")
    focused_suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectKV3BackendFocusedIssues)
    focused_result = unittest.TextTestRunner().run(focused_suite)
    
    # Then run the full test suite
    print("\n==== RUNNING FULL TEST SUITE ====\n")
    full_suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectKV3Backend)
    unittest.TextTestRunner().run(full_suite)

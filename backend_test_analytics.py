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

class TestTeacherAnalyticsEndpoints(unittest.TestCase):
    """Test cases for Teacher Analytics API endpoints"""

    def setUp(self):
        """Set up test case - create student and teacher accounts, class, and test data"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        self.test_id = None
        
        # Register student and teacher
        self.register_teacher()
        self.register_student()
        
        # Create class and join it
        if self.teacher_token and self.student_token:
            self.create_class()
            self.join_class()
            
            # Generate and submit practice test
            if self.student_token and self.class_id:
                self.generate_and_submit_practice_test()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"student_analytics_{uuid.uuid4()}@example.com",
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
            "email": f"teacher_analytics_{uuid.uuid4()}@example.com",
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

    def create_class(self):
        """Create a class for testing"""
        print("\n🔍 Creating class...")
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        payload = {
            "subject": Subject.PHYSICS.value,
            "class_name": "Physics 101",
            "grade_level": GradeLevel.GRADE_10.value,
            "description": "Introductory physics class covering mechanics and thermodynamics"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.class_id = data.get("class_id")
                self.join_code = data.get("join_code")
                print(f"Created class with ID: {self.class_id} and join code: {self.join_code}")
            else:
                print(f"Failed to create class: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error creating class: {str(e)}")

    def join_class(self):
        """Student joins the class"""
        print("\n🔍 Student joining class...")
        url = f"{API_URL}/student/join-class"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "join_code": self.join_code
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"Student joined class successfully")
            else:
                print(f"Failed to join class: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error joining class: {str(e)}")

    def generate_and_submit_practice_test(self):
        """Generate and submit a practice test"""
        print("\n🔍 Generating and submitting practice test...")
        
        # Generate test
        gen_url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        gen_payload = {
            "subject": Subject.PHYSICS.value,
            "topics": ["Mechanics"],
            "difficulty": DifficultyLevel.MEDIUM.value,
            "question_count": 5
        }
        
        try:
            gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                self.test_id = gen_data.get("test_id")
                questions = gen_data.get("questions", [])
                
                if questions:
                    # Create student answers (use correct answers for testing)
                    student_answers = {}
                    question_ids = []
                    for question in questions:
                        question_id = question.get("id")
                        question_ids.append(question_id)
                        student_answers[question_id] = question.get("correct_answer")
                    
                    # Submit the test
                    submit_url = f"{API_URL}/practice/submit"
                    submit_payload = {
                        "test_id": self.test_id,
                        "questions": question_ids,
                        "student_answers": student_answers,
                        "time_taken": 300  # 5 minutes
                    }
                    
                    submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                    if submit_response.status_code == 200:
                        print(f"Practice test submitted successfully")
                    else:
                        print(f"Failed to submit practice test: {submit_response.status_code} - {submit_response.text}")
                else:
                    print("No questions generated for practice test")
            else:
                print(f"Failed to generate practice test: {gen_response.status_code} - {gen_response.text}")
        except Exception as e:
            print(f"Error with practice test: {str(e)}")

    def test_01_analytics_overview(self):
        """Test teacher analytics overview endpoint"""
        print("\n🔍 Testing Teacher Analytics Overview...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/analytics/overview"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Analytics Overview Response: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
            
            self.assertEqual(response.status_code, 200, "Failed to get teacher analytics overview")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("overview_metrics", data, "Overview metrics not found in response")
            self.assertIn("class_summary", data, "Class summary not found in response")
            self.assertIn("subject_distribution", data, "Subject distribution not found in response")
            
            # Verify overview metrics
            metrics = data.get("overview_metrics", {})
            self.assertIn("total_classes", metrics, "Total classes not found in metrics")
            self.assertIn("total_students", metrics, "Total students not found in metrics")
            
            # Verify class summary
            class_summary = data.get("class_summary", [])
            self.assertIsInstance(class_summary, list, "Class summary should be a list")
            
            print("✅ Teacher analytics overview test passed")
        except Exception as e:
            print(f"❌ Teacher analytics overview test failed: {str(e)}")
            raise

    def test_02_test_results_analytics(self):
        """Test detailed test results analytics endpoint"""
        print("\n🔍 Testing Detailed Test Results Analytics...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        # Test with class_id filter
        url = f"{API_URL}/teacher/analytics/test-results?class_id={self.class_id}"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Test Results Analytics (class filter) Response: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
            
            self.assertEqual(response.status_code, 200, "Failed to get test results analytics with class filter")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("test_results", data, "Test results not found in response")
            self.assertIn("total_results", data, "Total results not found in response")
            self.assertIn("filters_applied", data, "Filters applied not found in response")
            
            # Verify filters
            filters = data.get("filters_applied", {})
            self.assertEqual(filters.get("class_id"), self.class_id, "Class ID filter mismatch")
            
            # Test with student_id filter
            if self.student_id:
                student_url = f"{API_URL}/teacher/analytics/test-results?student_id={self.student_id}"
                student_response = requests.get(student_url, headers=headers)
                print(f"Test Results Analytics (student filter) Response: {student_response.status_code}")
                
                self.assertEqual(student_response.status_code, 200, "Failed to get test results analytics with student filter")
                student_data = student_response.json()
                
                # Verify filters
                student_filters = student_data.get("filters_applied", {})
                self.assertEqual(student_filters.get("student_id"), self.student_id, "Student ID filter mismatch")
            
            print("✅ Detailed test results analytics test passed")
        except Exception as e:
            print(f"❌ Detailed test results analytics test failed: {str(e)}")
            raise

    def test_03_class_performance_analytics(self):
        """Test class performance analytics endpoint"""
        print("\n🔍 Testing Class Performance Analytics...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        url = f"{API_URL}/teacher/analytics/class-performance/{self.class_id}"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Class Performance Analytics Response: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars of response
            
            self.assertEqual(response.status_code, 200, "Failed to get class performance analytics")
            data = response.json()
            
            # Verify the structure of the response
            self.assertIn("class_info", data, "Class info not found in response")
            self.assertIn("student_count", data, "Student count not found in response")
            self.assertIn("performance_summary", data, "Performance summary not found in response")
            
            # Verify class info
            class_info = data.get("class_info", {})
            self.assertEqual(class_info.get("class_id"), self.class_id, "Class ID mismatch")
            
            print("✅ Class performance analytics test passed")
        except Exception as e:
            print(f"❌ Class performance analytics test failed: {str(e)}")
            raise

    def test_04_student_access_denied(self):
        """Test that students are denied access to teacher analytics endpoints"""
        print("\n🔍 Testing Student Access Denied to Teacher Analytics...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        # Test overview endpoint
        overview_url = f"{API_URL}/teacher/analytics/overview"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            overview_response = requests.get(overview_url, headers=headers)
            print(f"Student Access to Overview Response: {overview_response.status_code}")
            
            self.assertEqual(overview_response.status_code, 403, "Student should be denied access to teacher analytics overview")
            
            # Test test results endpoint
            test_results_url = f"{API_URL}/teacher/analytics/test-results"
            test_results_response = requests.get(test_results_url, headers=headers)
            print(f"Student Access to Test Results Response: {test_results_response.status_code}")
            
            self.assertEqual(test_results_response.status_code, 403, "Student should be denied access to teacher test results analytics")
            
            # Test class performance endpoint
            if self.class_id:
                class_perf_url = f"{API_URL}/teacher/analytics/class-performance/{self.class_id}"
                class_perf_response = requests.get(class_perf_url, headers=headers)
                print(f"Student Access to Class Performance Response: {class_perf_response.status_code}")
                
                self.assertEqual(class_perf_response.status_code, 403, "Student should be denied access to teacher class performance analytics")
            
            print("✅ Student access denied test passed")
        except Exception as e:
            print(f"❌ Student access denied test failed: {str(e)}")
            raise

    def test_05_teacher_access_other_class(self):
        """Test that teachers are denied access to other teachers' classes"""
        print("\n🔍 Testing Teacher Access Denied to Other Teachers' Classes...")
        
        if not self.teacher_token or not self.class_id:
            self.skipTest("Teacher token or class ID not available")
        
        # Create another teacher
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"teacher2_analytics_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Rajesh Verma",
            "user_type": UserType.TEACHER.value,
            "school_name": "Delhi Public School"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                other_teacher_token = data.get("access_token")
                
                # Try to access our class with the other teacher
                class_perf_url = f"{API_URL}/teacher/analytics/class-performance/{self.class_id}"
                headers = {"Authorization": f"Bearer {other_teacher_token}"}
                
                class_perf_response = requests.get(class_perf_url, headers=headers)
                print(f"Other Teacher Access to Class Performance Response: {class_perf_response.status_code}")
                
                self.assertEqual(class_perf_response.status_code, 403, "Other teacher should be denied access to this teacher's class")
                
                # Try to access test results with class_id filter
                test_results_url = f"{API_URL}/teacher/analytics/test-results?class_id={self.class_id}"
                test_results_response = requests.get(test_results_url, headers=headers)
                print(f"Other Teacher Access to Test Results Response: {test_results_response.status_code}")
                
                self.assertEqual(test_results_response.status_code, 403, "Other teacher should be denied access to this teacher's test results")
                
                print("✅ Teacher access to other classes denied test passed")
            else:
                print(f"Failed to register other teacher: {response.status_code} - {response.text}")
                self.skipTest("Failed to register other teacher")
        except Exception as e:
            print(f"❌ Teacher access to other classes denied test failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Run the tests
    print("\n==== TESTING TEACHER ANALYTICS API ENDPOINTS ====\n")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
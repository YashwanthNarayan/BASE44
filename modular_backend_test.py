#!/usr/bin/env python3
"""
Comprehensive test for the modular backend structure of AIR-PROJECT-K
Tests core functionality to verify the restructuring was successful
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
API_URL = f"{BACKEND_URL}/api"

print(f"Testing modular backend at: {API_URL}")

class ModularBackendTester:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        self.test_results = []

    def log_result(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{API_URL}/health")
            success = response.status_code == 200
            data = response.json() if success else {}
            message = f"Status: {response.status_code}, Service: {data.get('service', 'N/A')}"
            self.log_result("Health Check Endpoint", success, message)
            return success
        except Exception as e:
            self.log_result("Health Check Endpoint", False, f"Error: {str(e)}")
            return False

    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/")
            success = response.status_code == 200
            data = response.json() if success else {}
            message = f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
            self.log_result("Root Endpoint", success, message)
            return success
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_student_registration(self):
        """Test student registration (auth route)"""
        try:
            payload = {
                "email": f"student_{uuid.uuid4()}@example.com",
                "password": "SecurePass123!",
                "name": "Arjun Kumar",
                "user_type": "student",
                "grade_level": "10th"
            }
            
            response = requests.post(f"{API_URL}/auth/register", json=payload)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                message = f"Registered student ID: {self.student_id}"
            else:
                message = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_result("Student Registration (Auth Route)", success, message)
            return success
        except Exception as e:
            self.log_result("Student Registration (Auth Route)", False, f"Error: {str(e)}")
            return False

    def test_teacher_registration(self):
        """Test teacher registration (auth route)"""
        try:
            payload = {
                "email": f"teacher_{uuid.uuid4()}@example.com",
                "password": "SecurePass123!",
                "name": "Priya Sharma",
                "user_type": "teacher",
                "school_name": "Modern Public School"
            }
            
            response = requests.post(f"{API_URL}/auth/register", json=payload)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                message = f"Registered teacher ID: {self.teacher_id}"
            else:
                message = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_result("Teacher Registration (Auth Route)", success, message)
            return success
        except Exception as e:
            self.log_result("Teacher Registration (Auth Route)", False, f"Error: {str(e)}")
            return False

    def test_student_profile(self):
        """Test student profile access (student route)"""
        if not self.student_token:
            self.log_result("Student Profile Access (Student Route)", False, "No student token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{API_URL}/student/profile", headers=headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                message = f"Profile loaded for: {data.get('name', 'N/A')}"
            else:
                message = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_result("Student Profile Access (Student Route)", success, message)
            return success
        except Exception as e:
            self.log_result("Student Profile Access (Student Route)", False, f"Error: {str(e)}")
            return False

    def test_practice_test_generation(self):
        """Test practice test generation (practice route + AI service)"""
        if not self.student_token:
            self.log_result("Practice Test Generation (Practice Route + AI Service)", False, "No student token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 2
            }
            
            response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                questions = data.get("questions", [])
                message = f"Generated {len(questions)} questions for {data.get('subject', 'N/A')}"
            else:
                message = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_result("Practice Test Generation (Practice Route + AI Service)", success, message)
            return success
        except Exception as e:
            self.log_result("Practice Test Generation (Practice Route + AI Service)", False, f"Error: {str(e)}")
            return False

    def test_jwt_authentication(self):
        """Test JWT token validation"""
        try:
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid.token.here"}
            response = requests.get(f"{API_URL}/student/profile", headers=headers)
            
            # Should return 401 for invalid token
            success = response.status_code == 401
            message = f"Invalid token correctly returned: {response.status_code}"
            
            self.log_result("JWT Authentication Validation", success, message)
            return success
        except Exception as e:
            self.log_result("JWT Authentication Validation", False, f"Error: {str(e)}")
            return False

    def test_database_integration(self):
        """Test database integration by checking if data persists"""
        if not self.student_token:
            self.log_result("Database Integration Test", False, "No student token available")
            return False
        
        try:
            # Get profile twice to ensure data persists
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response1 = requests.get(f"{API_URL}/student/profile", headers=headers)
            response2 = requests.get(f"{API_URL}/student/profile", headers=headers)
            
            success = (response1.status_code == 200 and response2.status_code == 200)
            
            if success:
                data1 = response1.json()
                data2 = response2.json()
                # Check if the same user ID is returned both times
                same_user = data1.get("user_id") == data2.get("user_id")
                message = f"Data persistence verified: {same_user}"
                success = same_user
            else:
                message = f"Profile requests failed: {response1.status_code}, {response2.status_code}"
            
            self.log_result("Database Integration Test", success, message)
            return success
        except Exception as e:
            self.log_result("Database Integration Test", False, f"Error: {str(e)}")
            return False

    def test_modular_structure(self):
        """Test that modular structure is working by testing different route modules"""
        auth_working = self.student_token is not None and self.teacher_token is not None
        student_route_working = self.test_student_profile()
        practice_route_working = self.test_practice_test_generation()
        
        success = auth_working and student_route_working and practice_route_working
        message = f"Auth: {auth_working}, Student: {student_route_working}, Practice: {practice_route_working}"
        
        self.log_result("Modular Structure Integration", success, message)
        return success

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("TESTING MODULAR BACKEND STRUCTURE")
        print("="*60)
        
        # Core API tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Authentication module tests
        self.test_student_registration()
        self.test_teacher_registration()
        
        # Student module tests
        self.test_student_profile()
        
        # Practice module tests
        self.test_practice_test_generation()
        
        # Security tests
        self.test_jwt_authentication()
        
        # Database integration tests
        self.test_database_integration()
        
        # Overall modular structure test
        self.test_modular_structure()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Modular backend is working correctly!")
        else:
            print(f"\n⚠️  {total-passed} tests failed - Issues found in modular backend")
            
        return passed == total

if __name__ == "__main__":
    tester = ModularBackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
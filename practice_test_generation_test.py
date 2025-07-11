#!/usr/bin/env python3
"""
Comprehensive Practice Test Generation Testing
Focus on testing the practice test generation functionality specifically.
"""
import requests
import json
import time
import os
import uuid
from dotenv import load_dotenv
import sys

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Add /api prefix to the backend URL
API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class PracticeTestGenerationTester:
    def __init__(self):
        self.api_url = API_URL
        self.student_token = None
        self.student_data = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self):
        """Test API health check"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", True, f"Service: {data.get('service', 'Unknown')}")
                return True
            else:
                self.log_result("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Error: {str(e)}")
            return False
    
    def create_student_account(self):
        """Create a student account for testing"""
        try:
            # Generate unique email
            unique_id = str(uuid.uuid4())[:8]
            student_email = f"student_{unique_id}@test.com"
            
            student_data = {
                "email": student_email,
                "password": "TestPassword123!",
                "name": f"Test Student {unique_id}",
                "user_type": "student",
                "grade_level": "10th",
                "school_name": "Test High School"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=student_data, timeout=15)
            
            if response.status_code == 201:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_data = student_data
                self.log_result("Student Registration", True, f"Email: {student_email}")
                return True
            else:
                self.log_result("Student Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Registration", False, f"Error: {str(e)}")
            return False
    
    def login_student(self):
        """Login with student account"""
        try:
            if not self.student_data:
                self.log_result("Student Login", False, "No student data available")
                return False
                
            login_data = {
                "email": self.student_data["email"],
                "password": self.student_data["password"]
            }
            
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.log_result("Student Login", True, f"Token received: {bool(self.student_token)}")
                return True
            else:
                self.log_result("Student Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Login", False, f"Error: {str(e)}")
            return False
    
    def test_practice_generation_basic(self):
        """Test basic practice test generation"""
        try:
            if not self.student_token:
                self.log_result("Practice Generation Basic", False, "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test data as specified in the review request
            test_request = {
                "subject": "math",
                "topics": ["Algebra", "Geometry"],
                "difficulty": "medium",
                "question_count": 5,
                "question_types": ["mcq", "short_answer"]
            }
            
            print(f"🔄 Generating practice test with: {test_request}")
            
            response = requests.post(
                f"{self.api_url}/practice/generate", 
                json=test_request, 
                headers=headers,
                timeout=30  # Increased timeout for AI generation
            )
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                # Validate response structure
                if len(questions) == 5:
                    self.log_result("Practice Generation Basic", True, f"Generated {len(questions)} questions")
                    
                    # Validate question structure
                    self.validate_question_structure(questions)
                    return True
                else:
                    self.log_result("Practice Generation Basic", False, f"Expected 5 questions, got {len(questions)}")
                    return False
            else:
                self.log_result("Practice Generation Basic", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Practice Generation Basic", False, f"Error: {str(e)}")
            return False
    
    def validate_question_structure(self, questions):
        """Validate the structure of generated questions"""
        try:
            required_fields = ["id", "question_text", "question_type", "correct_answer", "subject", "difficulty"]
            
            for i, question in enumerate(questions):
                missing_fields = [field for field in required_fields if field not in question]
                
                if missing_fields:
                    self.log_result(f"Question {i+1} Structure", False, f"Missing fields: {missing_fields}")
                else:
                    # Check question types
                    if question["question_type"] in ["mcq", "short_answer"]:
                        self.log_result(f"Question {i+1} Structure", True, f"Type: {question['question_type']}")
                    else:
                        self.log_result(f"Question {i+1} Structure", False, f"Invalid type: {question['question_type']}")
                        
        except Exception as e:
            self.log_result("Question Structure Validation", False, f"Error: {str(e)}")
    
    def test_ai_service_integration(self):
        """Test AI service integration specifically"""
        try:
            if not self.student_token:
                self.log_result("AI Service Integration", False, "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test with different parameters to check AI flexibility
            test_cases = [
                {
                    "name": "Math Algebra",
                    "request": {
                        "subject": "math",
                        "topics": ["Algebra"],
                        "difficulty": "easy",
                        "question_count": 3,
                        "question_types": ["mcq"]
                    }
                },
                {
                    "name": "Physics Mechanics",
                    "request": {
                        "subject": "physics",
                        "topics": ["Mechanics"],
                        "difficulty": "medium",
                        "question_count": 2,
                        "question_types": ["short_answer"]
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"🔄 Testing AI service with: {test_case['name']}")
                
                response = requests.post(
                    f"{self.api_url}/practice/generate", 
                    json=test_case["request"], 
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    if len(questions) == test_case["request"]["question_count"]:
                        self.log_result(f"AI Service - {test_case['name']}", True, f"Generated {len(questions)} questions")
                    else:
                        self.log_result(f"AI Service - {test_case['name']}", False, f"Expected {test_case['request']['question_count']}, got {len(questions)}")
                else:
                    self.log_result(f"AI Service - {test_case['name']}", False, f"Status: {response.status_code}")
                    
                time.sleep(2)  # Brief pause between AI requests
                
        except Exception as e:
            self.log_result("AI Service Integration", False, f"Error: {str(e)}")
    
    def test_gemini_api_configuration(self):
        """Test if Gemini API is properly configured"""
        try:
            # Check if we can make a simple request that would use Gemini
            if not self.student_token:
                self.log_result("Gemini API Configuration", False, "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Simple request to test Gemini
            simple_request = {
                "subject": "math",
                "topics": ["Basic Math"],
                "difficulty": "easy",
                "question_count": 1,
                "question_types": ["mcq"]
            }
            
            print("🔄 Testing Gemini API configuration...")
            
            response = requests.post(
                f"{self.api_url}/practice/generate", 
                json=simple_request, 
                headers=headers,
                timeout=45  # Longer timeout for Gemini
            )
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                # Check if we got AI-generated content or fallback
                if questions and len(questions) > 0:
                    first_question = questions[0]
                    if "fallback" in first_question.get("id", "").lower():
                        self.log_result("Gemini API Configuration", False, "Using fallback questions - Gemini API may not be working")
                    else:
                        self.log_result("Gemini API Configuration", True, "AI-generated questions received")
                else:
                    self.log_result("Gemini API Configuration", False, "No questions generated")
            else:
                self.log_result("Gemini API Configuration", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Gemini API Configuration", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling for practice test generation"""
        try:
            if not self.student_token:
                self.log_result("Error Handling", False, "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test cases for error handling
            error_test_cases = [
                {
                    "name": "Missing Subject",
                    "request": {
                        "topics": ["Algebra"],
                        "difficulty": "medium",
                        "question_count": 5
                    },
                    "expected_status": [400, 422]  # Bad request or validation error
                },
                {
                    "name": "Invalid Subject",
                    "request": {
                        "subject": "invalid_subject",
                        "topics": ["Algebra"],
                        "difficulty": "medium",
                        "question_count": 5
                    },
                    "expected_status": [400, 422]
                },
                {
                    "name": "Empty Topics",
                    "request": {
                        "subject": "math",
                        "topics": [],
                        "difficulty": "medium",
                        "question_count": 5
                    },
                    "expected_status": [400, 422]
                },
                {
                    "name": "Invalid Question Count",
                    "request": {
                        "subject": "math",
                        "topics": ["Algebra"],
                        "difficulty": "medium",
                        "question_count": 0
                    },
                    "expected_status": [400, 422]
                }
            ]
            
            for test_case in error_test_cases:
                print(f"🔄 Testing error handling: {test_case['name']}")
                
                response = requests.post(
                    f"{self.api_url}/practice/generate", 
                    json=test_case["request"], 
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code in test_case["expected_status"]:
                    self.log_result(f"Error Handling - {test_case['name']}", True, f"Correctly returned {response.status_code}")
                else:
                    self.log_result(f"Error Handling - {test_case['name']}", False, f"Expected {test_case['expected_status']}, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Error: {str(e)}")
    
    def test_database_storage(self):
        """Test if questions are properly stored in database"""
        try:
            if not self.student_token:
                self.log_result("Database Storage", False, "No authentication token")
                return False
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Generate a practice test
            test_request = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 2,
                "question_types": ["mcq"]
            }
            
            print("🔄 Testing database storage...")
            
            response = requests.post(
                f"{self.api_url}/practice/generate", 
                json=test_request, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                if questions:
                    # Check if questions have proper metadata for database storage
                    first_question = questions[0]
                    required_db_fields = ["id", "subject", "difficulty", "question_text", "correct_answer"]
                    
                    has_all_fields = all(field in first_question for field in required_db_fields)
                    
                    if has_all_fields:
                        self.log_result("Database Storage", True, "Questions have proper metadata for storage")
                    else:
                        missing = [field for field in required_db_fields if field not in first_question]
                        self.log_result("Database Storage", False, f"Missing database fields: {missing}")
                else:
                    self.log_result("Database Storage", False, "No questions to store")
            else:
                self.log_result("Database Storage", False, f"Failed to generate questions: {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Storage", False, f"Error: {str(e)}")
    
    def test_authentication_required(self):
        """Test that authentication is required for practice generation"""
        try:
            # Test without authentication token
            test_request = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 5
            }
            
            print("🔄 Testing authentication requirement...")
            
            response = requests.post(
                f"{self.api_url}/practice/generate", 
                json=test_request,
                timeout=15
            )
            
            if response.status_code == 401 or response.status_code == 403:
                self.log_result("Authentication Required", True, f"Correctly rejected with {response.status_code}")
            else:
                self.log_result("Authentication Required", False, f"Expected 401/403, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all practice test generation tests"""
        print("🚀 Starting Practice Test Generation Testing")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return
        
        # Authentication setup
        if not self.create_student_account():
            print("❌ Student account creation failed - stopping tests")
            return
        
        if not self.login_student():
            print("❌ Student login failed - stopping tests")
            return
        
        # Core practice test functionality
        print("\n📝 Testing Core Practice Test Generation...")
        self.test_practice_generation_basic()
        
        print("\n🤖 Testing AI Service Integration...")
        self.test_ai_service_integration()
        
        print("\n🔧 Testing Gemini API Configuration...")
        self.test_gemini_api_configuration()
        
        print("\n⚠️ Testing Error Handling...")
        self.test_error_handling()
        
        print("\n💾 Testing Database Storage...")
        self.test_database_storage()
        
        print("\n🔒 Testing Authentication...")
        self.test_authentication_required()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 PRACTICE TEST GENERATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        # Critical issues
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "Practice Generation" in result["test"] or "AI Service" in result["test"] or "Gemini" in result["test"]:
                    critical_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"  • {issue}")
            print("\nThese issues prevent users from generating practice tests!")
        else:
            print("\n✅ No critical issues found - practice test generation is working!")

if __name__ == "__main__":
    tester = PracticeTestGenerationTester()
    tester.run_all_tests()
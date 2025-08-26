#!/usr/bin/env python3
"""
CRITICAL AUTHENTICATION REGRESSION TEST
Testing the specific authentication issues affecting the progress feature
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

print(f"🔍 AUTHENTICATION REGRESSION TEST")
print(f"Testing API: {API_URL}")
print("=" * 80)

class AuthRegressionTest:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {details}")
    
    def test_student_registration_and_authentication(self):
        """Test 1: Student Registration and JWT Token Generation"""
        print("\n🔍 TEST 1: Student Registration and JWT Token Generation")
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"auth_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Authentication Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                
                if self.student_token and self.student_id:
                    self.log_result("Student Registration", "PASS", 
                                  f"Successfully registered student {self.student_id} with JWT token")
                    return True
                else:
                    self.log_result("Student Registration", "FAIL", 
                                  "Registration succeeded but missing token or ID")
                    return False
            else:
                self.log_result("Student Registration", "FAIL", 
                              f"Registration failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Registration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_validation(self):
        """Test 2: JWT Token Validation with get_current_student"""
        print("\n🔍 TEST 2: JWT Token Validation with get_current_student")
        
        if not self.student_token:
            self.log_result("JWT Token Validation", "SKIP", "No student token available")
            return False
        
        # Test student profile endpoint (requires get_current_student)
        url = f"{API_URL}/student/profile"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Student Profile Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id") == self.student_id:
                    self.log_result("JWT Token Validation", "PASS", 
                                  "JWT token successfully validated by get_current_student")
                    return True
                else:
                    self.log_result("JWT Token Validation", "FAIL", 
                                  "Token validated but user ID mismatch")
                    return False
            elif response.status_code == 401:
                self.log_result("JWT Token Validation", "FAIL", 
                              "JWT token rejected with 401 Unauthorized")
                return False
            elif response.status_code == 403:
                self.log_result("JWT Token Validation", "FAIL", 
                              "JWT token rejected with 403 Forbidden")
                return False
            else:
                self.log_result("JWT Token Validation", "FAIL", 
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("JWT Token Validation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_practice_results_endpoint(self):
        """Test 3: Practice Results Endpoint (/api/practice/results)"""
        print("\n🔍 TEST 3: Practice Results Endpoint Authentication")
        
        if not self.student_token:
            self.log_result("Practice Results Endpoint", "SKIP", "No student token available")
            return False
        
        url = f"{API_URL}/practice/results"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Practice Results Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Practice Results Endpoint", "PASS", 
                              f"Successfully accessed practice results (found {len(data)} results)")
                return True
            elif response.status_code == 401:
                self.log_result("Practice Results Endpoint", "FAIL", 
                              "Authentication failed - 401 Unauthorized")
                return False
            elif response.status_code == 403:
                self.log_result("Practice Results Endpoint", "FAIL", 
                              "Authentication failed - 403 Forbidden")
                return False
            else:
                self.log_result("Practice Results Endpoint", "FAIL", 
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Practice Results Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_practice_stats_endpoint(self):
        """Test 4: Practice Stats Endpoint (/api/practice/stats/{subject})"""
        print("\n🔍 TEST 4: Practice Stats Endpoint Authentication")
        
        if not self.student_token:
            self.log_result("Practice Stats Endpoint", "SKIP", "No student token available")
            return False
        
        # Test with math subject
        url = f"{API_URL}/practice/stats/math"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Practice Stats Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Practice Stats Endpoint", "PASS", 
                              f"Successfully accessed practice stats for math (found {data.get('total_tests', 0)} tests)")
                return True
            elif response.status_code == 401:
                self.log_result("Practice Stats Endpoint", "FAIL", 
                              "Authentication failed - 401 Unauthorized")
                return False
            elif response.status_code == 403:
                self.log_result("Practice Stats Endpoint", "FAIL", 
                              "Authentication failed - 403 Forbidden")
                return False
            else:
                self.log_result("Practice Stats Endpoint", "FAIL", 
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Practice Stats Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_end_to_end_progress_flow(self):
        """Test 5: End-to-End Progress Flow (Create → Take → View Results)"""
        print("\n🔍 TEST 5: End-to-End Progress Flow")
        
        if not self.student_token:
            self.log_result("End-to-End Progress Flow", "SKIP", "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            # Step 1: Generate a practice test
            gen_url = f"{API_URL}/practice/generate"
            gen_payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 2
            }
            
            gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
            print(f"Generate Test Response: {gen_response.status_code}")
            
            if gen_response.status_code != 200:
                self.log_result("End-to-End Progress Flow", "FAIL", 
                              f"Failed to generate practice test: {gen_response.status_code}")
                return False
            
            gen_data = gen_response.json()
            questions = gen_data.get("questions", [])
            
            if not questions:
                self.log_result("End-to-End Progress Flow", "FAIL", "No questions generated")
                return False
            
            # Step 2: Submit the practice test
            submit_url = f"{API_URL}/practice/submit"
            student_answers = {}
            question_ids = []
            
            for question in questions:
                question_id = question.get("id")
                question_ids.append(question_id)
                # Use correct answer for 100% score
                student_answers[question_id] = question.get("correct_answer")
            
            submit_payload = {
                "questions": question_ids,
                "student_answers": student_answers,
                "subject": "math",
                "time_taken": 300
            }
            
            submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
            print(f"Submit Test Response: {submit_response.status_code}")
            
            if submit_response.status_code != 200:
                self.log_result("End-to-End Progress Flow", "FAIL", 
                              f"Failed to submit practice test: {submit_response.status_code}")
                return False
            
            submit_data = submit_response.json()
            attempt_id = submit_data.get("attempt_id")
            
            # Step 3: Verify results appear in practice results
            results_response = requests.get(f"{API_URL}/practice/results", headers=headers)
            print(f"Results Check Response: {results_response.status_code}")
            
            if results_response.status_code != 200:
                self.log_result("End-to-End Progress Flow", "FAIL", 
                              f"Failed to retrieve practice results: {results_response.status_code}")
                return False
            
            results_data = results_response.json()
            
            # Check if our submitted test appears in results
            found_test = False
            for result in results_data:
                if result.get("id") == attempt_id:
                    found_test = True
                    break
            
            if found_test:
                self.log_result("End-to-End Progress Flow", "PASS", 
                              f"Successfully completed end-to-end flow: generated → submitted → retrieved results")
                return True
            else:
                self.log_result("End-to-End Progress Flow", "FAIL", 
                              "Test submitted but not found in results")
                return False
                
        except Exception as e:
            self.log_result("End-to-End Progress Flow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_authentication_without_token(self):
        """Test 6: Authentication Behavior Without Token"""
        print("\n🔍 TEST 6: Authentication Behavior Without Token")
        
        # Test practice results without token
        url = f"{API_URL}/practice/results"
        
        try:
            response = requests.get(url)  # No Authorization header
            print(f"No Token Response: {response.status_code}")
            
            if response.status_code == 401:
                self.log_result("Authentication Without Token", "PASS", 
                              "Correctly returns 401 Unauthorized for missing token")
                return True
            elif response.status_code == 403:
                self.log_result("Authentication Without Token", "PASS", 
                              "Returns 403 Forbidden for missing token (acceptable)")
                return True
            else:
                self.log_result("Authentication Without Token", "FAIL", 
                              f"Unexpected response for missing token: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Without Token", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication regression tests"""
        print("🚀 STARTING AUTHENTICATION REGRESSION TESTS")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_student_registration_and_authentication,
            self.test_jwt_token_validation,
            self.test_practice_results_endpoint,
            self.test_practice_stats_endpoint,
            self.test_end_to_end_progress_flow,
            self.test_authentication_without_token
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test in tests:
            result = test()
            if result is True:
                passed += 1
            elif result is False:
                failed += 1
            else:
                skipped += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 AUTHENTICATION REGRESSION TEST SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"{status_icon} {result['test']}: {result['details']}")
        
        print(f"\n📊 RESULTS: {passed} PASSED, {failed} FAILED, {skipped} SKIPPED")
        
        # Determine overall status
        if failed == 0:
            print("🎉 ALL AUTHENTICATION TESTS PASSED - No regression detected!")
            return True
        else:
            print("🚨 AUTHENTICATION REGRESSION DETECTED - Issues found!")
            return False

if __name__ == "__main__":
    test = AuthRegressionTest()
    success = test.run_all_tests()
    exit(0 if success else 1)
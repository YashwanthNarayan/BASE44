#!/usr/bin/env python3
"""
CRITICAL REGRESSION DEBUG: Practice API Endpoints 500 Error Investigation
Testing the specific endpoints mentioned in the review request:
1. GET /api/practice/results
2. GET /api/practice/stats/{subject}  
3. GET /api/practice/results/{attempt_id}
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

print(f"🔍 DEBUGGING PRACTICE API ENDPOINTS")
print(f"Using API URL: {API_URL}")
print("=" * 80)

class PracticeAPIDebugger:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.practice_attempt_id = None
        
    def register_and_login_student(self):
        """Register and login a student for testing"""
        print("\n🔍 STEP 1: Setting up student account...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"debug_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Debug Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student registered successfully: {self.student_id}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def create_practice_test_data(self):
        """Create some practice test data to test with"""
        print("\n🔍 STEP 2: Creating practice test data...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Generate a practice test
        gen_url = f"{API_URL}/practice/generate"
        gen_payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        try:
            print(f"Generating practice test...")
            gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
            print(f"Generate Response: {gen_response.status_code}")
            
            if gen_response.status_code != 200:
                print(f"❌ Failed to generate practice test: {gen_response.text}")
                return False
            
            gen_data = gen_response.json()
            questions = gen_data.get("questions", [])
            
            if not questions:
                print("❌ No questions generated")
                return False
            
            print(f"✅ Generated {len(questions)} questions")
            
            # Submit the practice test
            submit_url = f"{API_URL}/practice/submit"
            
            # Create answers (use correct answers for testing)
            student_answers = {}
            question_ids = []
            for question in questions:
                question_id = question.get("id")
                if question_id:
                    question_ids.append(question_id)
                    student_answers[question_id] = question.get("correct_answer", "test answer")
            
            submit_payload = {
                "questions": question_ids,
                "student_answers": student_answers,
                "subject": "math",
                "time_taken": 300
            }
            
            print(f"Submitting practice test...")
            submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
            print(f"Submit Response: {submit_response.status_code}")
            
            if submit_response.status_code == 200:
                submit_data = submit_response.json()
                self.practice_attempt_id = submit_data.get("attempt_id")
                print(f"✅ Practice test submitted successfully: {self.practice_attempt_id}")
                print(f"Score: {submit_data.get('score')}%")
                return True
            else:
                print(f"❌ Failed to submit practice test: {submit_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating practice test data: {str(e)}")
            return False
    
    def test_practice_results_endpoint(self):
        """Test GET /api/practice/results endpoint"""
        print("\n🔍 STEP 3: Testing GET /api/practice/results endpoint...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        url = f"{API_URL}/practice/results"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Got {len(data)} practice results")
                
                if data:
                    first_result = data[0]
                    print(f"First result structure: {list(first_result.keys())}")
                    print(f"First result ID: {first_result.get('id')}")
                    print(f"First result subject: {first_result.get('subject')}")
                    print(f"First result score: {first_result.get('score')}")
                else:
                    print("⚠️ No practice results found")
                
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response body: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            return False
    
    def test_practice_stats_endpoint(self):
        """Test GET /api/practice/stats/{subject} endpoint"""
        print("\n🔍 STEP 4: Testing GET /api/practice/stats/{subject} endpoint...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        # Test with math subject
        subject = "math"
        url = f"{API_URL}/practice/stats/{subject}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Got stats for {subject}")
                print(f"Total tests: {data.get('total_tests')}")
                print(f"Average score: {data.get('average_score')}")
                print(f"Recent tests count: {len(data.get('recent_tests', []))}")
                
                # Check if recent tests have ID field
                recent_tests = data.get('recent_tests', [])
                if recent_tests:
                    first_recent = recent_tests[0]
                    print(f"Recent test structure: {list(first_recent.keys())}")
                    if 'id' in first_recent:
                        print(f"✅ Recent tests have 'id' field: {first_recent.get('id')}")
                    else:
                        print(f"❌ Recent tests missing 'id' field - this causes frontend click issues!")
                
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response body: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            return False
    
    def test_detailed_results_endpoint(self):
        """Test GET /api/practice/results/{attempt_id} endpoint"""
        print("\n🔍 STEP 5: Testing GET /api/practice/results/{attempt_id} endpoint...")
        
        if not self.student_token or not self.practice_attempt_id:
            print("❌ No student token or attempt ID available")
            return False
        
        url = f"{API_URL}/practice/results/{self.practice_attempt_id}"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Got detailed results")
                print(f"Result structure: {list(data.keys())}")
                
                # Check field consistency
                if 'id' in data:
                    print(f"✅ Has 'id' field: {data.get('id')}")
                else:
                    print(f"❌ Missing 'id' field")
                
                if 'attempt_id' in data:
                    print(f"✅ Has 'attempt_id' field: {data.get('attempt_id')}")
                else:
                    print(f"❌ Missing 'attempt_id' field")
                
                print(f"Score: {data.get('score')}")
                print(f"Subject: {data.get('subject')}")
                print(f"Total questions: {data.get('total_questions')}")
                
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response body: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            return False
    
    def run_debug_tests(self):
        """Run all debug tests"""
        print("🚨 CRITICAL REGRESSION DEBUG: Practice API Endpoints 500 Error Investigation")
        print("Testing endpoints that are preventing progress feature from working")
        print("=" * 80)
        
        results = {
            "student_setup": False,
            "practice_data_creation": False,
            "practice_results": False,
            "practice_stats": False,
            "detailed_results": False
        }
        
        # Step 1: Setup student account
        results["student_setup"] = self.register_and_login_student()
        
        if results["student_setup"]:
            # Step 2: Create practice test data
            results["practice_data_creation"] = self.create_practice_test_data()
            
            if results["practice_data_creation"]:
                # Step 3: Test the problematic endpoints
                results["practice_results"] = self.test_practice_results_endpoint()
                results["practice_stats"] = self.test_practice_stats_endpoint()
                results["detailed_results"] = self.test_detailed_results_endpoint()
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 DEBUG TEST RESULTS SUMMARY:")
        print("=" * 80)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Overall assessment
        critical_endpoints = ["practice_results", "practice_stats", "detailed_results"]
        critical_passed = all(results[endpoint] for endpoint in critical_endpoints if endpoint in results)
        
        print("\n" + "=" * 80)
        if critical_passed:
            print("🎉 CONCLUSION: All critical practice API endpoints are working correctly!")
            print("The 500 errors mentioned in the review request are NOT occurring in current testing.")
            print("The progress feature should be functional.")
        else:
            print("🚨 CONCLUSION: CRITICAL ISSUES FOUND!")
            print("The practice API endpoints are indeed returning errors.")
            print("This confirms the regression mentioned in the review request.")
            
            failed_endpoints = [endpoint for endpoint in critical_endpoints if not results.get(endpoint, False)]
            print(f"Failed endpoints: {failed_endpoints}")
        
        print("=" * 80)
        
        return results

if __name__ == "__main__":
    debugger = PracticeAPIDebugger()
    debugger.run_debug_tests()
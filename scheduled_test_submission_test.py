#!/usr/bin/env python3
"""
Focused test for the scheduled practice test submission fix.
Tests the critical bug fix where frontend was sending full question objects 
instead of question ID strings in the 'questions' field.
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

class ScheduledTestSubmissionTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        
    def register_and_login_student(self):
        """Register and login a student for testing"""
        print("\n🔍 Setting up student account for scheduled test submission testing...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"scheduled_test_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Patel",
            "user_type": "student",
            "grade_level": "10th"
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
    
    def test_scheduled_test_submission_with_correct_data_structure(self):
        """Test the /api/practice/submit-scheduled endpoint with the CORRECT data structure"""
        print("\n🎯 TESTING SCHEDULED TEST SUBMISSION WITH CORRECT DATA STRUCTURE")
        print("=" * 80)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/practice/submit-scheduled"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create sample question data (what would be embedded in scheduled tests)
        sample_questions = [
            {
                "id": "question-1",
                "question_text": "What is 2 + 2?",
                "question_type": "short_answer",
                "correct_answer": "4",
                "subject": "math",
                "topic": "Basic Arithmetic",
                "explanation": "Simple addition: 2 + 2 = 4"
            },
            {
                "id": "question-2", 
                "question_text": "What is the capital of India?",
                "question_type": "short_answer",
                "correct_answer": "New Delhi",
                "subject": "geography",
                "topic": "World Capitals",
                "explanation": "New Delhi is the capital city of India"
            },
            {
                "id": "question-3",
                "question_text": "What is 5 × 3?",
                "question_type": "short_answer", 
                "correct_answer": "15",
                "subject": "math",
                "topic": "Multiplication",
                "explanation": "5 multiplied by 3 equals 15"
            }
        ]
        
        # CORRECT payload structure (after the fix)
        correct_payload = {
            "questions": ["question-1", "question-2", "question-3"],  # Array of ID strings (FIXED)
            "student_answers": {
                "question-1": "4",
                "question-2": "New Delhi", 
                "question-3": "15"
            },
            "subject": "math",
            "time_taken": 300,
            "question_data": sample_questions  # Full question objects go here
        }
        
        print("🔍 Testing with CORRECT data structure:")
        print(f"   - questions field: {type(correct_payload['questions'])} with {len(correct_payload['questions'])} items")
        print(f"   - questions[0] type: {type(correct_payload['questions'][0])}")
        print(f"   - question_data field: {type(correct_payload['question_data'])} with {len(correct_payload['question_data'])} items")
        print(f"   - question_data[0] type: {type(correct_payload['question_data'][0])}")
        
        try:
            response = requests.post(url, json=correct_payload, headers=headers)
            print(f"\n📊 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: Scheduled test submission worked with correct data structure!")
                data = response.json()
                print(f"   - Attempt ID: {data.get('attempt_id')}")
                print(f"   - Score: {data.get('score')}%")
                print(f"   - Correct Answers: {data.get('correct_answers')}/{data.get('total_questions')}")
                print(f"   - Grade: {data.get('grade')}")
                print(f"   - XP Gained: {data.get('xp_gained')}")
                return True
            elif response.status_code == 422:
                print("❌ CRITICAL: Still getting 422 Unprocessable Entity error!")
                print("   This means the fix did not work correctly.")
                try:
                    error_data = response.json()
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw error response: {response.text}")
                return False
            else:
                print(f"❌ UNEXPECTED ERROR: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION during test: {str(e)}")
            return False
    
    def test_scheduled_test_submission_with_wrong_data_structure(self):
        """Test the /api/practice/submit-scheduled endpoint with the WRONG data structure (should fail)"""
        print("\n🎯 TESTING SCHEDULED TEST SUBMISSION WITH WRONG DATA STRUCTURE (SHOULD FAIL)")
        print("=" * 80)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/practice/submit-scheduled"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create sample question data
        sample_questions = [
            {
                "id": "question-1",
                "question_text": "What is 2 + 2?",
                "question_type": "short_answer",
                "correct_answer": "4",
                "subject": "math",
                "topic": "Basic Arithmetic"
            }
        ]
        
        # WRONG payload structure (before the fix)
        wrong_payload = {
            "questions": sample_questions,  # Full question objects (WRONG - should cause 422)
            "student_answers": {
                "question-1": "4"
            },
            "subject": "math",
            "time_taken": 300,
            "question_data": sample_questions
        }
        
        print("🔍 Testing with WRONG data structure (should fail with 422):")
        print(f"   - questions field: {type(wrong_payload['questions'])} with {len(wrong_payload['questions'])} items")
        print(f"   - questions[0] type: {type(wrong_payload['questions'][0])}")
        
        try:
            response = requests.post(url, json=wrong_payload, headers=headers)
            print(f"\n📊 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 422:
                print("✅ EXPECTED: Got 422 error with wrong data structure (validation working)")
                try:
                    error_data = response.json()
                    print(f"   Validation error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw error response: {response.text}")
                return True
            elif response.status_code == 200:
                print("⚠️ UNEXPECTED: Request succeeded with wrong data structure")
                print("   This might indicate the backend is too permissive")
                return False
            else:
                print(f"❌ UNEXPECTED ERROR: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION during test: {str(e)}")
            return False
    
    def test_pydantic_model_validation(self):
        """Test various data structures to verify Pydantic model validation"""
        print("\n🎯 TESTING PYDANTIC MODEL VALIDATION WITH VARIOUS DATA STRUCTURES")
        print("=" * 80)
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/practice/submit-scheduled"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        test_cases = [
            {
                "name": "Valid: questions as string array",
                "payload": {
                    "questions": ["q1", "q2"],
                    "student_answers": {"q1": "answer1", "q2": "answer2"},
                    "subject": "math",
                    "time_taken": 300,
                    "question_data": [
                        {"id": "q1", "question_text": "Test 1", "correct_answer": "answer1"},
                        {"id": "q2", "question_text": "Test 2", "correct_answer": "answer2"}
                    ]
                },
                "expected_status": 200
            },
            {
                "name": "Invalid: questions as object array",
                "payload": {
                    "questions": [{"id": "q1"}, {"id": "q2"}],
                    "student_answers": {"q1": "answer1", "q2": "answer2"},
                    "subject": "math", 
                    "time_taken": 300,
                    "question_data": [
                        {"id": "q1", "question_text": "Test 1", "correct_answer": "answer1"},
                        {"id": "q2", "question_text": "Test 2", "correct_answer": "answer2"}
                    ]
                },
                "expected_status": 422
            },
            {
                "name": "Invalid: missing questions field",
                "payload": {
                    "student_answers": {"q1": "answer1"},
                    "subject": "math",
                    "time_taken": 300,
                    "question_data": [{"id": "q1", "question_text": "Test 1", "correct_answer": "answer1"}]
                },
                "expected_status": 422
            },
            {
                "name": "Invalid: missing student_answers field",
                "payload": {
                    "questions": ["q1"],
                    "subject": "math",
                    "time_taken": 300,
                    "question_data": [{"id": "q1", "question_text": "Test 1", "correct_answer": "answer1"}]
                },
                "expected_status": 422
            }
        ]
        
        results = []
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['name']}")
            
            try:
                response = requests.post(url, json=test_case['payload'], headers=headers)
                actual_status = response.status_code
                expected_status = test_case['expected_status']
                
                print(f"   Expected: {expected_status}, Got: {actual_status}")
                
                if actual_status == expected_status:
                    print("   ✅ PASS")
                    results.append(True)
                else:
                    print("   ❌ FAIL")
                    if actual_status == 422:
                        try:
                            error_data = response.json()
                            print(f"   Validation error: {error_data}")
                        except:
                            print(f"   Raw response: {response.text}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 VALIDATION TEST RESULTS: {sum(results)}/{len(results)} passed ({success_rate:.1f}%)")
        
        return all(results)
    
    def run_all_tests(self):
        """Run all scheduled test submission tests"""
        print("🚀 STARTING SCHEDULED TEST SUBMISSION FIX VERIFICATION")
        print("=" * 80)
        print("Testing the critical bug fix where frontend was sending full question objects")
        print("instead of question ID strings in the 'questions' field.")
        print("=" * 80)
        
        # Setup
        if not self.register_and_login_student():
            print("❌ Failed to setup test environment")
            return False
        
        # Run tests
        test_results = []
        
        # Test 1: Correct data structure (should work)
        test_results.append(self.test_scheduled_test_submission_with_correct_data_structure())
        
        # Test 2: Wrong data structure (should fail with 422)
        test_results.append(self.test_scheduled_test_submission_with_wrong_data_structure())
        
        # Test 3: Pydantic model validation
        test_results.append(self.test_pydantic_model_validation())
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 FINAL TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = passed_tests / total_tests * 100
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if all(test_results):
            print("✅ ALL TESTS PASSED: Scheduled test submission fix is working correctly!")
            print("   - Frontend can now send question IDs in 'questions' field")
            print("   - Backend properly validates the TestSubmissionRequest model")
            print("   - No more 422 Unprocessable Entity errors")
            return True
        else:
            print("❌ SOME TESTS FAILED: Scheduled test submission fix needs attention")
            for i, result in enumerate(test_results, 1):
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   Test {i}: {status}")
            return False

if __name__ == "__main__":
    tester = ScheduledTestSubmissionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SCHEDULED TEST SUBMISSION FIX VERIFICATION COMPLETED SUCCESSFULLY!")
        exit(0)
    else:
        print("\n💥 SCHEDULED TEST SUBMISSION FIX VERIFICATION FAILED!")
        exit(1)
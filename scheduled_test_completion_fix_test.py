#!/usr/bin/env python3
"""
SCHEDULED TEST COMPLETION FIX VERIFICATION TEST
==============================================

This test verifies the FINAL fix for the scheduled practice test submission 422 error.
The main agent has fixed the root cause in the `/api/practice-scheduler/complete-scheduled-test/{test_id}` endpoint.

WHAT WAS FIXED:
- Backend endpoint was expecting `score: float` as function parameter
- Frontend was sending score in request body as `{"score": value}`
- Created new `CompleteTestRequest` Pydantic model with `score: float` field
- Updated endpoint to accept `request: CompleteTestRequest` instead of `score: float` parameter

TESTING FOCUS:
1. Test `/api/practice-scheduler/complete-scheduled-test/{test_id}` endpoint with POST request body `{"score": 85.5}`
2. Verify it returns 200 OK instead of 422 Unprocessable Entity
3. Test the complete scheduled test submission flow end-to-end
4. Test with various score values (0-100)
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import uuid

# API Configuration
API_BASE = "http://localhost:8001"

class ScheduledTestCompletionFixTest:
    def __init__(self):
        self.session = None
        self.student_token = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name, passed, details=""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results["test_details"].append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    async def register_and_login_student(self):
        """Register and login a test student"""
        try:
            # Register student
            student_data = {
                "username": f"test_student_{uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "testpass123",
                "user_type": "student",
                "full_name": "Test Student"
            }
            
            async with self.session.post(f"{API_BASE}/api/auth/register", json=student_data) as response:
                if response.status == 200:
                    register_data = await response.json()
                    self.student_token = register_data.get("access_token")
                    self.log_test_result("Student Registration", True, f"Token: {self.student_token[:20]}...")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("Student Registration", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        
        except Exception as e:
            self.log_test_result("Student Registration", False, f"Exception: {str(e)}")
            return False
    
    async def create_scheduled_test(self):
        """Create a scheduled test for testing completion"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Schedule a review test
            schedule_data = {
                "subject": "math",
                "topics": ["algebra", "equations"],
                "difficulty": "medium",
                "original_score": 75.0,
                "question_count": 3
            }
            
            async with self.session.post(f"{API_BASE}/api/practice-scheduler/schedule-review", 
                                       json=schedule_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    scheduled_test_id = data.get("scheduled_test_id")
                    self.log_test_result("Create Scheduled Test", True, f"Test ID: {scheduled_test_id}")
                    return scheduled_test_id
                else:
                    error_text = await response.text()
                    self.log_test_result("Create Scheduled Test", False, f"Status: {response.status}, Error: {error_text}")
                    return None
        
        except Exception as e:
            self.log_test_result("Create Scheduled Test", False, f"Exception: {str(e)}")
            return None
    
    async def take_scheduled_test(self, test_id):
        """Take a scheduled test to get questions"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            async with self.session.post(f"{API_BASE}/api/practice-scheduler/take-scheduled-test/{test_id}", 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    questions = data.get("questions", [])
                    self.log_test_result("Take Scheduled Test", True, f"Got {len(questions)} questions")
                    return questions
                else:
                    error_text = await response.text()
                    self.log_test_result("Take Scheduled Test", False, f"Status: {response.status}, Error: {error_text}")
                    return None
        
        except Exception as e:
            self.log_test_result("Take Scheduled Test", False, f"Exception: {str(e)}")
            return None
    
    async def submit_scheduled_test(self, questions):
        """Submit scheduled test answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Create student answers
            student_answers = {}
            for question in questions:
                question_id = question.get("id", "")
                if question_id:
                    student_answers[question_id] = "Test answer for completion"
            
            # Submit test using the fixed data structure
            submission_data = {
                "questions": [q.get("id", "") for q in questions],  # Question ID strings only
                "student_answers": student_answers,
                "subject": "math",
                "time_taken": 300,
                "difficulty": "medium",
                "question_data": questions  # Full question objects for processing
            }
            
            async with self.session.post(f"{API_BASE}/api/practice/submit-scheduled", 
                                       json=submission_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    attempt_id = data.get("attempt_id")
                    score = data.get("score", 0)
                    self.log_test_result("Submit Scheduled Test", True, f"Attempt ID: {attempt_id}, Score: {score}%")
                    return attempt_id, score
                else:
                    error_text = await response.text()
                    self.log_test_result("Submit Scheduled Test", False, f"Status: {response.status}, Error: {error_text}")
                    return None, None
        
        except Exception as e:
            self.log_test_result("Submit Scheduled Test", False, f"Exception: {str(e)}")
            return None, None
    
    async def test_complete_scheduled_test_endpoint(self, test_id, score):
        """Test the FIXED complete-scheduled-test endpoint with request body"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test the FIXED endpoint - score in request body
            completion_data = {"score": score}
            
            async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                       json=completion_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    self.log_test_result(f"Complete Scheduled Test (Score: {score})", True, 
                                       f"Status: 200 OK, Message: {message}")
                    return True
                elif response.status == 422:
                    self.log_test_result(f"Complete Scheduled Test (Score: {score})", False, 
                                       f"Status: 422 Unprocessable Entity - FIX NOT WORKING! Response: {response_text}")
                    return False
                else:
                    self.log_test_result(f"Complete Scheduled Test (Score: {score})", False, 
                                       f"Status: {response.status}, Response: {response_text}")
                    return False
        
        except Exception as e:
            self.log_test_result(f"Complete Scheduled Test (Score: {score})", False, f"Exception: {str(e)}")
            return False
    
    async def test_various_score_values(self, test_id):
        """Test the endpoint with various score values (0-100)"""
        test_scores = [0.0, 25.5, 50.0, 75.5, 85.5, 95.0, 100.0]
        
        print(f"\n🎯 TESTING VARIOUS SCORE VALUES:")
        print("=" * 50)
        
        success_count = 0
        for score in test_scores:
            # Create a new scheduled test for each score test
            new_test_id = await self.create_scheduled_test()
            if new_test_id:
                success = await self.test_complete_scheduled_test_endpoint(new_test_id, score)
                if success:
                    success_count += 1
        
        overall_success = success_count == len(test_scores)
        self.log_test_result("Various Score Values Test", overall_success, 
                           f"Passed {success_count}/{len(test_scores)} score tests")
        
        return overall_success
    
    async def test_end_to_end_flow(self):
        """Test the complete end-to-end scheduled test flow"""
        print(f"\n🔄 TESTING END-TO-END SCHEDULED TEST FLOW:")
        print("=" * 50)
        
        # Step 1: Create scheduled test
        test_id = await self.create_scheduled_test()
        if not test_id:
            return False
        
        # Step 2: Take scheduled test (get questions)
        questions = await self.take_scheduled_test(test_id)
        if not questions:
            return False
        
        # Step 3: Submit scheduled test answers
        attempt_id, score = await self.submit_scheduled_test(questions)
        if not attempt_id:
            return False
        
        # Step 4: Complete scheduled test with score
        success = await self.test_complete_scheduled_test_endpoint(test_id, score)
        
        self.log_test_result("End-to-End Flow", success, 
                           f"Complete flow from creation to completion")
        
        return success
    
    async def run_all_tests(self):
        """Run all scheduled test completion fix tests"""
        print("🚀 SCHEDULED TEST COMPLETION FIX VERIFICATION")
        print("=" * 60)
        print("Testing the FINAL fix for 422 Unprocessable Entity error")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Setup: Register and login student
            if not await self.register_and_login_student():
                print("❌ Failed to setup test student - aborting tests")
                return
            
            print(f"\n🎯 SPECIFIC TESTING REQUIRED:")
            print("1. Test /api/practice-scheduler/complete-scheduled-test/{test_id} endpoint")
            print("2. Verify it returns 200 OK instead of 422 Unprocessable Entity")
            print("3. Test with request body {\"score\": XX}")
            print("4. Test with various score values (0-100)")
            print("5. Test complete end-to-end flow")
            
            # Test 1: End-to-end flow
            await self.test_end_to_end_flow()
            
            # Test 2: Various score values
            await self.test_various_score_values(None)  # Will create its own test IDs
            
            # Test 3: Edge cases
            print(f"\n🧪 TESTING EDGE CASES:")
            print("=" * 30)
            
            # Test with invalid test ID
            await self.test_complete_scheduled_test_endpoint("invalid-test-id", 85.5)
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        print(f"\n📊 FINAL TEST RESULTS:")
        print("=" * 40)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {(self.test_results['passed_tests']/self.test_results['total_tests']*100):.1f}%")
        
        if self.test_results['failed_tests'] == 0:
            print("\n🎉 ALL TESTS PASSED! The scheduled test completion fix is working correctly!")
            print("✅ No more 422 Unprocessable Entity errors")
            print("✅ Request body {\"score\": XX} is properly accepted")
            print("✅ End-to-end flow works successfully")
        else:
            print(f"\n⚠️  {self.test_results['failed_tests']} TESTS FAILED")
            print("❌ The fix may not be working correctly")
            
            # Show failed tests
            print("\nFailed Tests:")
            for result in self.test_results['test_details']:
                if "❌ FAIL" in result['status']:
                    print(f"  - {result['test']}: {result['details']}")

async def main():
    """Main test execution"""
    test_runner = ScheduledTestCompletionFixTest()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
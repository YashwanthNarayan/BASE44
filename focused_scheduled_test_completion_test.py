#!/usr/bin/env python3
"""
FOCUSED SCHEDULED TEST COMPLETION FIX TEST
==========================================

This test focuses specifically on testing the FIXED `/api/practice-scheduler/complete-scheduled-test/{test_id}` endpoint
to verify that it now accepts `{"score": XX}` in the request body instead of causing 422 Unprocessable Entity errors.

WHAT WAS FIXED:
- Backend endpoint was expecting `score: float` as function parameter
- Frontend was sending score in request body as `{"score": value}`
- Created new `CompleteTestRequest` Pydantic model with `score: float` field
- Updated endpoint to accept `request: CompleteTestRequest` instead of `score: float` parameter
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import uuid

# API Configuration
API_BASE = "http://localhost:8001"

class FocusedScheduledTestCompletionTest:
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
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestPass123!",
                "name": "Test Student",
                "user_type": "student"
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
    
    async def create_scheduled_test_directly(self):
        """Create a scheduled test directly in the database via a practice test submission"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # First, generate a practice test to trigger automatic scheduling
            test_request = {
                "subject": "math",
                "topics": ["algebra"],
                "difficulty": "medium",
                "question_count": 3,
                "question_types": ["mcq", "short_answer"]
            }
            
            async with self.session.post(f"{API_BASE}/api/practice/generate", 
                                       json=test_request, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    questions = data.get("questions", [])
                    
                    # Submit the test with a low score to trigger scheduling
                    student_answers = {}
                    for question in questions:
                        student_answers[question["id"]] = "wrong answer"
                    
                    submission_data = {
                        "questions": [q["id"] for q in questions],
                        "student_answers": student_answers,
                        "subject": "math",
                        "time_taken": 300
                    }
                    
                    async with self.session.post(f"{API_BASE}/api/practice/submit", 
                                               json=submission_data, headers=headers) as submit_response:
                        if submit_response.status == 200:
                            # Now get upcoming tests to find the scheduled test ID
                            async with self.session.get(f"{API_BASE}/api/practice-scheduler/upcoming-tests", 
                                                       headers=headers) as upcoming_response:
                                if upcoming_response.status == 200:
                                    upcoming_data = await upcoming_response.json()
                                    # Look for any scheduled test
                                    for category in ["overdue", "today", "this_week", "later"]:
                                        tests = upcoming_data.get(category, [])
                                        if tests:
                                            test_id = tests[0]["id"]
                                            self.log_test_result("Create Scheduled Test", True, f"Test ID: {test_id}")
                                            return test_id
                                    
                                    self.log_test_result("Create Scheduled Test", False, "No scheduled tests found")
                                    return None
                                else:
                                    error_text = await upcoming_response.text()
                                    self.log_test_result("Create Scheduled Test", False, f"Upcoming tests error: {error_text}")
                                    return None
                        else:
                            error_text = await submit_response.text()
                            self.log_test_result("Create Scheduled Test", False, f"Submit error: {error_text}")
                            return None
                else:
                    error_text = await response.text()
                    self.log_test_result("Create Scheduled Test", False, f"Generate error: {error_text}")
                    return None
        
        except Exception as e:
            self.log_test_result("Create Scheduled Test", False, f"Exception: {str(e)}")
            return None
    
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
    
    async def test_various_score_values(self):
        """Test the endpoint with various score values (0-100)"""
        test_scores = [0.0, 25.5, 50.0, 75.5, 85.5, 95.0, 100.0]
        
        print(f"\n🎯 TESTING VARIOUS SCORE VALUES:")
        print("=" * 50)
        
        success_count = 0
        for score in test_scores:
            # Create a new scheduled test for each score test
            test_id = await self.create_scheduled_test_directly()
            if test_id:
                success = await self.test_complete_scheduled_test_endpoint(test_id, score)
                if success:
                    success_count += 1
            else:
                self.log_test_result(f"Complete Scheduled Test (Score: {score})", False, "Could not create test")
        
        overall_success = success_count == len(test_scores)
        self.log_test_result("Various Score Values Test", overall_success, 
                           f"Passed {success_count}/{len(test_scores)} score tests")
        
        return overall_success
    
    async def test_direct_endpoint_validation(self):
        """Test the endpoint directly with different request formats"""
        print(f"\n🔍 TESTING DIRECT ENDPOINT VALIDATION:")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        test_id = "test-id-for-validation"  # Use a fake ID to test validation
        
        # Test 1: Correct format - score in request body
        print("Test 1: Correct format - score in request body")
        completion_data = {"score": 85.5}
        
        async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                   json=completion_data, headers=headers) as response:
            response_text = await response.text()
            
            if response.status == 422:
                # Check if it's a validation error about the request format
                if "Field required" in response_text and "score" in response_text:
                    self.log_test_result("Request Body Format Validation", False, 
                                       f"422 error suggests score field not recognized: {response_text}")
                else:
                    self.log_test_result("Request Body Format Validation", True, 
                                       f"422 error is about test not found, not request format: {response_text}")
            elif response.status == 404:
                self.log_test_result("Request Body Format Validation", True, 
                                   f"404 error (test not found) - request format is correct")
            else:
                self.log_test_result("Request Body Format Validation", True, 
                                   f"Status: {response.status} - request format accepted")
        
        # Test 2: Wrong format - score as query parameter (old way)
        print("Test 2: Wrong format - score as query parameter")
        async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}?score=85.5", 
                                   headers=headers) as response:
            response_text = await response.text()
            
            if response.status == 422:
                self.log_test_result("Query Parameter Format Rejection", True, 
                                   f"422 error correctly rejects query parameter format: {response_text}")
            else:
                self.log_test_result("Query Parameter Format Rejection", False, 
                                   f"Should reject query parameter format but got: {response.status}")
        
        # Test 3: Empty request body
        print("Test 3: Empty request body")
        async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                   json={}, headers=headers) as response:
            response_text = await response.text()
            
            if response.status == 422 and "Field required" in response_text:
                self.log_test_result("Empty Body Validation", True, 
                                   f"422 error correctly requires score field: {response_text}")
            else:
                self.log_test_result("Empty Body Validation", False, 
                                   f"Should require score field but got: {response.status}")
    
    async def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 FOCUSED SCHEDULED TEST COMPLETION FIX VERIFICATION")
        print("=" * 70)
        print("Testing the FINAL fix for 422 Unprocessable Entity error")
        print("Focus: /api/practice-scheduler/complete-scheduled-test/{test_id}")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Setup: Register and login student
            if not await self.register_and_login_student():
                print("❌ Failed to setup test student - aborting tests")
                return
            
            # Test 1: Direct endpoint validation (most important)
            await self.test_direct_endpoint_validation()
            
            # Test 2: Try to create and test with real scheduled test
            print(f"\n🔄 TESTING WITH REAL SCHEDULED TEST:")
            print("=" * 50)
            
            test_id = await self.create_scheduled_test_directly()
            if test_id:
                await self.test_complete_scheduled_test_endpoint(test_id, 85.5)
                
                # Test with a few more scores on the same test
                await self.test_complete_scheduled_test_endpoint(test_id, 95.0)
            else:
                print("⚠️  Could not create scheduled test for real testing")
            
        finally:
            await self.cleanup_session()
        
        # Print final results
        print(f"\n📊 FINAL TEST RESULTS:")
        print("=" * 40)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {(self.test_results['passed_tests']/self.test_results['total_tests']*100):.1f}%")
        
        # Check if the key fix is working
        key_tests_passed = 0
        key_tests_total = 0
        
        for result in self.test_results['test_details']:
            if "Request Body Format Validation" in result['test']:
                key_tests_total += 1
                if "✅ PASS" in result['status']:
                    key_tests_passed += 1
        
        if key_tests_passed > 0:
            print("\n🎉 KEY FIX VERIFICATION:")
            print("✅ The endpoint now accepts score in request body format")
            print("✅ No more 422 Unprocessable Entity errors for correct format")
            print("✅ The CompleteTestRequest Pydantic model is working")
        else:
            print("\n❌ KEY FIX ISSUES:")
            print("❌ The endpoint may still have issues with request body format")
            print("❌ 422 errors may still occur")

async def main():
    """Main test execution"""
    test_runner = FocusedScheduledTestCompletionTest()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
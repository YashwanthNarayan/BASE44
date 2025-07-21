#!/usr/bin/env python3
"""
COMPREHENSIVE SCHEDULED TEST SUBMISSION FIX VERIFICATION
========================================================

This test verifies ALL aspects of the scheduled test submission fix as requested:

1. Test `/api/practice-scheduler/complete-scheduled-test/{test_id}` endpoint with POST request body `{"score": 85.5}`
2. Verify it returns 200 OK instead of 422 Unprocessable Entity
3. Test the complete scheduled test submission flow end-to-end:
   - Create scheduled test
   - Take scheduled test (get questions)
   - Submit scheduled test answers to `/api/practice/submit-scheduled`
   - Complete scheduled test with `/api/practice-scheduler/complete-scheduled-test/{test_id}`
4. Test with various score values (0-100)
5. Confirm no validation errors occur
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import uuid

# API Configuration
API_BASE = "http://localhost:8001"

class ComprehensiveScheduledTestFixVerification:
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
                    self.log_test_result("Student Registration", True, f"Token obtained")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test_result("Student Registration", False, f"Status: {response.status}")
                    return False
        
        except Exception as e:
            self.log_test_result("Student Registration", False, f"Exception: {str(e)}")
            return False
    
    async def create_scheduled_test_via_practice(self):
        """Create a scheduled test by submitting a practice test (triggers auto-scheduling)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Generate practice test
            test_request = {
                "subject": "math",
                "topics": ["algebra", "equations"],
                "difficulty": "medium",
                "question_count": 3,
                "question_types": ["mcq", "short_answer"]
            }
            
            async with self.session.post(f"{API_BASE}/api/practice/generate", 
                                       json=test_request, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    questions = data.get("questions", [])
                    
                    # Submit with low score to trigger scheduling
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
                            # Get upcoming tests to find scheduled test
                            async with self.session.get(f"{API_BASE}/api/practice-scheduler/upcoming-tests", 
                                                       headers=headers) as upcoming_response:
                                if upcoming_response.status == 200:
                                    upcoming_data = await upcoming_response.json()
                                    for category in ["overdue", "today", "this_week", "later"]:
                                        tests = upcoming_data.get(category, [])
                                        if tests:
                                            test_id = tests[0]["id"]
                                            self.log_test_result("Create Scheduled Test", True, f"Test ID: {test_id}")
                                            return test_id
                                    
                                    self.log_test_result("Create Scheduled Test", False, "No scheduled tests found")
                                    return None
                                else:
                                    self.log_test_result("Create Scheduled Test", False, "Failed to get upcoming tests")
                                    return None
                        else:
                            self.log_test_result("Create Scheduled Test", False, "Failed to submit practice test")
                            return None
                else:
                    self.log_test_result("Create Scheduled Test", False, "Failed to generate practice test")
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
                    self.log_test_result("Take Scheduled Test", False, f"Status: {response.status}")
                    return None
        
        except Exception as e:
            self.log_test_result("Take Scheduled Test", False, f"Exception: {str(e)}")
            return None
    
    async def submit_scheduled_test_answers(self, questions):
        """Submit scheduled test answers to /api/practice/submit-scheduled"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Create student answers
            student_answers = {}
            for question in questions:
                question_id = question.get("id", "")
                if question_id:
                    # Give some correct answers for a decent score
                    if "algebra" in question.get("topic", "").lower():
                        student_answers[question_id] = question.get("correct_answer", "test answer")
                    else:
                        student_answers[question_id] = "test answer"
            
            # Submit using the FIXED data structure
            submission_data = {
                "questions": [q.get("id", "") for q in questions],  # Question ID strings only (FIXED)
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
                    self.log_test_result("Submit Scheduled Test", True, f"Score: {score}%, Attempt: {attempt_id}")
                    return score
                elif response.status == 422:
                    error_text = await response.text()
                    self.log_test_result("Submit Scheduled Test", False, f"422 Error - Data structure issue: {error_text}")
                    return None
                else:
                    error_text = await response.text()
                    self.log_test_result("Submit Scheduled Test", False, f"Status: {response.status}")
                    return None
        
        except Exception as e:
            self.log_test_result("Submit Scheduled Test", False, f"Exception: {str(e)}")
            return None
    
    async def complete_scheduled_test(self, test_id, score):
        """Complete scheduled test with /api/practice-scheduler/complete-scheduled-test/{test_id}"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Use the FIXED request body format
            completion_data = {"score": score}
            
            async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                       json=completion_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    self.log_test_result("Complete Scheduled Test", True, f"200 OK - {message}")
                    return True
                elif response.status == 422:
                    error_text = await response.text()
                    self.log_test_result("Complete Scheduled Test", False, f"422 Error - FIX NOT WORKING: {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    self.log_test_result("Complete Scheduled Test", False, f"Status: {response.status}")
                    return False
        
        except Exception as e:
            self.log_test_result("Complete Scheduled Test", False, f"Exception: {str(e)}")
            return False
    
    async def test_end_to_end_flow(self):
        """Test the complete end-to-end scheduled test submission flow"""
        print(f"\n🔄 END-TO-END SCHEDULED TEST SUBMISSION FLOW:")
        print("=" * 60)
        print("1. Create scheduled test")
        print("2. Take scheduled test (get questions)")
        print("3. Submit scheduled test answers to /api/practice/submit-scheduled")
        print("4. Complete scheduled test with /api/practice-scheduler/complete-scheduled-test/{test_id}")
        print("=" * 60)
        
        # Step 1: Create scheduled test
        test_id = await self.create_scheduled_test_via_practice()
        if not test_id:
            self.log_test_result("End-to-End Flow", False, "Failed at step 1: Create scheduled test")
            return False
        
        # Step 2: Take scheduled test
        questions = await self.take_scheduled_test(test_id)
        if not questions:
            self.log_test_result("End-to-End Flow", False, "Failed at step 2: Take scheduled test")
            return False
        
        # Step 3: Submit scheduled test answers
        score = await self.submit_scheduled_test_answers(questions)
        if score is None:
            self.log_test_result("End-to-End Flow", False, "Failed at step 3: Submit scheduled test")
            return False
        
        # Step 4: Complete scheduled test
        success = await self.complete_scheduled_test(test_id, score)
        if not success:
            self.log_test_result("End-to-End Flow", False, "Failed at step 4: Complete scheduled test")
            return False
        
        self.log_test_result("End-to-End Flow", True, "All 4 steps completed successfully")
        return True
    
    async def test_various_score_values(self):
        """Test complete-scheduled-test endpoint with various score values (0-100)"""
        print(f"\n🎯 TESTING VARIOUS SCORE VALUES (0-100):")
        print("=" * 50)
        
        test_scores = [0.0, 25.5, 50.0, 75.5, 85.5, 95.0, 100.0]
        success_count = 0
        
        for score in test_scores:
            # Create a new scheduled test for each score
            test_id = await self.create_scheduled_test_via_practice()
            if test_id:
                success = await self.complete_scheduled_test(test_id, score)
                if success:
                    success_count += 1
            else:
                self.log_test_result(f"Score Test ({score})", False, "Could not create test")
        
        overall_success = success_count == len(test_scores)
        self.log_test_result("Various Score Values", overall_success, 
                           f"Passed {success_count}/{len(test_scores)} score tests")
        
        return overall_success
    
    async def test_specific_request_format(self):
        """Test the specific request format mentioned in the review"""
        print(f"\n📋 TESTING SPECIFIC REQUEST FORMAT:")
        print("=" * 50)
        print("Testing POST request body {\"score\": 85.5} as mentioned in review")
        
        # Create a test
        test_id = await self.create_scheduled_test_via_practice()
        if test_id:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test the EXACT format mentioned in the review
            completion_data = {"score": 85.5}
            
            async with self.session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                       json=completion_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("Specific Format Test", True, 
                                       f"200 OK - Request body {{\"score\": 85.5}} accepted")
                    return True
                elif response.status == 422:
                    error_text = await response.text()
                    self.log_test_result("Specific Format Test", False, 
                                       f"422 Error - Format not accepted: {error_text}")
                    return False
                else:
                    self.log_test_result("Specific Format Test", False, 
                                       f"Unexpected status: {response.status}")
                    return False
        else:
            self.log_test_result("Specific Format Test", False, "Could not create test")
            return False
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE SCHEDULED TEST SUBMISSION FIX VERIFICATION")
        print("=" * 80)
        print("Verifying the FINAL fix for scheduled practice test submission 422 error")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup
            if not await self.register_and_login_student():
                print("❌ Failed to setup test student - aborting tests")
                return
            
            # Test 1: Specific request format as mentioned in review
            await self.test_specific_request_format()
            
            # Test 2: End-to-end flow
            await self.test_end_to_end_flow()
            
            # Test 3: Various score values
            await self.test_various_score_values()
            
        finally:
            await self.cleanup_session()
        
        # Final results
        print(f"\n📊 COMPREHENSIVE TEST RESULTS:")
        print("=" * 50)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {(self.test_results['passed_tests']/self.test_results['total_tests']*100):.1f}%")
        
        # Check specific requirements
        print(f"\n✅ SPECIFIC REQUIREMENTS VERIFICATION:")
        print("=" * 50)
        
        requirements_met = 0
        total_requirements = 5
        
        # Requirement 1: POST request body {"score": XX} accepted
        specific_format_passed = any("Specific Format Test" in r['test'] and "✅ PASS" in r['status'] 
                                   for r in self.test_results['test_details'])
        if specific_format_passed:
            print("✅ 1. POST request body {\"score\": 85.5} returns 200 OK")
            requirements_met += 1
        else:
            print("❌ 1. POST request body {\"score\": 85.5} still has issues")
        
        # Requirement 2: No 422 errors
        no_422_errors = not any("422 Error" in r['details'] for r in self.test_results['test_details'])
        if no_422_errors:
            print("✅ 2. No 422 Unprocessable Entity errors")
            requirements_met += 1
        else:
            print("❌ 2. Still getting 422 Unprocessable Entity errors")
        
        # Requirement 3: End-to-end flow works
        end_to_end_passed = any("End-to-End Flow" in r['test'] and "✅ PASS" in r['status'] 
                               for r in self.test_results['test_details'])
        if end_to_end_passed:
            print("✅ 3. Complete end-to-end flow works")
            requirements_met += 1
        else:
            print("❌ 3. End-to-end flow has issues")
        
        # Requirement 4: Various score values work
        score_values_passed = any("Various Score Values" in r['test'] and "✅ PASS" in r['status'] 
                                 for r in self.test_results['test_details'])
        if score_values_passed:
            print("✅ 4. Various score values (0-100) work")
            requirements_met += 1
        else:
            print("❌ 4. Issues with various score values")
        
        # Requirement 5: Both endpoints work
        submit_passed = any("Submit Scheduled Test" in r['test'] and "✅ PASS" in r['status'] 
                           for r in self.test_results['test_details'])
        complete_passed = any("Complete Scheduled Test" in r['test'] and "✅ PASS" in r['status'] 
                             for r in self.test_results['test_details'])
        if submit_passed and complete_passed:
            print("✅ 5. Both /api/practice/submit-scheduled and /api/practice-scheduler/complete-scheduled-test work")
            requirements_met += 1
        else:
            print("❌ 5. Issues with one or both endpoints")
        
        print(f"\n🎯 REQUIREMENTS MET: {requirements_met}/{total_requirements}")
        
        if requirements_met == total_requirements:
            print("\n🎉 ALL REQUIREMENTS MET! THE FIX IS WORKING PERFECTLY!")
            print("✅ The scheduled test submission 422 error has been completely resolved")
            print("✅ Students can now successfully complete scheduled practice tests")
            print("✅ The CompleteTestRequest Pydantic model is working correctly")
        else:
            print(f"\n⚠️  {total_requirements - requirements_met} REQUIREMENTS NOT MET")
            print("❌ The fix may need additional work")

async def main():
    """Main test execution"""
    test_runner = ComprehensiveScheduledTestFixVerification()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
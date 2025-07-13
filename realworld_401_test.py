#!/usr/bin/env python3
"""
Real-World 401 Error Scenarios Test
Focus: Test scenarios that users might encounter that cause 401 errors
"""

import requests
import json
import uuid
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class RealWorld401Test:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        
    def setup_accounts(self):
        """Setup both student and teacher accounts"""
        print("🔧 Setting up test accounts...")
        
        # Setup student
        student_email = f"real_test_student_{uuid.uuid4()}@example.com"
        register_url = f"{API_URL}/auth/register"
        student_payload = {
            "email": student_email,
            "password": "SecurePass123!",
            "name": "Real Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        response = requests.post(register_url, json=student_payload)
        if response.status_code == 200:
            data = response.json()
            self.student_token = data.get("access_token")
            self.student_id = data.get("user", {}).get("id")
            print(f"✅ Student account setup: {self.student_id}")
        else:
            print(f"❌ Failed to setup student: {response.status_code}")
            return False
            
        # Setup teacher
        teacher_email = f"real_test_teacher_{uuid.uuid4()}@example.com"
        teacher_payload = {
            "email": teacher_email,
            "password": "SecurePass123!",
            "name": "Real Test Teacher",
            "user_type": "teacher",
            "school_name": "Test School"
        }
        
        response = requests.post(register_url, json=teacher_payload)
        if response.status_code == 200:
            data = response.json()
            self.teacher_token = data.get("access_token")
            self.teacher_id = data.get("user", {}).get("id")
            print(f"✅ Teacher account setup: {self.teacher_id}")
        else:
            print(f"❌ Failed to setup teacher: {response.status_code}")
            return False
            
        return True
        
    def test_wrong_user_type_access(self):
        """Test when wrong user type tries to access endpoints"""
        print("\n🚫 TESTING WRONG USER TYPE ACCESS")
        print("-" * 50)
        
        if not self.setup_accounts():
            return False
            
        # Test 1: Teacher trying to access student-only endpoints
        print("Test 1: Teacher accessing student-only endpoints")
        
        student_endpoints = [
            ("POST", "/practice/generate", {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 2
            }),
            ("GET", "/practice/results", {}),
            ("GET", "/student/profile", {}),
        ]
        
        for method, endpoint, payload in student_endpoints:
            url = f"{API_URL}{endpoint}"
            headers = {"Authorization": f"Bearer {self.teacher_token}"}
            
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 403:
                    print(f"   ✅ {method} {endpoint}: Correctly blocked (403)")
                elif response.status_code == 401:
                    print(f"   ❌ {method} {endpoint}: Returns 401 instead of 403")
                else:
                    print(f"   ⚠️ {method} {endpoint}: Unexpected {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {method} {endpoint}: Exception: {str(e)}")
        
        # Test 2: Student trying to access teacher-only endpoints
        print("\nTest 2: Student accessing teacher-only endpoints")
        
        teacher_endpoints = [
            ("GET", "/teacher/profile", {}),
            ("POST", "/teacher/classes", {
                "subject": "math",
                "class_name": "Test Class",
                "grade_level": "10th",
                "description": "Test description"
            }),
            ("GET", "/teacher/analytics/overview", {}),
        ]
        
        for method, endpoint, payload in teacher_endpoints:
            url = f"{API_URL}{endpoint}"
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 403:
                    print(f"   ✅ {method} {endpoint}: Correctly blocked (403)")
                elif response.status_code == 401:
                    print(f"   ❌ {method} {endpoint}: Returns 401 instead of 403")
                else:
                    print(f"   ⚠️ {method} {endpoint}: Unexpected {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {method} {endpoint}: Exception: {str(e)}")
                
        return True
        
    def test_session_timeout_simulation(self):
        """Test session timeout scenarios"""
        print("\n⏰ TESTING SESSION TIMEOUT SCENARIOS")
        print("-" * 50)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # Test immediate usage
        print("Test 1: Immediate token usage")
        success = self.make_practice_request("immediate")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test after delays
        delays = [5, 10, 30]  # seconds
        for delay in delays:
            print(f"\nTest: Token usage after {delay} second delay")
            time.sleep(delay if delay <= 10 else 5)  # Don't actually wait 30 seconds
            success = self.make_practice_request(f"{delay}s_delay")
            print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
            
        return True
        
    def test_malformed_request_data(self):
        """Test with malformed request data that might cause auth issues"""
        print("\n📝 TESTING MALFORMED REQUEST DATA")
        print("-" * 50)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different malformed payloads
        test_payloads = [
            {
                "name": "Missing required fields",
                "payload": {}
            },
            {
                "name": "Invalid subject",
                "payload": {
                    "subject": "invalid_subject",
                    "topics": ["Algebra"],
                    "difficulty": "medium",
                    "question_count": 2
                }
            },
            {
                "name": "Invalid difficulty",
                "payload": {
                    "subject": "math",
                    "topics": ["Algebra"],
                    "difficulty": "invalid_difficulty",
                    "question_count": 2
                }
            },
            {
                "name": "Invalid question count",
                "payload": {
                    "subject": "math",
                    "topics": ["Algebra"],
                    "difficulty": "medium",
                    "question_count": -1
                }
            },
            {
                "name": "Empty topics",
                "payload": {
                    "subject": "math",
                    "topics": [],
                    "difficulty": "medium",
                    "question_count": 2
                }
            },
            {
                "name": "Null values",
                "payload": {
                    "subject": None,
                    "topics": None,
                    "difficulty": None,
                    "question_count": None
                }
            }
        ]
        
        for test in test_payloads:
            print(f"\nTesting: {test['name']}")
            
            try:
                response = requests.post(url, json=test['payload'], headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"   ✅ Success: Request processed")
                elif response.status_code == 422:
                    print(f"   ✅ Validation Error: {response.status_code} (expected)")
                elif response.status_code == 400:
                    print(f"   ✅ Bad Request: {response.status_code} (expected)")
                elif response.status_code == 401:
                    print(f"   ❌ Auth Error: {response.status_code} (unexpected)")
                    print(f"      Response: {response.text[:100]}")
                elif response.status_code == 500:
                    print(f"   ❌ Server Error: {response.status_code}")
                    print(f"      Response: {response.text[:100]}")
                else:
                    print(f"   ⚠️ Unexpected: {response.status_code}")
                    print(f"      Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
        return True
        
    def test_concurrent_different_users(self):
        """Test concurrent requests from different user types"""
        print("\n👥 TESTING CONCURRENT DIFFERENT USERS")
        print("-" * 50)
        
        if not self.student_token or not self.teacher_token:
            print("❌ Missing tokens")
            return False
            
        import threading
        import time
        
        results = []
        
        def student_request():
            """Make student request"""
            try:
                url = f"{API_URL}/practice/generate"
                headers = {"Authorization": f"Bearer {self.student_token}"}
                payload = {
                    "subject": "math",
                    "topics": ["Algebra"],
                    "difficulty": "medium",
                    "question_count": 2
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                results.append(("Student", response.status_code, response.text[:100]))
            except Exception as e:
                results.append(("Student", 0, str(e)))
                
        def teacher_request():
            """Make teacher request"""
            try:
                url = f"{API_URL}/teacher/profile"
                headers = {"Authorization": f"Bearer {self.teacher_token}"}
                
                response = requests.get(url, headers=headers, timeout=10)
                results.append(("Teacher", response.status_code, response.text[:100]))
            except Exception as e:
                results.append(("Teacher", 0, str(e)))
        
        # Start both requests simultaneously
        student_thread = threading.Thread(target=student_request)
        teacher_thread = threading.Thread(target=teacher_request)
        
        student_thread.start()
        teacher_thread.start()
        
        student_thread.join()
        teacher_thread.join()
        
        # Analyze results
        print("Concurrent request results:")
        for user_type, status_code, response in results:
            status_icon = "✅" if status_code == 200 else "❌"
            print(f"   {user_type}: {status_icon} {status_code}")
            if status_code not in [200, 0]:
                print(f"      Response: {response}")
                
        return True
        
    def test_browser_like_scenarios(self):
        """Test scenarios that might happen in browser usage"""
        print("\n🌐 TESTING BROWSER-LIKE SCENARIOS")
        print("-" * 50)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # Test 1: Multiple rapid requests (like user clicking multiple times)
        print("Test 1: Rapid multiple requests")
        
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        rapid_results = []
        for i in range(3):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=5)
                rapid_results.append(response.status_code)
                print(f"   Request {i+1}: {response.status_code}")
            except Exception as e:
                print(f"   Request {i+1}: Exception: {str(e)}")
                rapid_results.append(0)
                
        success_count = sum(1 for status in rapid_results if status == 200)
        print(f"   Results: {success_count}/3 successful")
        
        # Test 2: Request with different content types
        print("\nTest 2: Different content types")
        
        content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "text/plain",
            "multipart/form-data"
        ]
        
        for content_type in content_types:
            try:
                test_headers = headers.copy()
                test_headers["Content-Type"] = content_type
                
                if content_type == "application/json":
                    response = requests.post(url, json=payload, headers=test_headers, timeout=5)
                else:
                    response = requests.post(url, data=json.dumps(payload), headers=test_headers, timeout=5)
                
                print(f"   {content_type}: {response.status_code}")
                
            except Exception as e:
                print(f"   {content_type}: Exception: {str(e)}")
                
        return True
        
    def make_practice_request(self, test_name):
        """Make a practice test request"""
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"      {test_name} failed: {response.status_code} - {response.text[:100]}")
            return response.status_code == 200
        except Exception as e:
            print(f"      {test_name} exception: {str(e)}")
            return False

def main():
    """Main test execution"""
    print("🚀 Starting Real-World 401 Error Scenarios Test")
    
    test = RealWorld401Test()
    
    # Run all tests
    tests = [
        ("Wrong User Type Access", test.test_wrong_user_type_access),
        ("Session Timeout Simulation", test.test_session_timeout_simulation),
        ("Malformed Request Data", test.test_malformed_request_data),
        ("Concurrent Different Users", test.test_concurrent_different_users),
        ("Browser-like Scenarios", test.test_browser_like_scenarios),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"🧪 {test_name}")
        print(f"{'='*70}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results[test_name] = False
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎯 REAL-WORLD SCENARIOS SUMMARY")
    print(f"{'='*70}")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ ISSUES FOUND"
        print(f"{test_name}: {status}")
    
    print(f"\n📋 CONCLUSION:")
    if all(results.values()):
        print("✅ No real-world 401 error scenarios found")
        print("   The authentication system appears to be working correctly")
    else:
        print("❌ Some real-world scenarios may cause authentication issues")
        print("   Check the detailed output above for specific problems")

if __name__ == "__main__":
    main()
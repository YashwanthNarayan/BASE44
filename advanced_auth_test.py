#!/usr/bin/env python3
"""
Advanced Authentication Edge Cases and Timing Issues Test
Focus: Identify specific scenarios that cause 401 errors
"""

import requests
import json
import time
import uuid
import os
import threading
import concurrent.futures
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class AdvancedAuthTest:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.student_email = None
        self.student_password = "SecurePass123!"
        
    def setup_student_account(self):
        """Setup a student account for testing"""
        print("🔧 Setting up student account...")
        
        self.student_email = f"edge_test_{uuid.uuid4()}@example.com"
        
        # Register
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": self.student_email,
            "password": self.student_password,
            "name": "Edge Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        response = requests.post(register_url, json=register_payload)
        if response.status_code == 200:
            data = response.json()
            self.student_token = data.get("access_token")
            self.student_id = data.get("user", {}).get("id")
            print(f"✅ Student account setup complete: {self.student_id}")
            return True
        else:
            print(f"❌ Failed to setup student account: {response.status_code}")
            return False
            
    def test_token_expiration_edge_cases(self):
        """Test token expiration scenarios"""
        print("\n⏰ TESTING TOKEN EXPIRATION EDGE CASES")
        print("-" * 50)
        
        if not self.setup_student_account():
            return False
            
        # Test 1: Use token immediately after creation
        print("Test 1: Immediate token usage")
        success = self.make_practice_test_request("immediate")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test 2: Use token after small delay
        print("Test 2: Token usage after 2 second delay")
        time.sleep(2)
        success = self.make_practice_test_request("2s_delay")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test 3: Use token after longer delay
        print("Test 3: Token usage after 5 second delay")
        time.sleep(3)  # Total 5 seconds
        success = self.make_practice_test_request("5s_delay")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
        
        return True
        
    def test_concurrent_requests(self):
        """Test concurrent practice test requests"""
        print("\n🔄 TESTING CONCURRENT REQUESTS")
        print("-" * 50)
        
        if not self.student_token:
            if not self.setup_student_account():
                return False
                
        def make_concurrent_request(request_id):
            """Make a practice test request"""
            try:
                url = f"{API_URL}/practice/generate"
                headers = {"Authorization": f"Bearer {self.student_token}"}
                payload = {
                    "subject": "math",
                    "topics": ["Algebra"],
                    "difficulty": "medium",
                    "question_count": 2
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_text": response.text[:200] if response.status_code != 200 else "Success"
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status_code": 0,
                    "success": False,
                    "response_text": str(e)
                }
        
        # Test with 5 concurrent requests
        print("Making 5 concurrent practice test requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        print(f"Results: {successful} successful, {failed} failed")
        
        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"   Request {result['request_id']}: {status} {result['status_code']} - {result['response_text'][:100]}")
            
        return failed == 0
        
    def test_malformed_tokens(self):
        """Test various malformed token scenarios"""
        print("\n🔍 TESTING MALFORMED TOKEN SCENARIOS")
        print("-" * 50)
        
        if not self.student_token:
            if not self.setup_student_account():
                return False
        
        # Test different malformed tokens
        malformed_tokens = [
            ("Empty token", ""),
            ("Invalid format", "invalid.token.here"),
            ("Missing parts", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
            ("Extra parts", f"{self.student_token}.extra"),
            ("Corrupted signature", self.student_token[:-10] + "corrupted"),
            ("Null token", None),
            ("Spaces in token", f" {self.student_token} "),
            ("Wrong case Bearer", f"bearer {self.student_token}"),
            ("Missing Bearer", self.student_token),
        ]
        
        url = f"{API_URL}/practice/generate"
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        results = []
        for test_name, token in malformed_tokens:
            try:
                if token is None:
                    headers = {}
                elif token == self.student_token:  # Missing Bearer test
                    headers = {"Authorization": token}
                elif test_name == "Wrong case Bearer":
                    headers = {"Authorization": token}
                else:
                    headers = {"Authorization": f"Bearer {token}"}
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                result = {
                    "test": test_name,
                    "status_code": response.status_code,
                    "expected_401": response.status_code == 401,
                    "got_500": response.status_code == 500,
                    "response": response.text[:100]
                }
                results.append(result)
                
                status_icon = "✅" if response.status_code == 401 else ("⚠️" if response.status_code == 500 else "❌")
                print(f"   {test_name}: {status_icon} {response.status_code}")
                
            except Exception as e:
                print(f"   {test_name}: ❌ Exception: {str(e)}")
                
        # Check for 500 errors (these indicate JWT validation issues)
        error_500_tests = [r for r in results if r["got_500"]]
        if error_500_tests:
            print(f"\n⚠️ FOUND {len(error_500_tests)} TESTS RETURNING 500 INSTEAD OF 401:")
            for test in error_500_tests:
                print(f"   - {test['test']}: {test['response']}")
                
        return len(error_500_tests) == 0
        
    def test_token_reuse_scenarios(self):
        """Test token reuse in different scenarios"""
        print("\n🔄 TESTING TOKEN REUSE SCENARIOS")
        print("-" * 50)
        
        if not self.student_token:
            if not self.setup_student_account():
                return False
        
        # Test 1: Multiple sequential requests with same token
        print("Test 1: Multiple sequential requests")
        for i in range(3):
            success = self.make_practice_test_request(f"sequential_{i}")
            print(f"   Request {i+1}: {'✅' if success else '❌'}")
            time.sleep(1)
            
        # Test 2: Login again and compare tokens
        print("\nTest 2: Re-login and token comparison")
        login_url = f"{API_URL}/auth/login"
        login_payload = {
            "email": self.student_email,
            "password": self.student_password
        }
        
        response = requests.post(login_url, json=login_payload)
        if response.status_code == 200:
            new_token = response.json().get("access_token")
            same_token = new_token == self.student_token
            print(f"   New login token same as original: {'Yes' if same_token else 'No'}")
            
            # Test both tokens
            old_success = self.make_practice_test_request("old_token", self.student_token)
            new_success = self.make_practice_test_request("new_token", new_token)
            
            print(f"   Old token works: {'✅' if old_success else '❌'}")
            print(f"   New token works: {'✅' if new_success else '❌'}")
            
        return True
        
    def test_different_endpoints_auth(self):
        """Test authentication across different endpoints"""
        print("\n🔗 TESTING AUTHENTICATION ACROSS ENDPOINTS")
        print("-" * 50)
        
        if not self.student_token:
            if not self.setup_student_account():
                return False
        
        endpoints = [
            ("GET", "/student/profile", {}),
            ("POST", "/practice/generate", {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 2
            }),
            ("GET", "/practice/results", {}),
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for method, endpoint, payload in endpoints:
            try:
                url = f"{API_URL}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"   {method} {endpoint}: {status_icon} {response.status_code}")
                
                if response.status_code == 401:
                    print(f"      401 Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   {method} {endpoint}: ❌ Exception: {str(e)}")
                
        return True
        
    def make_practice_test_request(self, test_name, token=None):
        """Make a practice test request"""
        if token is None:
            token = self.student_token
            
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"      {test_name} failed: {response.status_code} - {response.text[:100]}")
            return response.status_code == 200
        except Exception as e:
            print(f"      {test_name} exception: {str(e)}")
            return False

def main():
    """Main test execution"""
    print("🚀 Starting Advanced Authentication Edge Cases Test")
    
    test = AdvancedAuthTest()
    
    # Run all tests
    tests = [
        ("Token Expiration Edge Cases", test.test_token_expiration_edge_cases),
        ("Concurrent Requests", test.test_concurrent_requests),
        ("Malformed Tokens", test.test_malformed_tokens),
        ("Token Reuse Scenarios", test.test_token_reuse_scenarios),
        ("Different Endpoints Auth", test.test_different_endpoints_auth),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All advanced authentication tests passed!")
    else:
        print("⚠️ Some authentication issues found - check details above")

if __name__ == "__main__":
    main()
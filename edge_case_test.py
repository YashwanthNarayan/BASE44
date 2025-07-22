#!/usr/bin/env python3
"""
EDGE CASE TESTING: Practice API Endpoints
Testing various edge cases that might cause 500 errors:
1. Invalid authentication tokens
2. Non-existent attempt IDs
3. Invalid subject names
4. Empty database scenarios
5. Malformed requests
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

print(f"🔍 EDGE CASE TESTING: Practice API Endpoints")
print(f"Using API URL: {API_URL}")
print("=" * 80)

class EdgeCaseTester:
    def __init__(self):
        self.valid_student_token = None
        self.student_id = None
        
    def setup_valid_student(self):
        """Setup a valid student for comparison tests"""
        print("\n🔍 Setting up valid student for comparison...")
        
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"edge_test_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Edge Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            if response.status_code == 200:
                data = response.json()
                self.valid_student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Valid student setup: {self.student_id}")
                return True
            else:
                print(f"❌ Failed to setup valid student: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error setting up valid student: {str(e)}")
            return False
    
    def test_invalid_authentication(self):
        """Test endpoints with invalid authentication"""
        print("\n🔍 EDGE CASE 1: Invalid Authentication Tokens")
        
        test_cases = [
            ("No token", {}),
            ("Invalid token", {"Authorization": "Bearer invalid.token.here"}),
            ("Malformed token", {"Authorization": "Bearer malformed"}),
            ("Wrong scheme", {"Authorization": "Basic invalid"}),
            ("Empty token", {"Authorization": "Bearer "}),
        ]
        
        endpoints = [
            f"{API_URL}/practice/results",
            f"{API_URL}/practice/stats/math",
            f"{API_URL}/practice/results/fake-id"
        ]
        
        for case_name, headers in test_cases:
            print(f"\n  Testing: {case_name}")
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers)
                    print(f"    {endpoint.split('/')[-2:]}: {response.status_code}")
                    
                    if response.status_code == 500:
                        print(f"    🚨 500 ERROR FOUND: {endpoint}")
                        print(f"    Response: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"    ❌ Exception: {str(e)}")
    
    def test_nonexistent_resources(self):
        """Test endpoints with non-existent resources"""
        print("\n🔍 EDGE CASE 2: Non-existent Resources")
        
        if not self.valid_student_token:
            print("❌ No valid student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.valid_student_token}"}
        
        test_cases = [
            ("Non-existent attempt ID", f"{API_URL}/practice/results/non-existent-id"),
            ("Invalid UUID format", f"{API_URL}/practice/results/invalid-uuid-format"),
            ("Empty attempt ID", f"{API_URL}/practice/results/"),
            ("Non-existent subject", f"{API_URL}/practice/stats/nonexistentsubject"),
            ("Empty subject", f"{API_URL}/practice/stats/"),
            ("Special characters in subject", f"{API_URL}/practice/stats/math@#$%"),
        ]
        
        for case_name, endpoint in test_cases:
            try:
                print(f"\n  Testing: {case_name}")
                response = requests.get(endpoint, headers=headers)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"    🚨 500 ERROR FOUND: {endpoint}")
                    print(f"    Response: {response.text[:200]}")
                elif response.status_code == 404:
                    print(f"    ✅ Proper 404 response")
                elif response.status_code == 200:
                    print(f"    ✅ 200 OK (empty results expected)")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
    
    def test_malformed_requests(self):
        """Test endpoints with malformed requests"""
        print("\n🔍 EDGE CASE 3: Malformed Requests")
        
        if not self.valid_student_token:
            print("❌ No valid student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.valid_student_token}"}
        
        # Test with various malformed query parameters
        malformed_endpoints = [
            f"{API_URL}/practice/results?invalid=param",
            f"{API_URL}/practice/results?subject=",
            f"{API_URL}/practice/stats/math?extra=param",
            f"{API_URL}/practice/results/valid-id?malformed=query",
        ]
        
        for endpoint in malformed_endpoints:
            try:
                print(f"\n  Testing malformed request: {endpoint.split('?')[1] if '?' in endpoint else 'base endpoint'}")
                response = requests.get(endpoint, headers=headers)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"    🚨 500 ERROR FOUND: {endpoint}")
                    print(f"    Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
    
    def test_database_edge_cases(self):
        """Test scenarios that might cause database-related 500 errors"""
        print("\n🔍 EDGE CASE 4: Database Edge Cases")
        
        if not self.valid_student_token:
            print("❌ No valid student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.valid_student_token}"}
        
        # Test with a fresh student who has no practice test data
        print("\n  Testing with student who has no practice test data:")
        
        endpoints = [
            f"{API_URL}/practice/results",
            f"{API_URL}/practice/stats/math",
            f"{API_URL}/practice/stats/physics",
            f"{API_URL}/practice/stats/chemistry",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers)
                print(f"    {endpoint.split('/')[-1]}: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"    🚨 500 ERROR FOUND: {endpoint}")
                    print(f"    Response: {response.text[:200]}")
                elif response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"    ✅ Empty list returned: {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"    ✅ Empty stats returned: {data.get('total_tests', 'N/A')} tests")
                        
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
    
    def test_concurrent_requests(self):
        """Test concurrent requests that might cause race conditions"""
        print("\n🔍 EDGE CASE 5: Concurrent Requests")
        
        if not self.valid_student_token:
            print("❌ No valid student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.valid_student_token}"}
        
        import threading
        import time
        
        results = []
        
        def make_request(endpoint, request_id):
            try:
                response = requests.get(endpoint, headers=headers)
                results.append((request_id, response.status_code, endpoint))
            except Exception as e:
                results.append((request_id, "ERROR", str(e)))
        
        # Make 5 concurrent requests to each endpoint
        threads = []
        endpoints = [
            f"{API_URL}/practice/results",
            f"{API_URL}/practice/stats/math",
        ]
        
        print("  Making 10 concurrent requests...")
        for i in range(5):
            for endpoint in endpoints:
                thread = threading.Thread(target=make_request, args=(endpoint, f"req_{i}"))
                threads.append(thread)
                thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        error_count = 0
        success_count = 0
        
        for request_id, status, endpoint in results:
            if status == 500:
                print(f"    🚨 500 ERROR in concurrent request {request_id}: {endpoint}")
                error_count += 1
            elif status == 200:
                success_count += 1
            elif status == "ERROR":
                print(f"    ❌ Exception in concurrent request {request_id}: {endpoint}")
                error_count += 1
        
        print(f"  Concurrent test results: {success_count} success, {error_count} errors")
    
    def run_all_edge_case_tests(self):
        """Run all edge case tests"""
        print("🚨 EDGE CASE TESTING: Practice API Endpoints")
        print("Testing various scenarios that might cause 500 Internal Server Errors")
        print("=" * 80)
        
        # Setup
        if not self.setup_valid_student():
            print("❌ Cannot proceed without valid student setup")
            return
        
        # Run all edge case tests
        self.test_invalid_authentication()
        self.test_nonexistent_resources()
        self.test_malformed_requests()
        self.test_database_edge_cases()
        self.test_concurrent_requests()
        
        print("\n" + "=" * 80)
        print("🔍 EDGE CASE TESTING COMPLETED")
        print("If no 500 errors were found above, the endpoints are robust against common edge cases.")
        print("=" * 80)

if __name__ == "__main__":
    tester = EdgeCaseTester()
    tester.run_all_edge_case_tests()
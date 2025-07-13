#!/usr/bin/env python3
"""
JWT Token Validation Issue Investigation
Focus: Test the specific JWT validation issue mentioned in test_result.md
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class JWTValidationTest:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        
    def setup_student_account(self):
        """Setup a student account for testing"""
        print("🔧 Setting up student account...")
        
        student_email = f"jwt_test_{uuid.uuid4()}@example.com"
        
        # Register
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": student_email,
            "password": "SecurePass123!",
            "name": "JWT Test Student",
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
            
    def test_jwt_validation_issue(self):
        """Test the specific JWT validation issue from test_result.md"""
        print("\n🔍 TESTING JWT VALIDATION ISSUE")
        print("-" * 50)
        print("Issue: Invalid tokens return 500 Internal Server Error instead of 401 Unauthorized")
        
        if not self.setup_student_account():
            return False
            
        # Test cases that should return 401 but might return 500
        test_cases = [
            {
                "name": "Completely invalid token",
                "token": "completely.invalid.token",
                "expected": 401
            },
            {
                "name": "Malformed JWT (missing signature)",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0",
                "expected": 401
            },
            {
                "name": "Invalid signature",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid_signature",
                "expected": 401
            },
            {
                "name": "Expired token (fake)",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNTAwMDAwMDAwfQ.fake_signature",
                "expected": 401
            },
            {
                "name": "Random string",
                "token": "this_is_not_a_jwt_token_at_all",
                "expected": 401
            },
            {
                "name": "Empty token",
                "token": "",
                "expected": 401
            },
            {
                "name": "Only dots",
                "token": "...",
                "expected": 401
            }
        ]
        
        url = f"{API_URL}/practice/generate"
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        issues_found = []
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            headers = {"Authorization": f"Bearer {test_case['token']}"}
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Expected: {test_case['expected']}")
                
                if response.status_code == test_case['expected']:
                    print(f"   ✅ CORRECT: Returns {response.status_code} as expected")
                elif response.status_code == 500:
                    print(f"   ❌ ISSUE FOUND: Returns 500 instead of {test_case['expected']}")
                    print(f"   Response: {response.text[:200]}")
                    issues_found.append({
                        "test": test_case['name'],
                        "expected": test_case['expected'],
                        "actual": response.status_code,
                        "response": response.text
                    })
                else:
                    print(f"   ⚠️ UNEXPECTED: Returns {response.status_code} instead of {test_case['expected']}")
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                issues_found.append({
                    "test": test_case['name'],
                    "expected": test_case['expected'],
                    "actual": "Exception",
                    "response": str(e)
                })
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 JWT VALIDATION ISSUE SUMMARY")
        print(f"{'='*60}")
        
        if issues_found:
            print(f"❌ FOUND {len(issues_found)} JWT VALIDATION ISSUES:")
            for issue in issues_found:
                print(f"   - {issue['test']}: Expected {issue['expected']}, got {issue['actual']}")
                if issue['actual'] == 500:
                    print(f"     Response: {issue['response'][:100]}...")
        else:
            print("✅ NO JWT VALIDATION ISSUES FOUND - All invalid tokens properly return 401")
            
        return len(issues_found) == 0
        
    def test_missing_token_scenarios(self):
        """Test missing token scenarios"""
        print("\n🔍 TESTING MISSING TOKEN SCENARIOS")
        print("-" * 50)
        
        url = f"{API_URL}/practice/generate"
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        test_cases = [
            {
                "name": "No Authorization header",
                "headers": {},
                "expected": [401, 403]  # Either is acceptable
            },
            {
                "name": "Empty Authorization header",
                "headers": {"Authorization": ""},
                "expected": [401, 403]
            },
            {
                "name": "Authorization header with only 'Bearer'",
                "headers": {"Authorization": "Bearer"},
                "expected": [401, 403]
            },
            {
                "name": "Authorization header with 'Bearer '",
                "headers": {"Authorization": "Bearer "},
                "expected": [401, 403]
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            try:
                response = requests.post(url, json=payload, headers=test_case['headers'], timeout=10)
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Expected: {test_case['expected']}")
                
                if response.status_code in test_case['expected']:
                    print(f"   ✅ CORRECT: Returns {response.status_code} as expected")
                else:
                    print(f"   ❌ UNEXPECTED: Returns {response.status_code} instead of {test_case['expected']}")
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                
        return True
        
    def test_valid_token_edge_cases(self):
        """Test edge cases with valid tokens"""
        print("\n🔍 TESTING VALID TOKEN EDGE CASES")
        print("-" * 50)
        
        if not self.student_token:
            print("❌ No valid token available")
            return False
            
        url = f"{API_URL}/practice/generate"
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        test_cases = [
            {
                "name": "Standard Bearer token",
                "headers": {"Authorization": f"Bearer {self.student_token}"}
            },
            {
                "name": "Bearer with extra spaces",
                "headers": {"Authorization": f"Bearer  {self.student_token}"}
            },
            {
                "name": "bearer (lowercase)",
                "headers": {"Authorization": f"bearer {self.student_token}"}
            },
            {
                "name": "BEARER (uppercase)",
                "headers": {"Authorization": f"BEARER {self.student_token}"}
            },
            {
                "name": "Token with trailing space",
                "headers": {"Authorization": f"Bearer {self.student_token} "}
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            try:
                response = requests.post(url, json=payload, headers=test_case['headers'], timeout=10)
                
                print(f"   Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS: Token accepted")
                elif response.status_code == 401:
                    print(f"   ❌ REJECTED: Token not accepted (401)")
                elif response.status_code == 403:
                    print(f"   ❌ REJECTED: Token not accepted (403)")
                else:
                    print(f"   ⚠️ UNEXPECTED: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ EXCEPTION: {str(e)}")
                
        return True

def main():
    """Main test execution"""
    print("🚀 Starting JWT Token Validation Issue Investigation")
    
    test = JWTValidationTest()
    
    # Run all tests
    tests = [
        ("JWT Validation Issue", test.test_jwt_validation_issue),
        ("Missing Token Scenarios", test.test_missing_token_scenarios),
        ("Valid Token Edge Cases", test.test_valid_token_edge_cases),
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
    print("🎯 FINAL INVESTIGATION SUMMARY")
    print(f"{'='*70}")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ ISSUES FOUND"
        print(f"{test_name}: {status}")
    
    print(f"\n📋 CONCLUSION:")
    if all(results.values()):
        print("✅ JWT validation is working correctly - no 500 errors found")
    else:
        print("❌ JWT validation issues confirmed - some invalid tokens return 500 instead of 401")
        print("   This is the issue mentioned in test_result.md that needs to be fixed")

if __name__ == "__main__":
    main()
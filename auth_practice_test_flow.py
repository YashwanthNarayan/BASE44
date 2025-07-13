#!/usr/bin/env python3
"""
Comprehensive Authentication and Practice Test Generation Flow Test
Focus: Identify root cause of 401 errors when generating practice tests
"""

import requests
import json
import time
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class AuthPracticeTestFlow:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.student_email = None
        self.student_password = "SecurePass123!"
        
    def test_complete_flow(self):
        """Test the complete authentication and practice test generation flow"""
        print("\n" + "="*80)
        print("🎯 AUTHENTICATION & PRACTICE TEST GENERATION FLOW TEST")
        print("="*80)
        
        # Step 1: Register a new student account
        if not self.register_student():
            print("❌ CRITICAL: Student registration failed - cannot proceed")
            return False
            
        # Step 2: Login with the student account
        if not self.login_student():
            print("❌ CRITICAL: Student login failed - cannot proceed")
            return False
            
        # Step 3: Verify JWT token structure
        if not self.verify_jwt_token():
            print("❌ CRITICAL: JWT token verification failed")
            return False
            
        # Step 4: Test token validation with protected endpoint
        if not self.test_token_validation():
            print("❌ CRITICAL: Token validation failed")
            return False
            
        # Step 5: Generate practice test with JWT token
        if not self.generate_practice_test():
            print("❌ CRITICAL: Practice test generation failed")
            return False
            
        print("\n✅ COMPLETE FLOW TEST PASSED - All authentication and practice test generation working correctly!")
        return True
        
    def register_student(self):
        """Register a new student account"""
        print("\n📝 STEP 1: Student Registration")
        print("-" * 40)
        
        self.student_email = f"test_student_{uuid.uuid4()}@example.com"
        url = f"{API_URL}/auth/register"
        payload = {
            "email": self.student_email,
            "password": self.student_password,
            "name": "Ravi Kumar",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            print(f"🔄 Registering student: {self.student_email}")
            response = requests.post(url, json=payload, timeout=30)
            print(f"📊 Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                
                print(f"✅ Registration successful!")
                print(f"   Student ID: {self.student_id}")
                print(f"   Token received: {'Yes' if self.student_token else 'No'}")
                print(f"   Token length: {len(self.student_token) if self.student_token else 0}")
                
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
            
    def login_student(self):
        """Login with the student account"""
        print("\n🔐 STEP 2: Student Login")
        print("-" * 40)
        
        url = f"{API_URL}/auth/login"
        payload = {
            "email": self.student_email,
            "password": self.student_password
        }
        
        try:
            print(f"🔄 Logging in student: {self.student_email}")
            response = requests.post(url, json=payload, timeout=30)
            print(f"📊 Login Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                login_token = data.get("access_token")
                login_user_id = data.get("user", {}).get("id")
                
                print(f"✅ Login successful!")
                print(f"   User ID: {login_user_id}")
                print(f"   Token received: {'Yes' if login_token else 'No'}")
                print(f"   Token matches registration: {'Yes' if login_token == self.student_token else 'No'}")
                
                # Use login token (should be same as registration token)
                if login_token:
                    self.student_token = login_token
                    
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
            
    def verify_jwt_token(self):
        """Verify JWT token structure and content"""
        print("\n🔍 STEP 3: JWT Token Verification")
        print("-" * 40)
        
        if not self.student_token:
            print("❌ No token available for verification")
            return False
            
        try:
            # Decode JWT token (without verification for inspection)
            import jwt
            
            # Split token to inspect header and payload
            parts = self.student_token.split('.')
            if len(parts) != 3:
                print(f"❌ Invalid JWT format - expected 3 parts, got {len(parts)}")
                return False
                
            print(f"✅ JWT token format valid (3 parts)")
            print(f"   Token preview: {self.student_token[:50]}...")
            
            # Decode payload without verification (for inspection only)
            import base64
            import json
            
            # Add padding if needed
            payload_part = parts[1]
            payload_part += '=' * (4 - len(payload_part) % 4)
            
            try:
                decoded_payload = base64.b64decode(payload_part)
                payload_data = json.loads(decoded_payload)
                
                print(f"✅ JWT payload decoded successfully")
                print(f"   User ID (sub): {payload_data.get('sub')}")
                print(f"   User Type: {payload_data.get('user_type')}")
                print(f"   Expiration: {payload_data.get('exp')}")
                
                # Verify required fields
                if not payload_data.get('sub'):
                    print("❌ Missing 'sub' field in JWT payload")
                    return False
                    
                if payload_data.get('user_type') != 'student':
                    print(f"❌ Wrong user_type: expected 'student', got '{payload_data.get('user_type')}'")
                    return False
                    
                return True
                
            except Exception as e:
                print(f"❌ Failed to decode JWT payload: {str(e)}")
                return False
                
        except Exception as e:
            print(f"❌ JWT verification error: {str(e)}")
            return False
            
    def test_token_validation(self):
        """Test token validation with a protected endpoint"""
        print("\n🛡️ STEP 4: Token Validation Test")
        print("-" * 40)
        
        if not self.student_token:
            print("❌ No token available for validation")
            return False
            
        # Test with student profile endpoint
        url = f"{API_URL}/student/profile"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            print(f"🔄 Testing token with protected endpoint: /student/profile")
            response = requests.get(url, headers=headers, timeout=30)
            print(f"📊 Token Validation Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token validation successful!")
                print(f"   Profile retrieved for: {data.get('name')}")
                print(f"   User ID: {data.get('user_id')}")
                return True
            elif response.status_code == 401:
                print(f"❌ Token validation failed: 401 Unauthorized")
                print(f"   Response: {response.text}")
                return False
            elif response.status_code == 403:
                print(f"❌ Token validation failed: 403 Forbidden")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token validation error: {str(e)}")
            return False
            
    def generate_practice_test(self):
        """Generate practice test using JWT token"""
        print("\n📚 STEP 5: Practice Test Generation")
        print("-" * 40)
        
        if not self.student_token:
            print("❌ No token available for practice test generation")
            return False
            
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": "math",
            "topics": ["Algebra", "Geometry"],
            "difficulty": "medium",
            "question_count": 3,
            "question_types": ["mcq", "short_answer"]
        }
        
        try:
            print(f"🔄 Generating practice test...")
            print(f"   Subject: {payload['subject']}")
            print(f"   Topics: {payload['topics']}")
            print(f"   Difficulty: {payload['difficulty']}")
            print(f"   Question Count: {payload['question_count']}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            print(f"📊 Practice Test Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                print(f"✅ Practice test generation successful!")
                print(f"   Questions generated: {len(questions)}")
                print(f"   Subject: {data.get('subject')}")
                print(f"   Difficulty: {data.get('difficulty')}")
                
                # Show first question as example
                if questions:
                    first_q = questions[0]
                    print(f"   Sample question: {first_q.get('question_text', '')[:100]}...")
                    
                return True
            elif response.status_code == 401:
                print(f"❌ Practice test generation failed: 401 Unauthorized")
                print(f"   This is the main issue we're investigating!")
                print(f"   Response: {response.text}")
                
                # Additional debugging for 401 errors
                self.debug_401_error(response)
                return False
            elif response.status_code == 403:
                print(f"❌ Practice test generation failed: 403 Forbidden")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"❌ Practice test generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Practice test generation error: {str(e)}")
            return False
            
    def debug_401_error(self, response):
        """Debug 401 error in detail"""
        print("\n🔍 DEBUGGING 401 ERROR")
        print("-" * 30)
        
        try:
            # Check response headers
            print("Response Headers:")
            for header, value in response.headers.items():
                print(f"   {header}: {value}")
                
            # Check response body
            try:
                error_data = response.json()
                print(f"Error Detail: {error_data.get('detail', 'No detail provided')}")
            except:
                print(f"Raw Response: {response.text}")
                
            # Test token format
            print(f"\nToken Analysis:")
            print(f"   Token starts with 'Bearer ': {'Yes' if self.student_token.startswith('Bearer ') else 'No'}")
            print(f"   Token length: {len(self.student_token)}")
            print(f"   Token format (parts): {len(self.student_token.split('.'))}")
            
        except Exception as e:
            print(f"Debug error: {str(e)}")
            
    def test_different_auth_formats(self):
        """Test different authentication header formats"""
        print("\n🧪 TESTING DIFFERENT AUTH FORMATS")
        print("-" * 40)
        
        if not self.student_token:
            print("❌ No token available")
            return
            
        url = f"{API_URL}/practice/generate"
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        # Test different header formats
        auth_formats = [
            {"Authorization": f"Bearer {self.student_token}"},
            {"Authorization": f"bearer {self.student_token}"},
            {"authorization": f"Bearer {self.student_token}"},
            {"X-Auth-Token": self.student_token},
            {"Token": self.student_token}
        ]
        
        for i, headers in enumerate(auth_formats):
            try:
                print(f"Testing format #{i+1}: {list(headers.keys())[0]}")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                print(f"   Result: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS with format #{i+1}")
                    break
                    
            except Exception as e:
                print(f"   Error: {str(e)}")

def main():
    """Main test execution"""
    print("🚀 Starting Authentication & Practice Test Generation Flow Test")
    
    # Test complete flow
    flow_test = AuthPracticeTestFlow()
    success = flow_test.test_complete_flow()
    
    if not success:
        print("\n🔧 ADDITIONAL DEBUGGING")
        print("=" * 50)
        flow_test.test_different_auth_formats()
    
    print("\n" + "="*80)
    if success:
        print("🎉 FINAL RESULT: AUTHENTICATION & PRACTICE TEST FLOW WORKING CORRECTLY")
    else:
        print("❌ FINAL RESULT: AUTHENTICATION OR PRACTICE TEST ISSUES IDENTIFIED")
        print("   Check the detailed output above for specific error causes")
    print("="*80)

if __name__ == "__main__":
    main()
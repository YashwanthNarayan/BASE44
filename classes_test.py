#!/usr/bin/env python3
"""
Classes Functionality Test for ClassesComponent_Modern.js
Testing the class-related API endpoints as requested in the review.
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

# Add /api prefix to the backend URL
API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class ClassesFunctionalityTest:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.join_code = None
        
    def register_and_login_student(self):
        """Register and login a student for testing"""
        print("\n🔍 Setting up Student Account...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        student_email = f"classes_student_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": student_email,
            "password": "TestPass123!",
            "name": "Arjun Patel",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Student Registration: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student registered: {self.student_id}")
                return True
            else:
                print(f"❌ Student registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Student registration error: {str(e)}")
            return False
    
    def register_and_login_teacher(self):
        """Register and login a teacher for testing"""
        print("\n🔍 Setting up Teacher Account...")
        
        # Register teacher
        register_url = f"{API_URL}/auth/register"
        teacher_email = f"classes_teacher_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": teacher_email,
            "password": "TeacherPass123!",
            "name": "Dr. Priya Sharma",
            "user_type": "teacher",
            "school_name": "Delhi Public School"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Teacher Registration: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"✅ Teacher registered: {self.teacher_id}")
                return True
            else:
                print(f"❌ Teacher registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Teacher registration error: {str(e)}")
            return False
    
    def create_test_class(self):
        """Create a test class using teacher account"""
        print("\n🔍 Creating Test Class...")
        
        if not self.teacher_token:
            print("❌ Teacher token not available")
            return False
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        payload = {
            "class_name": "Advanced Mathematics",
            "subject": "math",
            "description": "Advanced mathematics class covering algebra, geometry, and calculus concepts for grade 10 students"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Create Class Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.class_id = data.get("class_id")
                self.join_code = data.get("join_code")
                
                print(f"✅ Class created successfully!")
                print(f"   Class ID: {self.class_id}")
                print(f"   Join Code: {self.join_code}")
                print(f"   Class Name: {payload['class_name']}")
                print(f"   Subject: {payload['subject']}")
                return True
            else:
                print(f"❌ Class creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Class creation error: {str(e)}")
            return False
    
    def test_student_joined_classes_empty(self):
        """Test GET /api/student/joined-classes when student hasn't joined any classes"""
        print("\n🔍 Testing GET /api/student/joined-classes (Empty State)...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/joined-classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response structure
                if isinstance(data, list):
                    print(f"✅ Response is array format: {len(data)} classes")
                    if len(data) == 0:
                        print("✅ Empty state correctly returned - student hasn't joined any classes yet")
                    return True
                else:
                    print(f"❌ Expected array, got: {type(data)}")
                    return False
            else:
                print(f"❌ Request failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_student_join_class_valid_code(self):
        """Test POST /api/student/join-class with valid join code"""
        print("\n🔍 Testing POST /api/student/join-class (Valid Join Code)...")
        
        if not self.student_token or not self.join_code:
            print("❌ Student token or join code not available")
            return False
        
        url = f"{API_URL}/student/join-class"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "join_code": self.join_code
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response structure
                expected_fields = ["message", "class_name", "subject", "class_id"]
                for field in expected_fields:
                    if field in data:
                        print(f"✅ Field '{field}': {data[field]}")
                    else:
                        print(f"❌ Missing field: {field}")
                        return False
                
                # Verify the class details match what we created
                if data.get("class_id") == self.class_id:
                    print("✅ Class ID matches created class")
                else:
                    print(f"❌ Class ID mismatch: expected {self.class_id}, got {data.get('class_id')}")
                    return False
                
                print("✅ Student successfully joined class with valid join code")
                return True
            else:
                print(f"❌ Request failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_student_join_class_invalid_code(self):
        """Test POST /api/student/join-class with invalid join code"""
        print("\n🔍 Testing POST /api/student/join-class (Invalid Join Code)...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/join-class"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "join_code": "INVALID123"  # Invalid join code
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 404:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                if "detail" in data and "Invalid join code" in data["detail"]:
                    print("✅ Correctly returned 404 with appropriate error message for invalid join code")
                    return True
                else:
                    print(f"❌ Unexpected error message: {data.get('detail')}")
                    return False
            else:
                print(f"❌ Expected 404, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_student_joined_classes_populated(self):
        """Test GET /api/student/joined-classes after joining a class"""
        print("\n🔍 Testing GET /api/student/joined-classes (After Joining Class)...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/joined-classes"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response structure
                if isinstance(data, list):
                    print(f"✅ Response is array format: {len(data)} classes")
                    
                    if len(data) > 0:
                        # Check the first class details
                        first_class = data[0]
                        expected_fields = [
                            "class_id", "class_name", "subject", "description", 
                            "join_code", "teacher_id", "created_at", "student_count"
                        ]
                        
                        print("\n📋 Verifying class data structure:")
                        for field in expected_fields:
                            if field in first_class:
                                print(f"✅ Field '{field}': {first_class[field]}")
                            else:
                                print(f"❌ Missing field: {field}")
                                return False
                        
                        # Verify this is the class we joined
                        if first_class.get("class_id") == self.class_id:
                            print("✅ Returned class matches the one we joined")
                        else:
                            print(f"❌ Class ID mismatch: expected {self.class_id}, got {first_class.get('class_id')}")
                            return False
                        
                        # Verify student count increased
                        if first_class.get("student_count", 0) >= 1:
                            print(f"✅ Student count shows {first_class.get('student_count')} students")
                        else:
                            print(f"❌ Student count should be at least 1, got {first_class.get('student_count')}")
                            return False
                        
                        print("✅ Student joined classes data structure verified successfully")
                        return True
                    else:
                        print("❌ Expected at least one class after joining, got empty array")
                        return False
                else:
                    print(f"❌ Expected array, got: {type(data)}")
                    return False
            else:
                print(f"❌ Request failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_authentication_requirements(self):
        """Test that endpoints require proper JWT authentication"""
        print("\n🔍 Testing Authentication Requirements...")
        
        # Test joined-classes without auth
        url = f"{API_URL}/student/joined-classes"
        try:
            response = requests.get(url)  # No auth header
            print(f"GET joined-classes without auth: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print("✅ Correctly rejected request without authentication")
            else:
                print(f"❌ Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing no auth: {str(e)}")
            return False
        
        # Test join-class without auth
        url = f"{API_URL}/student/join-class"
        payload = {"join_code": "TEST123"}
        try:
            response = requests.post(url, json=payload)  # No auth header
            print(f"POST join-class without auth: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print("✅ Correctly rejected request without authentication")
            else:
                print(f"❌ Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing no auth: {str(e)}")
            return False
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        url = f"{API_URL}/student/joined-classes"
        try:
            response = requests.get(url, headers=invalid_headers)
            print(f"GET joined-classes with invalid token: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print("✅ Correctly rejected request with invalid token")
                return True
            else:
                print(f"❌ Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing invalid token: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all class functionality tests"""
        print("🚀 Starting Classes Functionality Test Suite")
        print("=" * 60)
        
        test_results = []
        
        # Setup phase
        print("\n📋 SETUP PHASE")
        if not self.register_and_login_student():
            print("❌ Failed to setup student account")
            return False
        
        if not self.register_and_login_teacher():
            print("❌ Failed to setup teacher account")
            return False
        
        if not self.create_test_class():
            print("❌ Failed to create test class")
            return False
        
        # Test phase
        print("\n📋 TESTING PHASE")
        
        # Test 1: Empty joined classes
        test_results.append(("Empty Joined Classes", self.test_student_joined_classes_empty()))
        
        # Test 2: Authentication requirements
        test_results.append(("Authentication Requirements", self.test_authentication_requirements()))
        
        # Test 3: Invalid join code
        test_results.append(("Invalid Join Code", self.test_student_join_class_invalid_code()))
        
        # Test 4: Valid join code
        test_results.append(("Valid Join Code", self.test_student_join_class_valid_code()))
        
        # Test 5: Populated joined classes
        test_results.append(("Populated Joined Classes", self.test_student_joined_classes_populated()))
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📈 Overall Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Classes functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {failed} test(s) failed. Classes functionality needs attention.")
            return False

def main():
    """Main function to run the classes functionality test"""
    tester = ClassesFunctionalityTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Classes functionality test completed successfully!")
        exit(0)
    else:
        print("\n❌ Classes functionality test completed with failures!")
        exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
STUDENT JOIN CLASS DEBUG TEST
=============================

This test specifically investigates the issue where students are getting "code is incorrect" 
errors when trying to join classes. It follows the exact user workflow to identify the root cause.

Focus Areas:
1. Create real teacher account and class to get actual join code
2. Check exact database state and field values
3. Test exact join process that real users go through
4. Debug case sensitivity, whitespace, and formatting issues
5. Verify join code format and generation
"""

import requests
import json
import uuid
import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class StudentJoinClassDebugger:
    def __init__(self):
        self.teacher_token = None
        self.student_token = None
        self.teacher_id = None
        self.student_id = None
        self.class_id = None
        self.join_code = None
        self.teacher_email = None
        self.student_email = None
        
    def debug_student_join_class_issue(self):
        """Main debugging function that follows the exact user workflow"""
        print("🔍 DEBUGGING STUDENT JOIN CLASS ISSUE")
        print("=" * 60)
        
        # Step 1: Create real teacher account
        print("\n📝 STEP 1: Creating Real Teacher Account...")
        if not self.create_teacher_account():
            print("❌ Failed to create teacher account. Cannot proceed.")
            return False
            
        # Step 2: Create a class and capture exact join code
        print("\n📝 STEP 2: Creating Class and Capturing Join Code...")
        if not self.create_class_and_capture_join_code():
            print("❌ Failed to create class. Cannot proceed.")
            return False
            
        # Step 3: Check database state
        print("\n📝 STEP 3: Checking Database State...")
        self.check_database_state()
        
        # Step 4: Create real student account
        print("\n📝 STEP 4: Creating Real Student Account...")
        if not self.create_student_account():
            print("❌ Failed to create student account. Cannot proceed.")
            return False
            
        # Step 5: Test exact join process
        print("\n📝 STEP 5: Testing Exact Join Process...")
        self.test_join_process_variations()
        
        # Step 6: Debug specific issues
        print("\n📝 STEP 6: Debugging Specific Issues...")
        self.debug_specific_issues()
        
        return True
        
    def create_teacher_account(self):
        """Create a real teacher account with realistic data"""
        self.teacher_email = f"teacher_debug_{uuid.uuid4().hex[:8]}@school.edu"
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": self.teacher_email,
            "password": "TeacherPass123!",
            "name": "Dr. Rajesh Kumar",
            "user_type": "teacher",
            "school_name": "Delhi Public School, Sector 45"
        }
        
        try:
            print(f"📧 Registering teacher: {self.teacher_email}")
            response = requests.post(url, json=payload)
            print(f"📊 Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                
                print(f"✅ Teacher registered successfully")
                print(f"   Teacher ID: {self.teacher_id}")
                print(f"   Token: {self.teacher_token[:20]}...")
                return True
            else:
                print(f"❌ Teacher registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during teacher registration: {str(e)}")
            return False
            
    def create_class_and_capture_join_code(self):
        """Create a class and capture the exact join code returned"""
        if not self.teacher_token:
            print("❌ No teacher token available")
            return False
            
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        payload = {
            "class_name": "Advanced Mathematics - Class XII",
            "subject": "math",
            "description": "Advanced mathematics covering calculus, algebra, and trigonometry for Class XII students"
        }
        
        try:
            print(f"🏫 Creating class: {payload['class_name']}")
            response = requests.post(url, json=payload, headers=headers)
            print(f"📊 Class Creation Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.class_id = data.get("class_id")
                self.join_code = data.get("join_code")
                
                print(f"✅ Class created successfully")
                print(f"   Class ID: {self.class_id}")
                print(f"   Join Code: '{self.join_code}'")
                print(f"   Join Code Length: {len(self.join_code) if self.join_code else 'None'}")
                print(f"   Join Code Type: {type(self.join_code)}")
                print(f"   Join Code Repr: {repr(self.join_code)}")
                
                # Check for any whitespace or special characters
                if self.join_code:
                    print(f"   Join Code Bytes: {self.join_code.encode('utf-8')}")
                    print(f"   Has Leading/Trailing Spaces: {self.join_code != self.join_code.strip()}")
                    print(f"   Stripped Join Code: '{self.join_code.strip()}'")
                
                return True
            else:
                print(f"❌ Class creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during class creation: {str(e)}")
            return False
            
    def check_database_state(self):
        """Check the database state by retrieving the class information"""
        if not self.teacher_token or not self.class_id:
            print("❌ Missing teacher token or class ID")
            return
            
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            print("🔍 Checking database state by retrieving teacher's classes...")
            response = requests.get(url, headers=headers)
            print(f"📊 Get Classes Response: {response.status_code}")
            
            if response.status_code == 200:
                classes = response.json()
                print(f"✅ Retrieved {len(classes)} classes from database")
                
                # Find our specific class
                our_class = None
                for cls in classes:
                    if cls.get("class_id") == self.class_id:
                        our_class = cls
                        break
                
                if our_class:
                    print(f"🎯 Found our class in database:")
                    print(f"   Database Class ID: '{our_class.get('class_id')}'")
                    print(f"   Database Join Code: '{our_class.get('join_code')}'")
                    print(f"   Database Join Code Length: {len(our_class.get('join_code', ''))}")
                    print(f"   Database Join Code Type: {type(our_class.get('join_code'))}")
                    print(f"   Database Join Code Repr: {repr(our_class.get('join_code'))}")
                    print(f"   Database Class Name: '{our_class.get('class_name')}'")
                    print(f"   Database Subject: '{our_class.get('subject')}'")
                    print(f"   Database Active: {our_class.get('active')}")
                    print(f"   Database Teacher ID: '{our_class.get('teacher_id')}'")
                    
                    # Compare with what we stored
                    if our_class.get('join_code') == self.join_code:
                        print("✅ Join codes match between creation response and database")
                    else:
                        print("❌ Join codes DO NOT match!")
                        print(f"   Creation Response: '{self.join_code}'")
                        print(f"   Database Value: '{our_class.get('join_code')}'")
                else:
                    print(f"❌ Could not find our class (ID: {self.class_id}) in database")
            else:
                print(f"❌ Failed to retrieve classes: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception during database state check: {str(e)}")
            
    def create_student_account(self):
        """Create a real student account with realistic data"""
        self.student_email = f"student_debug_{uuid.uuid4().hex[:8]}@student.edu"
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": self.student_email,
            "password": "StudentPass123!",
            "name": "Priya Sharma",
            "user_type": "student",
            "grade_level": "12th"
        }
        
        try:
            print(f"📧 Registering student: {self.student_email}")
            response = requests.post(url, json=payload)
            print(f"📊 Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                
                print(f"✅ Student registered successfully")
                print(f"   Student ID: {self.student_id}")
                print(f"   Token: {self.student_token[:20]}...")
                return True
            else:
                print(f"❌ Student registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during student registration: {str(e)}")
            return False
            
    def test_join_process_variations(self):
        """Test the join process with various code variations to identify issues"""
        if not self.student_token or not self.join_code:
            print("❌ Missing student token or join code")
            return
            
        url = f"{API_URL}/student/join-class"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test variations of the join code
        test_variations = [
            ("Exact join code", self.join_code),
            ("Lowercase join code", self.join_code.lower()),
            ("Uppercase join code", self.join_code.upper()),
            ("Stripped join code", self.join_code.strip()),
            ("Join code with leading space", f" {self.join_code}"),
            ("Join code with trailing space", f"{self.join_code} "),
            ("Join code with both spaces", f" {self.join_code} "),
        ]
        
        print(f"🧪 Testing {len(test_variations)} join code variations...")
        
        for description, test_code in test_variations:
            payload = {"join_code": test_code}
            
            try:
                print(f"\n🔬 Testing: {description}")
                print(f"   Code: '{test_code}'")
                print(f"   Code Length: {len(test_code)}")
                print(f"   Code Repr: {repr(test_code)}")
                
                response = requests.post(url, json=payload, headers=headers)
                print(f"   Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS: {data.get('message', 'No message')}")
                    print(f"   Class Name: {data.get('class_name')}")
                    print(f"   Subject: {data.get('subject')}")
                    print(f"   Class ID: {data.get('class_id')}")
                    
                    # If successful, verify student profile shows joined class
                    self.verify_student_joined_class()
                    return  # Stop after first success
                    
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        print(f"   ❌ BAD REQUEST: {error_data.get('detail', 'No detail')}")
                    except:
                        print(f"   ❌ BAD REQUEST: {response.text}")
                        
                elif response.status_code == 404:
                    try:
                        error_data = response.json()
                        print(f"   ❌ NOT FOUND: {error_data.get('detail', 'No detail')}")
                    except:
                        print(f"   ❌ NOT FOUND: {response.text}")
                        
                else:
                    try:
                        error_data = response.json()
                        print(f"   ❌ ERROR {response.status_code}: {error_data.get('detail', 'No detail')}")
                    except:
                        print(f"   ❌ ERROR {response.status_code}: {response.text}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                
        print("\n❌ All join code variations failed!")
        
    def verify_student_joined_class(self):
        """Verify that the student profile shows the joined class"""
        if not self.student_token:
            print("❌ No student token available")
            return
            
        url = f"{API_URL}/student/profile"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            print("🔍 Verifying student profile shows joined class...")
            response = requests.get(url, headers=headers)
            print(f"📊 Profile Response: {response.status_code}")
            
            if response.status_code == 200:
                profile = response.json()
                joined_classes = profile.get("joined_classes", [])
                
                print(f"✅ Student profile retrieved")
                print(f"   Joined Classes: {joined_classes}")
                print(f"   Number of Joined Classes: {len(joined_classes)}")
                
                if self.class_id in joined_classes:
                    print(f"✅ Class {self.class_id} found in student's joined classes")
                else:
                    print(f"❌ Class {self.class_id} NOT found in student's joined classes")
                    
            else:
                print(f"❌ Failed to get student profile: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception during profile verification: {str(e)}")
            
    def debug_specific_issues(self):
        """Debug specific issues that might cause join failures"""
        print("🔧 DEBUGGING SPECIFIC ISSUES")
        print("-" * 40)
        
        # Issue 1: Check if join code generation has issues
        print("\n🔍 Issue 1: Join Code Generation Analysis")
        if self.join_code:
            print(f"   Join Code: '{self.join_code}'")
            print(f"   Length: {len(self.join_code)}")
            print(f"   Characters: {list(self.join_code)}")
            print(f"   ASCII Values: {[ord(c) for c in self.join_code]}")
            print(f"   Is Alphanumeric: {self.join_code.isalnum()}")
            print(f"   Is Upper: {self.join_code.isupper()}")
            print(f"   Contains Spaces: {' ' in self.join_code}")
            print(f"   Contains Special Chars: {not self.join_code.isalnum()}")
        
        # Issue 2: Test direct database query simulation
        print("\n🔍 Issue 2: Database Query Simulation")
        self.simulate_database_query()
        
        # Issue 3: Check field naming consistency
        print("\n🔍 Issue 3: Field Naming Consistency Check")
        self.check_field_naming_consistency()
        
        # Issue 4: Test authentication issues
        print("\n🔍 Issue 4: Authentication Issues Check")
        self.check_authentication_issues()
        
    def simulate_database_query(self):
        """Simulate the database query that the backend performs"""
        print("   Simulating backend database query logic...")
        
        # Get all teacher's classes to simulate the query
        if not self.teacher_token:
            print("   ❌ No teacher token for simulation")
            return
            
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                classes = response.json()
                
                print(f"   Total classes in database: {len(classes)}")
                
                # Simulate the exact query the backend does
                matching_classes = []
                for cls in classes:
                    if (cls.get("join_code") == self.join_code and 
                        cls.get("active") == True):
                        matching_classes.append(cls)
                
                print(f"   Classes matching join_code '{self.join_code}' and active=True: {len(matching_classes)}")
                
                if len(matching_classes) == 0:
                    print("   ❌ No classes match the query criteria!")
                    print("   Checking each class individually:")
                    for i, cls in enumerate(classes):
                        print(f"     Class {i+1}:")
                        print(f"       join_code: '{cls.get('join_code')}' (matches: {cls.get('join_code') == self.join_code})")
                        print(f"       active: {cls.get('active')} (matches: {cls.get('active') == True})")
                elif len(matching_classes) == 1:
                    print("   ✅ Exactly one class matches the query criteria")
                else:
                    print(f"   ⚠️  Multiple classes ({len(matching_classes)}) match the query criteria")
                    
            else:
                print(f"   ❌ Failed to get classes for simulation: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception during simulation: {str(e)}")
            
    def check_field_naming_consistency(self):
        """Check for field naming consistency issues"""
        print("   Checking field naming consistency...")
        
        # Check what fields are actually used in the class creation response
        if self.class_id and self.join_code:
            print(f"   Class creation returned:")
            print(f"     class_id: '{self.class_id}'")
            print(f"     join_code: '{self.join_code}'")
            
            # Check if the backend is using consistent field names
            print("   Backend should be using:")
            print("     - 'class_id' field for class identification")
            print("     - 'join_code' field for join codes")
            print("     - 'active' field for class status")
            
    def check_authentication_issues(self):
        """Check for authentication-related issues"""
        print("   Checking authentication issues...")
        
        # Test with invalid token
        url = f"{API_URL}/student/join-class"
        invalid_headers = {"Authorization": "Bearer invalid.token.here"}
        payload = {"join_code": self.join_code}
        
        try:
            response = requests.post(url, json=payload, headers=invalid_headers)
            print(f"   Invalid token response: {response.status_code}")
            
            if response.status_code == 401:
                print("   ✅ Invalid token correctly rejected with 401")
            elif response.status_code == 403:
                print("   ⚠️  Invalid token rejected with 403 (should be 401)")
            else:
                print(f"   ❌ Unexpected response for invalid token: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception during auth check: {str(e)}")
            
        # Test with missing token
        try:
            response = requests.post(url, json=payload)
            print(f"   Missing token response: {response.status_code}")
            
            if response.status_code == 401:
                print("   ✅ Missing token correctly rejected with 401")
            elif response.status_code == 403:
                print("   ⚠️  Missing token rejected with 403 (should be 401)")
            else:
                print(f"   ❌ Unexpected response for missing token: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception during missing token check: {str(e)}")

def main():
    """Main function to run the debugging test"""
    print("🚀 STUDENT JOIN CLASS DEBUGGING TEST")
    print("=" * 60)
    print("This test investigates the specific issue where students")
    print("are getting 'code is incorrect' errors when joining classes.")
    print("=" * 60)
    
    debugger = StudentJoinClassDebugger()
    
    try:
        success = debugger.debug_student_join_class_issue()
        
        if success:
            print("\n" + "=" * 60)
            print("🎯 DEBUGGING COMPLETED")
            print("=" * 60)
            print("Check the output above for specific issues identified.")
        else:
            print("\n" + "=" * 60)
            print("❌ DEBUGGING FAILED")
            print("=" * 60)
            print("Could not complete the debugging process.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Debugging interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
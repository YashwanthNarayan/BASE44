#!/usr/bin/env python3
"""
Teacher Class Creation Workflow Debug Test
=========================================

This test specifically debugs the teacher class creation workflow to identify
why classes aren't being created or displayed properly as requested in the review.

Focus Areas:
1. Teacher Registration
2. Teacher Authentication  
3. Class Creation (POST /api/teacher/classes)
4. Class Retrieval (GET /api/teacher/classes)
5. Database State verification
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
if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class TeacherClassCreationDebugger:
    def __init__(self):
        self.teacher_token = None
        self.teacher_id = None
        self.teacher_email = None
        self.class_id = None
        self.join_code = None
        
    def debug_step(self, step_name, description):
        """Print debug step header"""
        print(f"\n{'='*60}")
        print(f"🔍 STEP: {step_name}")
        print(f"📝 {description}")
        print(f"{'='*60}")
    
    def test_teacher_registration(self):
        """Step 1: Test teacher registration"""
        self.debug_step("TEACHER REGISTRATION", "Testing if teachers can register successfully")
        
        # Generate unique email for this test
        self.teacher_email = f"debug_teacher_{uuid.uuid4()}@example.com"
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": self.teacher_email,
            "password": "SecureTeacher123!",
            "name": "Debug Teacher",
            "user_type": "teacher",
            "school_name": "Debug High School"
        }
        
        print(f"📤 Registering teacher with email: {self.teacher_email}")
        print(f"📤 Registration payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"📥 Registration Response Status: {response.status_code}")
            print(f"📥 Registration Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Registration Response Data: {json.dumps(data, indent=2)}")
                
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                
                print(f"✅ Teacher registered successfully!")
                print(f"🆔 Teacher ID: {self.teacher_id}")
                print(f"🔑 Token received: {'Yes' if self.teacher_token else 'No'}")
                
                if self.teacher_token:
                    print(f"🔑 Token preview: {self.teacher_token[:20]}...")
                
                return True
            else:
                print(f"❌ Registration failed with status {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def test_teacher_authentication(self):
        """Step 2: Test teacher login and token validation"""
        self.debug_step("TEACHER AUTHENTICATION", "Verifying teacher login and token generation")
        
        if not self.teacher_email:
            print("❌ No teacher email available for login test")
            return False
        
        # Test login
        url = f"{API_URL}/auth/login"
        payload = {
            "email": self.teacher_email,
            "password": "SecureTeacher123!"
        }
        
        print(f"📤 Logging in teacher: {self.teacher_email}")
        print(f"📤 Login payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"📥 Login Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Login Response Data: {json.dumps(data, indent=2)}")
                
                # Update token if we get a new one
                login_token = data.get("access_token")
                if login_token:
                    self.teacher_token = login_token
                    print(f"✅ Teacher login successful!")
                    print(f"🔑 New token received: {login_token[:20]}...")
                    
                    # Test token validation by accessing teacher profile
                    return self.test_teacher_profile_access()
                else:
                    print(f"❌ Login successful but no token received")
                    return False
            else:
                print(f"❌ Login failed with status {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_teacher_profile_access(self):
        """Test teacher profile access to validate token"""
        print(f"\n🔍 Testing teacher profile access...")
        
        if not self.teacher_token:
            print("❌ No teacher token available")
            return False
        
        url = f"{API_URL}/auth/profile"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        print(f"📤 Accessing teacher profile with token")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📥 Profile Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Profile Response Data: {json.dumps(data, indent=2)}")
                print(f"✅ Teacher profile access successful!")
                return True
            else:
                print(f"❌ Profile access failed with status {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Profile access error: {str(e)}")
            return False
    
    def test_class_creation(self):
        """Step 3: Test class creation with teacher credentials"""
        self.debug_step("CLASS CREATION", "Testing POST /api/teacher/classes with actual teacher credentials")
        
        if not self.teacher_token:
            print("❌ No teacher token available for class creation")
            return False
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        payload = {
            "class_name": "Debug Physics Class",
            "subject": "physics",
            "description": "A debug physics class to test class creation workflow"
        }
        
        print(f"📤 Creating class with teacher token")
        print(f"📤 Class creation payload: {json.dumps(payload, indent=2)}")
        print(f"📤 Headers: {headers}")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"📥 Class Creation Response Status: {response.status_code}")
            print(f"📥 Class Creation Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Class Creation Response Data: {json.dumps(data, indent=2)}")
                
                self.class_id = data.get("class_id")
                self.join_code = data.get("join_code")
                
                print(f"✅ Class created successfully!")
                print(f"🆔 Class ID: {self.class_id}")
                print(f"🔗 Join Code: {self.join_code}")
                
                # Verify required fields are present
                required_fields = ["message", "class_id", "join_code"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"⚠️  Missing fields in response: {missing_fields}")
                else:
                    print(f"✅ All required fields present in response")
                
                return True
            else:
                print(f"❌ Class creation failed with status {response.status_code}")
                print(f"❌ Error response: {response.text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    print(f"❌ Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"❌ Raw error response: {response.text}")
                
                return False
                
        except Exception as e:
            print(f"❌ Class creation error: {str(e)}")
            return False
    
    def test_class_retrieval(self):
        """Step 4: Test class retrieval to verify creation"""
        self.debug_step("CLASS RETRIEVAL", "Testing GET /api/teacher/classes to see if created classes are returned")
        
        if not self.teacher_token:
            print("❌ No teacher token available for class retrieval")
            return False
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        print(f"📤 Retrieving teacher classes")
        print(f"📤 Headers: {headers}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📥 Class Retrieval Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Class Retrieval Response Data: {json.dumps(data, indent=2)}")
                
                if isinstance(data, list):
                    print(f"✅ Classes retrieved successfully!")
                    print(f"📊 Number of classes: {len(data)}")
                    
                    if len(data) > 0:
                        print(f"📋 Class details:")
                        for i, class_data in enumerate(data):
                            print(f"  Class {i+1}:")
                            print(f"    - ID: {class_data.get('class_id')}")
                            print(f"    - Name: {class_data.get('class_name')}")
                            print(f"    - Subject: {class_data.get('subject')}")
                            print(f"    - Join Code: {class_data.get('join_code')}")
                            print(f"    - Student Count: {class_data.get('student_count', 0)}")
                        
                        # Check if our created class is in the list
                        if self.class_id:
                            class_ids = [cls.get("class_id") for cls in data]
                            if self.class_id in class_ids:
                                print(f"✅ Created class found in teacher's classes!")
                            else:
                                print(f"❌ Created class NOT found in teacher's classes!")
                                print(f"❌ Expected class ID: {self.class_id}")
                                print(f"❌ Found class IDs: {class_ids}")
                        
                        return True
                    else:
                        print(f"⚠️  No classes found for teacher")
                        if self.class_id:
                            print(f"❌ Expected to find created class with ID: {self.class_id}")
                        return False
                else:
                    print(f"❌ Unexpected response format: {type(data)}")
                    return False
            else:
                print(f"❌ Class retrieval failed with status {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Class retrieval error: {str(e)}")
            return False
    
    def test_database_state(self):
        """Step 5: Test database state by checking health and making additional queries"""
        self.debug_step("DATABASE STATE", "Checking what's actually being stored in the database")
        
        # Test health endpoint
        print(f"🔍 Testing API health...")
        try:
            health_response = requests.get(f"{API_URL}/health")
            print(f"📥 Health Response Status: {health_response.status_code}")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"📥 Health Response: {json.dumps(health_data, indent=2)}")
                print(f"✅ API is healthy")
            else:
                print(f"❌ API health check failed")
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
        
        # Test teacher profile to see if teacher exists in database
        if self.teacher_token:
            print(f"\n🔍 Re-checking teacher profile...")
            try:
                profile_response = requests.get(
                    f"{API_URL}/auth/profile",
                    headers={"Authorization": f"Bearer {self.teacher_token}"}
                )
                print(f"📥 Profile Response Status: {profile_response.status_code}")
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"📥 Teacher Profile: {json.dumps(profile_data, indent=2)}")
                    print(f"✅ Teacher profile exists in database")
                else:
                    print(f"❌ Teacher profile not found: {profile_response.text}")
            except Exception as e:
                print(f"❌ Profile check error: {str(e)}")
        
        # Summary of database state
        print(f"\n📊 DATABASE STATE SUMMARY:")
        print(f"  - Teacher ID: {self.teacher_id}")
        print(f"  - Teacher Email: {self.teacher_email}")
        print(f"  - Class ID: {self.class_id}")
        print(f"  - Join Code: {self.join_code}")
        print(f"  - Token Available: {'Yes' if self.teacher_token else 'No'}")
    
    def run_complete_debug(self):
        """Run the complete teacher class creation debug workflow"""
        print(f"🚀 STARTING TEACHER CLASS CREATION DEBUG WORKFLOW")
        print(f"🎯 Focus: Debug teacher class creation workflow to identify issues")
        
        results = {
            "teacher_registration": False,
            "teacher_authentication": False,
            "class_creation": False,
            "class_retrieval": False,
            "database_state": True  # Always run this
        }
        
        # Step 1: Teacher Registration
        results["teacher_registration"] = self.test_teacher_registration()
        
        # Step 2: Teacher Authentication (only if registration succeeded)
        if results["teacher_registration"]:
            results["teacher_authentication"] = self.test_teacher_authentication()
        else:
            print(f"\n⏭️  Skipping authentication test due to registration failure")
        
        # Step 3: Class Creation (only if authentication succeeded)
        if results["teacher_authentication"]:
            results["class_creation"] = self.test_class_creation()
        else:
            print(f"\n⏭️  Skipping class creation test due to authentication failure")
        
        # Step 4: Class Retrieval (only if class creation succeeded)
        if results["class_creation"]:
            results["class_retrieval"] = self.test_class_retrieval()
        else:
            print(f"\n⏭️  Skipping class retrieval test due to class creation failure")
        
        # Step 5: Database State (always run)
        self.test_database_state()
        
        # Final Summary
        self.print_final_summary(results)
        
        return results
    
    def print_final_summary(self, results):
        """Print final summary of all tests"""
        print(f"\n{'='*80}")
        print(f"🎯 TEACHER CLASS CREATION DEBUG WORKFLOW SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len([k for k in results.keys() if k != "database_state"])
        passed_tests = len([k for k, v in results.items() if v and k != "database_state"])
        
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"")
        
        for test_name, result in results.items():
            if test_name == "database_state":
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"")
        print(f"🔍 KEY FINDINGS:")
        
        if not results["teacher_registration"]:
            print(f"  ❌ CRITICAL: Teacher registration is failing")
            print(f"     - Check auth service implementation")
            print(f"     - Verify database connection")
            print(f"     - Check user model validation")
        
        elif not results["teacher_authentication"]:
            print(f"  ❌ CRITICAL: Teacher authentication is failing")
            print(f"     - Check JWT token generation")
            print(f"     - Verify login endpoint")
            print(f"     - Check password hashing/verification")
        
        elif not results["class_creation"]:
            print(f"  ❌ CRITICAL: Class creation is failing")
            print(f"     - Check teacher routes implementation")
            print(f"     - Verify get_current_teacher dependency")
            print(f"     - Check database class insertion")
            print(f"     - Verify teacher profile exists in database")
        
        elif not results["class_retrieval"]:
            print(f"  ❌ CRITICAL: Class retrieval is failing")
            print(f"     - Check class query logic")
            print(f"     - Verify class data structure")
            print(f"     - Check database field naming consistency")
        
        else:
            print(f"  ✅ SUCCESS: All teacher class creation workflow steps working!")
            print(f"     - Teacher registration: Working")
            print(f"     - Teacher authentication: Working")
            print(f"     - Class creation: Working")
            print(f"     - Class retrieval: Working")
        
        print(f"")
        print(f"🔗 Test Data Generated:")
        print(f"  - Teacher Email: {self.teacher_email}")
        print(f"  - Teacher ID: {self.teacher_id}")
        print(f"  - Class ID: {self.class_id}")
        print(f"  - Join Code: {self.join_code}")
        
        print(f"")
        print(f"📝 Next Steps:")
        if passed_tests == total_tests:
            print(f"  ✅ Teacher class creation workflow is working correctly!")
            print(f"  ✅ Test the complete teacher → student workflow")
            print(f"  ✅ Verify frontend integration")
        else:
            print(f"  🔧 Fix the failing components identified above")
            print(f"  🔧 Re-run this debug test after fixes")
            print(f"  🔧 Check backend logs for detailed error information")

if __name__ == "__main__":
    debugger = TeacherClassCreationDebugger()
    results = debugger.run_complete_debug()
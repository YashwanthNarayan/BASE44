#!/usr/bin/env python3
import requests
import json
import time
import unittest
import os
import uuid
from dotenv import load_dotenv
import sys
from enum import Enum

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Add /api prefix to the backend URL
API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Enums to match backend
class GradeLevel(str, Enum):
    GRADE_6 = "6th"
    GRADE_7 = "7th" 
    GRADE_8 = "8th"
    GRADE_9 = "9th"
    GRADE_10 = "10th"
    GRADE_11 = "11th"
    GRADE_12 = "12th"

class Subject(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    ENGLISH = "english"
    HISTORY = "history"
    GEOGRAPHY = "geography"

class UserType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class TestTeacherAPIRoutes(unittest.TestCase):
    """Test cases specifically for the newly created Teacher API routes"""

    def setUp(self):
        """Set up test case - create student and teacher accounts"""
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.class_id = None
        self.class_code = None
        
        # Register student and teacher
        self.register_student()
        self.register_teacher()

    def register_student(self):
        """Register a student for testing"""
        print("\n🔍 Setting up student account...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"student_teacher_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Aarav Patel",
            "user_type": UserType.STUDENT.value,
            "grade_level": GradeLevel.GRADE_11.value
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"Registered student with ID: {self.student_id}")
            else:
                print(f"Failed to register student: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering student: {str(e)}")

    def register_teacher(self):
        """Register a teacher for testing"""
        print("\n🔍 Setting up teacher account...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"teacher_api_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Dr. Kavita Singh",
            "user_type": UserType.TEACHER.value,
            "school_name": "Kendriya Vidyalaya"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.teacher_token = data.get("access_token")
                self.teacher_id = data.get("user", {}).get("id")
                print(f"Registered teacher with ID: {self.teacher_id}")
            else:
                print(f"Failed to register teacher: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error registering teacher: {str(e)}")

    def test_01_health_check(self):
        """Test /api/health endpoint is still responding"""
        print("\n🔍 Testing Health Check Endpoint...")
        
        url = f"{API_URL}/health"
        
        try:
            response = requests.get(url)
            print(f"Health Check Response: {response.status_code}")
            
            self.assertEqual(response.status_code, 200, "Health check should return 200")
            data = response.json()
            
            self.assertEqual(data.get("status"), "healthy", "Status should be 'healthy'")
            self.assertIn("service", data, "Service should be included")
            self.assertIn("version", data, "Version should be included")
            
            print(f"API service: {data.get('service')}")
            print(f"API version: {data.get('version')}")
            print("✅ Health check test passed")
        except Exception as e:
            print(f"❌ Health check test failed: {str(e)}")
            self.fail(f"Health check test failed: {str(e)}")

    def test_02_create_class(self):
        """Test POST /api/teacher/classes (create class)"""
        print("\n🔍 Testing Teacher Class Creation...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Test with different class configurations
        test_classes = [
            {
                "class_name": "Advanced Mathematics",
                "subject": Subject.MATH.value,
                "description": "Advanced mathematics for grade 11 students covering calculus and algebra",
                "join_code": None  # Let system generate
            },
            {
                "class_name": "Physics Fundamentals",
                "subject": Subject.PHYSICS.value,
                "description": "Basic physics concepts including mechanics and thermodynamics",
                "join_code": "PHYS101"  # Custom code
            },
            {
                "class_name": "Chemistry Lab",
                "subject": Subject.CHEMISTRY.value,
                "description": "Hands-on chemistry experiments and theory",
                "join_code": None  # Let system generate
            }
        ]
        
        created_classes = []
        
        for i, class_data in enumerate(test_classes):
            try:
                print(f"Creating class #{i+1}: {class_data['class_name']}")
                response = requests.post(url, json=class_data, headers=headers)
                print(f"Create Class Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    self.assertIn("message", data, "Message should be present")
                    self.assertIn("class_id", data, "Class ID should be present")
                    self.assertIn("join_code", data, "Join code should be present")
                    
                    # Verify data values
                    self.assertIsNotNone(data.get("class_id"), "Class ID should not be None")
                    self.assertIsNotNone(data.get("join_code"), "Join code should not be None")
                    
                    # Store first class for further tests
                    if i == 0:
                        self.class_id = data.get("class_id")
                        self.class_code = data.get("join_code")
                    
                    created_classes.append({
                        "class_id": data.get("class_id"),
                        "join_code": data.get("join_code"),
                        "class_name": class_data["class_name"]
                    })
                    
                    print(f"✅ Successfully created class: {data.get('class_id')} with code: {data.get('join_code')}")
                else:
                    print(f"❌ Failed to create class: {response.status_code} - {response.text}")
                    self.fail(f"Failed to create class: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating class: {str(e)}")
                self.fail(f"Error creating class: {str(e)}")
        
        print(f"✅ Successfully created {len(created_classes)} classes")
        return created_classes

    def test_03_get_teacher_classes(self):
        """Test GET /api/teacher/classes (get teacher's classes)"""
        print("\n🔍 Testing Get Teacher Classes...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        # First create a class if we don't have one
        if not self.class_id:
            self.test_02_create_class()
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Get Teacher Classes Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response is a list
                self.assertIsInstance(data, list, "Response should be a list")
                self.assertTrue(len(data) > 0, "Teacher should have at least one class")
                
                # Check first class structure
                if len(data) > 0:
                    class_info = data[0]
                    expected_fields = [
                        "class_id", "class_name", "subject", "description", 
                        "class_code", "teacher_id", "created_at", 
                        "student_count", "test_count", "average_score"
                    ]
                    
                    for field in expected_fields:
                        self.assertIn(field, class_info, f"{field} should be present in class info")
                    
                    # Verify teacher ID matches
                    self.assertEqual(class_info.get("teacher_id"), self.teacher_id, "Teacher ID should match")
                    
                    # Verify data types
                    self.assertIsInstance(class_info.get("student_count"), int, "Student count should be integer")
                    self.assertIsInstance(class_info.get("test_count"), int, "Test count should be integer")
                    
                print(f"✅ Successfully retrieved {len(data)} classes for teacher")
                
                # Verify our created class is in the list
                if self.class_id:
                    class_ids = [cls.get("class_id") for cls in data]
                    self.assertIn(self.class_id, class_ids, "Created class should be in teacher's classes")
                    print("✅ Created class found in teacher's class list")
                
            else:
                print(f"❌ Failed to get teacher classes: {response.status_code} - {response.text}")
                self.fail(f"Failed to get teacher classes: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting teacher classes: {str(e)}")
            self.fail(f"Error getting teacher classes: {str(e)}")

    def test_04_teacher_analytics_overview(self):
        """Test GET /api/teacher/analytics/overview (teacher analytics)"""
        print("\n🔍 Testing Teacher Analytics Overview...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/analytics/overview"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Teacher Analytics Overview Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                expected_sections = [
                    "overview_metrics", "class_summary", "subject_distribution"
                ]
                
                for section in expected_sections:
                    self.assertIn(section, data, f"{section} should be present in analytics")
                
                # Verify overview metrics structure
                metrics = data.get("overview_metrics", {})
                expected_metrics = [
                    "total_classes", "total_students", "total_tests", "average_score"
                ]
                
                for metric in expected_metrics:
                    self.assertIn(metric, metrics, f"{metric} should be present in overview metrics")
                
                # Verify data types
                self.assertIsInstance(metrics.get("total_classes"), int, "Total classes should be integer")
                self.assertIsInstance(metrics.get("total_students"), int, "Total students should be integer")
                self.assertIsInstance(metrics.get("total_tests"), int, "Total tests should be integer")
                self.assertIsInstance(metrics.get("average_score"), (int, float), "Average score should be numeric")
                
                # Verify class summary is a list
                class_summary = data.get("class_summary", [])
                self.assertIsInstance(class_summary, list, "Class summary should be a list")
                
                # Verify subject distribution is a list
                subject_distribution = data.get("subject_distribution", [])
                self.assertIsInstance(subject_distribution, list, "Subject distribution should be a list")
                
                print(f"✅ Analytics Overview - Classes: {metrics.get('total_classes')}, Students: {metrics.get('total_students')}, Tests: {metrics.get('total_tests')}, Avg Score: {metrics.get('average_score')}")
                print("✅ Teacher analytics overview test passed")
                
            else:
                print(f"❌ Failed to get teacher analytics: {response.status_code} - {response.text}")
                self.fail(f"Failed to get teacher analytics: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting teacher analytics: {str(e)}")
            self.fail(f"Error getting teacher analytics: {str(e)}")

    def test_05_student_access_denied(self):
        """Test that students are denied access to teacher endpoints (403 errors)"""
        print("\n🔍 Testing Student Access Denied to Teacher Endpoints...")
        
        if not self.student_token:
            self.skipTest("Student token not available")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test all teacher endpoints with student token
        teacher_endpoints = [
            ("POST", f"{API_URL}/teacher/classes", {"class_name": "Test", "subject": "math"}),
            ("GET", f"{API_URL}/teacher/classes", None),
            ("GET", f"{API_URL}/teacher/analytics/overview", None)
        ]
        
        for method, url, payload in teacher_endpoints:
            try:
                print(f"Testing {method} {url} with student token...")
                
                if method == "POST":
                    response = requests.post(url, json=payload, headers=headers)
                elif method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers)
                
                print(f"Response: {response.status_code}")
                
                # Should return 403 Forbidden for students
                self.assertEqual(response.status_code, 403, 
                               f"Student should be denied access to {method} {url}")
                
                # Verify error message
                if response.status_code == 403:
                    try:
                        error_data = response.json()
                        self.assertIn("detail", error_data, "Error response should contain detail")
                        print(f"✅ Correctly denied: {error_data.get('detail')}")
                    except:
                        print("✅ Correctly denied access (non-JSON response)")
                
            except Exception as e:
                print(f"❌ Error testing student access denial: {str(e)}")
                self.fail(f"Error testing student access denial: {str(e)}")
        
        print("✅ All teacher endpoints correctly deny student access")

    def test_06_delete_class(self):
        """Test DELETE /api/teacher/classes/{class_id} (delete class)"""
        print("\n🔍 Testing Teacher Class Deletion...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        # First create a class specifically for deletion
        create_url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        create_payload = {
            "class_name": "Test Class for Deletion",
            "subject": Subject.BIOLOGY.value,
            "description": "This class will be deleted in the test",
            "class_code": None
        }
        
        try:
            # Create class
            create_response = requests.post(create_url, json=create_payload, headers=headers)
            self.assertEqual(create_response.status_code, 200, "Failed to create class for deletion test")
            
            create_data = create_response.json()
            delete_class_id = create_data.get("class_id")
            self.assertIsNotNone(delete_class_id, "Class ID should not be None")
            
            print(f"Created class for deletion: {delete_class_id}")
            
            # Now delete the class
            delete_url = f"{API_URL}/teacher/classes/{delete_class_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            print(f"Delete Class Response: {delete_response.status_code}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                
                # Verify response structure
                self.assertIn("message", delete_data, "Message should be present")
                
                print(f"✅ Successfully deleted class: {delete_data.get('message')}")
                
                # Verify class is no longer in teacher's class list
                get_classes_response = requests.get(f"{API_URL}/teacher/classes", headers=headers)
                if get_classes_response.status_code == 200:
                    classes = get_classes_response.json()
                    class_ids = [cls.get("class_id") for cls in classes]
                    self.assertNotIn(delete_class_id, class_ids, "Deleted class should not appear in class list")
                    print("✅ Confirmed class is removed from teacher's class list")
                
            else:
                print(f"❌ Failed to delete class: {delete_response.status_code} - {delete_response.text}")
                self.fail(f"Failed to delete class: {delete_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing class deletion: {str(e)}")
            self.fail(f"Error testing class deletion: {str(e)}")

    def test_07_class_code_generation_and_uniqueness(self):
        """Test class code generation and uniqueness"""
        print("\n🔍 Testing Class Code Generation and Uniqueness...")
        
        if not self.teacher_token:
            self.skipTest("Teacher token not available")
        
        url = f"{API_URL}/teacher/classes"
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Test 1: Auto-generated class codes
        generated_codes = []
        for i in range(3):
            payload = {
                "class_name": f"Auto Code Class {i+1}",
                "subject": Subject.MATH.value,
                "description": f"Test class {i+1} with auto-generated code",
                "class_code": None
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                self.assertEqual(response.status_code, 200, f"Failed to create class {i+1}")
                
                data = response.json()
                class_code = data.get("class_code")
                self.assertIsNotNone(class_code, "Class code should be generated")
                self.assertTrue(len(class_code) >= 6, "Class code should be at least 6 characters")
                
                # Check uniqueness
                self.assertNotIn(class_code, generated_codes, "Class codes should be unique")
                generated_codes.append(class_code)
                
                print(f"✅ Generated unique class code: {class_code}")
                
            except Exception as e:
                print(f"❌ Error testing auto-generated codes: {str(e)}")
                self.fail(f"Error testing auto-generated codes: {str(e)}")
        
        # Test 2: Custom class code
        custom_code = "CUSTOM123"
        custom_payload = {
            "class_name": "Custom Code Class",
            "subject": Subject.PHYSICS.value,
            "description": "Test class with custom code",
            "class_code": custom_code
        }
        
        try:
            response = requests.post(url, json=custom_payload, headers=headers)
            self.assertEqual(response.status_code, 200, "Failed to create class with custom code")
            
            data = response.json()
            returned_code = data.get("class_code")
            self.assertEqual(returned_code, custom_code, "Custom class code should be preserved")
            
            print(f"✅ Successfully used custom class code: {returned_code}")
            
        except Exception as e:
            print(f"❌ Error testing custom code: {str(e)}")
            self.fail(f"Error testing custom code: {str(e)}")
        
        # Test 3: Duplicate custom code should fail
        duplicate_payload = {
            "class_name": "Duplicate Code Class",
            "subject": Subject.CHEMISTRY.value,
            "description": "Test class with duplicate code",
            "class_code": custom_code  # Same as above
        }
        
        try:
            response = requests.post(url, json=duplicate_payload, headers=headers)
            self.assertEqual(response.status_code, 400, "Duplicate class code should be rejected")
            
            error_data = response.json()
            self.assertIn("detail", error_data, "Error response should contain detail")
            self.assertIn("already exists", error_data.get("detail", "").lower(), 
                         "Error should mention code already exists")
            
            print(f"✅ Correctly rejected duplicate class code: {error_data.get('detail')}")
            
        except Exception as e:
            print(f"❌ Error testing duplicate code rejection: {str(e)}")
            self.fail(f"Error testing duplicate code rejection: {str(e)}")
        
        print("✅ Class code generation and uniqueness tests passed")

    def test_08_authentication_requirements(self):
        """Test authentication requirements for teacher endpoints"""
        print("\n🔍 Testing Authentication Requirements for Teacher Endpoints...")
        
        # Test all teacher endpoints without authentication
        teacher_endpoints = [
            ("POST", f"{API_URL}/teacher/classes", {"class_name": "Test", "subject": "math"}),
            ("GET", f"{API_URL}/teacher/classes", None),
            ("DELETE", f"{API_URL}/teacher/classes/test-id", None),
            ("GET", f"{API_URL}/teacher/analytics/overview", None)
        ]
        
        for method, url, payload in teacher_endpoints:
            try:
                print(f"Testing {method} {url} without authentication...")
                
                if method == "POST":
                    response = requests.post(url, json=payload)
                elif method == "GET":
                    response = requests.get(url)
                elif method == "DELETE":
                    response = requests.delete(url)
                
                print(f"Response: {response.status_code}")
                
                # Should return 401 or 403 for missing authentication
                self.assertIn(response.status_code, [401, 403], 
                             f"Unauthenticated request to {method} {url} should be rejected")
                
                print(f"✅ Correctly requires authentication for {method} {url}")
                
            except Exception as e:
                print(f"❌ Error testing authentication requirement: {str(e)}")
                self.fail(f"Error testing authentication requirement: {str(e)}")
        
        print("✅ All teacher endpoints correctly require authentication")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING NEWLY CREATED TEACHER API ROUTES")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTeacherAPIRoutes)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEACHER API ROUTES TEST SUMMARY")
    print("="*60)
    
    if result.wasSuccessful():
        print("✅ ALL TEACHER API TESTS PASSED!")
    else:
        print("❌ SOME TEACHER API TESTS FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print(f"Tests run: {result.testsRun}")
    print(f"Skipped: {len(result.skipped)}")
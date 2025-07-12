#!/usr/bin/env python3
"""
Complete Teacher → Student Workflow Test
=======================================

This test verifies the complete workflow from teacher class creation
to student joining the class using the join code.
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

class TeacherStudentWorkflowTester:
    def __init__(self):
        self.teacher_token = None
        self.teacher_id = None
        self.student_token = None
        self.student_id = None
        self.class_id = None
        self.join_code = None
        
    def setup_teacher_and_class(self):
        """Setup teacher account and create a class"""
        print("🔍 Setting up teacher account and creating class...")
        
        # Register teacher
        teacher_email = f"workflow_teacher_{uuid.uuid4()}@example.com"
        teacher_payload = {
            "email": teacher_email,
            "password": "SecureTeacher123!",
            "name": "Workflow Teacher",
            "user_type": "teacher",
            "school_name": "Workflow High School"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
        if response.status_code != 200:
            print(f"❌ Teacher registration failed: {response.text}")
            return False
        
        teacher_data = response.json()
        self.teacher_token = teacher_data.get("access_token")
        self.teacher_id = teacher_data.get("user", {}).get("id")
        print(f"✅ Teacher registered: {self.teacher_id}")
        
        # Create class
        class_payload = {
            "class_name": "Workflow Math Class",
            "subject": "math",
            "description": "A math class for testing the complete workflow"
        }
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Class creation failed: {response.text}")
            return False
        
        class_data = response.json()
        self.class_id = class_data.get("class_id")
        self.join_code = class_data.get("join_code")
        print(f"✅ Class created: {self.class_id} with join code: {self.join_code}")
        
        return True
    
    def setup_student(self):
        """Setup student account"""
        print("🔍 Setting up student account...")
        
        student_email = f"workflow_student_{uuid.uuid4()}@example.com"
        student_payload = {
            "email": student_email,
            "password": "SecureStudent123!",
            "name": "Workflow Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=student_payload)
        if response.status_code != 200:
            print(f"❌ Student registration failed: {response.text}")
            return False
        
        student_data = response.json()
        self.student_token = student_data.get("access_token")
        self.student_id = student_data.get("user", {}).get("id")
        print(f"✅ Student registered: {self.student_id}")
        
        return True
    
    def test_student_join_class(self):
        """Test student joining the class using join code"""
        print(f"🔍 Testing student joining class with join code: {self.join_code}")
        
        if not self.student_token or not self.join_code:
            print("❌ Missing student token or join code")
            return False
        
        join_payload = {
            "join_code": self.join_code
        }
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=headers)
        
        print(f"📥 Join Class Response Status: {response.status_code}")
        print(f"📥 Join Class Response: {response.text}")
        
        if response.status_code == 200:
            join_data = response.json()
            print(f"✅ Student successfully joined class!")
            print(f"📥 Join Response Data: {json.dumps(join_data, indent=2)}")
            return True
        else:
            print(f"❌ Student failed to join class: {response.text}")
            return False
    
    def verify_student_in_class(self):
        """Verify student appears in teacher's class list"""
        print("🔍 Verifying student appears in teacher's class...")
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        response = requests.get(f"{API_URL}/teacher/classes", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get teacher classes: {response.text}")
            return False
        
        classes = response.json()
        target_class = None
        
        for cls in classes:
            if cls.get("class_id") == self.class_id:
                target_class = cls
                break
        
        if not target_class:
            print(f"❌ Class not found in teacher's classes")
            return False
        
        student_count = target_class.get("student_count", 0)
        print(f"📊 Class student count: {student_count}")
        
        if student_count > 0:
            print(f"✅ Student successfully added to class!")
            return True
        else:
            print(f"❌ Student count is still 0 - student not properly added")
            return False
    
    def verify_class_in_student_profile(self):
        """Verify class appears in student's joined classes"""
        print("🔍 Verifying class appears in student's profile...")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        response = requests.get(f"{API_URL}/auth/profile", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get student profile: {response.text}")
            return False
        
        profile = response.json()
        joined_classes = profile.get("joined_classes", [])
        
        print(f"📊 Student joined classes: {joined_classes}")
        
        if self.class_id in joined_classes:
            print(f"✅ Class found in student's joined classes!")
            return True
        else:
            print(f"❌ Class not found in student's joined classes")
            return False
    
    def test_case_sensitivity_issue(self):
        """Test the case sensitivity issue mentioned in the review"""
        print("🔍 Testing join code case sensitivity...")
        
        # Create another student for this test
        student_email = f"case_test_student_{uuid.uuid4()}@example.com"
        student_payload = {
            "email": student_email,
            "password": "SecureStudent123!",
            "name": "Case Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=student_payload)
        if response.status_code != 200:
            print(f"❌ Case test student registration failed")
            return False
        
        case_test_token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {case_test_token}"}
        
        # Test with lowercase join code
        lowercase_code = self.join_code.lower()
        print(f"🔍 Testing with lowercase join code: {lowercase_code}")
        
        join_payload = {"join_code": lowercase_code}
        response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=headers)
        
        print(f"📥 Lowercase Join Response Status: {response.status_code}")
        print(f"📥 Lowercase Join Response: {response.text}")
        
        if response.status_code == 404:
            print(f"❌ CONFIRMED: Case sensitivity issue exists - lowercase fails with 404")
            return False
        elif response.status_code == 200:
            print(f"✅ Case sensitivity has been fixed - lowercase works!")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
    
    def run_complete_workflow_test(self):
        """Run the complete teacher → student workflow test"""
        print("🚀 STARTING COMPLETE TEACHER → STUDENT WORKFLOW TEST")
        
        results = {
            "teacher_setup": False,
            "student_setup": False,
            "student_join": False,
            "teacher_verification": False,
            "student_verification": False,
            "case_sensitivity": False
        }
        
        # Step 1: Setup teacher and class
        results["teacher_setup"] = self.setup_teacher_and_class()
        if not results["teacher_setup"]:
            print("❌ Cannot continue without teacher setup")
            return results
        
        # Step 2: Setup student
        results["student_setup"] = self.setup_student()
        if not results["student_setup"]:
            print("❌ Cannot continue without student setup")
            return results
        
        # Step 3: Student joins class
        results["student_join"] = self.test_student_join_class()
        
        # Step 4: Verify from teacher side
        if results["student_join"]:
            results["teacher_verification"] = self.verify_student_in_class()
        
        # Step 5: Verify from student side
        if results["student_join"]:
            results["student_verification"] = self.verify_class_in_student_profile()
        
        # Step 6: Test case sensitivity issue
        results["case_sensitivity"] = self.test_case_sensitivity_issue()
        
        # Print summary
        self.print_workflow_summary(results)
        
        return results
    
    def print_workflow_summary(self, results):
        """Print workflow test summary"""
        print(f"\n{'='*80}")
        print(f"🎯 COMPLETE TEACHER → STUDENT WORKFLOW TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len(results)
        passed_tests = len([k for k, v in results.items() if v])
        
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        print(f"")
        print(f"🔍 KEY FINDINGS:")
        
        if results["teacher_setup"] and results["student_setup"] and results["student_join"]:
            if results["teacher_verification"] and results["student_verification"]:
                print(f"  ✅ COMPLETE WORKFLOW SUCCESS: Teacher → Student workflow working perfectly!")
                print(f"     - Teacher can create classes with join codes")
                print(f"     - Students can join classes using join codes")
                print(f"     - Class membership is properly tracked on both sides")
            else:
                print(f"  ⚠️  PARTIAL SUCCESS: Join works but verification has issues")
                if not results["teacher_verification"]:
                    print(f"     - Student count not updating in teacher's class view")
                if not results["student_verification"]:
                    print(f"     - Class not appearing in student's joined classes")
        else:
            print(f"  ❌ WORKFLOW FAILURE: Core join functionality not working")
        
        if not results["case_sensitivity"]:
            print(f"  ⚠️  UX ISSUE: Case sensitivity problem confirmed")
            print(f"     - Join codes must be entered in exact case (uppercase)")
            print(f"     - Recommendation: Implement input normalization")
        else:
            print(f"  ✅ CASE SENSITIVITY: Fixed or not an issue")
        
        print(f"")
        print(f"🔗 Test Data Generated:")
        print(f"  - Teacher ID: {self.teacher_id}")
        print(f"  - Student ID: {self.student_id}")
        print(f"  - Class ID: {self.class_id}")
        print(f"  - Join Code: {self.join_code}")

if __name__ == "__main__":
    tester = TeacherStudentWorkflowTester()
    results = tester.run_complete_workflow_test()
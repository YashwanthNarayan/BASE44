#!/usr/bin/env python3
"""
Detailed Classes API Test - Additional scenarios and data structure verification
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

class DetailedClassesTest:
    def __init__(self):
        self.student_token = None
        self.teacher_token = None
        self.student_id = None
        self.teacher_id = None
        self.classes_created = []
        
    def setup_accounts(self):
        """Setup student and teacher accounts"""
        print("🔧 Setting up test accounts...")
        
        # Register student
        student_email = f"detailed_student_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": student_email,
            "password": "TestPass123!",
            "name": "Kavya Singh",
            "user_type": "student",
            "grade_level": "11th"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=register_payload)
        if response.status_code == 200:
            data = response.json()
            self.student_token = data.get("access_token")
            self.student_id = data.get("user", {}).get("id")
            print(f"✅ Student setup: {self.student_id}")
        else:
            print(f"❌ Student setup failed: {response.status_code}")
            return False
        
        # Register teacher
        teacher_email = f"detailed_teacher_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": teacher_email,
            "password": "TeacherPass123!",
            "name": "Prof. Rajesh Kumar",
            "user_type": "teacher",
            "school_name": "Modern Public School"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=register_payload)
        if response.status_code == 200:
            data = response.json()
            self.teacher_token = data.get("access_token")
            self.teacher_id = data.get("user", {}).get("id")
            print(f"✅ Teacher setup: {self.teacher_id}")
            return True
        else:
            print(f"❌ Teacher setup failed: {response.status_code}")
            return False
    
    def create_multiple_classes(self):
        """Create multiple classes with different subjects"""
        print("\n🏫 Creating multiple test classes...")
        
        classes_to_create = [
            {
                "class_name": "Physics Fundamentals",
                "subject": "physics",
                "description": "Basic physics concepts for grade 11 students"
            },
            {
                "class_name": "Chemistry Lab",
                "subject": "chemistry", 
                "description": "Hands-on chemistry experiments and theory"
            },
            {
                "class_name": "Biology Essentials",
                "subject": "biology",
                "description": "Life sciences and biological processes"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        for class_data in classes_to_create:
            response = requests.post(f"{API_URL}/teacher/classes", json=class_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.classes_created.append({
                    "class_id": result.get("class_id"),
                    "join_code": result.get("join_code"),
                    "class_name": class_data["class_name"],
                    "subject": class_data["subject"]
                })
                print(f"✅ Created: {class_data['class_name']} (Code: {result.get('join_code')})")
            else:
                print(f"❌ Failed to create {class_data['class_name']}: {response.status_code}")
                return False
        
        print(f"✅ Successfully created {len(self.classes_created)} classes")
        return True
    
    def test_join_multiple_classes(self):
        """Test joining multiple classes and verify data structure"""
        print("\n🔗 Testing joining multiple classes...")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        joined_classes = []
        
        # Join first two classes
        for i, class_info in enumerate(self.classes_created[:2]):
            payload = {"join_code": class_info["join_code"]}
            response = requests.post(f"{API_URL}/student/join-class", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                joined_classes.append(class_info)
                print(f"✅ Joined: {class_info['class_name']}")
                
                # Verify response structure
                required_fields = ["message", "class_name", "subject", "class_id"]
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing field in join response: {field}")
                        return False
            else:
                print(f"❌ Failed to join {class_info['class_name']}: {response.status_code}")
                return False
        
        # Now test the joined-classes endpoint
        response = requests.get(f"{API_URL}/student/joined-classes", headers=headers)
        if response.status_code == 200:
            classes_data = response.json()
            print(f"✅ Retrieved {len(classes_data)} joined classes")
            
            # Verify data structure for each class
            for class_data in classes_data:
                print(f"\n📋 Verifying class: {class_data.get('class_name')}")
                
                # Check all required fields
                required_fields = [
                    "class_id", "class_name", "subject", "description",
                    "join_code", "teacher_id", "created_at", "student_count"
                ]
                
                for field in required_fields:
                    if field in class_data:
                        value = class_data[field]
                        print(f"   ✅ {field}: {value}")
                        
                        # Additional validation
                        if field == "student_count" and value < 1:
                            print(f"   ❌ Student count should be at least 1, got {value}")
                            return False
                        elif field == "subject" and value not in ["physics", "chemistry", "biology", "math", "english"]:
                            print(f"   ⚠️  Unexpected subject: {value}")
                        elif field == "created_at" and not value:
                            print(f"   ❌ Created_at should not be empty")
                            return False
                    else:
                        print(f"   ❌ Missing required field: {field}")
                        return False
            
            # Verify we got the correct number of classes
            if len(classes_data) == len(joined_classes):
                print(f"✅ Correct number of classes returned: {len(classes_data)}")
                return True
            else:
                print(f"❌ Expected {len(joined_classes)} classes, got {len(classes_data)}")
                return False
        else:
            print(f"❌ Failed to get joined classes: {response.status_code}")
            return False
    
    def test_duplicate_join_attempt(self):
        """Test attempting to join the same class twice"""
        print("\n🔄 Testing duplicate join attempt...")
        
        if not self.classes_created:
            print("❌ No classes available for testing")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        first_class = self.classes_created[0]
        payload = {"join_code": first_class["join_code"]}
        
        # Try to join the same class again
        response = requests.post(f"{API_URL}/student/join-class", json=payload, headers=headers)
        
        if response.status_code == 400:
            data = response.json()
            if "Already joined this class" in data.get("detail", ""):
                print("✅ Correctly prevented duplicate join with appropriate error message")
                return True
            else:
                print(f"❌ Unexpected error message: {data.get('detail')}")
                return False
        else:
            print(f"❌ Expected 400 status code, got {response.status_code}")
            return False
    
    def test_join_code_case_sensitivity(self):
        """Test join code with different cases"""
        print("\n🔤 Testing join code case sensitivity...")
        
        if len(self.classes_created) < 3:
            print("❌ Need at least 3 classes for this test")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        third_class = self.classes_created[2]
        original_code = third_class["join_code"]
        
        # Test with lowercase
        payload = {"join_code": original_code.lower()}
        response = requests.post(f"{API_URL}/student/join-class", json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Join code works with lowercase")
            return True
        elif response.status_code == 404:
            # Try with original case
            payload = {"join_code": original_code}
            response = requests.post(f"{API_URL}/student/join-class", json=payload, headers=headers)
            
            if response.status_code == 200:
                print("✅ Join code is case-sensitive (works with original case)")
                return True
            else:
                print(f"❌ Join code failed even with original case: {response.status_code}")
                return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    
    def test_data_consistency(self):
        """Test data consistency between endpoints"""
        print("\n🔍 Testing data consistency...")
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Get joined classes
        response = requests.get(f"{API_URL}/student/joined-classes", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get joined classes: {response.status_code}")
            return False
        
        joined_classes = response.json()
        
        # Get teacher's classes to compare
        teacher_headers = {"Authorization": f"Bearer {self.teacher_token}"}
        response = requests.get(f"{API_URL}/teacher/classes", headers=teacher_headers)
        if response.status_code != 200:
            print(f"❌ Failed to get teacher classes: {response.status_code}")
            return False
        
        teacher_classes = response.json()
        
        # Verify consistency
        for joined_class in joined_classes:
            class_id = joined_class["class_id"]
            
            # Find matching teacher class
            matching_teacher_class = None
            for teacher_class in teacher_classes:
                if teacher_class["class_id"] == class_id:
                    matching_teacher_class = teacher_class
                    break
            
            if not matching_teacher_class:
                print(f"❌ Class {class_id} not found in teacher's classes")
                return False
            
            # Compare key fields
            fields_to_compare = ["class_name", "subject", "join_code", "teacher_id"]
            for field in fields_to_compare:
                if joined_class.get(field) != matching_teacher_class.get(field):
                    print(f"❌ Mismatch in {field}: student sees '{joined_class.get(field)}', teacher has '{matching_teacher_class.get(field)}'")
                    return False
            
            print(f"✅ Data consistency verified for class: {joined_class['class_name']}")
        
        print("✅ All data consistency checks passed")
        return True
    
    def run_detailed_tests(self):
        """Run all detailed tests"""
        print("🚀 Starting Detailed Classes API Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_accounts():
            print("❌ Failed to setup accounts")
            return False
        
        if not self.create_multiple_classes():
            print("❌ Failed to create test classes")
            return False
        
        # Run tests
        tests = [
            ("Join Multiple Classes", self.test_join_multiple_classes),
            ("Duplicate Join Attempt", self.test_duplicate_join_attempt),
            ("Join Code Case Sensitivity", self.test_join_code_case_sensitivity),
            ("Data Consistency", self.test_data_consistency)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DETAILED TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        failed = len(results) - passed
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n📈 Results: {passed} passed, {failed} failed")
        return failed == 0

def main():
    tester = DetailedClassesTest()
    success = tester.run_detailed_tests()
    
    if success:
        print("\n🎉 All detailed tests passed!")
    else:
        print("\n⚠️ Some detailed tests failed!")
    
    return success

if __name__ == "__main__":
    main()
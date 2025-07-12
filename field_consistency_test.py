#!/usr/bin/env python3
import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 Testing Field Naming Consistency and API Data Structure")
print(f"Using API URL: {API_URL}")

def test_field_naming_consistency():
    """Test field naming consistency between teacher create and student join"""
    
    # Create teacher and class
    print("\n📝 Creating teacher and class...")
    teacher_email = f"teacher_{uuid.uuid4()}@example.com"
    teacher_payload = {
        "email": teacher_email,
        "password": "SecurePass123!",
        "name": "Dr. Neha Patel",
        "user_type": "teacher",
        "school_name": "Delhi Public School"
    }
    
    teacher_response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
    if teacher_response.status_code != 200:
        print(f"❌ Teacher registration failed: {teacher_response.text}")
        return False
    
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get("access_token")
    
    # Create class
    class_payload = {
        "class_name": "Mathematics Grade 10",
        "subject": "math",
        "description": "Comprehensive mathematics course for grade 10 students"
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
    
    if class_response.status_code != 200:
        print(f"❌ Class creation failed: {class_response.text}")
        return False
    
    class_data = class_response.json()
    class_id = class_data.get("class_id")
    join_code = class_data.get("join_code")
    
    print(f"✅ Class created - ID: {class_id}, Join Code: {join_code}")
    
    # Get teacher's classes to check field consistency
    get_classes_response = requests.get(f"{API_URL}/teacher/classes", headers=headers)
    if get_classes_response.status_code != 200:
        print(f"❌ Get teacher classes failed: {get_classes_response.text}")
        return False
    
    teacher_classes = get_classes_response.json()
    print(f"✅ Retrieved {len(teacher_classes)} teacher classes")
    
    # Check field naming in teacher response
    if len(teacher_classes) > 0:
        teacher_class = teacher_classes[0]
        print(f"Teacher class fields: {list(teacher_class.keys())}")
        
        # Verify expected fields
        expected_fields = ["class_id", "class_name", "subject", "join_code", "teacher_id", "created_at"]
        for field in expected_fields:
            if field not in teacher_class:
                print(f"❌ Missing field '{field}' in teacher class response")
                return False
        
        print(f"✅ All expected fields present in teacher class response")
    
    # Create student and join class
    print("\n📝 Creating student and testing join...")
    student_email = f"student_{uuid.uuid4()}@example.com"
    student_payload = {
        "email": student_email,
        "password": "SecurePass123!",
        "name": "Rahul Singh",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    student_response = requests.post(f"{API_URL}/auth/register", json=student_payload)
    if student_response.status_code != 200:
        print(f"❌ Student registration failed: {student_response.text}")
        return False
    
    student_data = student_response.json()
    student_token = student_data.get("access_token")
    
    # Join class
    join_payload = {"join_code": join_code}
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    join_response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=student_headers)
    if join_response.status_code != 200:
        print(f"❌ Join class failed: {join_response.text}")
        return False
    
    join_result = join_response.json()
    print(f"✅ Student joined class successfully")
    print(f"Join response fields: {list(join_result.keys())}")
    
    # Verify join response has consistent field naming
    if "class_id" not in join_result:
        print(f"❌ Missing 'class_id' in join response")
        return False
    
    if join_result.get("class_id") != class_id:
        print(f"❌ Class ID mismatch: expected {class_id}, got {join_result.get('class_id')}")
        return False
    
    print(f"✅ Field naming consistency verified between teacher create and student join")
    
    return True

def test_active_vs_is_active_consistency():
    """Test the active vs is_active field naming consistency"""
    
    print("\n📝 Testing active vs is_active field consistency...")
    
    # Create teacher and class
    teacher_email = f"teacher_{uuid.uuid4()}@example.com"
    teacher_payload = {
        "email": teacher_email,
        "password": "SecurePass123!",
        "name": "Prof. Amit Kumar",
        "user_type": "teacher",
        "school_name": "St. Xavier's School"
    }
    
    teacher_response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
    if teacher_response.status_code != 200:
        print(f"❌ Teacher registration failed: {teacher_response.text}")
        return False
    
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get("access_token")
    
    # Create class
    class_payload = {
        "class_name": "Chemistry Advanced",
        "subject": "chemistry",
        "description": "Advanced chemistry for grade 12"
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
    
    if class_response.status_code != 200:
        print(f"❌ Class creation failed: {class_response.text}")
        return False
    
    class_data = class_response.json()
    join_code = class_data.get("join_code")
    
    # Create student
    student_email = f"student_{uuid.uuid4()}@example.com"
    student_payload = {
        "email": student_email,
        "password": "SecurePass123!",
        "name": "Priya Sharma",
        "user_type": "student",
        "grade_level": "12th"
    }
    
    student_response = requests.post(f"{API_URL}/auth/register", json=student_payload)
    if student_response.status_code != 200:
        print(f"❌ Student registration failed: {student_response.text}")
        return False
    
    student_data = student_response.json()
    student_token = student_data.get("access_token")
    
    # Test joining with valid join code (should work with 'active' field)
    join_payload = {"join_code": join_code}
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    join_response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=student_headers)
    
    if join_response.status_code == 200:
        print(f"✅ Join class works correctly with current field naming")
        return True
    else:
        print(f"❌ Join class failed: {join_response.status_code} - {join_response.text}")
        return False

def test_api_data_structure():
    """Test API data structure consistency"""
    
    print("\n📝 Testing API data structure consistency...")
    
    # Create complete workflow and check data structures
    teacher_email = f"teacher_{uuid.uuid4()}@example.com"
    teacher_payload = {
        "email": teacher_email,
        "password": "SecurePass123!",
        "name": "Dr. Sunita Verma",
        "user_type": "teacher",
        "school_name": "Modern Academy"
    }
    
    teacher_response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
    if teacher_response.status_code != 200:
        print(f"❌ Teacher registration failed")
        return False
    
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get("access_token")
    
    # Create class and check response structure
    class_payload = {
        "class_name": "Biology Fundamentals",
        "subject": "biology",
        "description": "Basic biology concepts"
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
    
    if class_response.status_code != 200:
        print(f"❌ Class creation failed")
        return False
    
    class_data = class_response.json()
    
    # Check class creation response structure
    expected_create_fields = ["message", "class_id", "join_code"]
    for field in expected_create_fields:
        if field not in class_data:
            print(f"❌ Missing field '{field}' in class creation response")
            return False
    
    print(f"✅ Class creation response structure is correct")
    
    # Create student and test join response structure
    student_email = f"student_{uuid.uuid4()}@example.com"
    student_payload = {
        "email": student_email,
        "password": "SecurePass123!",
        "name": "Vikash Gupta",
        "user_type": "student",
        "grade_level": "11th"
    }
    
    student_response = requests.post(f"{API_URL}/auth/register", json=student_payload)
    if student_response.status_code != 200:
        print(f"❌ Student registration failed")
        return False
    
    student_data = student_response.json()
    student_token = student_data.get("access_token")
    
    # Test join class response structure
    join_payload = {"join_code": class_data.get("join_code")}
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    join_response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=student_headers)
    
    if join_response.status_code != 200:
        print(f"❌ Join class failed")
        return False
    
    join_result = join_response.json()
    
    # Check join response structure
    expected_join_fields = ["message", "class_name", "subject", "class_id"]
    for field in expected_join_fields:
        if field not in join_result:
            print(f"❌ Missing field '{field}' in join class response")
            return False
    
    print(f"✅ Join class response structure is correct")
    
    # Verify data consistency
    if join_result.get("class_id") != class_data.get("class_id"):
        print(f"❌ Class ID inconsistency between create and join responses")
        return False
    
    print(f"✅ Data consistency verified between create and join operations")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Field Naming and Data Structure Tests")
    
    tests = [
        ("Field Naming Consistency", test_field_naming_consistency),
        ("Active vs Is_Active Consistency", test_active_vs_is_active_consistency),
        ("API Data Structure", test_api_data_structure)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL TESTS PASSED - Field naming and data structure are consistent!")
    else:
        print("❌ SOME TESTS FAILED - There are field naming or data structure issues")
    print(f"{'='*50}")
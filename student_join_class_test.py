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

print(f"🔍 Testing Student Join Class Functionality")
print(f"Using API URL: {API_URL}")

def test_student_join_class():
    """Test the complete student join class workflow"""
    
    # Step 1: Create a teacher account
    print("\n📝 Step 1: Creating teacher account...")
    teacher_email = f"teacher_{uuid.uuid4()}@example.com"
    teacher_payload = {
        "email": teacher_email,
        "password": "SecurePass123!",
        "name": "Dr. Priya Sharma",
        "user_type": "teacher",
        "school_name": "Modern Public School"
    }
    
    teacher_response = requests.post(f"{API_URL}/auth/register", json=teacher_payload)
    print(f"Teacher registration: {teacher_response.status_code}")
    
    if teacher_response.status_code != 200:
        print(f"❌ Teacher registration failed: {teacher_response.text}")
        return False
    
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get("access_token")
    teacher_id = teacher_data.get("user", {}).get("id")
    print(f"✅ Teacher created with ID: {teacher_id}")
    
    # Step 2: Create a class using teacher API
    print("\n📝 Step 2: Creating class...")
    class_payload = {
        "class_name": "Advanced Physics",
        "subject": "physics",
        "description": "Advanced physics class covering mechanics and thermodynamics"
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_response = requests.post(f"{API_URL}/teacher/classes", json=class_payload, headers=headers)
    print(f"Class creation: {class_response.status_code}")
    
    if class_response.status_code != 200:
        print(f"❌ Class creation failed: {class_response.text}")
        return False
    
    class_data = class_response.json()
    class_id = class_data.get("class_id")
    join_code = class_data.get("join_code")
    print(f"✅ Class created with ID: {class_id}, Join code: {join_code}")
    
    # Step 3: Create a student account
    print("\n📝 Step 3: Creating student account...")
    student_email = f"student_{uuid.uuid4()}@example.com"
    student_payload = {
        "email": student_email,
        "password": "SecurePass123!",
        "name": "Arjun Kumar",
        "user_type": "student",
        "grade_level": "11th"
    }
    
    student_response = requests.post(f"{API_URL}/auth/register", json=student_payload)
    print(f"Student registration: {student_response.status_code}")
    
    if student_response.status_code != 200:
        print(f"❌ Student registration failed: {student_response.text}")
        return False
    
    student_data = student_response.json()
    student_token = student_data.get("access_token")
    student_id = student_data.get("user", {}).get("id")
    print(f"✅ Student created with ID: {student_id}")
    
    # Step 4: Test student joining the class
    print("\n📝 Step 4: Testing student join class...")
    join_payload = {
        "join_code": join_code
    }
    
    student_headers = {"Authorization": f"Bearer {student_token}"}
    join_response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=student_headers)
    print(f"Join class: {join_response.status_code}")
    
    if join_response.status_code != 200:
        print(f"❌ Join class failed: {join_response.text}")
        return False
    
    join_result = join_response.json()
    print(f"✅ Successfully joined class: {join_result.get('class_name')}")
    print(f"   Subject: {join_result.get('subject')}")
    print(f"   Class ID: {join_result.get('class_id')}")
    
    # Step 5: Verify student profile shows joined class
    print("\n📝 Step 5: Verifying student profile...")
    profile_response = requests.get(f"{API_URL}/student/profile", headers=student_headers)
    print(f"Student profile: {profile_response.status_code}")
    
    if profile_response.status_code != 200:
        print(f"❌ Student profile failed: {profile_response.text}")
        return False
    
    profile_data = profile_response.json()
    joined_classes = profile_data.get("joined_classes", [])
    print(f"✅ Student profile retrieved")
    print(f"   Joined classes: {joined_classes}")
    
    if class_id not in joined_classes:
        print(f"❌ Class ID {class_id} not found in joined classes")
        return False
    
    print(f"✅ Class correctly appears in student's joined classes")
    
    # Step 6: Test error scenarios
    print("\n📝 Step 6: Testing error scenarios...")
    
    # Test invalid join code
    invalid_join_payload = {
        "join_code": "INVALID"
    }
    
    invalid_response = requests.post(f"{API_URL}/student/join-class", json=invalid_join_payload, headers=student_headers)
    print(f"Invalid join code: {invalid_response.status_code}")
    
    if invalid_response.status_code != 404:
        print(f"❌ Invalid join code should return 404, got {invalid_response.status_code}")
        return False
    
    print(f"✅ Invalid join code correctly rejected")
    
    # Test joining same class twice
    duplicate_response = requests.post(f"{API_URL}/student/join-class", json=join_payload, headers=student_headers)
    print(f"Duplicate join: {duplicate_response.status_code}")
    
    if duplicate_response.status_code != 400:
        print(f"❌ Duplicate join should return 400, got {duplicate_response.status_code}")
        return False
    
    print(f"✅ Duplicate join correctly rejected")
    
    # Step 7: Test authentication requirements
    print("\n📝 Step 7: Testing authentication requirements...")
    
    no_auth_response = requests.post(f"{API_URL}/student/join-class", json=join_payload)
    print(f"No authentication: {no_auth_response.status_code}")
    
    if no_auth_response.status_code not in [401, 403]:
        print(f"❌ No auth should return 401/403, got {no_auth_response.status_code}")
        return False
    
    print(f"✅ Authentication requirement correctly enforced")
    
    print("\n🎉 All student join class tests passed!")
    return True

def test_health_check():
    """Test the health check endpoint"""
    print("\n📝 Testing Health Check...")
    
    response = requests.get(f"{API_URL}/health")
    print(f"Health check: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Health check failed: {response.text}")
        return False
    
    data = response.json()
    print(f"✅ Health check passed: {data.get('status')}")
    return True

if __name__ == "__main__":
    print("🚀 Starting Student Join Class Functionality Tests")
    
    # Test health check first
    health_ok = test_health_check()
    
    if health_ok:
        # Test student join class functionality
        join_ok = test_student_join_class()
        
        if join_ok:
            print("\n✅ ALL TESTS PASSED - Student join class functionality is working correctly!")
        else:
            print("\n❌ TESTS FAILED - Student join class functionality has issues")
    else:
        print("\n❌ HEALTH CHECK FAILED - Backend is not responding")
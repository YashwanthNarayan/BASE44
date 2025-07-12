#!/usr/bin/env python3
"""
ACTIVE FIELD INVESTIGATION TEST
===============================

This test specifically investigates why the 'active' field is None instead of True
in the database, which is causing the student join class functionality to fail.
"""

import requests
import json
import uuid
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def investigate_active_field_issue():
    """Investigate the active field issue"""
    print("🔍 INVESTIGATING ACTIVE FIELD ISSUE")
    print("=" * 50)
    
    # Step 1: Create teacher and class
    teacher_email = f"teacher_active_{uuid.uuid4().hex[:8]}@test.com"
    
    # Register teacher
    register_url = f"{API_URL}/auth/register"
    teacher_payload = {
        "email": teacher_email,
        "password": "TestPass123!",
        "name": "Test Teacher",
        "user_type": "teacher",
        "school_name": "Test School"
    }
    
    print("📝 Registering teacher...")
    teacher_response = requests.post(register_url, json=teacher_payload)
    
    if teacher_response.status_code != 200:
        print(f"❌ Teacher registration failed: {teacher_response.text}")
        return
        
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get("access_token")
    print("✅ Teacher registered successfully")
    
    # Create class
    create_class_url = f"{API_URL}/teacher/classes"
    headers = {"Authorization": f"Bearer {teacher_token}"}
    class_payload = {
        "class_name": "Active Field Test Class",
        "subject": "math",
        "description": "Testing active field issue"
    }
    
    print("📝 Creating class...")
    class_response = requests.post(create_class_url, json=class_payload, headers=headers)
    
    if class_response.status_code != 200:
        print(f"❌ Class creation failed: {class_response.text}")
        return
        
    class_data = class_response.json()
    class_id = class_data.get("class_id")
    join_code = class_data.get("join_code")
    print(f"✅ Class created with join code: {join_code}")
    
    # Step 2: Retrieve class and check active field
    get_classes_url = f"{API_URL}/teacher/classes"
    
    print("📝 Retrieving classes to check active field...")
    get_response = requests.get(get_classes_url, headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ Failed to get classes: {get_response.text}")
        return
        
    classes = get_response.json()
    print(f"✅ Retrieved {len(classes)} classes")
    
    # Find our class
    our_class = None
    for cls in classes:
        if cls.get("class_id") == class_id:
            our_class = cls
            break
    
    if not our_class:
        print("❌ Could not find our class in the response")
        return
        
    print("\n🔍 ACTIVE FIELD ANALYSIS:")
    print(f"   Class ID: {our_class.get('class_id')}")
    print(f"   Join Code: {our_class.get('join_code')}")
    print(f"   Active Field: {our_class.get('active')}")
    print(f"   Active Field Type: {type(our_class.get('active'))}")
    print(f"   Active Field Repr: {repr(our_class.get('active'))}")
    print(f"   'active' in class dict: {'active' in our_class}")
    
    # Check if active field is explicitly None or missing
    if 'active' not in our_class:
        print("❌ ISSUE: 'active' field is MISSING from the class document")
    elif our_class.get('active') is None:
        print("❌ ISSUE: 'active' field is explicitly set to None")
    elif our_class.get('active') is True:
        print("✅ 'active' field is correctly set to True")
    elif our_class.get('active') is False:
        print("⚠️  'active' field is set to False")
    else:
        print(f"⚠️  'active' field has unexpected value: {our_class.get('active')}")
    
    # Step 3: Test student join with this specific class
    print("\n📝 Testing student join with this class...")
    
    # Register student
    student_email = f"student_active_{uuid.uuid4().hex[:8]}@test.com"
    student_payload = {
        "email": student_email,
        "password": "TestPass123!",
        "name": "Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    student_response = requests.post(register_url, json=student_payload)
    
    if student_response.status_code != 200:
        print(f"❌ Student registration failed: {student_response.text}")
        return
        
    student_data = student_response.json()
    student_token = student_data.get("access_token")
    print("✅ Student registered successfully")
    
    # Try to join class
    join_url = f"{API_URL}/student/join-class"
    student_headers = {"Authorization": f"Bearer {student_token}"}
    join_payload = {"join_code": join_code}
    
    print(f"📝 Attempting to join class with code: {join_code}")
    join_response = requests.post(join_url, json=join_payload, headers=student_headers)
    
    print(f"📊 Join Response: {join_response.status_code}")
    
    if join_response.status_code == 200:
        join_data = join_response.json()
        print(f"✅ Successfully joined class: {join_data.get('message')}")
    else:
        try:
            error_data = join_response.json()
            print(f"❌ Join failed: {error_data.get('detail', 'No detail')}")
        except:
            print(f"❌ Join failed: {join_response.text}")
    
    # Step 4: Manual database query simulation
    print("\n🔍 MANUAL DATABASE QUERY SIMULATION:")
    
    # Simulate the exact query the backend does
    print("   Simulating query: {'join_code': join_code, 'active': True}")
    
    # Check if our class would match this query
    matches_join_code = our_class.get('join_code') == join_code
    matches_active = our_class.get('active') == True  # Note: using == True for exact match
    
    print(f"   Join code matches: {matches_join_code}")
    print(f"   Active field matches: {matches_active}")
    print(f"   Overall query match: {matches_join_code and matches_active}")
    
    if not matches_active:
        print("\n❌ ROOT CAUSE CONFIRMED:")
        print("   The 'active' field is not True, so the database query fails")
        print("   This is why students get 'Invalid join code or class not found' error")
        
        # Suggest fix
        print("\n💡 SUGGESTED FIX:")
        print("   1. Check if the class creation is properly setting active=True")
        print("   2. Check if there's a database serialization issue")
        print("   3. Verify the MongoDB driver is handling boolean values correctly")
    else:
        print("\n✅ Active field is working correctly")

if __name__ == "__main__":
    investigate_active_field_issue()
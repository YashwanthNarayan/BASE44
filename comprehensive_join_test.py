#!/usr/bin/env python3
"""
COMPREHENSIVE STUDENT JOIN CLASS TEST
====================================

This test performs multiple iterations of the student join class workflow
to identify any intermittent issues or edge cases that might cause failures.
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

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def test_student_join_multiple_iterations():
    """Test student join class functionality multiple times to catch intermittent issues"""
    print("🔍 COMPREHENSIVE STUDENT JOIN CLASS TEST")
    print("=" * 60)
    
    total_tests = 5
    successful_joins = 0
    failed_joins = 0
    test_results = []
    
    for i in range(total_tests):
        print(f"\n🧪 TEST ITERATION {i+1}/{total_tests}")
        print("-" * 40)
        
        result = run_single_join_test(i+1)
        test_results.append(result)
        
        if result['success']:
            successful_joins += 1
            print(f"✅ Test {i+1}: SUCCESS")
        else:
            failed_joins += 1
            print(f"❌ Test {i+1}: FAILED - {result['error']}")
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Successful Joins: {successful_joins}")
    print(f"Failed Joins: {failed_joins}")
    print(f"Success Rate: {(successful_joins/total_tests)*100:.1f}%")
    
    if failed_joins > 0:
        print("\n❌ FAILED TEST DETAILS:")
        for i, result in enumerate(test_results):
            if not result['success']:
                print(f"   Test {i+1}: {result['error']}")
                print(f"   Join Code: {result.get('join_code', 'N/A')}")
                print(f"   Response: {result.get('response_code', 'N/A')}")
    
    # Analyze patterns
    if failed_joins > 0:
        print("\n🔍 FAILURE PATTERN ANALYSIS:")
        
        # Check if all failures have the same error
        error_types = {}
        for result in test_results:
            if not result['success']:
                error = result['error']
                if error not in error_types:
                    error_types[error] = 0
                error_types[error] += 1
        
        for error, count in error_types.items():
            print(f"   '{error}': {count} occurrences")
    
    return successful_joins == total_tests

def run_single_join_test(test_num):
    """Run a single student join class test"""
    result = {
        'test_num': test_num,
        'success': False,
        'error': None,
        'join_code': None,
        'response_code': None,
        'teacher_id': None,
        'student_id': None,
        'class_id': None
    }
    
    try:
        # Step 1: Create teacher
        teacher_email = f"teacher_test_{test_num}_{uuid.uuid4().hex[:6]}@test.com"
        teacher_data = register_user(teacher_email, "teacher", f"Teacher {test_num}")
        
        if not teacher_data:
            result['error'] = "Teacher registration failed"
            return result
        
        result['teacher_id'] = teacher_data['user_id']
        
        # Step 2: Create class
        class_data = create_class(teacher_data['token'], f"Test Class {test_num}")
        
        if not class_data:
            result['error'] = "Class creation failed"
            return result
        
        result['class_id'] = class_data['class_id']
        result['join_code'] = class_data['join_code']
        
        # Step 3: Create student
        student_email = f"student_test_{test_num}_{uuid.uuid4().hex[:6]}@test.com"
        student_data = register_user(student_email, "student", f"Student {test_num}")
        
        if not student_data:
            result['error'] = "Student registration failed"
            return result
        
        result['student_id'] = student_data['user_id']
        
        # Step 4: Attempt to join class
        join_result = attempt_join_class(student_data['token'], class_data['join_code'])
        
        result['response_code'] = join_result['status_code']
        
        if join_result['success']:
            result['success'] = True
        else:
            result['error'] = join_result['error']
        
        return result
        
    except Exception as e:
        result['error'] = f"Exception: {str(e)}"
        return result

def register_user(email, user_type, name):
    """Register a user and return token and user_id"""
    url = f"{API_URL}/auth/register"
    
    payload = {
        "email": email,
        "password": "TestPass123!",
        "name": name,
        "user_type": user_type
    }
    
    if user_type == "teacher":
        payload["school_name"] = "Test School"
    else:
        payload["grade_level"] = "10th"
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'token': data.get("access_token"),
                'user_id': data.get("user", {}).get("id")
            }
        else:
            print(f"   Registration failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   Registration exception: {str(e)}")
        return None

def create_class(teacher_token, class_name):
    """Create a class and return class_id and join_code"""
    url = f"{API_URL}/teacher/classes"
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    payload = {
        "class_name": class_name,
        "subject": "math",
        "description": f"Test class: {class_name}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'class_id': data.get("class_id"),
                'join_code': data.get("join_code")
            }
        else:
            print(f"   Class creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   Class creation exception: {str(e)}")
        return None

def attempt_join_class(student_token, join_code):
    """Attempt to join a class"""
    url = f"{API_URL}/student/join-class"
    headers = {"Authorization": f"Bearer {student_token}"}
    
    payload = {"join_code": join_code}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        result = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'error': None
        }
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                result['error'] = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                result['error'] = f'HTTP {response.status_code}: {response.text}'
        
        return result
        
    except Exception as e:
        return {
            'status_code': None,
            'success': False,
            'error': f'Exception: {str(e)}'
        }

def test_edge_cases():
    """Test specific edge cases that might cause issues"""
    print("\n🔍 TESTING EDGE CASES")
    print("=" * 40)
    
    # Create a teacher and class for edge case testing
    teacher_email = f"teacher_edge_{uuid.uuid4().hex[:6]}@test.com"
    teacher_data = register_user(teacher_email, "teacher", "Edge Case Teacher")
    
    if not teacher_data:
        print("❌ Could not create teacher for edge case testing")
        return
    
    class_data = create_class(teacher_data['token'], "Edge Case Test Class")
    
    if not class_data:
        print("❌ Could not create class for edge case testing")
        return
    
    join_code = class_data['join_code']
    print(f"📝 Testing with join code: '{join_code}'")
    
    # Create student for testing
    student_email = f"student_edge_{uuid.uuid4().hex[:6]}@test.com"
    student_data = register_user(student_email, "student", "Edge Case Student")
    
    if not student_data:
        print("❌ Could not create student for edge case testing")
        return
    
    # Test cases
    edge_cases = [
        ("Exact join code", join_code),
        ("Lowercase join code", join_code.lower()),
        ("Mixed case join code", join_code.lower().capitalize()),
        ("Join code with leading space", f" {join_code}"),
        ("Join code with trailing space", f"{join_code} "),
        ("Join code with both spaces", f" {join_code} "),
        ("Empty join code", ""),
        ("None join code", None),
        ("Very long join code", "A" * 100),
        ("Join code with special chars", f"{join_code}!@#"),
    ]
    
    for description, test_code in edge_cases:
        print(f"\n🧪 Testing: {description}")
        
        if test_code is None:
            # Special case for None
            url = f"{API_URL}/student/join-class"
            headers = {"Authorization": f"Bearer {student_data['token']}"}
            payload = {}  # Missing join_code field
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"   Response: {response.status_code}")
            except Exception as e:
                print(f"   Exception: {str(e)}")
        else:
            result = attempt_join_class(student_data['token'], test_code)
            print(f"   Response: {result['status_code']}")
            
            if result['success']:
                print(f"   ✅ SUCCESS")
                # If successful, we need to create a new student for next test
                # (since a student can only join a class once)
                student_email = f"student_edge_{uuid.uuid4().hex[:6]}@test.com"
                student_data = register_user(student_email, "student", "Edge Case Student")
            else:
                print(f"   ❌ FAILED: {result['error']}")

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE STUDENT JOIN CLASS TEST")
    
    # Test multiple iterations
    success = test_student_join_multiple_iterations()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST COMPLETED")
    print("=" * 60)
    
    if success:
        print("✅ All basic join tests passed")
    else:
        print("❌ Some join tests failed - check details above")
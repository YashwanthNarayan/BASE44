#!/usr/bin/env python3
"""
Focused test for Modern UI Components API endpoints
Testing specific endpoints causing "failed to load data" errors
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

print(f"🔍 Testing Modern UI Components API Endpoints")
print(f"Using API URL: {API_URL}")

def create_test_user():
    """Create a test student user and return token"""
    print("\n📝 Creating test student user...")
    
    url = f"{API_URL}/auth/register"
    payload = {
        "email": f"modern_ui_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Modern UI Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Created test user: {user_id}")
            return token, user_id
        else:
            print(f"❌ Failed to create user: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Exception creating user: {str(e)}")
        return None, None

def create_test_data(token):
    """Create some test data for the user"""
    print("\n📝 Creating test data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create practice test
    try:
        gen_url = f"{API_URL}/practice/generate"
        gen_payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
        if gen_response.status_code == 200:
            gen_data = gen_response.json()
            questions = gen_data.get("questions", [])
            
            if questions:
                # Submit the test
                submit_url = f"{API_URL}/practice/submit"
                student_answers = {}
                question_ids = []
                
                for question in questions:
                    question_id = question.get("id")
                    question_ids.append(question_id)
                    student_answers[question_id] = question.get("correct_answer", "A")
                
                submit_payload = {
                    "questions": question_ids,
                    "student_answers": student_answers,
                    "subject": "math",
                    "time_taken": 180
                }
                
                submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                if submit_response.status_code == 200:
                    print("✅ Created practice test data")
                else:
                    print(f"❌ Failed to submit practice test: {submit_response.status_code}")
            else:
                print("❌ No questions generated")
        else:
            print(f"❌ Failed to generate practice test: {gen_response.status_code}")
    except Exception as e:
        print(f"❌ Exception creating practice test: {str(e)}")
    
    # Create notes
    try:
        notes_url = f"{API_URL}/notes/generate"
        notes_payload = {
            "subject": "math",
            "topic": "Quadratic Equations",
            "grade_level": "10th"
        }
        
        notes_response = requests.post(notes_url, json=notes_payload, headers=headers)
        if notes_response.status_code == 200:
            print("✅ Created notes data")
        else:
            print(f"❌ Failed to create notes: {notes_response.status_code}")
    except Exception as e:
        print(f"❌ Exception creating notes: {str(e)}")

def test_endpoints(token):
    """Test all the specific endpoints mentioned in the review"""
    print("\n🔍 Testing Modern UI Component Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("Dashboard", f"{API_URL}/dashboard"),
        ("Practice Results", f"{API_URL}/practice/results"),
        ("Strengths & Weaknesses", f"{API_URL}/student/analytics/strengths-weaknesses"),
        ("Performance Trends", f"{API_URL}/student/analytics/performance-trends"),
        ("Subject Breakdown", f"{API_URL}/student/analytics/subject-breakdown"),
        ("Learning Insights", f"{API_URL}/student/analytics/learning-insights"),
        ("Notes", f"{API_URL}/notes/")
    ]
    
    results = {}
    
    for name, url in endpoints:
        try:
            print(f"\n  🔍 Testing {name}...")
            
            # Test with authentication
            response = requests.get(url, headers=headers)
            print(f"    With Auth: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ {name} working - Response type: {type(data)}")
                
                # Show some details about the response
                if isinstance(data, list):
                    print(f"    📊 Array with {len(data)} items")
                elif isinstance(data, dict):
                    print(f"    📊 Object with keys: {list(data.keys())[:5]}")
                
                results[name] = {"status": "working", "response_type": type(data).__name__}
            else:
                print(f"    ❌ {name} failed: {response.status_code}")
                print(f"    Error: {response.text[:200]}")
                results[name] = {"status": "failed", "error": f"HTTP {response.status_code}"}
            
            # Test without authentication
            no_auth_response = requests.get(url)
            print(f"    No Auth: {no_auth_response.status_code}")
            
            if no_auth_response.status_code in [401, 403]:
                print(f"    ✅ Properly requires authentication")
            else:
                print(f"    ⚠️ Doesn't require authentication")
                
        except Exception as e:
            print(f"    ❌ Exception testing {name}: {str(e)}")
            results[name] = {"status": "error", "error": str(e)}
    
    return results

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 MODERN UI COMPONENTS API ENDPOINT TESTING")
    print("=" * 60)
    
    # Create test user
    token, user_id = create_test_user()
    if not token:
        print("❌ Cannot proceed without test user")
        return
    
    # Create test data
    create_test_data(token)
    
    # Test endpoints
    results = test_endpoints(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    working_count = sum(1 for r in results.values() if r.get("status") == "working")
    total_count = len(results)
    
    print(f"Total Endpoints Tested: {total_count}")
    print(f"Working Endpoints: {working_count}")
    print(f"Success Rate: {(working_count/total_count)*100:.1f}%")
    
    print("\nDetailed Results:")
    for endpoint, result in results.items():
        status = result.get("status", "unknown")
        if status == "working":
            print(f"  ✅ {endpoint}: WORKING")
        else:
            error = result.get("error", "Unknown error")
            print(f"  ❌ {endpoint}: FAILED - {error}")
    
    if working_count == total_count:
        print("\n🎉 ALL ENDPOINTS ARE WORKING CORRECTLY!")
    elif working_count >= total_count * 0.8:
        print(f"\n✅ Most endpoints working ({working_count}/{total_count})")
    else:
        print(f"\n⚠️ Several endpoints need attention ({working_count}/{total_count})")

if __name__ == "__main__":
    main()
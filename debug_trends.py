#!/usr/bin/env python3
"""
Debug the performance trends endpoint issue
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

def debug_trends():
    print("🔍 Debugging Performance Trends Endpoint...")
    
    # Register student
    register_url = f"{API_URL}/auth/register"
    register_payload = {
        "email": f"debug_trends_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Debug Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    response = requests.post(register_url, json=register_payload)
    if response.status_code != 200:
        print(f"❌ Failed to register: {response.status_code}")
        return False
    
    data = response.json()
    token = data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create some practice test data first
    print("Creating practice test data...")
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
            student_answers = {}
            question_ids = []
            for question in questions:
                question_id = question.get("id")
                question_ids.append(question_id)
                student_answers[question_id] = question.get("correct_answer")
            
            submit_url = f"{API_URL}/practice/submit"
            submit_payload = {
                "questions": question_ids,
                "student_answers": student_answers,
                "subject": "math",
                "time_taken": 300
            }
            
            submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
            if submit_response.status_code == 200:
                print("✅ Created practice test data")
            else:
                print(f"❌ Failed to submit test: {submit_response.status_code}")
    
    # Now test performance trends
    url = f"{API_URL}/student/analytics/performance-trends?days=7"
    response = requests.get(url, headers=headers)
    
    print(f"📈 Performance Trends Response: {response.status_code}")
    print(f"📈 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Response: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
        
        # Try to get more debug info
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")
    
    return response.status_code == 200

if __name__ == "__main__":
    debug_trends()
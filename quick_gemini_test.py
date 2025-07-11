#!/usr/bin/env python3
"""
Quick test to check if Gemini API is working with the new model
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

# Create a student account and test practice generation
def quick_test():
    # Register student
    student_data = {
        "email": "quicktest@test.com",
        "password": "TestPassword123!",
        "name": "Quick Test Student",
        "user_type": "student",
        "grade_level": "10th",
        "school_name": "Test School"
    }
    
    try:
        # Register
        response = requests.post(f"{API_URL}/auth/register", json=student_data, timeout=10)
        if response.status_code not in [200, 201]:
            print(f"Registration failed: {response.status_code}")
            return
        
        token = response.json().get("access_token")
        if not token:
            print("No token received")
            return
        
        # Test practice generation
        headers = {"Authorization": f"Bearer {token}"}
        test_request = {
            "subject": "math",
            "topics": ["Basic Math"],
            "difficulty": "easy",
            "question_count": 1,
            "question_types": ["mcq"]
        }
        
        print("Testing practice generation...")
        response = requests.post(f"{API_URL}/practice/generate", json=test_request, headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Generated {len(data.get('questions', []))} questions")
            if data.get('questions'):
                first_q = data['questions'][0]
                print(f"First question ID: {first_q.get('id', 'N/A')}")
                if 'fallback' in first_q.get('id', '').lower():
                    print("⚠️ Using fallback questions - Gemini API may not be working")
                else:
                    print("✅ AI-generated questions received")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
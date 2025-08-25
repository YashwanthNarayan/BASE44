#!/usr/bin/env python3
"""
Quick test to verify practice test submission and results retrieval are working correctly
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

def test_practice_test_submission():
    """Test the complete practice test flow: generate -> submit -> retrieve results"""
    print("🔍 Testing Practice Test Submission Flow...")
    
    # Register test student
    register_url = f"{API_URL}/auth/register"
    register_payload = {
        "email": f"submission_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Submission Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    try:
        register_response = requests.post(register_url, json=register_payload)
        if register_response.status_code != 200:
            print(f"❌ Failed to register student: {register_response.status_code}")
            return False
        
        student_data = register_response.json()
        student_token = student_data.get("access_token")
        student_id = student_data.get("user", {}).get("id")
        headers = {"Authorization": f"Bearer {student_token}"}
        
        print(f"✅ Registered student: {student_id}")
        
        # Generate practice test
        generate_url = f"{API_URL}/practice/generate"
        generate_payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        generate_response = requests.post(generate_url, json=generate_payload, headers=headers)
        if generate_response.status_code != 200:
            print(f"❌ Failed to generate test: {generate_response.status_code}")
            return False
        
        generate_data = generate_response.json()
        questions = generate_data.get("questions", [])
        print(f"✅ Generated {len(questions)} questions")
        
        # Submit practice test
        submit_url = f"{API_URL}/practice/submit"
        student_answers = {}
        question_ids = []
        
        for question in questions:
            question_id = question.get("id")
            question_ids.append(question_id)
            # Use correct answer for testing
            student_answers[question_id] = question.get("correct_answer")
        
        submit_payload = {
            "questions": question_ids,
            "student_answers": student_answers,
            "subject": "math",
            "time_taken": 300
        }
        
        submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
        if submit_response.status_code != 200:
            print(f"❌ Failed to submit test: {submit_response.status_code} - {submit_response.text}")
            return False
        
        submit_data = submit_response.json()
        attempt_id = submit_data.get("attempt_id")
        score = submit_data.get("score")
        print(f"✅ Submitted test - Score: {score}%, Attempt ID: {attempt_id}")
        
        # Get detailed results
        results_url = f"{API_URL}/practice/results/{attempt_id}"
        results_response = requests.get(results_url, headers=headers)
        if results_response.status_code != 200:
            print(f"❌ Failed to get results: {results_response.status_code}")
            return False
        
        results_data = results_response.json()
        print(f"✅ Retrieved detailed results - Score: {results_data.get('score')}%")
        
        # Get practice results list
        list_url = f"{API_URL}/practice/results"
        list_response = requests.get(list_url, headers=headers)
        if list_response.status_code != 200:
            print(f"❌ Failed to get results list: {list_response.status_code}")
            return False
        
        list_data = list_response.json()
        print(f"✅ Retrieved results list - {len(list_data)} attempts found")
        
        # Get subject stats
        stats_url = f"{API_URL}/practice/stats/math"
        stats_response = requests.get(stats_url, headers=headers)
        if stats_response.status_code != 200:
            print(f"❌ Failed to get stats: {stats_response.status_code}")
            return False
        
        stats_data = stats_response.json()
        print(f"✅ Retrieved subject stats - {stats_data.get('total_tests')} tests, {stats_data.get('average_score')}% avg")
        
        print("✅ Practice test submission flow working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in practice test submission test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_practice_test_submission()
    if not success:
        exit(1)
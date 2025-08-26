#!/usr/bin/env python3
"""
Quick test for Performance Trends endpoint fix
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

def test_performance_trends():
    print("🔍 Testing Performance Trends Endpoint Fix...")
    
    # Register student
    register_url = f"{API_URL}/auth/register"
    register_payload = {
        "email": f"trends_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Test Student",
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
    
    # Test performance trends with different days parameters
    test_cases = [7, 14, 30, 60]
    
    for days in test_cases:
        url = f"{API_URL}/student/analytics/performance-trends?days={days}"
        response = requests.get(url, headers=headers)
        
        print(f"📈 Performance Trends ({days} days): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Trend direction: {data.get('trend_direction')}")
            print(f"   Total tests: {data.get('total_tests_period')}")
            print(f"   Period days: {data.get('period_days')}")
        else:
            print(f"❌ Failed: {response.text}")
            return False
    
    print("🎉 All performance trends tests passed!")
    return True

if __name__ == "__main__":
    test_performance_trends()
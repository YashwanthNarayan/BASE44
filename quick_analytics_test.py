#!/usr/bin/env python3
"""
Quick Analytics Data Format Test
===============================
Focused test to compare Progress vs Analytics endpoint data structures
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 Quick Analytics Data Format Test")
print(f"🔍 Using API URL: {API_URL}")

def register_test_user():
    """Register a test user and return token"""
    register_url = f"{API_URL}/auth/register"
    student_email = f"quick_test_{uuid.uuid4()}@example.com"
    
    register_payload = {
        "email": student_email,
        "password": "TestPass123!",
        "name": "Quick Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    try:
        response = requests.post(register_url, json=register_payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print(f"✅ Registered user: {user_id}")
            return token, user_id
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None, None

def test_endpoints_with_auth(token):
    """Test all endpoints with authentication"""
    if not token:
        print("❌ No token available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    endpoints_to_test = [
        # Progress endpoints
        ("Progress Results", f"{API_URL}/practice/results"),
        ("Progress Stats Math", f"{API_URL}/practice/stats/math"),
        
        # Analytics endpoints  
        ("Analytics Strengths/Weaknesses", f"{API_URL}/student/analytics/strengths-weaknesses"),
        ("Analytics Performance Trends", f"{API_URL}/student/analytics/performance-trends"),
        ("Analytics Subject Breakdown", f"{API_URL}/student/analytics/subject-breakdown"),
        ("Analytics Learning Insights", f"{API_URL}/student/analytics/learning-insights"),
    ]
    
    results = {}
    
    for name, url in endpoints_to_test:
        print(f"\n📊 Testing {name}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS")
                print(f"   Data Type: {type(data).__name__}")
                
                if isinstance(data, dict):
                    print(f"   Fields: {list(data.keys())}")
                    # Check for empty data
                    empty_fields = []
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) == 0:
                            empty_fields.append(key)
                        elif value is None or value == "":
                            empty_fields.append(key)
                    
                    if empty_fields:
                        print(f"   ⚠️  Empty fields: {empty_fields}")
                    
                    # Show sample data structure
                    print(f"   📋 Sample structure:")
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"     - {key}: list[{len(value)}] {type(value[0]).__name__ if value else 'empty'}")
                        elif isinstance(value, dict):
                            print(f"     - {key}: dict with keys: {list(value.keys())}")
                        else:
                            print(f"     - {key}: {type(value).__name__} = {str(value)[:30]}...")
                
                elif isinstance(data, list):
                    print(f"   Array Length: {len(data)}")
                    if data:
                        print(f"   Item Type: {type(data[0]).__name__}")
                        if isinstance(data[0], dict):
                            print(f"   Item Fields: {list(data[0].keys())}")
                
                results[name] = {
                    "status": "success",
                    "data": data,
                    "data_type": type(data).__name__
                }
                
            elif response.status_code == 401:
                print(f"   ❌ AUTHENTICATION ERROR")
                results[name] = {"status": "auth_error", "code": 401}
                
            elif response.status_code == 403:
                print(f"   ❌ FORBIDDEN")
                results[name] = {"status": "forbidden", "code": 403}
                
            else:
                print(f"   ❌ ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                results[name] = {
                    "status": "error", 
                    "code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results[name] = {"status": "exception", "error": str(e)}
    
    return results

def analyze_results(results):
    """Analyze the test results"""
    print(f"\n🎯 ANALYSIS SUMMARY:")
    print(f"=" * 50)
    
    progress_endpoints = [k for k in results.keys() if k.startswith("Progress")]
    analytics_endpoints = [k for k in results.keys() if k.startswith("Analytics")]
    
    print(f"\n📊 PROGRESS ENDPOINTS:")
    progress_working = 0
    for endpoint in progress_endpoints:
        result = results[endpoint]
        status = result.get("status")
        if status == "success":
            print(f"   ✅ {endpoint}: Working")
            progress_working += 1
            
            # Show data details
            data = result.get("data")
            if isinstance(data, list):
                print(f"      Data: Array with {len(data)} items")
            elif isinstance(data, dict):
                print(f"      Data: Object with keys: {list(data.keys())}")
        else:
            print(f"   ❌ {endpoint}: {status}")
    
    print(f"\n📈 ANALYTICS ENDPOINTS:")
    analytics_working = 0
    for endpoint in analytics_endpoints:
        result = results[endpoint]
        status = result.get("status")
        if status == "success":
            print(f"   ✅ {endpoint}: Working")
            analytics_working += 1
            
            # Show data details
            data = result.get("data")
            if isinstance(data, list):
                print(f"      Data: Array with {len(data)} items")
            elif isinstance(data, dict):
                print(f"      Data: Object with keys: {list(data.keys())}")
                
                # Check for empty analytics data
                empty_count = 0
                for key, value in data.items():
                    if isinstance(value, list) and len(value) == 0:
                        empty_count += 1
                    elif value is None or value == "":
                        empty_count += 1
                
                if empty_count > 0:
                    print(f"      ⚠️  {empty_count} empty/null fields detected")
        else:
            print(f"   ❌ {endpoint}: {status}")
            if result.get("error"):
                print(f"      Error: {result['error'][:100]}...")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"   Progress Working: {progress_working}/{len(progress_endpoints)}")
    print(f"   Analytics Working: {analytics_working}/{len(analytics_endpoints)}")
    
    if progress_working > 0 and analytics_working == 0:
        print(f"   🚨 ISSUE: Progress works but Analytics completely fails")
        print(f"   🔍 Likely cause: Analytics backend processing issue")
        
    elif progress_working > 0 and analytics_working > 0:
        print(f"   ✅ Both systems responding")
        print(f"   🔍 Check for empty data in analytics responses")
        
        # Compare data structures
        progress_data = None
        analytics_data = None
        
        for endpoint in progress_endpoints:
            if results[endpoint].get("status") == "success":
                progress_data = results[endpoint].get("data")
                break
        
        for endpoint in analytics_endpoints:
            if results[endpoint].get("status") == "success":
                analytics_data = results[endpoint].get("data")
                break
        
        if progress_data and analytics_data:
            print(f"\n📋 DATA STRUCTURE COMPARISON:")
            print(f"   Progress data type: {type(progress_data).__name__}")
            print(f"   Analytics data type: {type(analytics_data).__name__}")
            
            if isinstance(progress_data, list) and len(progress_data) > 0:
                print(f"   Progress has {len(progress_data)} items")
                if isinstance(progress_data[0], dict):
                    print(f"   Progress item fields: {list(progress_data[0].keys())}")
            
            if isinstance(analytics_data, dict):
                print(f"   Analytics fields: {list(analytics_data.keys())}")
                
    elif progress_working == 0 and analytics_working == 0:
        print(f"   🚨 CRITICAL: Both systems failing - authentication issue?")
        
    return {
        "progress_working": progress_working,
        "analytics_working": analytics_working,
        "total_progress": len(progress_endpoints),
        "total_analytics": len(analytics_endpoints)
    }

def main():
    """Main test function"""
    print("🚀 Starting Quick Analytics Test...")
    
    # Register user
    token, user_id = register_test_user()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test endpoints
    results = test_endpoints_with_auth(token)
    
    # Analyze results
    summary = analyze_results(results)
    
    print(f"\n✅ Test Complete!")
    return results, summary

if __name__ == "__main__":
    main()
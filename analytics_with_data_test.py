#!/usr/bin/env python3
"""
Analytics with Real Data Test
============================
Test analytics endpoints after creating actual practice test data
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 Analytics with Real Data Test")
print(f"🔍 Using API URL: {API_URL}")

def register_test_user():
    """Register a test user and return token"""
    register_url = f"{API_URL}/auth/register"
    student_email = f"data_test_{uuid.uuid4()}@example.com"
    
    register_payload = {
        "email": student_email,
        "password": "TestPass123!",
        "name": "Data Test Student",
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

def create_practice_test_data(token):
    """Create actual practice test data"""
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Creating practice test data...")
    
    # Create multiple practice tests
    test_scenarios = [
        {"subject": "math", "topics": ["Algebra"], "difficulty": "medium", "target_score": 85},
        {"subject": "physics", "topics": ["Motion"], "difficulty": "easy", "target_score": 70},
        {"subject": "math", "topics": ["Geometry"], "difficulty": "hard", "target_score": 95}
    ]
    
    successful_tests = 0
    
    for i, scenario in enumerate(test_scenarios):
        print(f"  Creating test {i+1}: {scenario['subject']} - {scenario['topics'][0]}")
        
        # Generate practice test
        gen_url = f"{API_URL}/practice/generate"
        gen_payload = {
            "subject": scenario["subject"],
            "topics": scenario["topics"],
            "difficulty": scenario["difficulty"],
            "question_count": 3
        }
        
        try:
            gen_response = requests.get(gen_url, json=gen_payload, headers=headers, timeout=30)
            if gen_response.status_code != 200:
                print(f"    ❌ Failed to generate: {gen_response.status_code}")
                continue
            
            gen_data = gen_response.json()
            questions = gen_data.get("questions", [])
            
            if not questions:
                print(f"    ❌ No questions generated")
                continue
            
            print(f"    ✅ Generated {len(questions)} questions")
            
            # Create student answers based on target score
            student_answers = {}
            question_ids = []
            correct_count = int(len(questions) * scenario["target_score"] / 100)
            
            for j, question in enumerate(questions):
                question_id = question.get("id")
                question_ids.append(question_id)
                
                # Give correct answer for first 'correct_count' questions
                if j < correct_count:
                    student_answers[question_id] = question.get("correct_answer")
                else:
                    # Give wrong answer
                    student_answers[question_id] = "Wrong Answer"
            
            # Submit the test
            submit_url = f"{API_URL}/practice/submit"
            submit_payload = {
                "test_id": f"test_{uuid.uuid4()}",
                "questions": question_ids,
                "student_answers": student_answers,
                "time_taken": 300,
                "subject": scenario["subject"]
            }
            
            submit_response = requests.post(submit_url, json=submit_payload, headers=headers, timeout=30)
            if submit_response.status_code == 200:
                submit_data = submit_response.json()
                actual_score = submit_data.get("score", 0)
                print(f"    ✅ Test submitted - Score: {actual_score}%")
                successful_tests += 1
            else:
                print(f"    ❌ Failed to submit: {submit_response.status_code}")
                print(f"    Error: {submit_response.text[:200]}")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
    
    print(f"✅ Created {successful_tests}/{len(test_scenarios)} practice tests")
    return successful_tests > 0

def test_all_endpoints(token):
    """Test all endpoints after creating data"""
    if not token:
        return {}
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing all endpoints with real data...")
    
    # Test endpoints
    endpoints_to_test = [
        # Progress endpoints
        ("Progress Results", f"{API_URL}/practice/results"),
        ("Progress Stats Math", f"{API_URL}/practice/stats/math"),
        ("Progress Stats Physics", f"{API_URL}/practice/stats/physics"),
        
        # Analytics endpoints  
        ("Analytics Strengths/Weaknesses", f"{API_URL}/student/analytics/strengths-weaknesses"),
        ("Analytics Performance Trends", f"{API_URL}/student/analytics/performance-trends"),
        ("Analytics Subject Breakdown", f"{API_URL}/student/analytics/subject-breakdown"),
        ("Analytics Learning Insights", f"{API_URL}/student/analytics/learning-insights"),
    ]
    
    results = {}
    
    for name, url in endpoints_to_test:
        print(f"\n📊 Testing {name}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS")
                
                # Analyze data content
                if isinstance(data, list):
                    print(f"   📋 Array with {len(data)} items")
                    if data:
                        print(f"   📋 Sample item: {type(data[0]).__name__}")
                        if isinstance(data[0], dict):
                            print(f"   📋 Item fields: {list(data[0].keys())}")
                            # Show sample values
                            sample = data[0]
                            for key, value in sample.items():
                                print(f"     - {key}: {type(value).__name__} = {str(value)[:40]}...")
                
                elif isinstance(data, dict):
                    print(f"   📋 Object with {len(data)} fields")
                    
                    # Check for populated vs empty fields
                    populated_fields = []
                    empty_fields = []
                    
                    for key, value in data.items():
                        if isinstance(value, list):
                            if len(value) > 0:
                                populated_fields.append(f"{key}[{len(value)}]")
                            else:
                                empty_fields.append(key)
                        elif isinstance(value, dict):
                            if value:
                                populated_fields.append(f"{key}(dict)")
                            else:
                                empty_fields.append(key)
                        elif value is not None and value != "":
                            populated_fields.append(key)
                        else:
                            empty_fields.append(key)
                    
                    if populated_fields:
                        print(f"   ✅ Populated fields: {populated_fields}")
                    if empty_fields:
                        print(f"   ⚠️  Empty fields: {empty_fields}")
                    
                    # Show sample data for key fields
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"     - {key}: [{len(value)} items] {type(value[0]).__name__}")
                        elif isinstance(value, dict) and value:
                            print(f"     - {key}: {value}")
                        elif not isinstance(value, (list, dict)):
                            print(f"     - {key}: {type(value).__name__} = {str(value)[:40]}...")
                
                results[name] = {
                    "status": "success",
                    "data": data,
                    "populated": len([k for k, v in data.items() if v]) if isinstance(data, dict) else len(data) if isinstance(data, list) else 1
                }
                
            else:
                print(f"   ❌ ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                results[name] = {"status": "error", "code": response.status_code}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results[name] = {"status": "exception", "error": str(e)}
    
    return results

def analyze_data_comparison(results):
    """Compare Progress vs Analytics data"""
    print(f"\n🎯 DATA COMPARISON ANALYSIS:")
    print(f"=" * 60)
    
    # Separate results
    progress_results = {k: v for k, v in results.items() if k.startswith("Progress")}
    analytics_results = {k: v for k, v in results.items() if k.startswith("Analytics")}
    
    print(f"\n📊 PROGRESS ENDPOINTS ANALYSIS:")
    progress_has_data = False
    for name, result in progress_results.items():
        if result.get("status") == "success":
            data = result.get("data")
            populated = result.get("populated", 0)
            
            print(f"   ✅ {name}: {populated} populated fields/items")
            
            if isinstance(data, list) and len(data) > 0:
                progress_has_data = True
                print(f"      📋 Contains {len(data)} practice test results")
                
                # Show structure of first result
                if isinstance(data[0], dict):
                    print(f"      📋 Result structure: {list(data[0].keys())}")
                    
            elif isinstance(data, dict):
                non_zero_fields = [k for k, v in data.items() if v and v != 0 and v != []]
                if non_zero_fields:
                    progress_has_data = True
                    print(f"      📋 Non-empty fields: {non_zero_fields}")
        else:
            print(f"   ❌ {name}: {result.get('status')}")
    
    print(f"\n📈 ANALYTICS ENDPOINTS ANALYSIS:")
    analytics_has_data = False
    analytics_populated_count = 0
    
    for name, result in analytics_results.items():
        if result.get("status") == "success":
            data = result.get("data")
            populated = result.get("populated", 0)
            
            print(f"   ✅ {name}: {populated} populated fields")
            
            if populated > 0:
                analytics_has_data = True
                analytics_populated_count += populated
                
                # Show what's populated
                if isinstance(data, dict):
                    populated_fields = []
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            populated_fields.append(f"{key}[{len(value)}]")
                        elif isinstance(value, dict) and value:
                            populated_fields.append(f"{key}(dict)")
                        elif value is not None and value != "" and value != 0:
                            populated_fields.append(key)
                    
                    if populated_fields:
                        print(f"      📋 Populated: {populated_fields}")
        else:
            print(f"   ❌ {name}: {result.get('status')}")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"   Progress has data: {'Yes' if progress_has_data else 'No'}")
    print(f"   Analytics has data: {'Yes' if analytics_has_data else 'No'}")
    print(f"   Analytics populated fields total: {analytics_populated_count}")
    
    if progress_has_data and not analytics_has_data:
        print(f"\n🚨 CONFIRMED ISSUE:")
        print(f"   ✅ Progress endpoints contain practice test data")
        print(f"   ❌ Analytics endpoints return empty/default responses")
        print(f"   🔍 Root cause: Analytics not processing practice test data")
        
    elif progress_has_data and analytics_has_data:
        print(f"\n✅ BOTH SYSTEMS WORKING:")
        print(f"   Both Progress and Analytics contain data")
        print(f"   Issue may be frontend-specific")
        
    elif not progress_has_data and not analytics_has_data:
        print(f"\n⚠️  NO DATA IN EITHER SYSTEM:")
        print(f"   Neither Progress nor Analytics have data")
        print(f"   May need more time for data to populate")
        
    return {
        "progress_has_data": progress_has_data,
        "analytics_has_data": analytics_has_data,
        "analytics_populated_count": analytics_populated_count
    }

def main():
    """Main test function"""
    print("🚀 Starting Analytics with Real Data Test...")
    
    # Register user
    token, user_id = register_test_user()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Create practice test data
    data_created = create_practice_test_data(token)
    if not data_created:
        print("⚠️  No practice test data created, testing with empty state")
    
    # Wait a moment for data to be processed
    print("⏳ Waiting 3 seconds for data processing...")
    time.sleep(3)
    
    # Test all endpoints
    results = test_all_endpoints(token)
    
    # Analyze comparison
    summary = analyze_data_comparison(results)
    
    print(f"\n✅ Test Complete!")
    return results, summary

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Analytics Data Format Investigation Test
========================================

This test investigates the data format mismatch issue between Progress and Analytics features.
User reports:
1. Practice test results ARE showing up in Progress (backend working)
2. Analytics features are NOT showing data (suggests data format mismatch)

We will test and compare the exact data structures returned by:
- Progress endpoints: /api/practice/results, /api/practice/stats/{subject}
- Analytics endpoints: /api/student/analytics/* (4 endpoints)
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 Testing Analytics Data Format Investigation")
print(f"🔍 Using API URL: {API_URL}")

class AnalyticsDataFormatTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = {}
        
    def register_and_login_student(self):
        """Register a test student and get authentication token"""
        print("\n🔍 Step 1: Registering test student...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        student_email = f"analytics_test_{uuid.uuid4()}@example.com"
        
        register_payload = {
            "email": student_email,
            "password": "TestPass123!",
            "name": "Analytics Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student registered successfully: {self.student_id}")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def create_test_data(self):
        """Create practice test data to ensure we have data for analytics"""
        print("\n🔍 Step 2: Creating practice test data...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Generate and submit multiple practice tests to create analytics data
        test_scenarios = [
            {"subject": "math", "topics": ["Algebra"], "difficulty": "medium", "score_target": 85},
            {"subject": "physics", "topics": ["Motion"], "difficulty": "easy", "score_target": 70},
            {"subject": "math", "topics": ["Geometry"], "difficulty": "hard", "score_target": 95},
            {"subject": "chemistry", "topics": ["Acids and Bases"], "difficulty": "medium", "score_target": 80}
        ]
        
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
                gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
                if gen_response.status_code != 200:
                    print(f"    ❌ Failed to generate test: {gen_response.status_code}")
                    continue
                
                gen_data = gen_response.json()
                questions = gen_data.get("questions", [])
                
                if not questions:
                    print(f"    ❌ No questions generated")
                    continue
                
                # Create student answers (simulate correct answers based on target score)
                student_answers = {}
                question_ids = []
                correct_count = int(len(questions) * scenario["score_target"] / 100)
                
                for j, question in enumerate(questions):
                    question_id = question.get("id")
                    question_ids.append(question_id)
                    
                    # Give correct answer for first 'correct_count' questions
                    if j < correct_count:
                        student_answers[question_id] = question.get("correct_answer")
                    else:
                        # Give wrong answer for remaining questions
                        options = question.get("options", [])
                        correct_answer = question.get("correct_answer")
                        wrong_options = [opt for opt in options if opt != correct_answer]
                        student_answers[question_id] = wrong_options[0] if wrong_options else "Wrong Answer"
                
                # Submit the test
                submit_url = f"{API_URL}/practice/submit"
                submit_payload = {
                    "test_id": f"test_{uuid.uuid4()}",
                    "questions": question_ids,
                    "student_answers": student_answers,
                    "time_taken": 300,
                    "subject": scenario["subject"]
                }
                
                submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                if submit_response.status_code == 200:
                    submit_data = submit_response.json()
                    print(f"    ✅ Test submitted - Score: {submit_data.get('score', 0)}%")
                else:
                    print(f"    ❌ Failed to submit test: {submit_response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Error creating test {i+1}: {str(e)}")
        
        print("✅ Test data creation completed")
        return True
    
    def test_progress_endpoints(self):
        """Test Progress endpoints and capture their data structure"""
        print("\n🔍 Step 3: Testing Progress Endpoints...")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test 1: GET /api/practice/results
        print("\n  📊 Testing GET /api/practice/results")
        try:
            response = requests.get(f"{API_URL}/practice/results", headers=headers)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ SUCCESS - Data type: {type(data)}")
                print(f"    📋 Number of results: {len(data) if isinstance(data, list) else 'Not a list'}")
                
                if isinstance(data, list) and len(data) > 0:
                    sample_result = data[0]
                    print(f"    🔍 Sample result structure:")
                    for key, value in sample_result.items():
                        print(f"      - {key}: {type(value).__name__} = {str(value)[:50]}...")
                
                self.test_results["progress_results"] = {
                    "status": "success",
                    "data_type": type(data).__name__,
                    "count": len(data) if isinstance(data, list) else 0,
                    "sample_fields": list(data[0].keys()) if isinstance(data, list) and len(data) > 0 else [],
                    "raw_sample": data[0] if isinstance(data, list) and len(data) > 0 else None
                }
            else:
                print(f"    ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
                self.test_results["progress_results"] = {
                    "status": "failed",
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"    ❌ EXCEPTION: {str(e)}")
            self.test_results["progress_results"] = {
                "status": "exception",
                "error": str(e)
            }
        
        # Test 2: GET /api/practice/stats/{subject} for each subject
        subjects_to_test = ["math", "physics", "chemistry"]
        
        for subject in subjects_to_test:
            print(f"\n  📊 Testing GET /api/practice/stats/{subject}")
            try:
                response = requests.get(f"{API_URL}/practice/stats/{subject}", headers=headers)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ SUCCESS - Data type: {type(data)}")
                    print(f"    🔍 Stats structure for {subject}:")
                    for key, value in data.items():
                        if key == "recent_tests" and isinstance(value, list):
                            print(f"      - {key}: list with {len(value)} items")
                        else:
                            print(f"      - {key}: {type(value).__name__} = {str(value)}")
                    
                    self.test_results[f"progress_stats_{subject}"] = {
                        "status": "success",
                        "data_type": type(data).__name__,
                        "fields": list(data.keys()),
                        "raw_data": data
                    }
                else:
                    print(f"    ❌ FAILED - Status: {response.status_code}, Error: {response.text}")
                    self.test_results[f"progress_stats_{subject}"] = {
                        "status": "failed",
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"    ❌ EXCEPTION: {str(e)}")
                self.test_results[f"progress_stats_{subject}"] = {
                    "status": "exception",
                    "error": str(e)
                }
    
    def test_analytics_endpoints(self):
        """Test Analytics endpoints and capture their data structure"""
        print("\n🔍 Step 4: Testing Analytics Endpoints...")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        analytics_endpoints = [
            {
                "name": "Strengths & Weaknesses",
                "url": f"{API_URL}/student/analytics/strengths-weaknesses",
                "key": "strengths_weaknesses"
            },
            {
                "name": "Performance Trends",
                "url": f"{API_URL}/student/analytics/performance-trends",
                "key": "performance_trends"
            },
            {
                "name": "Subject Breakdown",
                "url": f"{API_URL}/student/analytics/subject-breakdown",
                "key": "subject_breakdown"
            },
            {
                "name": "Learning Insights",
                "url": f"{API_URL}/student/analytics/learning-insights",
                "key": "learning_insights"
            }
        ]
        
        for endpoint in analytics_endpoints:
            print(f"\n  📊 Testing {endpoint['name']}: {endpoint['url']}")
            try:
                response = requests.get(endpoint["url"], headers=headers)
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ SUCCESS - Data type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"    🔍 Response structure:")
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"      - {key}: list with {len(value)} items")
                                if len(value) > 0:
                                    print(f"        Sample item: {type(value[0]).__name__}")
                            elif isinstance(value, dict):
                                print(f"      - {key}: dict with {len(value)} keys: {list(value.keys())}")
                            else:
                                print(f"      - {key}: {type(value).__name__} = {str(value)[:50]}...")
                    
                    self.test_results[f"analytics_{endpoint['key']}"] = {
                        "status": "success",
                        "data_type": type(data).__name__,
                        "fields": list(data.keys()) if isinstance(data, dict) else [],
                        "raw_data": data
                    }
                else:
                    print(f"    ❌ FAILED - Status: {response.status_code}")
                    print(f"    Error: {response.text}")
                    self.test_results[f"analytics_{endpoint['key']}"] = {
                        "status": "failed",
                        "error": response.text,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                print(f"    ❌ EXCEPTION: {str(e)}")
                self.test_results[f"analytics_{endpoint['key']}"] = {
                    "status": "exception",
                    "error": str(e)
                }
    
    def analyze_data_format_differences(self):
        """Analyze and compare data formats between Progress and Analytics"""
        print("\n🔍 Step 5: Data Format Analysis...")
        
        print("\n📋 PROGRESS vs ANALYTICS DATA COMPARISON:")
        print("=" * 60)
        
        # Progress Results Analysis
        progress_results = self.test_results.get("progress_results", {})
        if progress_results.get("status") == "success":
            print(f"\n✅ PROGRESS RESULTS (/api/practice/results):")
            print(f"   - Status: Working ✅")
            print(f"   - Data Type: {progress_results.get('data_type')}")
            print(f"   - Count: {progress_results.get('count')} results")
            print(f"   - Fields: {progress_results.get('sample_fields')}")
            
            if progress_results.get("raw_sample"):
                sample = progress_results["raw_sample"]
                print(f"   - Sample Data Structure:")
                for key, value in sample.items():
                    print(f"     * {key}: {type(value).__name__}")
        else:
            print(f"\n❌ PROGRESS RESULTS: {progress_results.get('status', 'unknown')}")
        
        # Progress Stats Analysis
        print(f"\n✅ PROGRESS STATS (/api/practice/stats/{{subject}}):")
        for subject in ["math", "physics", "chemistry"]:
            stats_key = f"progress_stats_{subject}"
            stats_data = self.test_results.get(stats_key, {})
            if stats_data.get("status") == "success":
                print(f"   - {subject.upper()}: Working ✅")
                print(f"     Fields: {stats_data.get('fields')}")
            else:
                print(f"   - {subject.upper()}: {stats_data.get('status', 'unknown')} ❌")
        
        # Analytics Endpoints Analysis
        print(f"\n📊 ANALYTICS ENDPOINTS (/api/student/analytics/*):")
        analytics_endpoints = [
            ("strengths_weaknesses", "Strengths & Weaknesses"),
            ("performance_trends", "Performance Trends"),
            ("subject_breakdown", "Subject Breakdown"),
            ("learning_insights", "Learning Insights")
        ]
        
        working_analytics = 0
        total_analytics = len(analytics_endpoints)
        
        for key, name in analytics_endpoints:
            analytics_key = f"analytics_{key}"
            analytics_data = self.test_results.get(analytics_key, {})
            
            if analytics_data.get("status") == "success":
                print(f"   - {name}: Working ✅")
                print(f"     Fields: {analytics_data.get('fields')}")
                working_analytics += 1
                
                # Check if data is empty
                raw_data = analytics_data.get("raw_data", {})
                if isinstance(raw_data, dict):
                    empty_fields = []
                    for field, value in raw_data.items():
                        if isinstance(value, list) and len(value) == 0:
                            empty_fields.append(field)
                        elif value is None or value == "":
                            empty_fields.append(field)
                    
                    if empty_fields:
                        print(f"     ⚠️  Empty fields: {empty_fields}")
            else:
                print(f"   - {name}: {analytics_data.get('status', 'unknown')} ❌")
                if analytics_data.get("error"):
                    print(f"     Error: {analytics_data['error'][:100]}...")
        
        # Summary Analysis
        print(f"\n🎯 SUMMARY ANALYSIS:")
        print(f"=" * 40)
        
        progress_working = progress_results.get("status") == "success"
        analytics_working_rate = working_analytics / total_analytics * 100
        
        print(f"✅ Progress Feature: {'Working' if progress_working else 'Not Working'}")
        print(f"📊 Analytics Feature: {working_analytics}/{total_analytics} endpoints working ({analytics_working_rate:.1f}%)")
        
        if progress_working and working_analytics > 0:
            print(f"\n🔍 DATA FORMAT COMPARISON:")
            
            # Compare field structures
            progress_fields = set(progress_results.get("sample_fields", []))
            
            # Get analytics fields from working endpoints
            analytics_fields = set()
            for key, _ in analytics_endpoints:
                analytics_key = f"analytics_{key}"
                analytics_data = self.test_results.get(analytics_key, {})
                if analytics_data.get("status") == "success":
                    analytics_fields.update(analytics_data.get("fields", []))
            
            common_fields = progress_fields.intersection(analytics_fields)
            progress_only = progress_fields - analytics_fields
            analytics_only = analytics_fields - progress_fields
            
            print(f"   - Common fields: {list(common_fields)}")
            print(f"   - Progress-only fields: {list(progress_only)}")
            print(f"   - Analytics-only fields: {list(analytics_only)}")
            
        elif progress_working and working_analytics == 0:
            print(f"\n🚨 CRITICAL ISSUE IDENTIFIED:")
            print(f"   - Progress endpoints are working and returning data")
            print(f"   - Analytics endpoints are ALL failing")
            print(f"   - This suggests a backend issue with analytics processing")
            
        elif not progress_working and working_analytics > 0:
            print(f"\n🚨 UNEXPECTED SCENARIO:")
            print(f"   - Progress endpoints are failing")
            print(f"   - Analytics endpoints are working")
            print(f"   - This contradicts the user report")
            
        else:
            print(f"\n🚨 BOTH SYSTEMS FAILING:")
            print(f"   - Both Progress and Analytics endpoints are failing")
            print(f"   - This suggests a broader authentication or backend issue")
    
    def generate_detailed_report(self):
        """Generate a detailed report of findings"""
        print(f"\n📄 DETAILED INVESTIGATION REPORT:")
        print(f"=" * 50)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Report Generated: {timestamp}")
        print(f"Student ID: {self.student_id}")
        
        print(f"\n🔍 RAW TEST RESULTS:")
        for key, result in self.test_results.items():
            print(f"\n{key.upper()}:")
            if result.get("status") == "success":
                print(f"  ✅ Status: Success")
                if "raw_data" in result:
                    raw_data = result["raw_data"]
                    if isinstance(raw_data, dict):
                        print(f"  📊 Data Keys: {list(raw_data.keys())}")
                        # Show sample values for key fields
                        for k, v in raw_data.items():
                            if isinstance(v, list):
                                print(f"    - {k}: [{len(v)} items] {type(v[0]).__name__ if v else 'empty'}")
                            elif isinstance(v, (int, float, str)):
                                print(f"    - {k}: {v}")
                    elif isinstance(raw_data, list):
                        print(f"  📊 Array Length: {len(raw_data)}")
                        if raw_data:
                            print(f"  📊 Item Structure: {list(raw_data[0].keys()) if isinstance(raw_data[0], dict) else type(raw_data[0]).__name__}")
            else:
                print(f"  ❌ Status: {result.get('status', 'unknown')}")
                if result.get("error"):
                    print(f"  🚨 Error: {result['error']}")
        
        return self.test_results
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🚀 Starting Analytics Data Format Investigation...")
        
        # Step 1: Authentication
        if not self.register_and_login_student():
            print("❌ Failed to authenticate - cannot proceed")
            return False
        
        # Step 2: Create test data
        if not self.create_test_data():
            print("❌ Failed to create test data - proceeding anyway")
        
        # Step 3: Test Progress endpoints
        self.test_progress_endpoints()
        
        # Step 4: Test Analytics endpoints
        self.test_analytics_endpoints()
        
        # Step 5: Analyze differences
        self.analyze_data_format_differences()
        
        # Step 6: Generate report
        return self.generate_detailed_report()

if __name__ == "__main__":
    tester = AnalyticsDataFormatTester()
    results = tester.run_investigation()
    
    print(f"\n🎯 INVESTIGATION COMPLETE!")
    print(f"Check the detailed output above for data format analysis.")
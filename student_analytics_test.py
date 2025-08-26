#!/usr/bin/env python3
"""
Student Analytics Endpoints Testing
Testing the critical bug fix for 500 Internal Server Errors in student analytics service
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Add /api prefix to the backend URL
API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class StudentAnalyticsTest:
    """Test class for Student Analytics endpoints"""
    
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = []
        
    def register_student(self):
        """Register a student for testing analytics"""
        print("\n🔍 Setting up student account for analytics testing...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"analytics_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Kavya Sharma",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Registered student with ID: {self.student_id}")
                return True
            else:
                print(f"❌ Failed to register student: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error registering student: {str(e)}")
            return False

    def create_practice_test_data(self):
        """Create practice test data to have analytics to analyze"""
        if not self.student_token:
            return False
            
        print("\n🔍 Creating practice test data for analytics...")
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create tests for different subjects with varying scores
        test_scenarios = [
            {"subject": "math", "topics": ["Algebra"], "expected_score": 85},
            {"subject": "physics", "topics": ["Mechanics"], "expected_score": 70},
            {"subject": "chemistry", "topics": ["Organic Chemistry"], "expected_score": 60},
            {"subject": "math", "topics": ["Geometry"], "expected_score": 90},
            {"subject": "physics", "topics": ["Thermodynamics"], "expected_score": 75},
        ]
        
        successful_tests = 0
        
        for scenario in test_scenarios:
            try:
                # Generate practice test
                gen_url = f"{API_URL}/practice/generate"
                gen_payload = {
                    "subject": scenario["subject"],
                    "topics": scenario["topics"],
                    "difficulty": "medium",
                    "question_count": 3
                }
                
                gen_response = requests.post(gen_url, json=gen_payload, headers=headers)
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    questions = gen_data.get("questions", [])
                    
                    if questions:
                        # Create student answers to achieve target score
                        student_answers = {}
                        question_ids = []
                        correct_count = int(len(questions) * scenario["expected_score"] / 100)
                        
                        for i, question in enumerate(questions):
                            question_id = question.get("id")
                            question_ids.append(question_id)
                            
                            # Give correct answer for first 'correct_count' questions
                            if i < correct_count:
                                student_answers[question_id] = question.get("correct_answer")
                            else:
                                # Give wrong answer (pick first option that's not correct)
                                options = question.get("options", [])
                                correct_answer = question.get("correct_answer")
                                wrong_answer = next((opt for opt in options if opt != correct_answer), options[0] if options else "Wrong")
                                student_answers[question_id] = wrong_answer
                        
                        # Submit the test
                        submit_url = f"{API_URL}/practice/submit"
                        submit_payload = {
                            "questions": question_ids,
                            "student_answers": student_answers,
                            "subject": scenario["subject"],
                            "time_taken": 300
                        }
                        
                        submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                        
                        if submit_response.status_code == 200:
                            submit_data = submit_response.json()
                            print(f"✅ Created {scenario['subject']} test with score: {submit_data.get('score')}%")
                            successful_tests += 1
                        else:
                            print(f"❌ Failed to submit {scenario['subject']} test: {submit_response.status_code}")
                    else:
                        print(f"⚠️ No questions generated for {scenario['subject']}")
                else:
                    print(f"❌ Failed to generate {scenario['subject']} test: {gen_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating {scenario['subject']} test: {str(e)}")
        
        print(f"✅ Successfully created {successful_tests} practice tests for analytics")
        return successful_tests > 0

    def test_strengths_weaknesses_endpoint(self):
        """Test /api/student/analytics/strengths-weaknesses endpoint"""
        print("\n🔍 Testing Strengths & Weaknesses Analytics Endpoint...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/analytics/strengths-weaknesses"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📊 Strengths & Weaknesses Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Strengths & Weaknesses endpoint returns 200 OK (Fixed from 500 error!)")
                
                # Verify response structure
                required_fields = ["strengths", "weaknesses", "improving_areas", "declining_areas", "overall_performance", "recommendations"]
                for field in required_fields:
                    if field not in data:
                        print(f"⚠️ Missing field: {field}")
                        return False
                
                # Verify overall performance structure
                overall_perf = data.get("overall_performance", {})
                perf_fields = ["average_score", "total_tests", "subjects_tested"]
                for field in perf_fields:
                    if field not in overall_perf:
                        print(f"⚠️ Missing overall_performance field: {field}")
                        return False
                
                print(f"📈 Overall Performance: {overall_perf.get('average_score')}% avg, {overall_perf.get('total_tests')} tests, {overall_perf.get('subjects_tested')} subjects")
                print(f"💪 Strengths: {len(data.get('strengths', []))} identified")
                print(f"🎯 Weaknesses: {len(data.get('weaknesses', []))} identified")
                print(f"📊 Recommendations: {len(data.get('recommendations', []))} provided")
                
                self.test_results.append({
                    "endpoint": "strengths-weaknesses",
                    "status": "PASS",
                    "message": "Endpoint working correctly, returns comprehensive analysis"
                })
                return True
                
            else:
                print(f"❌ Strengths & Weaknesses endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append({
                    "endpoint": "strengths-weaknesses", 
                    "status": "FAIL",
                    "message": f"HTTP {response.status_code}: {response.text}"
                })
                return False
                
        except Exception as e:
            print(f"❌ Strengths & Weaknesses endpoint test failed: {str(e)}")
            self.test_results.append({
                "endpoint": "strengths-weaknesses",
                "status": "ERROR", 
                "message": str(e)
            })
            return False

    def test_performance_trends_endpoint(self):
        """Test /api/student/analytics/performance-trends endpoint"""
        print("\n🔍 Testing Performance Trends Analytics Endpoint...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        # Test with different time periods
        time_periods = [7, 14, 30, 60]
        
        for days in time_periods:
            url = f"{API_URL}/student/analytics/performance-trends?days={days}"
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            try:
                response = requests.get(url, headers=headers)
                print(f"📈 Performance Trends ({days} days) Response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Performance Trends ({days} days) endpoint returns 200 OK (Fixed from 500 error!)")
                    
                    # Verify response structure
                    required_fields = ["trend_data", "trend_direction", "total_tests_period", "period_days"]
                    for field in required_fields:
                        if field not in data:
                            print(f"⚠️ Missing field: {field}")
                            return False
                    
                    trend_data = data.get("trend_data", [])
                    print(f"📊 Trend Data: {len(trend_data)} weeks of data")
                    print(f"📈 Trend Direction: {data.get('trend_direction')}")
                    print(f"🧪 Total Tests in Period: {data.get('total_tests_period')}")
                    
                    # Verify trend data structure if present
                    if trend_data:
                        first_week = trend_data[0]
                        week_fields = ["week", "average_score", "test_count", "highest_score", "lowest_score"]
                        for field in week_fields:
                            if field not in first_week:
                                print(f"⚠️ Missing trend data field: {field}")
                                return False
                    
                    self.test_results.append({
                        "endpoint": f"performance-trends-{days}d",
                        "status": "PASS",
                        "message": f"Endpoint working correctly for {days} days period"
                    })
                    
                else:
                    print(f"❌ Performance Trends ({days} days) endpoint failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    self.test_results.append({
                        "endpoint": f"performance-trends-{days}d",
                        "status": "FAIL", 
                        "message": f"HTTP {response.status_code}: {response.text}"
                    })
                    return False
                    
            except Exception as e:
                print(f"❌ Performance Trends ({days} days) endpoint test failed: {str(e)}")
                self.test_results.append({
                    "endpoint": f"performance-trends-{days}d",
                    "status": "ERROR",
                    "message": str(e)
                })
                return False
        
        return True

    def test_subject_breakdown_endpoint(self):
        """Test /api/student/analytics/subject-breakdown endpoint"""
        print("\n🔍 Testing Subject Breakdown Analytics Endpoint...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/analytics/subject-breakdown"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📚 Subject Breakdown Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Subject Breakdown endpoint returns 200 OK (Fixed from 500 error!)")
                
                # Verify response structure
                required_fields = ["subject_breakdown", "total_subjects", "analysis_date"]
                for field in required_fields:
                    if field not in data:
                        print(f"⚠️ Missing field: {field}")
                        return False
                
                subject_breakdown = data.get("subject_breakdown", [])
                print(f"📊 Subject Breakdown: {len(subject_breakdown)} subjects analyzed")
                print(f"🔢 Total Subjects: {data.get('total_subjects')}")
                
                # Verify subject breakdown structure if present
                if subject_breakdown:
                    first_subject = subject_breakdown[0]
                    subject_fields = ["subject", "subject_display", "total_tests", "average_score", 
                                    "highest_score", "lowest_score", "performance_grade"]
                    for field in subject_fields:
                        if field not in first_subject:
                            print(f"⚠️ Missing subject breakdown field: {field}")
                            return False
                    
                    # Display subject performance
                    for subject in subject_breakdown:
                        print(f"  📖 {subject['subject_display']}: {subject['average_score']}% avg ({subject['total_tests']} tests) - Grade {subject['performance_grade']}")
                
                best_subject = data.get("best_subject")
                if best_subject:
                    print(f"🏆 Best Subject: {best_subject['subject_display']} with {best_subject['average_score']}% average")
                
                self.test_results.append({
                    "endpoint": "subject-breakdown",
                    "status": "PASS",
                    "message": "Endpoint working correctly, provides detailed subject analysis"
                })
                return True
                
            else:
                print(f"❌ Subject Breakdown endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append({
                    "endpoint": "subject-breakdown",
                    "status": "FAIL",
                    "message": f"HTTP {response.status_code}: {response.text}"
                })
                return False
                
        except Exception as e:
            print(f"❌ Subject Breakdown endpoint test failed: {str(e)}")
            self.test_results.append({
                "endpoint": "subject-breakdown",
                "status": "ERROR",
                "message": str(e)
            })
            return False

    def test_learning_insights_endpoint(self):
        """Test /api/student/analytics/learning-insights endpoint"""
        print("\n🔍 Testing Learning Insights Analytics Endpoint...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/student/analytics/learning-insights"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"💡 Learning Insights Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Learning Insights endpoint returns 200 OK (Fixed from 500 error!)")
                
                # Verify response structure
                required_fields = ["insights", "study_tips"]
                for field in required_fields:
                    if field not in data:
                        print(f"⚠️ Missing field: {field}")
                        return False
                
                insights = data.get("insights", [])
                study_tips = data.get("study_tips", [])
                recent_activity = data.get("recent_activity", {})
                
                print(f"💡 Insights: {len(insights)} personalized insights generated")
                print(f"📚 Study Tips: {len(study_tips)} tips provided")
                
                # Display insights
                for insight in insights:
                    insight_fields = ["type", "title", "message", "icon", "action"]
                    for field in insight_fields:
                        if field not in insight:
                            print(f"⚠️ Missing insight field: {field}")
                            return False
                    
                    print(f"  {insight['icon']} {insight['title']}: {insight['message']}")
                
                # Display recent activity if present
                if recent_activity:
                    print(f"📊 Recent Activity: {recent_activity.get('tests_taken', 0)} tests, {recent_activity.get('average_score', 0)}% avg, {recent_activity.get('subjects_practiced', 0)} subjects")
                
                self.test_results.append({
                    "endpoint": "learning-insights",
                    "status": "PASS", 
                    "message": "Endpoint working correctly, provides AI-powered insights"
                })
                return True
                
            else:
                print(f"❌ Learning Insights endpoint failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append({
                    "endpoint": "learning-insights",
                    "status": "FAIL",
                    "message": f"HTTP {response.status_code}: {response.text}"
                })
                return False
                
        except Exception as e:
            print(f"❌ Learning Insights endpoint test failed: {str(e)}")
            self.test_results.append({
                "endpoint": "learning-insights",
                "status": "ERROR",
                "message": str(e)
            })
            return False

    def test_authentication_requirements(self):
        """Test that all analytics endpoints require authentication"""
        print("\n🔍 Testing Authentication Requirements...")
        
        endpoints = [
            "strengths-weaknesses",
            "performance-trends",
            "subject-breakdown", 
            "learning-insights"
        ]
        
        auth_tests_passed = 0
        
        for endpoint in endpoints:
            url = f"{API_URL}/student/analytics/{endpoint}"
            
            try:
                # Test without authentication
                response = requests.get(url)
                print(f"🔒 {endpoint} (no auth): {response.status_code}")
                
                if response.status_code in [401, 403]:
                    print(f"✅ {endpoint} properly requires authentication")
                    auth_tests_passed += 1
                else:
                    print(f"❌ {endpoint} should require authentication but returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing {endpoint} authentication: {str(e)}")
        
        return auth_tests_passed == len(endpoints)

    def run_comprehensive_test(self):
        """Run comprehensive test of all student analytics endpoints"""
        print("🚀 Starting Comprehensive Student Analytics Testing")
        print("=" * 60)
        
        # Setup
        if not self.register_student():
            print("❌ Failed to register student, cannot continue testing")
            return False
        
        # Create test data
        if not self.create_practice_test_data():
            print("⚠️ Failed to create practice test data, testing with empty data")
        
        # Test all endpoints
        tests = [
            ("Authentication Requirements", self.test_authentication_requirements),
            ("Strengths & Weaknesses", self.test_strengths_weaknesses_endpoint),
            ("Performance Trends", self.test_performance_trends_endpoint),
            ("Subject Breakdown", self.test_subject_breakdown_endpoint),
            ("Learning Insights", self.test_learning_insights_endpoint),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {str(e)}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 STUDENT ANALYTICS TESTING SUMMARY")
        print("="*60)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['endpoint']}: {result['status']} - {result['message']}")
        
        # Critical assessment
        critical_endpoints = ["strengths-weaknesses", "performance-trends", "subject-breakdown", "learning-insights"]
        critical_passed = sum(1 for result in self.test_results 
                            if any(endpoint in result["endpoint"] for endpoint in critical_endpoints) 
                            and result["status"] == "PASS")
        
        print(f"\n🎯 CRITICAL ANALYTICS ENDPOINTS: {critical_passed}/{len(critical_endpoints)} working")
        
        if critical_passed == len(critical_endpoints):
            print("🎉 SUCCESS: All critical student analytics endpoints are working correctly!")
            print("🔧 The 500 Internal Server Error bug fix has been verified successfully!")
            return True
        else:
            print("⚠️ WARNING: Some critical analytics endpoints are still failing")
            return False

def main():
    """Main function to run the analytics test"""
    tester = StudentAnalyticsTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 STUDENT ANALYTICS BUG FIX VERIFICATION: SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ STUDENT ANALYTICS BUG FIX VERIFICATION: ISSUES FOUND")
        sys.exit(1)

if __name__ == "__main__":
    main()
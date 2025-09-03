#!/usr/bin/env python3
"""
Endpoint Mapping Test - Maps review request endpoints to actual working endpoints
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 ENDPOINT MAPPING AND VERIFICATION TEST")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class EndpointMappingTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.setup_account()

    def setup_account(self):
        """Setup a test account"""
        student_payload = {
            "email": f"endpoint_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Endpoint Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(f"{API_URL}/auth/register", json=student_payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Test account created: {self.student_id}")
                
                # Create some test data
                self.create_test_data()
            else:
                print(f"❌ Failed to create test account: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating test account: {str(e)}")

    def create_test_data(self):
        """Create test data for better API responses"""
        if not self.student_token:
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Generate and submit a practice test
        try:
            gen_payload = {
                "subject": "math",
                "topics": ["Algebra"],
                "difficulty": "medium",
                "question_count": 3
            }
            
            gen_response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                questions = gen_data.get("questions", [])
                
                if questions:
                    student_answers = {}
                    question_ids = []
                    for question in questions:
                        question_id = question.get("id")
                        question_ids.append(question_id)
                        student_answers[question_id] = question.get("correct_answer")
                    
                    submit_payload = {
                        "questions": question_ids,
                        "student_answers": student_answers,
                        "subject": "math",
                        "time_taken": 300
                    }
                    
                    submit_response = requests.post(f"{API_URL}/practice/submit", json=submit_payload, headers=headers)
                    if submit_response.status_code == 200:
                        print("✅ Test data created successfully")
        except Exception as e:
            print(f"❌ Error creating test data: {str(e)}")

    def test_endpoint_mappings(self):
        """Test the mapping between requested endpoints and actual endpoints"""
        if not self.student_token:
            print("❌ No student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Endpoint mappings: requested -> actual
        endpoint_mappings = {
            # Student Dashboard APIs
            "/api/student/dashboard": "/api/dashboard",
            "/api/student/progress": "/api/student/profile",
            
            # Progress Component APIs  
            "/api/student/progress (for overall progress)": "/api/practice/results",
            "/api/student/test-results": "/api/practice/stats/math",
            
            # Notes Component APIs
            "/api/notes/user": "/api/notes/",
            "/api/notes/create": "/api/notes/generate",
            "/api/notes/update/{id}": "/api/notes/{id}/favorite",
            "/api/notes/delete/{id}": "/api/notes/{id}/delete",
            
            # Scheduled Tests APIs
            "/api/practice-scheduler/scheduled-tests": "/api/practice-scheduler/upcoming-tests",
            "/api/practice-scheduler/complete-scheduled-test/{test_id}": "/api/practice-scheduler/complete-scheduled-test/{test_id}",
            
            # Analytics APIs
            "/api/student-analytics/strengths": "/api/student/analytics/strengths-weaknesses",
            "/api/student-analytics/weaknesses": "/api/student/analytics/strengths-weaknesses",
            "/api/student-analytics/performance-trends": "/api/student/analytics/performance-trends",
            "/api/student-analytics/subject-breakdown": "/api/student/analytics/subject-breakdown",
            "/api/student-analytics/learning-insights": "/api/student/analytics/learning-insights",
            
            # Tutor Component APIs
            "/api/tutor/chat": "/api/tutor/chat"
        }
        
        print("\n📋 ENDPOINT MAPPING VERIFICATION")
        print("="*80)
        print("Format: REQUESTED ENDPOINT -> ACTUAL ENDPOINT : STATUS")
        print("="*80)
        
        working_count = 0
        total_count = len(endpoint_mappings)
        
        for requested, actual in endpoint_mappings.items():
            try:
                # Handle special cases that need specific data or methods
                if "notes/generate" in actual:
                    payload = {"subject": "math", "topic": "Test Topic", "grade_level": "10th"}
                    response = requests.post(f"{API_URL.replace('/api', '')}{actual}", json=payload, headers=headers)
                elif "tutor/session" in actual:
                    payload = {"subject": "math", "session_type": "tutoring"}
                    response = requests.post(f"{API_URL.replace('/api', '')}{actual}", json=payload, headers=headers)
                elif "tutor/chat" in actual:
                    # First create a session
                    session_payload = {"subject": "math", "session_type": "tutoring"}
                    session_response = requests.post(f"{API_URL}/tutor/session", json=session_payload, headers=headers)
                    if session_response.status_code == 200:
                        session_id = session_response.json().get("session_id")
                        chat_payload = {"message": "Test message", "subject": "math", "session_id": session_id}
                        response = requests.post(f"{API_URL.replace('/api', '')}{actual}", json=chat_payload, headers=headers)
                    else:
                        response = session_response
                elif "performance-trends" in actual:
                    response = requests.get(f"{API_URL.replace('/api', '')}{actual}?days=7", headers=headers)
                else:
                    response = requests.get(f"{API_URL.replace('/api', '')}{actual}", headers=headers)
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                status_code = response.status_code
                
                if response.status_code == 200:
                    working_count += 1
                    # Show sample data structure for working endpoints
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]  # Show first 3 keys
                            sample_info = f"Keys: {keys}"
                        elif isinstance(data, list):
                            sample_info = f"Array with {len(data)} items"
                        else:
                            sample_info = f"Type: {type(data).__name__}"
                    except:
                        sample_info = "Response received"
                else:
                    sample_info = f"Error: {response.text[:50]}..."
                
                print(f"{status_icon} {requested}")
                print(f"    -> {actual} : {status_code}")
                print(f"    -> {sample_info}")
                print()
                
            except Exception as e:
                print(f"❌ {requested}")
                print(f"    -> {actual} : Exception - {str(e)}")
                print()
        
        print("="*80)
        print(f"📊 MAPPING VERIFICATION SUMMARY")
        print(f"Working Endpoints: {working_count}/{total_count} ({working_count/total_count*100:.1f}%)")
        print("="*80)
        
        # Provide specific recommendations
        print("\n🔧 FRONTEND INTEGRATION RECOMMENDATIONS:")
        print("="*50)
        
        recommendations = [
            "1. Update frontend API calls to use correct endpoint paths:",
            "   - Use /api/dashboard instead of /api/student/dashboard",
            "   - Use /api/student/profile instead of /api/student/progress", 
            "   - Use /api/practice/results instead of /api/student/progress",
            "   - Use /api/notes/ instead of /api/notes/user",
            "   - Use /api/notes/generate instead of /api/notes/create",
            "",
            "2. Analytics endpoints are under /api/student/analytics/ prefix:",
            "   - /api/student/analytics/strengths-weaknesses (combines strengths & weaknesses)",
            "   - /api/student/analytics/performance-trends",
            "   - /api/student/analytics/subject-breakdown", 
            "   - /api/student/analytics/learning-insights",
            "",
            "3. Scheduled tests endpoints:",
            "   - Use /api/practice-scheduler/upcoming-tests for loading tests",
            "   - Complete tests via /api/practice-scheduler/complete-scheduled-test/{id}",
            "",
            "4. Notes CRUD operations:",
            "   - Create: POST /api/notes/generate",
            "   - Read: GET /api/notes/",
            "   - Update: PUT /api/notes/{id}/favorite", 
            "   - Delete: DELETE /api/notes/{id}/delete",
            "",
            "5. All endpoints require proper JWT authentication headers"
        ]
        
        for rec in recommendations:
            print(rec)

if __name__ == "__main__":
    tester = EndpointMappingTester()
    tester.test_endpoint_mappings()
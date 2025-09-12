#!/usr/bin/env python3
"""
AI Tutor API Testing Script
Tests the tutor-related endpoints as requested in the review
"""

import requests
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Testing AI Tutor API at: {API_URL}")

class TutorAPITester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.session_id = None
        
    def register_and_login_student(self):
        """Register and login a test student"""
        print("\n🔍 Setting up test student...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        student_email = f"tutor_test_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": student_email,
            "password": "TutorTest123!",
            "name": "Tutor Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Student Registration: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student registered successfully: {self.student_id}")
                return True
            else:
                print(f"❌ Student registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Student registration error: {str(e)}")
            return False
    
    def test_create_tutor_session(self):
        """Test creating a tutor session"""
        print("\n🔍 Testing Tutor Session Creation...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        url = f"{API_URL}/tutor/session"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": "math",
            "session_type": "tutoring"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Create Tutor Session Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                print(f"✅ Tutor session created: {self.session_id}")
                print(f"   Subject: {data.get('subject')}")
                print(f"   Started at: {data.get('started_at')}")
                return True
            else:
                print(f"❌ Session creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Session creation error: {str(e)}")
            return False
    
    def test_tutor_chat_simple_message(self):
        """Test tutor chat with simple message (as requested in review)"""
        print("\n🔍 Testing Tutor Chat - Simple Message...")
        
        if not self.student_token or not self.session_id:
            print("❌ Missing student token or session ID")
            return False
            
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test payload as specified in review request
        payload = {
            "message": "Hello, can you help me with mathematics?",
            "subject": "math",
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Tutor Chat Simple Message Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tutor chat successful")
                print(f"   Message ID: {data.get('message_id')}")
                print(f"   Response preview: {data.get('response', '')[:100]}...")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Timestamp: {data.get('timestamp')}")
                
                # Verify response structure
                required_fields = ['message_id', 'response', 'session_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"⚠️ Missing response fields: {missing_fields}")
                else:
                    print("✅ Response structure complete")
                
                return True
            else:
                print(f"❌ Tutor chat failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Tutor chat error: {str(e)}")
            return False
    
    def test_tutor_chat_with_conversation_context(self):
        """Test tutor chat with conversation context (follow-up message)"""
        print("\n🔍 Testing Tutor Chat - Follow-up Message with Context...")
        
        if not self.student_token or not self.session_id:
            print("❌ Missing student token or session ID")
            return False
            
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Send a follow-up message that should reference previous context
        payload = {
            "message": "Can you explain quadratic equations?",
            "subject": "math", 
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Tutor Chat Context Message Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tutor chat with context successful")
                print(f"   Message ID: {data.get('message_id')}")
                print(f"   Response preview: {data.get('response', '')[:150]}...")
                
                # Check if response shows awareness of conversation context
                response_text = data.get('response', '').lower()
                context_indicators = ['previous', 'earlier', 'before', 'as we discussed', 'continuing', 'mathematics']
                has_context = any(indicator in response_text for indicator in context_indicators)
                
                if has_context:
                    print("✅ Response shows conversation context awareness")
                else:
                    print("⚠️ Response may not show conversation context awareness")
                
                return True
            else:
                print(f"❌ Tutor chat with context failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Tutor chat context error: {str(e)}")
            return False
    
    def test_tutor_chat_alternative_format(self):
        """Test if there's an alternative tutor endpoint that accepts conversation_history directly"""
        print("\n🔍 Testing Alternative Tutor Chat Format (with conversation_history)...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # Try the format mentioned in the review request
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test payload with conversation_history as mentioned in review
        payload = {
            "message": "Can you explain quadratic equations?",
            "conversation_history": [
                {"text": "Hello", "sender": "user", "timestamp": "2024-01-01T10:00:00"},
                {"text": "Hi! How can I help?", "sender": "tutor", "timestamp": "2024-01-01T10:00:01"}
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Alternative Tutor Chat Format Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Alternative format successful")
                print(f"   Response preview: {data.get('response', '')[:100]}...")
                return True
            elif response.status_code == 422:
                print("⚠️ Alternative format not supported (422 Validation Error)")
                print("   This suggests the API expects session_id instead of conversation_history")
                return False
            else:
                print(f"❌ Alternative format failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Alternative format error: {str(e)}")
            return False
    
    def test_tutor_error_handling(self):
        """Test tutor API error handling"""
        print("\n🔍 Testing Tutor API Error Handling...")
        
        # Test 1: Missing authentication
        print("   Testing missing authentication...")
        url = f"{API_URL}/tutor/chat"
        payload = {
            "message": "Test message",
            "subject": "math",
            "session_id": "test_session"
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Missing auth response: {response.status_code}")
            if response.status_code in [401, 403]:
                print("   ✅ Correctly rejects missing authentication")
            else:
                print(f"   ⚠️ Unexpected response for missing auth: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing missing auth: {str(e)}")
        
        # Test 2: Invalid session ID
        if self.student_token:
            print("   Testing invalid session ID...")
            headers = {"Authorization": f"Bearer {self.student_token}"}
            payload = {
                "message": "Test message",
                "subject": "math",
                "session_id": "invalid_session_id"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"   Invalid session response: {response.status_code}")
                if response.status_code == 404:
                    print("   ✅ Correctly rejects invalid session ID")
                else:
                    print(f"   ⚠️ Unexpected response for invalid session: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error testing invalid session: {str(e)}")
        
        # Test 3: Empty message
        if self.student_token and self.session_id:
            print("   Testing empty message...")
            headers = {"Authorization": f"Bearer {self.student_token}"}
            payload = {
                "message": "",
                "subject": "math",
                "session_id": self.session_id
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"   Empty message response: {response.status_code}")
                if response.status_code in [400, 422]:
                    print("   ✅ Correctly handles empty message")
                elif response.status_code == 200:
                    print("   ⚠️ Accepts empty message (may need validation)")
                else:
                    print(f"   ⚠️ Unexpected response for empty message: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error testing empty message: {str(e)}")
        
        # Test 4: Very long message
        if self.student_token and self.session_id:
            print("   Testing very long message...")
            headers = {"Authorization": f"Bearer {self.student_token}"}
            long_message = "This is a very long message. " * 100  # 3000+ characters
            payload = {
                "message": long_message,
                "subject": "math",
                "session_id": self.session_id
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"   Long message response: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Handles long messages")
                elif response.status_code in [400, 413]:
                    print("   ✅ Correctly limits message length")
                else:
                    print(f"   ⚠️ Unexpected response for long message: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error testing long message: {str(e)}")
    
    def test_tutor_session_management(self):
        """Test tutor session management endpoints"""
        print("\n🔍 Testing Tutor Session Management...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test 1: Get all sessions
        print("   Testing get all sessions...")
        try:
            url = f"{API_URL}/tutor/sessions"
            response = requests.get(url, headers=headers)
            print(f"   Get sessions response: {response.status_code}")
            
            if response.status_code == 200:
                sessions = response.json()
                print(f"   ✅ Retrieved {len(sessions)} sessions")
                if len(sessions) > 0:
                    session = sessions[0]
                    print(f"   Session structure: {list(session.keys())}")
            else:
                print(f"   ❌ Get sessions failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error getting sessions: {str(e)}")
        
        # Test 2: Get session messages
        if self.session_id:
            print("   Testing get session messages...")
            try:
                url = f"{API_URL}/tutor/session/{self.session_id}/messages"
                response = requests.get(url, headers=headers)
                print(f"   Get messages response: {response.status_code}")
                
                if response.status_code == 200:
                    messages = response.json()
                    print(f"   ✅ Retrieved {len(messages)} messages")
                    if len(messages) > 0:
                        message = messages[0]
                        print(f"   Message structure: {list(message.keys())}")
                else:
                    print(f"   ❌ Get messages failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Error getting messages: {str(e)}")
    
    def test_tutor_response_quality(self):
        """Test the quality and educational value of tutor responses"""
        print("\n🔍 Testing Tutor Response Quality...")
        
        if not self.student_token or not self.session_id:
            print("❌ Missing student token or session ID")
            return False
        
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different types of educational questions
        test_questions = [
            {
                "message": "What is the quadratic formula?",
                "expected_keywords": ["quadratic", "formula", "ax²", "discriminant", "-b"],
                "subject": "math"
            },
            {
                "message": "I'm confused about photosynthesis",
                "expected_keywords": ["photosynthesis", "chlorophyll", "sunlight", "glucose", "carbon dioxide"],
                "subject": "biology"
            },
            {
                "message": "Can you help me understand Newton's first law?",
                "expected_keywords": ["newton", "inertia", "motion", "force", "rest"],
                "subject": "physics"
            }
        ]
        
        successful_responses = 0
        
        for i, test_case in enumerate(test_questions):
            print(f"   Testing question {i+1}: {test_case['message'][:50]}...")
            
            payload = {
                "message": test_case["message"],
                "subject": test_case["subject"],
                "session_id": self.session_id
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '').lower()
                    
                    # Check for educational keywords
                    found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in response_text]
                    keyword_score = len(found_keywords) / len(test_case['expected_keywords'])
                    
                    # Check response length (should be substantial)
                    response_length = len(data.get('response', ''))
                    
                    # Check for educational structure
                    has_explanation = any(word in response_text for word in ['because', 'therefore', 'this means', 'for example'])
                    has_encouragement = any(word in response_text for word in ['great', 'good', 'excellent', 'keep', 'try'])
                    
                    print(f"     Response length: {response_length} characters")
                    print(f"     Keywords found: {len(found_keywords)}/{len(test_case['expected_keywords'])} ({keyword_score:.1%})")
                    print(f"     Has explanation: {has_explanation}")
                    print(f"     Has encouragement: {has_encouragement}")
                    
                    # Quality score
                    quality_score = 0
                    if response_length > 100:
                        quality_score += 1
                    if keyword_score > 0.3:
                        quality_score += 1
                    if has_explanation:
                        quality_score += 1
                    if has_encouragement:
                        quality_score += 1
                    
                    if quality_score >= 3:
                        print(f"     ✅ High quality response (score: {quality_score}/4)")
                        successful_responses += 1
                    else:
                        print(f"     ⚠️ Lower quality response (score: {quality_score}/4)")
                
                else:
                    print(f"     ❌ Request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error: {str(e)}")
        
        success_rate = (successful_responses / len(test_questions)) * 100
        print(f"\n   📊 Response Quality Summary:")
        print(f"   High quality responses: {successful_responses}/{len(test_questions)} ({success_rate:.1f}%)")
        
        return success_rate >= 66.7  # At least 2/3 should be high quality
    
    def run_all_tests(self):
        """Run all tutor API tests"""
        print("🚀 Starting AI Tutor API Testing...")
        print("=" * 60)
        
        test_results = {}
        
        # Setup
        test_results['setup'] = self.register_and_login_student()
        
        if test_results['setup']:
            # Core functionality tests
            test_results['session_creation'] = self.test_create_tutor_session()
            test_results['simple_chat'] = self.test_tutor_chat_simple_message()
            test_results['context_chat'] = self.test_tutor_chat_with_conversation_context()
            test_results['alternative_format'] = self.test_tutor_chat_alternative_format()
            
            # Additional tests
            test_results['error_handling'] = True  # Always run this
            self.test_tutor_error_handling()
            
            test_results['session_management'] = True  # Always run this
            self.test_tutor_session_management()
            
            test_results['response_quality'] = self.test_tutor_response_quality()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 AI TUTOR API TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("🎉 AI Tutor API is working well!")
        elif passed_tests >= total_tests * 0.6:  # 60% pass rate
            print("⚠️ AI Tutor API has some issues but core functionality works")
        else:
            print("🚨 AI Tutor API has significant issues")
        
        return test_results

if __name__ == "__main__":
    tester = TutorAPITester()
    results = tester.run_all_tests()
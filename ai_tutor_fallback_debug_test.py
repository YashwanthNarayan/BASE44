#!/usr/bin/env python3
"""
AI Tutor Fallback Debug Test
Specifically designed to debug why AI Tutor is returning fallback messages
instead of working properly as reported by the user.
"""

import requests
import json
import uuid
import os
import time
import subprocess
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
print(f"🔍 AI Tutor Fallback Debug Test - API URL: {API_URL}")

class AITutorFallbackDebugger:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.session_id = None
        self.fallback_responses = []
        self.successful_responses = []
        
    def setup_test_student(self):
        """Register and login a test student"""
        print("\n🔧 Setting up test student for AI Tutor debugging...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        student_email = f"tutor_debug_{uuid.uuid4()}@example.com"
        register_payload = {
            "email": student_email,
            "password": "TutorDebug123!",
            "name": "AI Tutor Debug Student",
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
                print(f"✅ Test student registered: {self.student_id}")
                return True
            else:
                print(f"❌ Student registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Student registration error: {str(e)}")
            return False
    
    def create_tutor_session(self):
        """Create a tutor session for testing"""
        print("\n🔧 Creating tutor session...")
        
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
            print(f"Create Tutor Session: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                print(f"✅ Tutor session created: {self.session_id}")
                return True
            else:
                print(f"❌ Session creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Session creation error: {str(e)}")
            return False
    
    def check_backend_logs_before_test(self):
        """Check backend logs before testing to establish baseline"""
        print("\n📋 Checking backend logs before testing...")
        try:
            # Get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                print("📋 Recent backend error logs:")
                print("-" * 50)
                print(logs[-1000:])  # Last 1000 characters
                print("-" * 50)
            else:
                print("⚠️ Could not read backend error logs")
                
        except Exception as e:
            print(f"⚠️ Error reading backend logs: {str(e)}")
    
    def test_tutor_chat_with_detailed_logging(self, message, expected_type="educational"):
        """Test tutor chat with detailed logging and analysis"""
        print(f"\n🔍 Testing AI Tutor Chat: '{message[:50]}...'")
        
        if not self.student_token or not self.session_id:
            print("❌ Missing student token or session ID")
            return None
            
        url = f"{API_URL}/tutor/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "message": message,
            "subject": "math",
            "session_id": self.session_id
        }
        
        # Record start time for log correlation
        start_time = datetime.now()
        print(f"🕐 Request sent at: {start_time.strftime('%H:%M:%S')}")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                # Check if this is a fallback response
                is_fallback = self.is_fallback_response(response_text)
                
                print(f"📝 Response Length: {len(response_text)} characters")
                print(f"📝 Response Preview: {response_text[:200]}...")
                print(f"🎯 Is Fallback Response: {'YES' if is_fallback else 'NO'}")
                
                # Analyze response quality
                quality_analysis = self.analyze_response_quality(response_text, expected_type)
                print(f"📊 Response Quality: {quality_analysis}")
                
                # Store results
                result = {
                    "message": message,
                    "response": response_text,
                    "is_fallback": is_fallback,
                    "response_time": response_time,
                    "quality": quality_analysis,
                    "timestamp": start_time
                }
                
                if is_fallback:
                    self.fallback_responses.append(result)
                    print("❌ FALLBACK RESPONSE DETECTED")
                else:
                    self.successful_responses.append(result)
                    print("✅ SUCCESSFUL AI RESPONSE")
                
                return result
            else:
                print(f"❌ Request failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return None
    
    def is_fallback_response(self, response_text):
        """Check if response is a fallback message"""
        fallback_indicators = [
            "I'm having a technical issue right now",
            "Let's try again",
            "technical issue",
            "try again later",
            "unable to generate",
            "service unavailable"
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in fallback_indicators)
    
    def analyze_response_quality(self, response_text, expected_type):
        """Analyze the quality and educational value of the response"""
        analysis = {
            "length_score": 0,
            "educational_score": 0,
            "engagement_score": 0,
            "subject_relevance": 0
        }
        
        response_lower = response_text.lower()
        
        # Length analysis
        if len(response_text) > 200:
            analysis["length_score"] = 3
        elif len(response_text) > 100:
            analysis["length_score"] = 2
        elif len(response_text) > 50:
            analysis["length_score"] = 1
        
        # Educational content analysis
        educational_keywords = [
            "explain", "understand", "learn", "concept", "formula", "equation",
            "solve", "step", "method", "example", "practice", "theorem"
        ]
        educational_count = sum(1 for keyword in educational_keywords if keyword in response_lower)
        analysis["educational_score"] = min(3, educational_count)
        
        # Engagement analysis
        engagement_keywords = [
            "let's", "can you", "try", "think", "what do you", "great", "good",
            "excellent", "question", "help", "guide"
        ]
        engagement_count = sum(1 for keyword in engagement_keywords if keyword in response_lower)
        analysis["engagement_score"] = min(3, engagement_count)
        
        # Subject relevance (math)
        math_keywords = [
            "math", "equation", "solve", "calculate", "number", "formula",
            "algebra", "geometry", "quadratic", "linear", "function"
        ]
        math_count = sum(1 for keyword in math_keywords if keyword in response_lower)
        analysis["subject_relevance"] = min(3, math_count)
        
        # Overall quality score
        total_score = sum(analysis.values())
        analysis["overall_score"] = total_score
        analysis["quality_rating"] = "High" if total_score >= 8 else "Medium" if total_score >= 5 else "Low"
        
        return analysis
    
    def check_backend_logs_after_test(self):
        """Check backend logs after testing to identify errors"""
        print("\n📋 Checking backend logs after testing...")
        try:
            # Get recent backend logs
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for AI/Gemini related errors
                ai_errors = []
                gemini_errors = []
                quota_errors = []
                
                for line in logs.split('\n'):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['ai', 'gemini', 'generate']):
                        if 'error' in line_lower or 'exception' in line_lower:
                            ai_errors.append(line)
                    if 'gemini' in line_lower:
                        gemini_errors.append(line)
                    if any(keyword in line_lower for keyword in ['quota', '429', 'rate limit']):
                        quota_errors.append(line)
                
                print("🔍 AI-related errors found:")
                for error in ai_errors[-5:]:  # Last 5 errors
                    print(f"   ❌ {error}")
                
                print("🔍 Gemini API logs:")
                for log in gemini_errors[-5:]:  # Last 5 logs
                    print(f"   📝 {log}")
                
                print("🔍 Quota/Rate limit errors:")
                for error in quota_errors[-3:]:  # Last 3 errors
                    print(f"   ⚠️ {error}")
                
                if not ai_errors and not quota_errors:
                    print("✅ No obvious AI or quota errors found in logs")
                
            else:
                print("⚠️ Could not read backend logs")
                
        except Exception as e:
            print(f"⚠️ Error reading backend logs: {str(e)}")
    
    def test_gemini_api_directly(self):
        """Test if Gemini API is working by checking the AI service directly"""
        print("\n🔍 Testing Gemini API Connectivity...")
        
        # Check if Gemini API key is available
        try:
            with open('/app/backend/.env', 'r') as f:
                env_content = f.read()
                if 'GEMINI_API_KEY' in env_content:
                    print("✅ Gemini API key found in backend .env")
                    # Extract the key (safely)
                    for line in env_content.split('\n'):
                        if line.startswith('GEMINI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip('"')
                            print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
                            break
                else:
                    print("❌ Gemini API key not found in backend .env")
                    return False
        except Exception as e:
            print(f"❌ Error reading backend .env: {str(e)}")
            return False
        
        # Test a simple AI generation request similar to tutor
        print("🧪 Testing AI generation similar to tutor request...")
        
        test_message = "Can you help me understand quadratic equations?"
        
        # This would require importing the AI service, but we can test the endpoint instead
        # Let's test with a practice generation request to see if AI is working
        if self.student_token:
            url = f"{API_URL}/practice/generate"
            headers = {"Authorization": f"Bearer {self.student_token}"}
            payload = {
                "subject": "math",
                "topics": ["Quadratic Equations"],
                "difficulty": "medium",
                "question_count": 1
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                print(f"Practice Generation Test: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get('questions', [])
                    if questions:
                        print("✅ AI service is working for practice generation")
                        print(f"   Generated question: {questions[0].get('question_text', '')[:100]}...")
                        return True
                    else:
                        print("⚠️ AI service returned empty questions")
                        return False
                else:
                    print(f"❌ Practice generation failed: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Practice generation error: {str(e)}")
                return False
        
        return False
    
    def compare_with_working_features(self):
        """Compare tutor responses with other working AI features"""
        print("\n🔍 Comparing AI Tutor with other working AI features...")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        # Test practice generation (known to be working)
        print("📊 Testing Practice Generation (known working feature)...")
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', [])
                print(f"✅ Practice generation working: {len(questions)} questions generated")
                if questions:
                    print(f"   Sample question: {questions[0].get('question_text', '')[:100]}...")
            else:
                print(f"❌ Practice generation failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Practice generation error: {str(e)}")
        
        # Test study planner (another AI feature)
        print("📊 Testing Study Planner AI...")
        url = f"{API_URL}/study-planner/chat"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "message": "I want to study math for 1 hour"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"✅ Study planner working: {len(response_text)} character response")
                print(f"   Sample response: {response_text[:100]}...")
            else:
                print(f"❌ Study planner failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Study planner error: {str(e)}")
    
    def run_comprehensive_debug_test(self):
        """Run comprehensive debugging test for AI Tutor fallback issue"""
        print("🚀 AI TUTOR FALLBACK DEBUG TEST")
        print("=" * 60)
        print("🎯 Goal: Debug why AI Tutor returns fallback messages instead of working properly")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_student():
            print("❌ Failed to setup test student")
            return
        
        if not self.create_tutor_session():
            print("❌ Failed to create tutor session")
            return
        
        # Pre-test checks
        self.check_backend_logs_before_test()
        gemini_working = self.test_gemini_api_directly()
        
        # Test various tutor messages
        test_messages = [
            "Hello, can you help me with mathematics?",
            "Explain quadratic equations",
            "What is the quadratic formula?",
            "I'm confused about solving x² - 5x + 6 = 0",
            "Can you teach me about algebra?"
        ]
        
        print(f"\n🧪 Testing {len(test_messages)} different tutor messages...")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i}/{len(test_messages)} ---")
            result = self.test_tutor_chat_with_detailed_logging(message)
            
            # Small delay between requests
            time.sleep(1)
        
        # Post-test analysis
        self.check_backend_logs_after_test()
        self.compare_with_working_features()
        
        # Generate comprehensive report
        self.generate_debug_report(gemini_working)
    
    def generate_debug_report(self, gemini_working):
        """Generate comprehensive debug report"""
        print("\n" + "=" * 60)
        print("📊 AI TUTOR FALLBACK DEBUG REPORT")
        print("=" * 60)
        
        total_tests = len(self.fallback_responses) + len(self.successful_responses)
        fallback_count = len(self.fallback_responses)
        success_count = len(self.successful_responses)
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful Responses: {success_count}")
        print(f"   Fallback Responses: {fallback_count}")
        print(f"   Fallback Rate: {(fallback_count/total_tests)*100:.1f}%")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if fallback_count == total_tests:
            print("   🚨 CRITICAL: 100% fallback rate - AI Tutor completely non-functional")
            print("   🎯 PRIMARY ISSUE: AI service is failing for tutor requests")
            
            if not gemini_working:
                print("   🔧 LIKELY CAUSE: Gemini API connectivity or quota issues")
                print("   💡 RECOMMENDATION: Check Gemini API key, quota, and network connectivity")
            else:
                print("   🔧 LIKELY CAUSE: Tutor-specific AI prompt or processing issue")
                print("   💡 RECOMMENDATION: Review tutor AI prompt format and error handling")
                
        elif fallback_count > success_count:
            print("   ⚠️ HIGH: Majority of requests failing")
            print("   🎯 PRIMARY ISSUE: Intermittent AI service failures")
            print("   💡 RECOMMENDATION: Investigate rate limiting and error handling")
            
        elif fallback_count > 0:
            print("   ⚠️ MODERATE: Some requests failing")
            print("   🎯 PRIMARY ISSUE: Occasional AI service timeouts or errors")
            print("   💡 RECOMMENDATION: Improve retry logic and error handling")
            
        else:
            print("   ✅ GOOD: No fallback responses detected")
            print("   🎯 STATUS: AI Tutor appears to be working correctly")
        
        print(f"\n📝 DETAILED FINDINGS:")
        
        if self.fallback_responses:
            print("   ❌ FALLBACK RESPONSES:")
            for i, response in enumerate(self.fallback_responses[:3], 1):
                print(f"      {i}. Message: '{response['message'][:50]}...'")
                print(f"         Response: '{response['response'][:100]}...'")
                print(f"         Time: {response['response_time']:.2f}s")
        
        if self.successful_responses:
            print("   ✅ SUCCESSFUL RESPONSES:")
            for i, response in enumerate(self.successful_responses[:3], 1):
                print(f"      {i}. Message: '{response['message'][:50]}...'")
                print(f"         Quality: {response['quality']['quality_rating']}")
                print(f"         Time: {response['response_time']:.2f}s")
        
        print(f"\n🎯 SPECIFIC RECOMMENDATIONS:")
        
        if fallback_count > 0:
            print("   1. 🔧 Check backend logs for specific AI service errors")
            print("   2. 🔑 Verify Gemini API key is valid and has sufficient quota")
            print("   3. 🌐 Test network connectivity to Gemini API endpoints")
            print("   4. 📝 Review tutor AI prompt format and length")
            print("   5. ⚡ Implement better retry logic for AI service failures")
            print("   6. 📊 Add monitoring for AI service response rates")
        
        if success_count > 0:
            print("   ✅ AI Tutor is capable of working - focus on reliability improvements")
        
        print(f"\n🚨 USER IMPACT:")
        if fallback_count == total_tests:
            print("   CRITICAL: Users cannot access AI tutoring functionality")
            print("   PRIORITY: HIGH - Immediate fix required")
        elif fallback_count > success_count:
            print("   HIGH: Users frequently encounter fallback messages")
            print("   PRIORITY: HIGH - Fix needed soon")
        elif fallback_count > 0:
            print("   MODERATE: Users occasionally encounter fallback messages")
            print("   PRIORITY: MEDIUM - Improvement recommended")
        else:
            print("   LOW: AI Tutor working as expected")
            print("   PRIORITY: LOW - Monitor for regressions")
        
        print("\n" + "=" * 60)
        
        return {
            "total_tests": total_tests,
            "fallback_count": fallback_count,
            "success_count": success_count,
            "fallback_rate": (fallback_count/total_tests)*100 if total_tests > 0 else 0,
            "gemini_working": gemini_working,
            "recommendations": self.get_recommendations(fallback_count, total_tests, gemini_working)
        }
    
    def get_recommendations(self, fallback_count, total_tests, gemini_working):
        """Get specific recommendations based on test results"""
        recommendations = []
        
        if fallback_count == total_tests:
            recommendations.append("URGENT: AI Tutor completely non-functional - immediate investigation required")
            if not gemini_working:
                recommendations.append("Check Gemini API key validity and quota limits")
                recommendations.append("Verify network connectivity to Gemini API")
            else:
                recommendations.append("Review tutor-specific AI service implementation")
                recommendations.append("Check tutor prompt format and processing logic")
        
        elif fallback_count > 0:
            recommendations.append("Implement better error handling and retry logic")
            recommendations.append("Add monitoring for AI service response rates")
            recommendations.append("Consider fallback to simpler AI responses before showing technical error")
        
        recommendations.append("Add detailed logging for AI service calls")
        recommendations.append("Implement health checks for AI service availability")
        
        return recommendations

if __name__ == "__main__":
    debugger = AITutorFallbackDebugger()
    results = debugger.run_comprehensive_debug_test()
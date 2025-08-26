#!/usr/bin/env python3
"""
AI vs Fallback System Testing
Tests to determine if questions are coming from AI generation or fallback system
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 AI vs FALLBACK SYSTEM TESTING")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class AIFallbackTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None

    def setup_student_account(self):
        """Setup student account for testing"""
        print("\n🔧 SETTING UP TEST ACCOUNT...")
        
        student_payload = {
            "email": f"ai_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "AI Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(f"{API_URL}/auth/register", json=student_payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student account created: {self.student_id}")
                return True
            else:
                print(f"❌ Failed to create student account: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating student account: {str(e)}")
            return False

    def test_ai_vs_fallback_patterns(self):
        """Test to identify AI-generated vs fallback questions"""
        print("\n🤖 TESTING AI vs FALLBACK PATTERNS...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Known fallback questions from the code
        known_fallback_questions = {
            "math": {
                "Real Numbers": [
                    "Which of the following is an irrational number?",
                    "What is the decimal expansion of a rational number?"
                ],
                "Quadratic Equations": [
                    "What is the discriminant of x² - 4x + 3 = 0?",
                    "If the discriminant of a quadratic equation is zero, the roots are:"
                ],
                "Polynomials": [
                    "What is the degree of the polynomial 3x³ + 2x² - x + 5?"
                ]
            },
            "physics": {
                "Laws of Motion": [
                    "According to Newton's first law, an object at rest will:"
                ]
            },
            "biology": {
                "The Fundamental Unit of Life": [
                    "What is the basic unit of life?"
                ],
                "Tissues": [
                    "Which tissue is responsible for movement in animals?"
                ],
                "Nutrition in Plants": [
                    "Which part of the plant cell contains chlorophyll?"
                ]
            },
            "chemistry": {
                "Acids, Bases and Salts": [
                    "What is the pH of pure water?"
                ]
            }
        }
        
        # Test different NCERT units
        test_units = [
            {"subject": "math", "unit": "Real Numbers"},
            {"subject": "math", "unit": "Quadratic Equations"},
            {"subject": "physics", "unit": "Laws of Motion"},
            {"subject": "biology", "unit": "Nutrition in Plants"},
            {"subject": "chemistry", "unit": "Acids, Bases and Salts"}
        ]
        
        ai_questions = []
        fallback_questions = []
        
        for unit_info in test_units:
            subject = unit_info["subject"]
            unit = unit_info["unit"]
            
            print(f"\n📋 Testing {subject.upper()} - {unit}")
            
            # Make multiple requests to get variety
            for attempt in range(5):
                gen_payload = {
                    "subject": subject,
                    "topics": [unit],
                    "difficulty": "medium",
                    "question_count": 3
                }
                
                try:
                    response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get("questions", [])
                        
                        for question in questions:
                            question_text = question.get("question_text", "")
                            
                            # Check if this matches a known fallback question
                            is_fallback = False
                            if subject in known_fallback_questions and unit in known_fallback_questions[subject]:
                                for fallback_q in known_fallback_questions[subject][unit]:
                                    if fallback_q in question_text:
                                        is_fallback = True
                                        fallback_questions.append({
                                            "subject": subject,
                                            "unit": unit,
                                            "question": question_text,
                                            "attempt": attempt + 1
                                        })
                                        print(f"   🔄 FALLBACK: {question_text[:60]}...")
                                        break
                            
                            if not is_fallback:
                                ai_questions.append({
                                    "subject": subject,
                                    "unit": unit,
                                    "question": question_text,
                                    "attempt": attempt + 1
                                })
                                print(f"   🤖 AI: {question_text[:60]}...")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ❌ Error in attempt {attempt + 1}: {str(e)}")
        
        # Analyze results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   • AI-Generated Questions: {len(ai_questions)}")
        print(f"   • Fallback Questions: {len(fallback_questions)}")
        
        total_questions = len(ai_questions) + len(fallback_questions)
        if total_questions > 0:
            ai_percentage = (len(ai_questions) / total_questions) * 100
            fallback_percentage = (len(fallback_questions) / total_questions) * 100
            
            print(f"   • AI Generation Rate: {ai_percentage:.1f}%")
            print(f"   • Fallback Rate: {fallback_percentage:.1f}%")
            
            if fallback_percentage > 50:
                print(f"   ⚠️ HIGH FALLBACK USAGE: AI generation may be failing frequently")
            elif fallback_percentage > 20:
                print(f"   ⚠️ MODERATE FALLBACK USAGE: Some AI generation failures")
            else:
                print(f"   ✅ LOW FALLBACK USAGE: AI generation working well")
        
        # Show examples
        if fallback_questions:
            print(f"\n🔄 FALLBACK QUESTION EXAMPLES:")
            for i, fq in enumerate(fallback_questions[:5]):
                print(f"   {i+1}. {fq['subject']} - {fq['unit']}: {fq['question'][:80]}...")
        
        if ai_questions:
            print(f"\n🤖 AI-GENERATED QUESTION EXAMPLES:")
            for i, aq in enumerate(ai_questions[:5]):
                print(f"   {i+1}. {aq['subject']} - {aq['unit']}: {aq['question'][:80]}...")
        
        return True

    def test_unrelated_questions_specifically(self):
        """Test for the specific issue of unrelated questions"""
        print(f"\n🎯 TESTING FOR UNRELATED QUESTIONS...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test cases that might produce unrelated questions
        problematic_cases = [
            # English subject (might generate generic English questions)
            {"subject": "english", "topics": ["Nelson Mandela: Long Walk to Freedom"], "expected_content": ["mandela", "apartheid", "freedom", "south africa"]},
            
            # Multiple topics (might cause confusion)
            {"subject": "math", "topics": ["Real Numbers", "Quadratic Equations"], "expected_content": ["rational", "irrational", "quadratic", "discriminant"]},
            
            # Less common subjects
            {"subject": "history", "topics": ["The Rise of Nationalism in Europe"], "expected_content": ["nationalism", "europe", "revolution"]},
            {"subject": "geography", "topics": ["Resources and Development"], "expected_content": ["resources", "development", "natural"]},
        ]
        
        unrelated_questions = []
        
        for case in problematic_cases:
            subject = case["subject"]
            topics = case["topics"]
            expected_content = case["expected_content"]
            
            print(f"\n📋 Testing {subject.upper()} - {topics}")
            
            for attempt in range(3):
                gen_payload = {
                    "subject": subject,
                    "topics": topics,
                    "difficulty": "medium",
                    "question_count": 5
                }
                
                try:
                    response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get("questions", [])
                        
                        if not questions:
                            print(f"   ❌ No questions generated for {subject}")
                            continue
                        
                        for i, question in enumerate(questions):
                            question_text = question.get("question_text", "").lower()
                            explanation = question.get("explanation", "").lower()
                            topic = question.get("topic", "")
                            
                            # Check if question contains expected content
                            has_expected_content = any(
                                content in question_text or content in explanation 
                                for content in expected_content
                            )
                            
                            # Check if topic matches expected topics
                            topic_matches = any(
                                expected_topic.lower() in topic.lower() 
                                for expected_topic in topics
                            )
                            
                            if not has_expected_content and not topic_matches:
                                unrelated_questions.append({
                                    "subject": subject,
                                    "expected_topics": topics,
                                    "actual_topic": topic,
                                    "question": question.get("question_text", ""),
                                    "explanation": explanation,
                                    "attempt": attempt + 1,
                                    "question_num": i + 1
                                })
                                print(f"   ❌ UNRELATED Q{i+1}: {question.get('question_text', '')[:60]}...")
                                print(f"      Topic: '{topic}' (Expected: {topics})")
                            else:
                                print(f"   ✅ RELATED Q{i+1}: {question.get('question_text', '')[:60]}...")
                    
                    else:
                        print(f"   ❌ Generation failed: {response.status_code}")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"   ❌ Error in attempt {attempt + 1}: {str(e)}")
        
        # Report unrelated questions
        if unrelated_questions:
            print(f"\n🚨 FOUND {len(unrelated_questions)} UNRELATED QUESTIONS:")
            
            for i, uq in enumerate(unrelated_questions):
                print(f"\n   {i+1}. Subject: {uq['subject']}")
                print(f"      Expected Topics: {uq['expected_topics']}")
                print(f"      Actual Topic: '{uq['actual_topic']}'")
                print(f"      Question: {uq['question']}")
                print(f"      Explanation: {uq['explanation'][:100]}...")
        else:
            print(f"\n✅ NO UNRELATED QUESTIONS FOUND")
        
        return len(unrelated_questions) == 0

    def run_ai_fallback_test(self):
        """Run comprehensive AI vs fallback testing"""
        print("🚀 STARTING AI vs FALLBACK SYSTEM TESTING")
        
        # Setup account
        if not self.setup_student_account():
            print("❌ Failed to setup account - cannot proceed")
            return False
        
        # Test AI vs fallback patterns
        self.test_ai_vs_fallback_patterns()
        
        # Test for unrelated questions specifically
        no_unrelated = self.test_unrelated_questions_specifically()
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if no_unrelated:
            print("   ✅ No unrelated questions found in current testing")
        else:
            print("   ❌ Found unrelated questions - issue confirmed")
        
        return True

if __name__ == "__main__":
    tester = AIFallbackTester()
    success = tester.run_ai_fallback_test()
    exit(0 if success else 1)
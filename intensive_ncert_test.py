#!/usr/bin/env python3
"""
INTENSIVE NCERT Units Relevancy Testing - Edge Cases
Tests different scenarios to reproduce the inconsistency issue
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv
import time
import random

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 INTENSIVE NCERT EDGE CASE TESTING")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class IntensiveNCERTTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.problematic_questions = []

    def setup_student_account(self):
        """Setup student account for testing"""
        print("\n🔧 SETTING UP TEST ACCOUNT...")
        
        student_payload = {
            "email": f"intensive_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Intensive Test Student",
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

    def test_different_scenarios(self):
        """Test different scenarios that might trigger generic questions"""
        print("\n🔍 TESTING DIFFERENT SCENARIOS...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test scenarios that might trigger issues
        test_scenarios = [
            # Different question counts
            {"name": "High Question Count", "subject": "math", "topics": ["Real Numbers"], "difficulty": "medium", "question_count": 10},
            {"name": "Low Question Count", "subject": "math", "topics": ["Real Numbers"], "difficulty": "medium", "question_count": 1},
            
            # Different difficulties
            {"name": "Easy Difficulty", "subject": "math", "topics": ["Quadratic Equations"], "difficulty": "easy", "question_count": 5},
            {"name": "Hard Difficulty", "subject": "math", "topics": ["Quadratic Equations"], "difficulty": "hard", "question_count": 5},
            {"name": "Mixed Difficulty", "subject": "math", "topics": ["Quadratic Equations"], "difficulty": "mixed", "question_count": 5},
            
            # Multiple topics (might cause confusion)
            {"name": "Multiple Math Topics", "subject": "math", "topics": ["Real Numbers", "Quadratic Equations", "Polynomials"], "difficulty": "medium", "question_count": 6},
            {"name": "Multiple Biology Topics", "subject": "biology", "topics": ["Nutrition in Plants", "The Fundamental Unit of Life"], "difficulty": "medium", "question_count": 4},
            
            # Different subjects
            {"name": "English Subject", "subject": "english", "topics": ["Nelson Mandela: Long Walk to Freedom"], "difficulty": "medium", "question_count": 3},
            {"name": "History Subject", "subject": "history", "topics": ["The Rise of Nationalism in Europe"], "difficulty": "medium", "question_count": 3},
            
            # Rapid fire requests (might hit cache issues)
            {"name": "Rapid Fire 1", "subject": "physics", "topics": ["Laws of Motion"], "difficulty": "medium", "question_count": 3},
            {"name": "Rapid Fire 2", "subject": "physics", "topics": ["Laws of Motion"], "difficulty": "medium", "question_count": 3},
            {"name": "Rapid Fire 3", "subject": "physics", "topics": ["Laws of Motion"], "difficulty": "medium", "question_count": 3},
        ]
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            print(f"   Subject: {scenario['subject']}, Topics: {scenario['topics']}")
            print(f"   Difficulty: {scenario['difficulty']}, Count: {scenario['question_count']}")
            
            # Make multiple attempts for each scenario
            for attempt in range(1, 4):  # 3 attempts per scenario
                print(f"   Attempt {attempt}/3...")
                
                gen_payload = {
                    "subject": scenario["subject"],
                    "topics": scenario["topics"],
                    "difficulty": scenario["difficulty"],
                    "question_count": scenario["question_count"]
                }
                
                try:
                    response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                    
                    if response.status_code != 200:
                        print(f"   ❌ Generation failed: {response.status_code}")
                        print(f"      Response: {response.text[:200]}...")
                        continue
                    
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    if not questions:
                        print(f"   ❌ No questions generated")
                        continue
                    
                    print(f"   ✅ Generated {len(questions)} questions")
                    
                    # Analyze each question in detail
                    for i, question in enumerate(questions):
                        self.analyze_question_detailed(question, scenario, attempt, i+1)
                    
                    # Small delay for rapid fire tests
                    if "Rapid Fire" in scenario["name"]:
                        time.sleep(0.5)
                    else:
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"   ❌ Error in attempt {attempt}: {str(e)}")
                    continue
        
        return True

    def analyze_question_detailed(self, question, scenario, attempt, question_num):
        """Analyze a question in detail for potential issues"""
        question_text = question.get("question_text", "")
        topic = question.get("topic", "")
        explanation = question.get("explanation", "")
        options = question.get("options", [])
        
        print(f"      Q{question_num}: {question_text[:80]}...")
        print(f"         Topic: '{topic}'")
        
        # Check for potential issues
        issues = []
        
        # Check if question is too generic
        generic_phrases = [
            "what is the main concept",
            "choose the correct option",
            "which of the following is true",
            "select the right answer",
            "what is the basic",
            "identify the correct",
            "sample question",
            "example problem"
        ]
        
        if any(phrase in question_text.lower() for phrase in generic_phrases):
            issues.append("Generic phrasing detected")
        
        # Check if topic field matches expected topics
        expected_topics = scenario["topics"]
        topic_matches = any(expected_topic.lower() in topic.lower() for expected_topic in expected_topics)
        if not topic_matches and topic:
            issues.append(f"Topic mismatch: got '{topic}', expected one of {expected_topics}")
        
        # Check if question mentions specific NCERT concepts
        ncert_concepts = {
            "Real Numbers": ["rational", "irrational", "decimal", "terminating", "non-terminating"],
            "Quadratic Equations": ["quadratic", "discriminant", "roots", "factoring"],
            "Nutrition in Plants": ["photosynthesis", "chlorophyll", "stomata", "autotrophic"],
            "Laws of Motion": ["newton", "force", "acceleration", "inertia", "momentum"],
            "Polynomials": ["polynomial", "degree", "coefficient", "factorization"],
            "The Fundamental Unit of Life": ["cell", "nucleus", "cytoplasm", "organelles"],
            "Nelson Mandela: Long Walk to Freedom": ["mandela", "apartheid", "freedom", "south africa"]
        }
        
        has_relevant_concepts = False
        for expected_topic in expected_topics:
            if expected_topic in ncert_concepts:
                concepts = ncert_concepts[expected_topic]
                if any(concept in question_text.lower() or concept in explanation.lower() for concept in concepts):
                    has_relevant_concepts = True
                    break
        
        if not has_relevant_concepts:
            issues.append("No NCERT-specific concepts found")
        
        # Check for repetitive content (might indicate caching issues)
        question_hash = hash(question_text)
        if hasattr(self, 'seen_questions'):
            if question_hash in self.seen_questions:
                issues.append("Duplicate question detected (possible cache issue)")
        else:
            self.seen_questions = set()
        self.seen_questions.add(question_hash)
        
        # Report issues
        if issues:
            print(f"         ⚠️ ISSUES: {', '.join(issues)}")
            self.problematic_questions.append({
                "scenario": scenario["name"],
                "attempt": attempt,
                "question_num": question_num,
                "question_text": question_text,
                "topic": topic,
                "explanation": explanation,
                "issues": issues,
                "expected_topics": expected_topics
            })
        else:
            print(f"         ✅ No issues detected")

    def test_cache_behavior(self):
        """Test if cache is causing issues with stale/wrong questions"""
        print(f"\n🗄️ TESTING CACHE BEHAVIOR...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test same request multiple times to check cache consistency
        test_payload = {
            "subject": "math",
            "topics": ["Real Numbers"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        print("   Making 10 identical requests to check cache consistency...")
        
        all_responses = []
        for i in range(10):
            try:
                response = requests.post(f"{API_URL}/practice/generate", json=test_payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    all_responses.append(questions)
                    print(f"   Request {i+1}: {len(questions)} questions")
                else:
                    print(f"   Request {i+1}: Failed ({response.status_code})")
                
                time.sleep(0.2)  # Small delay
            except Exception as e:
                print(f"   Request {i+1}: Error - {str(e)}")
        
        # Analyze cache behavior
        if all_responses:
            # Check if all responses are identical (strong caching)
            first_response = json.dumps(all_responses[0], sort_keys=True)
            all_identical = all(json.dumps(resp, sort_keys=True) == first_response for resp in all_responses)
            
            if all_identical:
                print("   📋 CACHE BEHAVIOR: All responses identical (strong caching)")
            else:
                print("   📋 CACHE BEHAVIOR: Responses vary (weak/no caching or fresh generation)")
                
                # Check for patterns in variation
                unique_responses = set(json.dumps(resp, sort_keys=True) for resp in all_responses)
                print(f"   📊 Found {len(unique_responses)} unique response patterns")
        
        return True

    def run_intensive_test(self):
        """Run intensive testing to find edge cases"""
        print("🚀 STARTING INTENSIVE NCERT EDGE CASE TESTING")
        
        # Setup account
        if not self.setup_student_account():
            print("❌ Failed to setup account - cannot proceed")
            return False
        
        # Run different test scenarios
        self.test_different_scenarios()
        
        # Test cache behavior
        self.test_cache_behavior()
        
        # Generate report
        self.generate_intensive_report()
        
        return True

    def generate_intensive_report(self):
        """Generate detailed report of intensive testing"""
        print("\n" + "="*80)
        print("📊 INTENSIVE TESTING REPORT")
        print("="*80)
        
        if self.problematic_questions:
            print(f"\n🚨 FOUND {len(self.problematic_questions)} PROBLEMATIC QUESTIONS:")
            
            # Group by issue type
            issue_types = {}
            for pq in self.problematic_questions:
                for issue in pq["issues"]:
                    if issue not in issue_types:
                        issue_types[issue] = []
                    issue_types[issue].append(pq)
            
            for issue_type, questions in issue_types.items():
                print(f"\n   📋 {issue_type.upper()} ({len(questions)} questions):")
                for i, pq in enumerate(questions[:3]):  # Show first 3 examples
                    print(f"      {i+1}. Scenario: {pq['scenario']}")
                    print(f"         Question: {pq['question_text'][:100]}...")
                    print(f"         Topic: '{pq['topic']}'")
                    print(f"         Expected: {pq['expected_topics']}")
                
                if len(questions) > 3:
                    print(f"      ... and {len(questions) - 3} more")
            
            print(f"\n💡 RECOMMENDATIONS BASED ON ISSUES FOUND:")
            if any("Generic phrasing" in pq["issues"] for pq in self.problematic_questions):
                print("   • Improve AI prompts to avoid generic question templates")
            if any("Topic mismatch" in issue for pq in self.problematic_questions for issue in pq["issues"]):
                print("   • Fix topic field assignment in question generation")
            if any("No NCERT-specific concepts" in pq["issues"] for pq in self.problematic_questions):
                print("   • Strengthen unit-specific content validation")
            if any("Duplicate question" in issue for pq in self.problematic_questions for issue in pq["issues"]):
                print("   • Review caching strategy to ensure variety")
        
        else:
            print("\n✅ NO PROBLEMATIC QUESTIONS FOUND IN INTENSIVE TESTING")
            print("   All generated questions appear to be unit-specific and relevant")
        
        print(f"\n🎯 INTENSIVE TEST CONCLUSION:")
        if len(self.problematic_questions) == 0:
            print("   ✅ EXCELLENT: No issues found in edge case testing")
        elif len(self.problematic_questions) < 5:
            print("   ⚠️ MINOR ISSUES: Few edge cases found, mostly working well")
        else:
            print("   ❌ SIGNIFICANT ISSUES: Multiple problems found requiring attention")

if __name__ == "__main__":
    tester = IntensiveNCERTTester()
    success = tester.run_intensive_test()
    exit(0 if success else 1)
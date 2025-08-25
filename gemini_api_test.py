#!/usr/bin/env python3
"""
CRITICAL GEMINI API KEY VERIFICATION TEST
Tests the new Gemini API key functionality to ensure AI-powered practice test questions
are being generated instead of fallback questions.
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

print(f"🎯 CRITICAL GEMINI API KEY VERIFICATION TEST")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class GeminiAPITester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = []

    def log_result(self, test_name, success, message="", details=None):
        """Log test result with details"""
        status = "✅ WORKING" if success else "❌ BROKEN"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if details and not success:
            print(f"    Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })

    def setup_student_account(self):
        """Setup student account for testing"""
        print("\n🔧 SETTING UP TEST STUDENT ACCOUNT...")
        
        student_payload = {
            "email": f"gemini_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Gemini Test Student",
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

    def test_gemini_api_key_functionality(self):
        """Test 1: Verify Gemini API Key is Working"""
        print("\n1️⃣ TESTING GEMINI API KEY FUNCTIONALITY...")
        
        if not self.student_token:
            self.log_result("Gemini API Key Test", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test subjects to verify AI generation
        test_subjects = [
            {"subject": "math", "topics": ["Algebra"], "expected_concepts": ["equation", "solve", "variable", "x"]},
            {"subject": "physics", "topics": ["Mechanics"], "expected_concepts": ["force", "motion", "newton", "velocity"]},
            {"subject": "chemistry", "topics": ["Organic Chemistry"], "expected_concepts": ["carbon", "molecule", "bond", "compound"]},
            {"subject": "biology", "topics": ["Cell Biology"], "expected_concepts": ["cell", "membrane", "nucleus", "organelle"]},
            {"subject": "english", "topics": ["Grammar"], "expected_concepts": ["sentence", "verb", "noun", "grammar"]}
        ]
        
        ai_generated_count = 0
        fallback_count = 0
        total_tests = len(test_subjects)
        
        for test_case in test_subjects:
            try:
                print(f"\n   Testing {test_case['subject']} - {test_case['topics'][0]}...")
                
                gen_payload = {
                    "subject": test_case["subject"],
                    "topics": test_case["topics"],
                    "difficulty": "medium",
                    "question_count": 3
                }
                
                response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    if questions:
                        # Analyze questions to determine if they're AI-generated or fallback
                        is_ai_generated = self.analyze_question_quality(questions, test_case)
                        
                        if is_ai_generated:
                            ai_generated_count += 1
                            print(f"   ✅ {test_case['subject']}: AI-generated questions detected")
                            
                            # Show sample question for verification
                            sample_q = questions[0]
                            print(f"   📝 Sample: {sample_q.get('question_text', '')[:100]}...")
                        else:
                            fallback_count += 1
                            print(f"   ⚠️ {test_case['subject']}: Fallback questions detected")
                    else:
                        fallback_count += 1
                        print(f"   ❌ {test_case['subject']}: No questions generated")
                else:
                    fallback_count += 1
                    print(f"   ❌ {test_case['subject']}: Generation failed ({response.status_code})")
                    
            except Exception as e:
                fallback_count += 1
                print(f"   ❌ {test_case['subject']}: Exception - {str(e)}")
        
        # Determine overall result
        ai_percentage = (ai_generated_count / total_tests) * 100
        
        if ai_generated_count >= 4:  # At least 4 out of 5 subjects should use AI
            self.log_result(
                "Gemini API Key Test", 
                True, 
                f"AI generation working: {ai_generated_count}/{total_tests} subjects ({ai_percentage:.0f}%)"
            )
            return True
        elif ai_generated_count >= 2:  # Partial success
            self.log_result(
                "Gemini API Key Test", 
                False, 
                f"Partial AI generation: {ai_generated_count}/{total_tests} subjects ({ai_percentage:.0f}%) - Some subjects still using fallback"
            )
            return False
        else:
            self.log_result(
                "Gemini API Key Test", 
                False, 
                f"AI generation failed: Only {ai_generated_count}/{total_tests} subjects using AI ({ai_percentage:.0f}%) - Mostly fallback questions"
            )
            return False

    def analyze_question_quality(self, questions, test_case):
        """Analyze if questions are AI-generated or fallback"""
        ai_indicators = 0
        fallback_indicators = 0
        
        for question in questions:
            question_text = question.get("question_text", "").lower()
            explanation = question.get("explanation", "").lower()
            
            # Check for fallback question patterns
            fallback_patterns = [
                "what is a fundamental concept",
                "basic principle of",
                "advanced application in",
                "historical development of",
                "modern research in",
                "solve for x: 2x + 5 = 17",  # Known fallback questions
                "what is the slope of the line y = 3x - 4",
                "what is newton's first law of motion",
                "what is the molecular formula for methane",
                "what is the powerhouse of the cell",
                "who wrote romeo and juliet"
            ]
            
            # Check for AI-generated indicators
            ai_patterns = [
                "calculate", "determine", "find the value", "solve the equation",
                "explain why", "what happens when", "compare and contrast",
                "analyze the", "evaluate the", "derive the formula"
            ]
            
            # Check for subject-specific expected concepts
            expected_concepts = test_case.get("expected_concepts", [])
            concept_matches = sum(1 for concept in expected_concepts if concept in question_text or concept in explanation)
            
            # Scoring logic
            if any(pattern in question_text for pattern in fallback_patterns):
                fallback_indicators += 2
            
            if any(pattern in question_text for pattern in ai_patterns):
                ai_indicators += 1
                
            if concept_matches >= 1:
                ai_indicators += 1
                
            # Check for unique, contextual content (not generic)
            if len(question_text) > 50 and "fundamental concept" not in question_text:
                ai_indicators += 1
                
            # Check for detailed explanations (AI tends to give better explanations)
            if len(explanation) > 100:
                ai_indicators += 1
        
        # Determine if questions are AI-generated
        return ai_indicators > fallback_indicators

    def test_question_uniqueness(self):
        """Test 2: Verify Questions are Unique and Varied"""
        print("\n2️⃣ TESTING QUESTION UNIQUENESS AND VARIETY...")
        
        if not self.student_token:
            self.log_result("Question Uniqueness Test", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Generate multiple tests for the same subject to check uniqueness
        gen_payload = {
            "subject": "math",
            "topics": ["Algebra"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        all_questions = []
        unique_questions = set()
        
        try:
            # Generate 3 different tests
            for i in range(3):
                response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    for question in questions:
                        question_text = question.get("question_text", "")
                        all_questions.append(question_text)
                        unique_questions.add(question_text)
                else:
                    print(f"   ❌ Generation {i+1} failed: {response.status_code}")
            
            # Calculate uniqueness
            total_questions = len(all_questions)
            unique_count = len(unique_questions)
            uniqueness_percentage = (unique_count / total_questions * 100) if total_questions > 0 else 0
            
            print(f"   📊 Generated {total_questions} questions, {unique_count} unique ({uniqueness_percentage:.0f}%)")
            
            if uniqueness_percentage >= 80:  # At least 80% should be unique
                self.log_result(
                    "Question Uniqueness Test", 
                    True, 
                    f"Good variety: {uniqueness_percentage:.0f}% unique questions"
                )
                return True
            else:
                self.log_result(
                    "Question Uniqueness Test", 
                    False, 
                    f"Poor variety: Only {uniqueness_percentage:.0f}% unique questions - may be using fallback bank"
                )
                return False
                
        except Exception as e:
            self.log_result("Question Uniqueness Test", False, f"Exception: {str(e)}")
            return False

    def test_no_rate_limit_errors(self):
        """Test 3: Verify No 429 Rate Limit Errors"""
        print("\n3️⃣ TESTING FOR RATE LIMIT ERRORS...")
        
        if not self.student_token:
            self.log_result("Rate Limit Test", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        rate_limit_errors = 0
        successful_requests = 0
        
        # Make multiple rapid requests to test rate limiting
        for i in range(5):
            try:
                gen_payload = {
                    "subject": "math",
                    "topics": ["Geometry"],
                    "difficulty": "easy",
                    "question_count": 2
                }
                
                response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                
                if response.status_code == 429:
                    rate_limit_errors += 1
                    print(f"   ❌ Request {i+1}: Rate limit error (429)")
                elif response.status_code == 200:
                    successful_requests += 1
                    print(f"   ✅ Request {i+1}: Success (200)")
                else:
                    print(f"   ⚠️ Request {i+1}: Other error ({response.status_code})")
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Request {i+1}: Exception - {str(e)}")
        
        if rate_limit_errors == 0:
            self.log_result(
                "Rate Limit Test", 
                True, 
                f"No rate limit errors: {successful_requests}/5 requests successful"
            )
            return True
        else:
            self.log_result(
                "Rate Limit Test", 
                False, 
                f"Rate limit errors detected: {rate_limit_errors}/5 requests failed with 429"
            )
            return False

    def test_question_educational_quality(self):
        """Test 4: Verify Educational Quality of Generated Questions"""
        print("\n4️⃣ TESTING EDUCATIONAL QUALITY...")
        
        if not self.student_token:
            self.log_result("Educational Quality Test", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test different difficulty levels
        difficulty_tests = [
            {"difficulty": "easy", "expected_complexity": "basic"},
            {"difficulty": "medium", "expected_complexity": "moderate"},
            {"difficulty": "hard", "expected_complexity": "advanced"}
        ]
        
        quality_score = 0
        total_tests = len(difficulty_tests)
        
        for test_case in difficulty_tests:
            try:
                gen_payload = {
                    "subject": "physics",
                    "topics": ["Mechanics"],
                    "difficulty": test_case["difficulty"],
                    "question_count": 2
                }
                
                response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    if questions:
                        # Analyze educational quality
                        has_proper_structure = all(
                            q.get("question_text") and 
                            q.get("correct_answer") and 
                            q.get("explanation") 
                            for q in questions
                        )
                        
                        has_educational_content = any(
                            len(q.get("explanation", "")) > 20 
                            for q in questions
                        )
                        
                        if has_proper_structure and has_educational_content:
                            quality_score += 1
                            print(f"   ✅ {test_case['difficulty']}: Good educational quality")
                        else:
                            print(f"   ⚠️ {test_case['difficulty']}: Poor educational quality")
                    else:
                        print(f"   ❌ {test_case['difficulty']}: No questions generated")
                else:
                    print(f"   ❌ {test_case['difficulty']}: Generation failed ({response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {test_case['difficulty']}: Exception - {str(e)}")
        
        quality_percentage = (quality_score / total_tests) * 100
        
        if quality_score >= 2:  # At least 2 out of 3 difficulty levels should pass
            self.log_result(
                "Educational Quality Test", 
                True, 
                f"Good educational quality: {quality_score}/{total_tests} difficulty levels passed ({quality_percentage:.0f}%)"
            )
            return True
        else:
            self.log_result(
                "Educational Quality Test", 
                False, 
                f"Poor educational quality: Only {quality_score}/{total_tests} difficulty levels passed ({quality_percentage:.0f}%)"
            )
            return False

    def run_comprehensive_gemini_test(self):
        """Run all Gemini API tests"""
        print("🚀 STARTING COMPREHENSIVE GEMINI API KEY VERIFICATION")
        
        # Setup
        if not self.setup_student_account():
            print("❌ Failed to setup student account - cannot proceed")
            return False
        
        # Run all critical tests
        test_functions = [
            self.test_gemini_api_key_functionality,
            self.test_question_uniqueness,
            self.test_no_rate_limit_errors,
            self.test_question_educational_quality
        ]
        
        for test_func in test_functions:
            test_func()
        
        # Summary
        print("\n" + "="*80)
        print("📊 GEMINI API KEY VERIFICATION SUMMARY")
        print("="*80)
        
        working_features = [result for result in self.test_results if result["success"]]
        broken_features = [result for result in self.test_results if not result["success"]]
        
        print(f"\n✅ WORKING FEATURES ({len(working_features)}):")
        for result in working_features:
            print(f"   • {result['test']}: {result['message']}")
        
        if broken_features:
            print(f"\n❌ ISSUES FOUND ({len(broken_features)}):")
            for result in broken_features:
                print(f"   • {result['test']}: {result['message']}")
        
        success_rate = (len(working_features) / len(self.test_results)) * 100
        print(f"\n📈 SUCCESS RATE: {success_rate:.1f}% ({len(working_features)}/{len(self.test_results)} tests passed)")
        
        if success_rate >= 75:
            print("\n🎉 GEMINI API KEY IS WORKING!")
            print("✅ AI-powered question generation is operational")
            print("✅ Ready for demo with dynamic, varied educational content")
        else:
            print("\n⚠️ GEMINI API KEY NEEDS ATTENTION")
            print("❌ AI generation may not be working properly")
            print("❌ May still be using fallback questions")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = GeminiAPITester()
    success = tester.run_comprehensive_gemini_test()
    exit(0 if success else 1)
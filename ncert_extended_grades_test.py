#!/usr/bin/env python3
"""
NCERT Extended Grades Integration Test (6th, 7th, 8th)
Testing the newly added NCERT units for younger grade levels
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
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class NCERTExtendedGradesTest:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        
    def register_student(self):
        """Register a test student"""
        print("\n🔍 Registering test student...")
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"ncert_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Arjun Kumar",
            "user_type": "student",
            "grade_level": "8th"
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

    def test_ncert_extended_grades_integration(self):
        """Test NCERT Units Integration for Extended Grades 6th, 7th, and 8th"""
        print("\n🔍 Testing NCERT Extended Grades Integration (6th, 7th, 8th)...")
        
        if not self.student_token:
            print("❌ Student token not available")
            return False
        
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test scenarios for NEW grade levels (6th, 7th, 8th) as requested in review
        test_scenarios = [
            {
                "name": "Math 6th Grade - Basic Concepts",
                "subject": "math",
                "topics": ["Knowing Our Numbers", "Whole Numbers", "Fractions"],
                "expected_terms": ["number", "whole", "fraction", "numerator", "denominator", "basic"],
                "grade": "6th"
            },
            {
                "name": "Math 7th Grade - Intermediate Concepts", 
                "subject": "math",
                "topics": ["Integers", "Simple Equations", "Rational Numbers"],
                "expected_terms": ["integer", "equation", "rational", "positive", "negative", "solve"],
                "grade": "7th"
            },
            {
                "name": "Math 8th Grade - Advanced Concepts",
                "subject": "math",
                "topics": ["Rational Numbers", "Linear Equations in One Variable", "Algebraic Expressions and Identities"],
                "expected_terms": ["rational", "linear", "algebraic", "expression", "identity", "variable"],
                "grade": "8th"
            },
            {
                "name": "Biology 7th Grade - Life Processes",
                "subject": "biology",
                "topics": ["Nutrition in Plants", "Respiration in Organisms", "Transportation in Animals and Plants"],
                "expected_terms": ["nutrition", "plant", "respiration", "organism", "transportation", "photosynthesis"],
                "grade": "7th"
            },
            {
                "name": "Physics 8th Grade - Forces and Motion",
                "subject": "physics",
                "topics": ["Force and Pressure", "Friction", "Sound"],
                "expected_terms": ["force", "pressure", "friction", "sound", "motion", "energy"],
                "grade": "8th"
            },
            {
                "name": "Chemistry 8th Grade - Materials",
                "subject": "chemistry",
                "topics": ["Materials: Metals and Non-Metals", "Combustion and Flame", "Chemical Effects of Electric Current"],
                "expected_terms": ["metal", "non-metal", "combustion", "flame", "chemical", "reaction"],
                "grade": "8th"
            }
        ]
        
        successful_tests = 0
        total_tests = len(test_scenarios)
        age_appropriate_questions = 0
        
        for scenario in test_scenarios:
            try:
                payload = {
                    "subject": scenario["subject"],
                    "topics": scenario["topics"],
                    "difficulty": "easy" if scenario["grade"] in ["6th", "7th"] else "medium",
                    "question_count": 3
                }
                
                response = requests.post(url, json=payload, headers=headers)
                print(f"\nTesting {scenario['name']}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    if len(questions) > 0:
                        # Check if questions contain relevant terminology
                        relevant_content_found = False
                        age_appropriate_content = False
                        
                        for question in questions:
                            question_text = question.get("question_text", "").lower()
                            explanation = question.get("explanation", "").lower()
                            combined_text = question_text + " " + explanation
                            
                            # Check for subject-specific terminology
                            for term in scenario["expected_terms"]:
                                if term in combined_text:
                                    relevant_content_found = True
                                    break
                            
                            # Check for age-appropriate language for younger grades
                            if scenario["grade"] in ["6th", "7th", "8th"]:
                                # Look for simpler language patterns
                                simple_words = ["basic", "simple", "easy", "understand", "learn", "know", "find", "what", "which"]
                                complex_words = ["sophisticated", "complex", "advanced", "intricate", "elaborate"]
                                
                                simple_count = sum(1 for word in simple_words if word in combined_text)
                                complex_count = sum(1 for word in complex_words if word in combined_text)
                                
                                # Age-appropriate if more simple words than complex words or equal
                                if simple_count >= complex_count:
                                    age_appropriate_content = True
                            
                            print(f"   ✅ {scenario['grade']} Grade Question: {question_text[:60]}...")
                        
                        if relevant_content_found:
                            successful_tests += 1
                            print(f"   ✓ Contains relevant {scenario['subject']} terminology")
                        
                        if age_appropriate_content:
                            age_appropriate_questions += 1
                            print(f"   ✓ Age-appropriate language for {scenario['grade']} grade")
                        
                        if not relevant_content_found:
                            print(f"   ⚠️ Missing expected terminology for {scenario['name']}")
                    else:
                        print(f"   ❌ No questions generated for {scenario['name']}")
                else:
                    print(f"   ❌ Failed to generate questions for {scenario['name']}: {response.status_code}")
                    if response.status_code != 200:
                        print(f"      Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception testing {scenario['name']}: {str(e)}")
        
        # Calculate success metrics
        success_rate = (successful_tests / total_tests) * 100
        age_appropriate_rate = (age_appropriate_questions / total_tests) * 100
        
        print(f"\n📊 NCERT Extended Grades Integration Results:")
        print(f"   Total scenarios tested: {total_tests}")
        print(f"   Successful tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   Age-appropriate questions: {age_appropriate_questions}/{total_tests} ({age_appropriate_rate:.1f}%)")
        
        # Verify that the backend handles the expanded grade range seamlessly
        if successful_tests > 0 and success_rate >= 70:
            if success_rate >= 90:
                print("✅ EXCELLENT: NCERT Extended Grades Integration working perfectly!")
            elif success_rate >= 70:
                print("✅ GOOD: NCERT Extended Grades Integration working well with minor issues")
            print("✅ NCERT Extended Grades (6th, 7th, 8th) Integration test completed successfully")
            return True
        else:
            print("⚠️ NEEDS IMPROVEMENT: NCERT Extended Grades Integration has significant issues")
            print("❌ NCERT Extended Grades (6th, 7th, 8th) Integration test failed")
            return False

    def run_all_tests(self):
        """Run all NCERT extended grades tests"""
        print("🚀 Starting NCERT Extended Grades Integration Testing...")
        
        # Register student
        if not self.register_student():
            print("❌ Failed to register student, cannot continue testing")
            return False
        
        # Test NCERT extended grades integration
        test_result = self.test_ncert_extended_grades_integration()
        
        if test_result:
            print("\n🎉 All NCERT Extended Grades Integration tests passed!")
            return True
        else:
            print("\n❌ Some NCERT Extended Grades Integration tests failed")
            return False

if __name__ == "__main__":
    tester = NCERTExtendedGradesTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
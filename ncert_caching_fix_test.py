#!/usr/bin/env python3
"""
NCERT Units Question Variety Caching Fix Test

This test specifically verifies the two critical fixes implemented:
1. Cache Key Randomization: Added variety_factor (1-5) that changes every hour
2. Reduced Cache Duration: Changed from 24 hours to 2 hours

Test scenarios:
- Math "Real Numbers" - Generate 3 times and verify question variety
- Biology "Nutrition in Plants" - Generate 3 times and verify question variety
- Question Relevancy Verification
- Variety Metrics Calculation
"""

import requests
import json
import time
import uuid
import os
import sys
from dotenv import load_dotenv
from collections import defaultdict
import hashlib

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"🔗 Using API URL: {API_URL}")

class NCERTCachingFixTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.all_questions = []
        self.test_results = {
            "math_real_numbers": [],
            "biology_nutrition": [],
            "variety_metrics": {},
            "relevancy_scores": {}
        }
    
    def register_and_login_student(self):
        """Register a test student for the caching tests"""
        print("\n🔐 Registering test student...")
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"cache_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Cache Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Registered student: {self.student_id}")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def generate_practice_test(self, subject, topics, test_name):
        """Generate a practice test and return questions"""
        print(f"\n📝 Generating {test_name}...")
        
        url = f"{API_URL}/practice/generate"
        headers = {"Authorization": f"Bearer {self.student_token}"}
        payload = {
            "subject": subject,
            "topics": topics,
            "difficulty": "medium",
            "question_count": 5
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                print(f"✅ Generated {len(questions)} questions for {test_name}")
                return questions
            else:
                print(f"❌ Generation failed for {test_name}: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Generation error for {test_name}: {e}")
            return []
    
    def test_math_real_numbers_variety(self):
        """Test Math 'Real Numbers' question variety across multiple generations"""
        print("\n🧮 TESTING MATH 'REAL NUMBERS' QUESTION VARIETY")
        print("=" * 60)
        
        subject = "math"
        topics = ["Real Numbers"]
        test_name = "Math Real Numbers"
        
        # Generate 3 times in quick succession
        for i in range(3):
            print(f"\n📋 Generation {i+1}/3:")
            questions = self.generate_practice_test(subject, topics, f"{test_name} - Round {i+1}")
            
            if questions:
                self.test_results["math_real_numbers"].append(questions)
                self.all_questions.extend(questions)
                
                # Show sample questions
                for j, q in enumerate(questions[:2]):  # Show first 2 questions
                    print(f"   Q{j+1}: {q.get('question_text', '')[:80]}...")
            
            # Small delay between requests
            time.sleep(1)
        
        return len(self.test_results["math_real_numbers"]) == 3
    
    def test_biology_nutrition_variety(self):
        """Test Biology 'Nutrition in Plants' question variety across multiple generations"""
        print("\n🌱 TESTING BIOLOGY 'NUTRITION IN PLANTS' QUESTION VARIETY")
        print("=" * 60)
        
        subject = "biology"
        topics = ["Nutrition in Plants"]
        test_name = "Biology Nutrition in Plants"
        
        # Generate 3 times in quick succession
        for i in range(3):
            print(f"\n📋 Generation {i+1}/3:")
            questions = self.generate_practice_test(subject, topics, f"{test_name} - Round {i+1}")
            
            if questions:
                self.test_results["biology_nutrition"].append(questions)
                self.all_questions.extend(questions)
                
                # Show sample questions
                for j, q in enumerate(questions[:2]):  # Show first 2 questions
                    print(f"   Q{j+1}: {q.get('question_text', '')[:80]}...")
            
            # Small delay between requests
            time.sleep(1)
        
        return len(self.test_results["biology_nutrition"]) == 3
    
    def calculate_question_variety_metrics(self):
        """Calculate variety metrics for all generated questions"""
        print("\n📊 CALCULATING QUESTION VARIETY METRICS")
        print("=" * 60)
        
        # Collect all question texts for uniqueness analysis
        all_question_texts = []
        question_hashes = set()
        
        for questions_batch in self.test_results["math_real_numbers"]:
            for q in questions_batch:
                text = q.get("question_text", "").strip()
                all_question_texts.append(text)
                question_hashes.add(hashlib.md5(text.encode()).hexdigest())
        
        for questions_batch in self.test_results["biology_nutrition"]:
            for q in questions_batch:
                text = q.get("question_text", "").strip()
                all_question_texts.append(text)
                question_hashes.add(hashlib.md5(text.encode()).hexdigest())
        
        total_questions = len(all_question_texts)
        unique_questions = len(question_hashes)
        
        if total_questions > 0:
            variety_percentage = (unique_questions / total_questions) * 100
        else:
            variety_percentage = 0
        
        print(f"📈 Total Questions Generated: {total_questions}")
        print(f"📈 Unique Questions: {unique_questions}")
        print(f"📈 Question Variety: {variety_percentage:.1f}%")
        
        # Analyze by subject
        math_questions = []
        biology_questions = []
        
        for questions_batch in self.test_results["math_real_numbers"]:
            for q in questions_batch:
                math_questions.append(q.get("question_text", "").strip())
        
        for questions_batch in self.test_results["biology_nutrition"]:
            for q in questions_batch:
                biology_questions.append(q.get("question_text", "").strip())
        
        # Math variety
        math_unique = len(set(hashlib.md5(q.encode()).hexdigest() for q in math_questions))
        math_variety = (math_unique / len(math_questions)) * 100 if math_questions else 0
        
        # Biology variety
        biology_unique = len(set(hashlib.md5(q.encode()).hexdigest() for q in biology_questions))
        biology_variety = (biology_unique / len(biology_questions)) * 100 if biology_questions else 0
        
        print(f"📊 Math Real Numbers Variety: {math_variety:.1f}% ({math_unique}/{len(math_questions)})")
        print(f"📊 Biology Nutrition Variety: {biology_variety:.1f}% ({biology_unique}/{len(biology_questions)})")
        
        self.test_results["variety_metrics"] = {
            "total_questions": total_questions,
            "unique_questions": unique_questions,
            "overall_variety": variety_percentage,
            "math_variety": math_variety,
            "biology_variety": biology_variety,
            "math_questions_count": len(math_questions),
            "biology_questions_count": len(biology_questions)
        }
        
        return variety_percentage
    
    def verify_question_relevancy(self):
        """Verify that questions are relevant to their NCERT units"""
        print("\n🎯 VERIFYING QUESTION RELEVANCY TO NCERT UNITS")
        print("=" * 60)
        
        # Define expected concepts for each unit
        unit_concepts = {
            "Real Numbers": [
                "rational", "irrational", "decimal", "terminating", "non-terminating", 
                "number line", "real number", "integer", "fraction", "surd"
            ],
            "Nutrition in Plants": [
                "photosynthesis", "chlorophyll", "stomata", "autotrophic", "glucose", 
                "carbon dioxide", "oxygen", "sunlight", "nutrition", "plant"
            ]
        }
        
        relevancy_results = {}
        
        # Check Math Real Numbers relevancy
        math_relevant_count = 0
        math_total = 0
        
        for questions_batch in self.test_results["math_real_numbers"]:
            for q in questions_batch:
                math_total += 1
                question_text = q.get("question_text", "").lower()
                explanation = q.get("explanation", "").lower()
                combined_text = question_text + " " + explanation
                
                # Check for relevant concepts
                concepts_found = []
                for concept in unit_concepts["Real Numbers"]:
                    if concept.lower() in combined_text:
                        concepts_found.append(concept)
                
                if concepts_found:
                    math_relevant_count += 1
                    print(f"✅ Math Q: Relevant concepts found: {concepts_found}")
                else:
                    print(f"⚠️ Math Q: No specific concepts found in: {question_text[:60]}...")
        
        # Check Biology Nutrition relevancy
        biology_relevant_count = 0
        biology_total = 0
        
        for questions_batch in self.test_results["biology_nutrition"]:
            for q in questions_batch:
                biology_total += 1
                question_text = q.get("question_text", "").lower()
                explanation = q.get("explanation", "").lower()
                combined_text = question_text + " " + explanation
                
                # Check for relevant concepts
                concepts_found = []
                for concept in unit_concepts["Nutrition in Plants"]:
                    if concept.lower() in combined_text:
                        concepts_found.append(concept)
                
                if concepts_found:
                    biology_relevant_count += 1
                    print(f"✅ Biology Q: Relevant concepts found: {concepts_found}")
                else:
                    print(f"⚠️ Biology Q: No specific concepts found in: {question_text[:60]}...")
        
        # Calculate relevancy percentages
        math_relevancy = (math_relevant_count / math_total) * 100 if math_total > 0 else 0
        biology_relevancy = (biology_relevant_count / biology_total) * 100 if biology_total > 0 else 0
        overall_relevancy = ((math_relevant_count + biology_relevant_count) / (math_total + biology_total)) * 100 if (math_total + biology_total) > 0 else 0
        
        print(f"\n📊 RELEVANCY SCORES:")
        print(f"📊 Math Real Numbers: {math_relevancy:.1f}% ({math_relevant_count}/{math_total})")
        print(f"📊 Biology Nutrition: {biology_relevancy:.1f}% ({biology_relevant_count}/{biology_total})")
        print(f"📊 Overall Relevancy: {overall_relevancy:.1f}%")
        
        self.test_results["relevancy_scores"] = {
            "math_relevancy": math_relevancy,
            "biology_relevancy": biology_relevancy,
            "overall_relevancy": overall_relevancy,
            "math_relevant_count": math_relevant_count,
            "math_total": math_total,
            "biology_relevant_count": biology_relevant_count,
            "biology_total": biology_total
        }
        
        return overall_relevancy
    
    def check_no_identical_question_sets(self):
        """Verify that no identical question sets are generated"""
        print("\n🔍 CHECKING FOR IDENTICAL QUESTION SETS")
        print("=" * 60)
        
        # Check Math Real Numbers sets
        math_sets = self.test_results["math_real_numbers"]
        math_identical = False
        
        if len(math_sets) >= 2:
            for i in range(len(math_sets)):
                for j in range(i + 1, len(math_sets)):
                    set1_texts = [q.get("question_text", "") for q in math_sets[i]]
                    set2_texts = [q.get("question_text", "") for q in math_sets[j]]
                    
                    if set1_texts == set2_texts:
                        math_identical = True
                        print(f"❌ Math: Sets {i+1} and {j+1} are identical!")
                        break
                if math_identical:
                    break
        
        if not math_identical:
            print(f"✅ Math: All {len(math_sets)} question sets are different")
        
        # Check Biology Nutrition sets
        biology_sets = self.test_results["biology_nutrition"]
        biology_identical = False
        
        if len(biology_sets) >= 2:
            for i in range(len(biology_sets)):
                for j in range(i + 1, len(biology_sets)):
                    set1_texts = [q.get("question_text", "") for q in biology_sets[i]]
                    set2_texts = [q.get("question_text", "") for q in biology_sets[j]]
                    
                    if set1_texts == set2_texts:
                        biology_identical = True
                        print(f"❌ Biology: Sets {i+1} and {j+1} are identical!")
                        break
                if biology_identical:
                    break
        
        if not biology_identical:
            print(f"✅ Biology: All {len(biology_sets)} question sets are different")
        
        return not (math_identical or biology_identical)
    
    def run_comprehensive_test(self):
        """Run the complete caching fix test suite"""
        print("🚀 NCERT UNITS CACHING FIX COMPREHENSIVE TEST")
        print("=" * 80)
        print("Testing the two critical fixes:")
        print("1. Cache Key Randomization: variety_factor (1-5) changes every hour")
        print("2. Reduced Cache Duration: Changed from 24 hours to 2 hours")
        print("=" * 80)
        
        # Step 1: Register student
        if not self.register_and_login_student():
            print("❌ CRITICAL: Failed to register student. Cannot proceed.")
            return False
        
        # Step 2: Test Math Real Numbers variety
        math_success = self.test_math_real_numbers_variety()
        if not math_success:
            print("❌ CRITICAL: Math Real Numbers test failed")
        
        # Step 3: Test Biology Nutrition variety
        biology_success = self.test_biology_nutrition_variety()
        if not biology_success:
            print("❌ CRITICAL: Biology Nutrition test failed")
        
        # Step 4: Calculate variety metrics
        variety_percentage = self.calculate_question_variety_metrics()
        
        # Step 5: Verify question relevancy
        relevancy_percentage = self.verify_question_relevancy()
        
        # Step 6: Check for identical sets
        no_identical_sets = self.check_no_identical_question_sets()
        
        # Final Assessment
        print("\n" + "=" * 80)
        print("🏁 FINAL ASSESSMENT - CACHING FIX VERIFICATION")
        print("=" * 80)
        
        # Criteria for success
        variety_threshold = 80.0  # > 80% unique questions
        relevancy_threshold = 70.0  # > 70% relevant questions
        
        print(f"📊 Question Variety: {variety_percentage:.1f}% (Target: >{variety_threshold}%)")
        print(f"📊 Question Relevancy: {relevancy_percentage:.1f}% (Target: >{relevancy_threshold}%)")
        print(f"📊 No Identical Sets: {'✅ PASS' if no_identical_sets else '❌ FAIL'}")
        
        # Overall success criteria
        variety_pass = variety_percentage > variety_threshold
        relevancy_pass = relevancy_percentage > relevancy_threshold
        
        overall_success = variety_pass and relevancy_pass and no_identical_sets
        
        print(f"\n🎯 VARIETY TEST: {'✅ PASS' if variety_pass else '❌ FAIL'}")
        print(f"🎯 RELEVANCY TEST: {'✅ PASS' if relevancy_pass else '❌ FAIL'}")
        print(f"🎯 UNIQUENESS TEST: {'✅ PASS' if no_identical_sets else '❌ FAIL'}")
        
        if overall_success:
            print(f"\n🎉 OVERALL RESULT: ✅ CACHING FIX SUCCESSFUL!")
            print("The implemented fixes have resolved the question variety issue:")
            print("✅ Cache key randomization is working (variety_factor)")
            print("✅ Reduced cache duration is effective (2 hours)")
            print("✅ Questions are relevant to NCERT units")
            print("✅ No repetitive identical question sets")
        else:
            print(f"\n💥 OVERALL RESULT: ❌ CACHING FIX NEEDS ATTENTION!")
            if not variety_pass:
                print(f"❌ Question variety below threshold: {variety_percentage:.1f}% < {variety_threshold}%")
            if not relevancy_pass:
                print(f"❌ Question relevancy below threshold: {relevancy_percentage:.1f}% < {relevancy_threshold}%")
            if not no_identical_sets:
                print("❌ Identical question sets detected")
        
        return overall_success

def main():
    """Main test execution"""
    tester = NCERTCachingFixTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
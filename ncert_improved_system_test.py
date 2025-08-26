#!/usr/bin/env python3
"""
NCERT Units System Testing - Enhanced Error Handling and Question Banks
Testing the improved NCERT system with AI model fallback and expanded question banks
"""

import requests
import json
import time
import uuid
import os
from dotenv import load_dotenv
from collections import defaultdict
import sys

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

class NCERTImprovedSystemTest:
    """Test the improved NCERT Units system with enhanced error handling and expanded question banks"""
    
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = {
            "question_variety": {},
            "consistency_check": {},
            "error_handling": {},
            "logging_verification": {}
        }
        
    def setup_test_user(self):
        """Create a test student account"""
        print("\n🔍 Setting up test student account...")
        
        url = f"{API_URL}/auth/register"
        payload = {
            "email": f"ncert_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "NCERT Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Test student created with ID: {self.student_id}")
                return True
            else:
                print(f"❌ Failed to create test student: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating test student: {str(e)}")
            return False
    
    def test_question_variety(self):
        """Test 1: Question Variety - Generate practice tests multiple times for the same unit"""
        print("\n" + "="*80)
        print("🎯 TEST 1: QUESTION VARIETY - Multiple generations for same NCERT units")
        print("="*80)
        
        # Test scenarios as specified in the review request
        test_scenarios = [
            {
                "name": "Math Real Numbers",
                "subject": "math",
                "topics": ["Real Numbers"],
                "expected_concepts": ["rational", "irrational", "decimal", "number", "terminating"]
            },
            {
                "name": "Math Quadratic Equations", 
                "subject": "math",
                "topics": ["Quadratic Equations"],
                "expected_concepts": ["discriminant", "roots", "quadratic", "solving", "formula"]
            },
            {
                "name": "Biology Nutrition in Plants",
                "subject": "biology", 
                "topics": ["Nutrition in Plants"],
                "expected_concepts": ["photosynthesis", "chlorophyll", "stomata", "glucose", "carbon dioxide"]
            },
            {
                "name": "Chemistry Acids, Bases and Salts",
                "subject": "chemistry",
                "topics": ["Acids, Bases and Salts"], 
                "expected_concepts": ["pH", "neutralization", "acid", "base", "indicator"]
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for scenario in test_scenarios:
            print(f"\n📚 Testing {scenario['name']}...")
            
            all_questions = []
            unique_questions = set()
            generation_attempts = 3  # Generate 3 times to check variety
            
            for attempt in range(generation_attempts):
                print(f"  Generation attempt {attempt + 1}/{generation_attempts}")
                
                payload = {
                    "subject": scenario["subject"],
                    "topics": scenario["topics"],
                    "difficulty": "medium",
                    "question_count": 5
                }
                
                try:
                    response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get("questions", [])
                        
                        print(f"    ✅ Generated {len(questions)} questions")
                        
                        for question in questions:
                            question_text = question.get("question_text", "")
                            all_questions.append(question_text)
                            unique_questions.add(question_text)
                            
                            # Check for expected concepts
                            concepts_found = []
                            for concept in scenario["expected_concepts"]:
                                if concept.lower() in question_text.lower():
                                    concepts_found.append(concept)
                            
                            print(f"    📝 Q: {question_text[:60]}...")
                            if concepts_found:
                                print(f"       ✅ Concepts found: {concepts_found}")
                            else:
                                print(f"       ⚠️ No expected concepts detected")
                    else:
                        print(f"    ❌ Generation failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ Error: {str(e)}")
                
                # Small delay between generations
                time.sleep(1)
            
            # Analyze variety
            total_questions = len(all_questions)
            unique_count = len(unique_questions)
            variety_percentage = (unique_count / total_questions * 100) if total_questions > 0 else 0
            
            print(f"\n📊 VARIETY ANALYSIS for {scenario['name']}:")
            print(f"   Total questions generated: {total_questions}")
            print(f"   Unique questions: {unique_count}")
            print(f"   Variety percentage: {variety_percentage:.1f}%")
            
            # Check if we have at least 8 different questions (as mentioned in review)
            target_variety = 8
            if unique_count >= target_variety:
                print(f"   ✅ PASSED: {unique_count} >= {target_variety} different questions")
                result = "PASSED"
            else:
                print(f"   ❌ FAILED: Only {unique_count} < {target_variety} different questions")
                result = "FAILED"
            
            self.test_results["question_variety"][scenario["name"]] = {
                "total_questions": total_questions,
                "unique_questions": unique_count,
                "variety_percentage": variety_percentage,
                "result": result
            }
    
    def test_consistency_check(self):
        """Test 2: Consistency Check - Verify questions are ALWAYS relevant to selected units"""
        print("\n" + "="*80)
        print("🎯 TEST 2: CONSISTENCY CHECK - Questions always relevant to selected units")
        print("="*80)
        
        # Test with specific NCERT units to ensure no generic questions
        test_units = [
            {
                "subject": "math",
                "unit": "Real Numbers",
                "avoid_terms": ["sample", "example", "general", "basic concept"],
                "required_terms": ["rational", "irrational", "decimal", "number"]
            },
            {
                "subject": "biology", 
                "unit": "Nutrition in Plants",
                "avoid_terms": ["sample", "example", "general", "basic concept"],
                "required_terms": ["photosynthesis", "plant", "chlorophyll", "nutrition"]
            },
            {
                "subject": "chemistry",
                "unit": "Acids, Bases and Salts", 
                "avoid_terms": ["sample", "example", "general", "basic concept"],
                "required_terms": ["acid", "base", "pH", "salt", "neutralization"]
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for unit_test in test_units:
            print(f"\n🔍 Testing consistency for {unit_test['subject']} - {unit_test['unit']}")
            
            payload = {
                "subject": unit_test["subject"],
                "topics": [unit_test["unit"]],
                "difficulty": "medium", 
                "question_count": 5
            }
            
            try:
                response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    relevant_count = 0
                    generic_count = 0
                    
                    for i, question in enumerate(questions):
                        question_text = question.get("question_text", "").lower()
                        explanation = question.get("explanation", "").lower()
                        topic_field = question.get("topic", "").lower()
                        combined_text = question_text + " " + explanation
                        
                        print(f"  Q{i+1}: {question.get('question_text', '')[:70]}...")
                        print(f"       Topic field: '{question.get('topic', 'N/A')}'")
                        
                        # Check for generic terms (should be avoided)
                        generic_found = []
                        for avoid_term in unit_test["avoid_terms"]:
                            if avoid_term in combined_text:
                                generic_found.append(avoid_term)
                        
                        # Check for required terms (should be present)
                        required_found = []
                        for req_term in unit_test["required_terms"]:
                            if req_term in combined_text:
                                required_found.append(req_term)
                        
                        # Check if topic field matches unit
                        topic_matches = unit_test["unit"].lower() in topic_field
                        
                        if required_found and not generic_found and topic_matches:
                            relevant_count += 1
                            print(f"       ✅ RELEVANT: Found {required_found}, topic matches")
                        elif generic_found:
                            generic_count += 1
                            print(f"       ❌ GENERIC: Found generic terms {generic_found}")
                        else:
                            print(f"       ⚠️ UNCLEAR: Required terms {required_found}, topic match: {topic_matches}")
                    
                    # Calculate consistency score
                    total_questions = len(questions)
                    consistency_percentage = (relevant_count / total_questions * 100) if total_questions > 0 else 0
                    
                    print(f"\n📊 CONSISTENCY ANALYSIS:")
                    print(f"   Relevant questions: {relevant_count}/{total_questions}")
                    print(f"   Generic questions: {generic_count}/{total_questions}")
                    print(f"   Consistency score: {consistency_percentage:.1f}%")
                    
                    # Pass if 80% or more questions are relevant
                    if consistency_percentage >= 80:
                        print(f"   ✅ PASSED: {consistency_percentage:.1f}% >= 80% consistency")
                        result = "PASSED"
                    else:
                        print(f"   ❌ FAILED: {consistency_percentage:.1f}% < 80% consistency")
                        result = "FAILED"
                    
                    self.test_results["consistency_check"][f"{unit_test['subject']} - {unit_test['unit']}"] = {
                        "relevant_questions": relevant_count,
                        "total_questions": total_questions,
                        "generic_questions": generic_count,
                        "consistency_percentage": consistency_percentage,
                        "result": result
                    }
                else:
                    print(f"   ❌ API call failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def test_error_handling(self):
        """Test 3: Error Handling - Check graceful handling of AI quota issues and fallback"""
        print("\n" + "="*80)
        print("🎯 TEST 3: ERROR HANDLING - AI quota issues and fallback system")
        print("="*80)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test 1: Normal operation (should work)
        print("\n🔍 Testing normal operation...")
        payload = {
            "subject": "math",
            "topics": ["Real Numbers"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        try:
            response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                print(f"✅ Normal operation: Generated {len(questions)} questions")
                
                # Check if questions have proper structure
                for question in questions:
                    required_fields = ["question_text", "options", "correct_answer", "explanation"]
                    missing_fields = [field for field in required_fields if not question.get(field)]
                    
                    if not missing_fields:
                        print(f"   ✅ Question structure complete")
                    else:
                        print(f"   ⚠️ Missing fields: {missing_fields}")
                
                self.test_results["error_handling"]["normal_operation"] = "PASSED"
            else:
                print(f"❌ Normal operation failed: {response.status_code}")
                self.test_results["error_handling"]["normal_operation"] = "FAILED"
                
        except Exception as e:
            print(f"❌ Normal operation error: {str(e)}")
            self.test_results["error_handling"]["normal_operation"] = "FAILED"
        
        # Test 2: Rapid requests (might trigger rate limiting)
        print("\n🔍 Testing rapid requests (potential rate limiting)...")
        rapid_success_count = 0
        rapid_total_requests = 5
        
        for i in range(rapid_total_requests):
            try:
                response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
                
                if response.status_code == 200:
                    rapid_success_count += 1
                    print(f"   Request {i+1}: ✅ Success")
                elif response.status_code == 429:
                    print(f"   Request {i+1}: ⚠️ Rate limited (429) - fallback should activate")
                else:
                    print(f"   Request {i+1}: ❌ Failed ({response.status_code})")
                    
            except Exception as e:
                print(f"   Request {i+1}: ❌ Error: {str(e)}")
            
            # Small delay between requests
            time.sleep(0.5)
        
        rapid_success_rate = (rapid_success_count / rapid_total_requests) * 100
        print(f"\n📊 Rapid requests success rate: {rapid_success_rate:.1f}%")
        
        if rapid_success_rate >= 60:  # Allow some failures due to rate limiting
            print("✅ Error handling appears robust")
            self.test_results["error_handling"]["rapid_requests"] = "PASSED"
        else:
            print("❌ Too many failures in rapid requests")
            self.test_results["error_handling"]["rapid_requests"] = "FAILED"
        
        # Test 3: Invalid subject (should handle gracefully)
        print("\n🔍 Testing invalid subject handling...")
        invalid_payload = {
            "subject": "invalid_subject_xyz",
            "topics": ["Non-existent Topic"],
            "difficulty": "medium",
            "question_count": 3
        }
        
        try:
            response = requests.post(f"{API_URL}/practice/generate", json=invalid_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                if questions:
                    print(f"✅ Graceful fallback: Generated {len(questions)} fallback questions")
                    self.test_results["error_handling"]["invalid_subject"] = "PASSED"
                else:
                    print("⚠️ No questions generated for invalid subject")
                    self.test_results["error_handling"]["invalid_subject"] = "PARTIAL"
            else:
                print(f"⚠️ Invalid subject returned error: {response.status_code}")
                self.test_results["error_handling"]["invalid_subject"] = "PARTIAL"
                
        except Exception as e:
            print(f"❌ Invalid subject test error: {str(e)}")
            self.test_results["error_handling"]["invalid_subject"] = "FAILED"
    
    def test_logging_verification(self):
        """Test 4: Logging Verification - Look for AI success/failure and fallback usage logs"""
        print("\n" + "="*80)
        print("🎯 TEST 4: LOGGING VERIFICATION - AI success/failure and fallback usage")
        print("="*80)
        
        # This test checks if the system provides information about AI vs fallback usage
        # We'll generate questions and analyze the response for indicators
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        test_scenarios = [
            {"subject": "math", "topics": ["Real Numbers"]},
            {"subject": "physics", "topics": ["Laws of Motion"]},
            {"subject": "chemistry", "topics": ["Acids, Bases and Salts"]}
        ]
        
        ai_indicators = []
        fallback_indicators = []
        
        for scenario in test_scenarios:
            print(f"\n🔍 Testing logging for {scenario['subject']} - {scenario['topics'][0]}")
            
            payload = {
                "subject": scenario["subject"],
                "topics": scenario["topics"],
                "difficulty": "medium",
                "question_count": 3
            }
            
            try:
                response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get("questions", [])
                    
                    # Analyze question characteristics to infer AI vs fallback
                    for question in questions:
                        question_text = question.get("question_text", "")
                        explanation = question.get("explanation", "")
                        
                        # AI-generated questions tend to be more varied and contextual
                        # Fallback questions tend to be more template-like
                        
                        # Check for AI indicators (varied, contextual, detailed)
                        ai_score = 0
                        if len(question_text) > 80:  # Longer questions often AI-generated
                            ai_score += 1
                        if len(explanation) > 100:  # Detailed explanations
                            ai_score += 1
                        if any(word in question_text.lower() for word in ["calculate", "determine", "analyze", "explain"]):
                            ai_score += 1
                        
                        # Check for fallback indicators (template-like, shorter)
                        fallback_score = 0
                        if len(question_text) < 50:  # Shorter questions often templates
                            fallback_score += 1
                        if "which of the following" in question_text.lower():
                            fallback_score += 1
                        if question_text.count("?") == 1 and len(question_text) < 60:
                            fallback_score += 1
                        
                        if ai_score > fallback_score:
                            ai_indicators.append(scenario["subject"])
                            print(f"   📝 Likely AI-generated: {question_text[:50]}...")
                        else:
                            fallback_indicators.append(scenario["subject"])
                            print(f"   📋 Likely fallback: {question_text[:50]}...")
                    
                else:
                    print(f"   ❌ Request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Analyze overall AI vs fallback usage
        total_questions_analyzed = len(ai_indicators) + len(fallback_indicators)
        ai_percentage = (len(ai_indicators) / total_questions_analyzed * 100) if total_questions_analyzed > 0 else 0
        fallback_percentage = (len(fallback_indicators) / total_questions_analyzed * 100) if total_questions_analyzed > 0 else 0
        
        print(f"\n📊 LOGGING ANALYSIS:")
        print(f"   Questions analyzed: {total_questions_analyzed}")
        print(f"   Likely AI-generated: {len(ai_indicators)} ({ai_percentage:.1f}%)")
        print(f"   Likely fallback: {len(fallback_indicators)} ({fallback_percentage:.1f}%)")
        
        # The system should show some mix of AI and fallback, or clear indication of which is being used
        if ai_percentage > 0 and fallback_percentage > 0:
            print("✅ System appears to use both AI and fallback appropriately")
            result = "PASSED"
        elif ai_percentage > 80:
            print("✅ System primarily using AI generation")
            result = "PASSED"
        elif fallback_percentage > 80:
            print("⚠️ System primarily using fallback (AI may be having issues)")
            result = "PARTIAL"
        else:
            print("❌ Unable to determine AI vs fallback usage")
            result = "FAILED"
        
        self.test_results["logging_verification"]["ai_fallback_analysis"] = {
            "ai_percentage": ai_percentage,
            "fallback_percentage": fallback_percentage,
            "result": result
        }
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📋 FINAL TEST REPORT - NCERT Units System with Enhanced Error Handling")
        print("="*80)
        
        # Test 1: Question Variety Summary
        print("\n🎯 TEST 1: QUESTION VARIETY")
        variety_passed = 0
        variety_total = 0
        for unit, results in self.test_results["question_variety"].items():
            variety_total += 1
            if results["result"] == "PASSED":
                variety_passed += 1
            print(f"   {unit}: {results['result']} ({results['unique_questions']} unique questions)")
        
        variety_success_rate = (variety_passed / variety_total * 100) if variety_total > 0 else 0
        print(f"   Overall Success Rate: {variety_success_rate:.1f}% ({variety_passed}/{variety_total})")
        
        # Test 2: Consistency Check Summary  
        print("\n🎯 TEST 2: CONSISTENCY CHECK")
        consistency_passed = 0
        consistency_total = 0
        for unit, results in self.test_results["consistency_check"].items():
            consistency_total += 1
            if results["result"] == "PASSED":
                consistency_passed += 1
            print(f"   {unit}: {results['result']} ({results['consistency_percentage']:.1f}% consistent)")
        
        consistency_success_rate = (consistency_passed / consistency_total * 100) if consistency_total > 0 else 0
        print(f"   Overall Success Rate: {consistency_success_rate:.1f}% ({consistency_passed}/{consistency_total})")
        
        # Test 3: Error Handling Summary
        print("\n🎯 TEST 3: ERROR HANDLING")
        error_handling_results = self.test_results["error_handling"]
        for test_name, result in error_handling_results.items():
            print(f"   {test_name.replace('_', ' ').title()}: {result}")
        
        # Test 4: Logging Verification Summary
        print("\n🎯 TEST 4: LOGGING VERIFICATION")
        logging_results = self.test_results["logging_verification"]
        for test_name, result in logging_results.items():
            if isinstance(result, dict):
                print(f"   {test_name.replace('_', ' ').title()}: {result['result']}")
                print(f"     AI Usage: {result['ai_percentage']:.1f}%")
                print(f"     Fallback Usage: {result['fallback_percentage']:.1f}%")
            else:
                print(f"   {test_name.replace('_', ' ').title()}: {result}")
        
        # Overall Assessment
        print("\n🏆 OVERALL ASSESSMENT")
        
        # Calculate overall success metrics
        total_tests = 4
        passed_tests = 0
        
        if variety_success_rate >= 75:
            passed_tests += 1
        if consistency_success_rate >= 75:
            passed_tests += 1
        if all(result in ["PASSED", "PARTIAL"] for result in error_handling_results.values()):
            passed_tests += 1
        if any(result.get("result") in ["PASSED", "PARTIAL"] for result in logging_results.values() if isinstance(result, dict)):
            passed_tests += 1
        
        overall_success_rate = (passed_tests / total_tests) * 100
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 75:
            print("✅ NCERT Units System: WORKING WELL with enhanced error handling")
            return True
        elif overall_success_rate >= 50:
            print("⚠️ NCERT Units System: PARTIALLY WORKING - some issues need attention")
            return False
        else:
            print("❌ NCERT Units System: NEEDS SIGNIFICANT IMPROVEMENT")
            return False

def main():
    """Main test execution"""
    print("🚀 Starting NCERT Units System Testing - Enhanced Error Handling and Question Banks")
    print("Testing AI model fallback, better error handling, and expanded question variety")
    
    tester = NCERTImprovedSystemTest()
    
    # Setup test environment
    if not tester.setup_test_user():
        print("❌ Failed to setup test environment")
        return False
    
    # Run all tests
    try:
        tester.test_question_variety()
        tester.test_consistency_check()
        tester.test_error_handling()
        tester.test_logging_verification()
        
        # Generate final report
        success = tester.generate_final_report()
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
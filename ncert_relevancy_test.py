#!/usr/bin/env python3
"""
EXTENSIVE NCERT Units Relevancy Testing
Tests the inconsistency issue where AI is still generating unrelated questions sometimes.
Conducts multiple test runs for each NCERT unit to check for consistency.
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv
import time
import re
from collections import defaultdict

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 EXTENSIVE NCERT UNITS RELEVANCY TESTING")
print(f"Testing Backend API at: {API_URL}")
print("="*80)

class NCERTRelevancyTester:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.test_results = []
        self.relevancy_issues = []
        self.pattern_analysis = defaultdict(list)

    def setup_student_account(self):
        """Setup student account for testing"""
        print("\n🔧 SETTING UP TEST ACCOUNT...")
        
        student_payload = {
            "email": f"ncert_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "NCERT Test Student",
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

    def analyze_question_relevancy(self, question, expected_unit, subject):
        """Analyze if a question is relevant to the expected NCERT unit"""
        question_text = question.get("question_text", "").lower()
        explanation = question.get("explanation", "").lower()
        topic = question.get("topic", "").lower()
        
        # Define unit-specific keywords for each NCERT unit
        unit_keywords = {
            "real numbers": [
                "rational", "irrational", "decimal", "terminating", "non-terminating", 
                "repeating", "number line", "integers", "whole numbers", "natural numbers",
                "fraction", "p/q", "surd", "√", "square root"
            ],
            "quadratic equations": [
                "quadratic", "discriminant", "roots", "factoring", "completing square",
                "quadratic formula", "parabola", "x²", "ax²+bx+c", "vertex", "axis of symmetry"
            ],
            "nutrition in plants": [
                "photosynthesis", "chlorophyll", "stomata", "autotrophic", "glucose", 
                "carbon dioxide", "oxygen", "sunlight", "leaves", "green plants",
                "heterotrophic", "parasitic", "saprophytic", "symbiotic"
            ],
            "acids, bases and salts": [
                "acid", "base", "salt", "ph", "indicator", "litmus", "neutralization",
                "hydrochloric", "sulfuric", "sodium hydroxide", "alkaline", "acidic"
            ],
            "laws of motion": [
                "newton", "force", "acceleration", "inertia", "momentum", "motion",
                "velocity", "f=ma", "action", "reaction", "friction", "gravity"
            ],
            "polynomials": [
                "polynomial", "degree", "coefficient", "monomial", "binomial", "trinomial",
                "factorization", "zeros", "remainder theorem", "factor theorem"
            ],
            "triangles": [
                "triangle", "congruent", "similar", "pythagoras", "hypotenuse", "isosceles",
                "equilateral", "scalene", "angle", "side", "sss", "sas", "asa", "rhs"
            ],
            "coordinate geometry": [
                "coordinate", "cartesian", "x-axis", "y-axis", "origin", "quadrant",
                "distance formula", "section formula", "midpoint", "slope"
            ],
            "introduction to trigonometry": [
                "trigonometry", "sine", "cosine", "tangent", "sin", "cos", "tan",
                "angle", "opposite", "adjacent", "hypotenuse", "30°", "45°", "60°"
            ],
            "the fundamental unit of life": [
                "cell", "nucleus", "cytoplasm", "cell membrane", "cell wall", "organelles",
                "prokaryotic", "eukaryotic", "mitochondria", "chloroplast", "vacuole"
            ],
            "tissues": [
                "tissue", "epithelial", "connective", "muscular", "nervous", "meristematic",
                "permanent", "parenchyma", "collenchyma", "sclerenchyma", "xylem", "phloem"
            ]
        }
        
        # Get expected keywords for this unit
        expected_keywords = unit_keywords.get(expected_unit.lower(), [])
        
        # Check if question contains unit-specific keywords
        found_keywords = []
        for keyword in expected_keywords:
            if keyword in question_text or keyword in explanation or keyword in topic:
                found_keywords.append(keyword)
        
        # Calculate relevancy score
        relevancy_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
        
        # Check for generic/unrelated content
        generic_indicators = [
            "main concept", "sample", "example", "general", "basic", "simple",
            "what is the", "which of the following", "choose the correct"
        ]
        
        has_generic_content = any(indicator in question_text for indicator in generic_indicators)
        
        # Determine if question is relevant
        is_relevant = (
            relevancy_score > 0.1 or  # Has some unit-specific keywords
            expected_unit.lower() in question_text or
            expected_unit.lower() in explanation or
            expected_unit.lower() in topic
        ) and not (has_generic_content and relevancy_score == 0)
        
        return {
            "is_relevant": is_relevant,
            "relevancy_score": relevancy_score,
            "found_keywords": found_keywords,
            "expected_keywords": expected_keywords,
            "has_generic_content": has_generic_content,
            "analysis": {
                "question_mentions_unit": expected_unit.lower() in question_text,
                "explanation_mentions_unit": expected_unit.lower() in explanation,
                "topic_matches_unit": expected_unit.lower() in topic,
                "keyword_coverage": f"{len(found_keywords)}/{len(expected_keywords)}"
            }
        }

    def test_ncert_unit_multiple_times(self, subject, unit_name, test_count=5):
        """Test a specific NCERT unit multiple times to check consistency"""
        print(f"\n🔍 TESTING {subject.upper()} - '{unit_name}' ({test_count} attempts)")
        
        if not self.student_token:
            print("❌ No student token available")
            return []
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        unit_results = []
        
        for attempt in range(1, test_count + 1):
            print(f"   Attempt {attempt}/{test_count}...")
            
            # Generate practice test
            gen_payload = {
                "subject": subject,
                "topics": [unit_name],
                "difficulty": "medium",
                "question_count": 3
            }
            
            try:
                response = requests.post(f"{API_URL}/practice/generate", json=gen_payload, headers=headers)
                
                if response.status_code != 200:
                    print(f"   ❌ Generation failed: {response.status_code}")
                    continue
                
                data = response.json()
                questions = data.get("questions", [])
                
                if not questions:
                    print(f"   ❌ No questions generated")
                    continue
                
                # Analyze each question for relevancy
                attempt_results = {
                    "attempt": attempt,
                    "subject": subject,
                    "unit": unit_name,
                    "questions_analyzed": len(questions),
                    "relevant_questions": 0,
                    "irrelevant_questions": 0,
                    "question_details": []
                }
                
                for i, question in enumerate(questions):
                    relevancy_analysis = self.analyze_question_relevancy(question, unit_name, subject)
                    
                    question_detail = {
                        "question_number": i + 1,
                        "question_text": question.get("question_text", "")[:100] + "...",
                        "topic": question.get("topic", ""),
                        "is_relevant": relevancy_analysis["is_relevant"],
                        "relevancy_score": relevancy_analysis["relevancy_score"],
                        "found_keywords": relevancy_analysis["found_keywords"],
                        "analysis": relevancy_analysis["analysis"]
                    }
                    
                    attempt_results["question_details"].append(question_detail)
                    
                    if relevancy_analysis["is_relevant"]:
                        attempt_results["relevant_questions"] += 1
                        print(f"   ✅ Q{i+1}: RELEVANT (Score: {relevancy_analysis['relevancy_score']:.2f})")
                        print(f"      Keywords: {', '.join(relevancy_analysis['found_keywords'][:3])}")
                    else:
                        attempt_results["irrelevant_questions"] += 1
                        print(f"   ❌ Q{i+1}: IRRELEVANT (Score: {relevancy_analysis['relevancy_score']:.2f})")
                        print(f"      Question: {question.get('question_text', '')[:80]}...")
                        
                        # Record this as a relevancy issue
                        self.relevancy_issues.append({
                            "subject": subject,
                            "unit": unit_name,
                            "attempt": attempt,
                            "question": question.get("question_text", ""),
                            "topic": question.get("topic", ""),
                            "explanation": question.get("explanation", ""),
                            "analysis": relevancy_analysis
                        })
                
                # Calculate relevancy percentage for this attempt
                relevancy_percentage = (attempt_results["relevant_questions"] / len(questions)) * 100
                attempt_results["relevancy_percentage"] = relevancy_percentage
                
                print(f"   📊 Attempt {attempt} Relevancy: {relevancy_percentage:.1f}% ({attempt_results['relevant_questions']}/{len(questions)})")
                
                unit_results.append(attempt_results)
                
                # Small delay between attempts
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error in attempt {attempt}: {str(e)}")
                continue
        
        return unit_results

    def run_comprehensive_relevancy_test(self):
        """Run comprehensive relevancy testing across multiple NCERT units"""
        print("🚀 STARTING COMPREHENSIVE NCERT RELEVANCY TESTING")
        
        # Setup account
        if not self.setup_student_account():
            print("❌ Failed to setup account - cannot proceed")
            return False
        
        # Define NCERT units to test (as mentioned in the review request)
        test_units = [
            {"subject": "math", "unit": "Real Numbers"},
            {"subject": "math", "unit": "Quadratic Equations"},
            {"subject": "biology", "unit": "Nutrition in Plants"},
            {"subject": "chemistry", "unit": "Acids, Bases and Salts"},
            {"subject": "physics", "unit": "Laws of Motion"},
            # Additional units for comprehensive testing
            {"subject": "math", "unit": "Polynomials"},
            {"subject": "math", "unit": "Triangles"},
            {"subject": "math", "unit": "Coordinate Geometry"},
            {"subject": "biology", "unit": "The Fundamental Unit of Life"},
            {"subject": "biology", "unit": "Tissues"}
        ]
        
        all_results = []
        
        # Test each unit multiple times
        for unit_info in test_units:
            unit_results = self.test_ncert_unit_multiple_times(
                unit_info["subject"], 
                unit_info["unit"], 
                test_count=5  # Test each unit 5 times as requested
            )
            all_results.extend(unit_results)
        
        # Analyze patterns and generate report
        self.analyze_patterns_and_generate_report(all_results)
        
        return True

    def analyze_patterns_and_generate_report(self, all_results):
        """Analyze patterns in relevancy issues and generate comprehensive report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE NCERT RELEVANCY ANALYSIS REPORT")
        print("="*80)
        
        # Overall statistics
        total_attempts = len(all_results)
        total_questions = sum(result["questions_analyzed"] for result in all_results)
        total_relevant = sum(result["relevant_questions"] for result in all_results)
        total_irrelevant = sum(result["irrelevant_questions"] for result in all_results)
        
        overall_relevancy = (total_relevant / total_questions) * 100 if total_questions > 0 else 0
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   • Total Test Attempts: {total_attempts}")
        print(f"   • Total Questions Generated: {total_questions}")
        print(f"   • Relevant Questions: {total_relevant} ({(total_relevant/total_questions)*100:.1f}%)")
        print(f"   • Irrelevant Questions: {total_irrelevant} ({(total_irrelevant/total_questions)*100:.1f}%)")
        print(f"   • Overall Relevancy Score: {overall_relevancy:.1f}%")
        
        # Subject-wise analysis
        print(f"\n📚 SUBJECT-WISE ANALYSIS:")
        subject_stats = defaultdict(lambda: {"attempts": 0, "questions": 0, "relevant": 0, "irrelevant": 0})
        
        for result in all_results:
            subject = result["subject"]
            subject_stats[subject]["attempts"] += 1
            subject_stats[subject]["questions"] += result["questions_analyzed"]
            subject_stats[subject]["relevant"] += result["relevant_questions"]
            subject_stats[subject]["irrelevant"] += result["irrelevant_questions"]
        
        for subject, stats in subject_stats.items():
            relevancy = (stats["relevant"] / stats["questions"]) * 100 if stats["questions"] > 0 else 0
            print(f"   • {subject.upper()}: {relevancy:.1f}% relevancy ({stats['relevant']}/{stats['questions']} questions)")
        
        # Unit-wise consistency analysis
        print(f"\n🎯 UNIT-WISE CONSISTENCY ANALYSIS:")
        unit_stats = defaultdict(lambda: {"attempts": [], "avg_relevancy": 0, "consistency": "Unknown"})
        
        for result in all_results:
            unit_key = f"{result['subject']} - {result['unit']}"
            unit_stats[unit_key]["attempts"].append(result["relevancy_percentage"])
        
        for unit, stats in unit_stats.items():
            attempts = stats["attempts"]
            if attempts:
                avg_relevancy = sum(attempts) / len(attempts)
                std_dev = (sum((x - avg_relevancy) ** 2 for x in attempts) / len(attempts)) ** 0.5
                
                # Determine consistency
                if std_dev < 10:
                    consistency = "HIGHLY CONSISTENT"
                elif std_dev < 20:
                    consistency = "MODERATELY CONSISTENT"
                else:
                    consistency = "INCONSISTENT ⚠️"
                
                print(f"   • {unit}:")
                print(f"     - Average Relevancy: {avg_relevancy:.1f}%")
                print(f"     - Consistency: {consistency} (σ={std_dev:.1f})")
                print(f"     - Attempts: {attempts}")
        
        # Identify problematic patterns
        print(f"\n🚨 PROBLEMATIC PATTERNS IDENTIFIED:")
        
        if self.relevancy_issues:
            print(f"   • Total Irrelevant Questions Found: {len(self.relevancy_issues)}")
            
            # Group by subject
            subject_issues = defaultdict(list)
            for issue in self.relevancy_issues:
                subject_issues[issue["subject"]].append(issue)
            
            for subject, issues in subject_issues.items():
                print(f"\n   📋 {subject.upper()} Issues ({len(issues)} questions):")
                
                # Show examples of irrelevant questions
                for i, issue in enumerate(issues[:3]):  # Show first 3 examples
                    print(f"      {i+1}. Unit: {issue['unit']}")
                    print(f"         Question: {issue['question'][:100]}...")
                    print(f"         Topic Field: '{issue['topic']}'")
                    print(f"         Relevancy Score: {issue['analysis']['relevancy_score']:.2f}")
                
                if len(issues) > 3:
                    print(f"      ... and {len(issues) - 3} more issues")
        else:
            print("   ✅ No irrelevant questions found - all questions are unit-specific!")
        
        # Cache vs AI generation analysis
        print(f"\n🤖 AI vs FALLBACK SYSTEM ANALYSIS:")
        print("   Analyzing question sources to determine if issues come from:")
        print("   • AI generation (Gemini API) returning generic content")
        print("   • Fallback system returning wrong questions")
        print("   • Parsing/formatting issues")
        
        # Look for patterns in irrelevant questions
        if self.relevancy_issues:
            generic_patterns = []
            for issue in self.relevancy_issues:
                question = issue["question"].lower()
                if any(pattern in question for pattern in ["what is the main", "choose the correct", "which of the following"]):
                    generic_patterns.append(issue)
            
            if generic_patterns:
                print(f"   ⚠️ Found {len(generic_patterns)} questions with generic patterns")
                print("   This suggests fallback system may be serving generic questions")
            else:
                print("   ✅ No obvious generic patterns found")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if overall_relevancy < 90:
            print("   🔧 IMMEDIATE ACTIONS NEEDED:")
            print("   1. Review AI prompt engineering for unit-specific generation")
            print("   2. Improve fallback question banks with unit-specific content")
            print("   3. Add better validation for question relevancy before serving")
            print("   4. Consider caching only verified unit-specific questions")
        else:
            print("   ✅ GOOD PERFORMANCE:")
            print("   1. Continue monitoring for consistency")
            print("   2. Consider expanding to more NCERT units")
            print("   3. Fine-tune edge cases where relevancy drops")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if overall_relevancy >= 95:
            print("   ✅ EXCELLENT: NCERT units relevancy is working very well")
        elif overall_relevancy >= 85:
            print("   ✅ GOOD: NCERT units relevancy is mostly working, minor improvements needed")
        elif overall_relevancy >= 70:
            print("   ⚠️ MODERATE: NCERT units relevancy needs improvement")
        else:
            print("   ❌ POOR: NCERT units relevancy has significant issues requiring immediate attention")
        
        print(f"\n📝 DETAILED FINDINGS FOR MAIN AGENT:")
        print("   • Questions are being generated but some lack unit-specific content")
        print("   • Need to strengthen AI prompts to ensure unit relevancy")
        print("   • Consider implementing relevancy validation before serving questions")
        print("   • Monitor for consistency across different subjects and units")

if __name__ == "__main__":
    tester = NCERTRelevancyTester()
    success = tester.run_comprehensive_relevancy_test()
    exit(0 if success else 1)
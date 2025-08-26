#!/usr/bin/env python3
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

def register_test_student():
    """Register a test student for comprehensive NCERT testing"""
    url = f"{API_URL}/auth/register"
    payload = {
        "email": f"ncert_comprehensive_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "NCERT Comprehensive Test Student",
        "user_type": "student",
        "grade_level": "11th"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None

def test_comprehensive_ncert_scenarios(token):
    """Test comprehensive NCERT scenarios including edge cases"""
    
    if not token:
        print("❌ No authentication token available")
        return False
    
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Comprehensive NCERT test scenarios
    test_scenarios = [
        {
            "name": "Math 9th Grade - Multiple Units",
            "subject": "math",
            "topics": ["Polynomials", "Linear Equations in Two Variables", "Triangles"],
            "difficulty": "easy",
            "question_count": 3
        },
        {
            "name": "Physics 12th Grade - Advanced Units",
            "subject": "physics", 
            "topics": ["Electromagnetic Induction", "Alternating Current", "Wave Optics"],
            "difficulty": "hard",
            "question_count": 2
        },
        {
            "name": "Chemistry 11th Grade - Organic Chemistry",
            "subject": "chemistry",
            "topics": ["Organic Chemistry - Some Basic Principles", "Hydrocarbons"],
            "difficulty": "medium",
            "question_count": 2
        },
        {
            "name": "Biology 12th Grade - Genetics & Evolution",
            "subject": "biology",
            "topics": ["Principles of Inheritance and Variation", "Molecular Basis of Inheritance", "Evolution"],
            "difficulty": "hard",
            "question_count": 3
        },
        {
            "name": "English 11th Grade - Prose & Poetry",
            "subject": "english",
            "topics": ["The Portrait of a Lady", "We're Not Afraid to Die... if We Can All Be Together", "Father to Son"],
            "difficulty": "medium",
            "question_count": 2
        },
        {
            "name": "Mixed Difficulty Test - Math 10th",
            "subject": "math",
            "topics": ["Real Numbers", "Coordinate Geometry"],
            "difficulty": "mixed",
            "question_count": 4
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_scenarios)
    detailed_results = []
    
    print(f"\n🧪 Running {total_tests} Comprehensive NCERT Tests...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}/{total_tests}: {scenario['name']} ---")
        print(f"Topics: {', '.join(scenario['topics'])}")
        print(f"Difficulty: {scenario['difficulty']}")
        print(f"Question Count: {scenario['question_count']}")
        
        payload = {
            "subject": scenario["subject"],
            "topics": scenario["topics"],
            "difficulty": scenario["difficulty"],
            "question_count": scenario["question_count"]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                test_id = data.get("test_id", "N/A")
                
                if len(questions) > 0:
                    print(f"✅ Generated {len(questions)} questions (Test ID: {test_id})")
                    
                    # Analyze question quality in detail
                    quality_score = 0
                    max_quality_score = len(questions) * 4  # 4 points per question
                    
                    for j, question in enumerate(questions):
                        question_text = question.get("question_text", "")
                        explanation = question.get("explanation", "")
                        options = question.get("options", [])
                        correct_answer = question.get("correct_answer", "")
                        
                        print(f"   Q{j+1}: {question_text[:120]}...")
                        
                        # Quality checks
                        if len(question_text) > 30:
                            quality_score += 1
                            print(f"   ✓ Substantial content")
                        
                        if len(options) >= 4:
                            quality_score += 1
                            print(f"   ✓ Multiple choice options ({len(options)})")
                        
                        if correct_answer and correct_answer in options:
                            quality_score += 1
                            print(f"   ✓ Valid correct answer")
                        
                        if len(explanation) > 20:
                            quality_score += 1
                            print(f"   ✓ Detailed explanation")
                    
                    quality_percentage = (quality_score / max_quality_score) * 100
                    print(f"   📊 Quality Score: {quality_percentage:.1f}% ({quality_score}/{max_quality_score})")
                    
                    if quality_percentage >= 75:
                        successful_tests += 1
                        result_status = "PASSED"
                        print(f"✅ {scenario['name']}: {result_status}")
                    else:
                        result_status = "PARTIAL"
                        print(f"⚠️ {scenario['name']}: {result_status} - Quality below threshold")
                    
                    detailed_results.append({
                        "name": scenario['name'],
                        "status": result_status,
                        "questions_generated": len(questions),
                        "quality_score": quality_percentage,
                        "test_id": test_id
                    })
                else:
                    print(f"❌ {scenario['name']}: No questions generated")
                    detailed_results.append({
                        "name": scenario['name'],
                        "status": "FAILED",
                        "questions_generated": 0,
                        "quality_score": 0,
                        "test_id": "N/A"
                    })
            else:
                print(f"❌ {scenario['name']}: API call failed - {response.status_code}")
                if response.text:
                    error_text = response.text[:200]
                    print(f"   Error: {error_text}")
                detailed_results.append({
                    "name": scenario['name'],
                    "status": "FAILED",
                    "questions_generated": 0,
                    "quality_score": 0,
                    "error": f"HTTP {response.status_code}"
                })
                    
        except Exception as e:
            print(f"❌ {scenario['name']}: Exception - {str(e)}")
            detailed_results.append({
                "name": scenario['name'],
                "status": "ERROR",
                "questions_generated": 0,
                "quality_score": 0,
                "error": str(e)
            })
    
    # Calculate comprehensive results
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n📊 Comprehensive NCERT Units Integration Results:")
    print(f"   Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    print(f"   Successful Tests: {successful_tests}")
    print(f"   Failed/Partial Tests: {total_tests - successful_tests}")
    
    print(f"\n📋 Detailed Results:")
    for result in detailed_results:
        status_emoji = "✅" if result["status"] == "PASSED" else "⚠️" if result["status"] == "PARTIAL" else "❌"
        print(f"   {status_emoji} {result['name']}: {result['status']} "
              f"({result['questions_generated']} questions, {result['quality_score']:.1f}% quality)")
    
    # Test submission workflow with one of the generated tests
    if detailed_results and detailed_results[0]["status"] == "PASSED":
        print(f"\n🔄 Testing submission workflow with first test...")
        test_submission_workflow(token, detailed_results[0]["test_id"])
    
    if success_rate >= 80:
        print("\n🎉 Comprehensive NCERT Units Integration: EXCELLENT")
        return True
    elif success_rate >= 60:
        print("\n✅ Comprehensive NCERT Units Integration: GOOD")
        return True
    else:
        print("\n❌ Comprehensive NCERT Units Integration: NEEDS IMPROVEMENT")
        return False

def test_submission_workflow(token, test_id):
    """Test the complete submission workflow for NCERT generated tests"""
    
    if not test_id or test_id == "N/A":
        print("❌ No valid test ID for submission testing")
        return
    
    print(f"Testing submission workflow for test ID: {test_id}")
    
    # First, get the test details to understand the questions
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generate a simple test for submission
    payload = {
        "subject": "math",
        "topics": ["Real Numbers"],
        "difficulty": "easy",
        "question_count": 2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            new_test_id = data.get("test_id")
            
            if questions and new_test_id:
                # Create submission payload
                student_answers = {}
                question_ids = []
                
                for question in questions:
                    question_id = question.get("id")
                    correct_answer = question.get("correct_answer")
                    if question_id and correct_answer:
                        question_ids.append(question_id)
                        student_answers[question_id] = correct_answer  # Use correct answer for testing
                
                # Submit the test
                submit_url = f"{API_URL}/practice/submit"
                submit_payload = {
                    "test_id": new_test_id,
                    "questions": question_ids,
                    "student_answers": student_answers,
                    "time_taken": 300  # 5 minutes
                }
                
                submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                print(f"Submission Response: {submit_response.status_code}")
                
                if submit_response.status_code == 200:
                    submit_data = submit_response.json()
                    score = submit_data.get("score", 0)
                    print(f"✅ Submission successful! Score: {score}%")
                    print(f"   XP Earned: {submit_data.get('xp_earned', 0)}")
                    print(f"   Correct Answers: {submit_data.get('correct_answers', 0)}/{submit_data.get('total_questions', 0)}")
                else:
                    print(f"❌ Submission failed: {submit_response.status_code}")
            else:
                print("❌ No questions available for submission test")
        else:
            print(f"❌ Failed to generate test for submission: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Submission workflow error: {str(e)}")

def main():
    print("🚀 Comprehensive NCERT Units Integration Testing")
    print("=" * 60)
    
    # Register test student
    print("🔐 Registering test student...")
    token = register_test_student()
    
    if token:
        print("✅ Student registered successfully")
        
        # Test comprehensive NCERT scenarios
        success = test_comprehensive_ncert_scenarios(token)
        
        if success:
            print("\n🎉 Comprehensive NCERT Units Integration Testing: PASSED")
        else:
            print("\n❌ Comprehensive NCERT Units Integration Testing: FAILED")
    else:
        print("❌ Failed to register test student")

if __name__ == "__main__":
    main()
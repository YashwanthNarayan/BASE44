#!/usr/bin/env python3
"""
Focused NCERT Extended Grades Test
Testing specific scenarios for 6th, 7th, and 8th grade NCERT units
"""
import requests
import json
import uuid

API_URL = "https://ncert-study-hub.preview.emergentagent.com/api"

def register_test_student():
    """Register a test student"""
    print("🔍 Registering test student...")
    url = f"{API_URL}/auth/register"
    payload = {
        "email": f"focused_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Test Student",
        "user_type": "student",
        "grade_level": "8th"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            student_id = data.get("user", {}).get("id")
            print(f"✅ Registered student with ID: {student_id}")
            return token, student_id
        else:
            print(f"❌ Failed to register student: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error registering student: {str(e)}")
        return None, None

def test_practice_generation(token, subject, topics, grade, difficulty="easy"):
    """Test practice test generation for specific NCERT units"""
    print(f"\n🔍 Testing {subject.title()} {grade} Grade: {', '.join(topics[:2])}...")
    
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "subject": subject,
        "topics": topics,
        "difficulty": difficulty,
        "question_count": 2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            
            if len(questions) > 0:
                print(f"   ✅ Generated {len(questions)} questions")
                
                # Show sample question
                first_question = questions[0]
                question_text = first_question.get("question_text", "")
                print(f"   📝 Sample Question: {question_text[:80]}...")
                
                # Check if it has proper structure
                has_options = "options" in first_question
                has_correct_answer = "correct_answer" in first_question
                has_explanation = "explanation" in first_question
                
                print(f"   ✓ Has options: {has_options}")
                print(f"   ✓ Has correct answer: {has_correct_answer}")
                print(f"   ✓ Has explanation: {has_explanation}")
                
                return True
            else:
                print("   ❌ No questions generated")
                return False
        else:
            print(f"   ❌ API call failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    print("🚀 Starting Focused NCERT Extended Grades Test...")
    
    # Register student
    token, student_id = register_test_student()
    if not token:
        print("❌ Cannot continue without student token")
        return False
    
    # Test scenarios for extended grades (6th, 7th, 8th)
    test_scenarios = [
        # 6th Grade Tests
        ("math", ["Knowing Our Numbers", "Whole Numbers"], "6th", "easy"),
        ("biology", ["Getting to Know Plants", "Body Movements"], "6th", "easy"),
        
        # 7th Grade Tests  
        ("math", ["Integers", "Simple Equations"], "7th", "easy"),
        ("biology", ["Nutrition in Plants", "Respiration in Organisms"], "7th", "easy"),
        
        # 8th Grade Tests
        ("math", ["Rational Numbers", "Linear Equations in One Variable"], "8th", "medium"),
        ("physics", ["Force and Pressure", "Friction"], "8th", "medium"),
        ("chemistry", ["Materials: Metals and Non-Metals", "Combustion and Flame"], "8th", "medium"),
    ]
    
    successful_tests = 0
    total_tests = len(test_scenarios)
    
    for subject, topics, grade, difficulty in test_scenarios:
        success = test_practice_generation(token, subject, topics, grade, difficulty)
        if success:
            successful_tests += 1
    
    # Results
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n📊 Test Results:")
    print(f"   Successful tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ EXCELLENT: NCERT Extended Grades Integration working well!")
        return True
    elif success_rate >= 60:
        print("✅ GOOD: NCERT Extended Grades Integration working with minor issues")
        return True
    else:
        print("⚠️ NEEDS IMPROVEMENT: NCERT Extended Grades Integration has issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
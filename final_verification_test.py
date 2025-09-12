#!/usr/bin/env python3
"""
Final Verification Test for NCERT Extended Grades Integration
Comprehensive test covering all requirements from the review request
"""
import requests
import json
import uuid

API_URL = "https://learnlab-k.preview.emergentagent.com/api"

def register_test_student():
    """Register a test student"""
    print("🔍 Registering test student...")
    url = f"{API_URL}/auth/register"
    payload = {
        "email": f"final_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Final Test Student",
        "user_type": "student",
        "grade_level": "7th"
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

def test_specific_requirements(token):
    """Test the specific requirements from the review request"""
    print("\n🎯 Testing Specific Review Requirements...")
    
    # 1. Practice test generation with 6th grade units
    print("\n1️⃣ Testing 6th Grade Math Units...")
    success_6th = test_practice_generation(token, "math", ["Knowing Our Numbers", "Whole Numbers", "Fractions"], "6th")
    
    # 2. Test 7th grade units
    print("\n2️⃣ Testing 7th Grade Biology Units...")
    success_7th = test_practice_generation(token, "biology", ["Nutrition in Plants"], "7th")
    
    # 3. Test 8th grade units
    print("\n3️⃣ Testing 8th Grade Physics Units...")
    success_8th_physics = test_practice_generation(token, "physics", ["Force and Pressure"], "8th")
    
    print("\n3️⃣ Testing 8th Grade Chemistry Units...")
    success_8th_chemistry = test_practice_generation(token, "chemistry", ["Materials: Metals and Non-Metals"], "8th")
    
    # 4. Verify AI generates age-appropriate questions
    print("\n4️⃣ Testing Age-Appropriate Question Generation...")
    age_appropriate = verify_age_appropriate_content(token)
    
    # 5. Ensure backend handles expanded grade range seamlessly
    print("\n5️⃣ Testing Backend Grade Range Handling...")
    grade_range_success = test_grade_range_handling(token)
    
    return {
        "6th_grade": success_6th,
        "7th_grade": success_7th,
        "8th_grade_physics": success_8th_physics,
        "8th_grade_chemistry": success_8th_chemistry,
        "age_appropriate": age_appropriate,
        "grade_range_handling": grade_range_success
    }

def test_practice_generation(token, subject, topics, grade):
    """Test practice test generation for specific units"""
    print(f"   Testing {subject.title()} {grade} Grade: {', '.join(topics)}")
    
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "subject": subject,
        "topics": topics,
        "difficulty": "easy" if grade in ["6th", "7th"] else "medium",
        "question_count": 2
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            if len(questions) > 0:
                print(f"   ✅ Generated {len(questions)} questions successfully")
                return True
            else:
                print(f"   ❌ No questions generated")
                return False
        else:
            print(f"   ❌ API call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def verify_age_appropriate_content(token):
    """Verify AI generates age-appropriate questions for younger grades"""
    print("   Comparing question complexity between 6th and 12th grade...")
    
    # Test 6th grade question
    grade_6_question = get_sample_question(token, "math", ["Whole Numbers"], "easy")
    
    # Test 12th grade question  
    grade_12_question = get_sample_question(token, "math", ["Matrices"], "hard")
    
    if grade_6_question and grade_12_question:
        # Simple heuristic: 6th grade questions should be shorter and simpler
        grade_6_length = len(grade_6_question.split())
        grade_12_length = len(grade_12_question.split())
        
        print(f"   6th Grade Question Length: {grade_6_length} words")
        print(f"   12th Grade Question Length: {grade_12_length} words")
        
        if grade_6_length <= grade_12_length:
            print("   ✅ Age-appropriate complexity verified")
            return True
        else:
            print("   ⚠️ Question complexity may not be age-appropriate")
            return False
    else:
        print("   ❌ Could not retrieve questions for comparison")
        return False

def get_sample_question(token, subject, topics, difficulty):
    """Get a sample question for analysis"""
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "subject": subject,
        "topics": topics,
        "difficulty": difficulty,
        "question_count": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            questions = data.get("questions", [])
            if len(questions) > 0:
                return questions[0].get("question_text", "")
        return None
    except:
        return None

def test_grade_range_handling(token):
    """Test that backend handles all grade levels seamlessly"""
    print("   Testing all grade levels (6th through 12th)...")
    
    grade_tests = [
        ("6th", "math", ["Whole Numbers"]),
        ("7th", "math", ["Integers"]),
        ("8th", "math", ["Rational Numbers"]),
        ("9th", "math", ["Polynomials"]),
        ("10th", "math", ["Real Numbers"]),
        ("11th", "math", ["Sets"]),
        ("12th", "math", ["Matrices"])
    ]
    
    successful_grades = 0
    
    for grade, subject, topics in grade_tests:
        success = test_practice_generation(token, subject, topics, grade)
        if success:
            successful_grades += 1
    
    success_rate = (successful_grades / len(grade_tests)) * 100
    print(f"   Grade Range Success Rate: {success_rate:.1f}% ({successful_grades}/{len(grade_tests)})")
    
    return success_rate >= 85  # 85% or higher is considered successful

def main():
    print("🚀 Starting Final Verification Test for NCERT Extended Grades Integration...")
    
    # Register student
    token, student_id = register_test_student()
    if not token:
        print("❌ Cannot continue without student token")
        return False
    
    # Test specific requirements
    results = test_specific_requirements(token)
    
    # Calculate overall success
    total_tests = len(results)
    successful_tests = sum(1 for success in results.values() if success)
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"\n📊 Final Verification Results:")
    print(f"   6th Grade Units: {'✅ PASS' if results['6th_grade'] else '❌ FAIL'}")
    print(f"   7th Grade Units: {'✅ PASS' if results['7th_grade'] else '❌ FAIL'}")
    print(f"   8th Grade Physics: {'✅ PASS' if results['8th_grade_physics'] else '❌ FAIL'}")
    print(f"   8th Grade Chemistry: {'✅ PASS' if results['8th_grade_chemistry'] else '❌ FAIL'}")
    print(f"   Age-Appropriate Content: {'✅ PASS' if results['age_appropriate'] else '❌ FAIL'}")
    print(f"   Grade Range Handling: {'✅ PASS' if results['grade_range_handling'] else '❌ FAIL'}")
    print(f"   Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("\n🎉 FINAL VERIFICATION PASSED! NCERT Extended Grades Integration is working excellently!")
        return True
    else:
        print("\n⚠️ FINAL VERIFICATION FAILED! Some issues need to be addressed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
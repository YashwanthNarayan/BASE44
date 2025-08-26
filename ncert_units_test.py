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

print(f"🔍 Testing NCERT Units Integration")
print(f"Using API URL: {API_URL}")

def register_test_student():
    """Register a test student for NCERT testing"""
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
            return data.get("access_token")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None

def test_ncert_units_integration(token):
    """Test NCERT units integration across different subjects and grades"""
    
    if not token:
        print("❌ No authentication token available")
        return False
    
    url = f"{API_URL}/practice/generate"
    headers = {"Authorization": f"Bearer {token}"}
    
    # NCERT test scenarios
    test_scenarios = [
        {
            "name": "Math 10th Grade - Real Numbers & Quadratic Equations",
            "subject": "math",
            "topics": ["Real Numbers", "Quadratic Equations"],
            "expected_terms": ["real", "number", "quadratic", "equation", "polynomial", "coefficient"]
        },
        {
            "name": "Physics 11th Grade - Laws of Motion",
            "subject": "physics", 
            "topics": ["Laws of Motion", "Work, Energy and Power"],
            "expected_terms": ["force", "motion", "newton", "energy", "power", "work", "acceleration"]
        },
        {
            "name": "Chemistry 12th Grade - Electrochemistry",
            "subject": "chemistry",
            "topics": ["Electrochemistry", "Chemical Kinetics"],
            "expected_terms": ["electro", "reaction", "kinetics", "rate", "electrode", "cell"]
        },
        {
            "name": "Biology 9th Grade - Cell Biology",
            "subject": "biology",
            "topics": ["The Fundamental Unit of Life", "Tissues"],
            "expected_terms": ["cell", "tissue", "organism", "membrane", "nucleus", "cytoplasm"]
        },
        {
            "name": "English 10th Grade - Literature",
            "subject": "english",
            "topics": ["Nelson Mandela: Long Walk to Freedom", "From the Diary of Anne Frank"],
            "expected_terms": ["character", "story", "author", "theme", "literature", "mandela", "anne"]
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_scenarios)
    
    print(f"\n🧪 Running {total_tests} NCERT Units Integration Tests...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}/{total_tests}: {scenario['name']} ---")
        
        payload = {
            "subject": scenario["subject"],
            "topics": scenario["topics"],
            "difficulty": "medium",
            "question_count": 2
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                if len(questions) > 0:
                    print(f"✅ Generated {len(questions)} questions")
                    
                    # Analyze question quality
                    relevant_content_found = False
                    for j, question in enumerate(questions):
                        question_text = question.get("question_text", "")
                        explanation = question.get("explanation", "")
                        combined_text = (question_text + " " + explanation).lower()
                        
                        print(f"   Q{j+1}: {question_text[:100]}...")
                        
                        # Check for subject-specific terminology
                        for term in scenario["expected_terms"]:
                            if term.lower() in combined_text:
                                relevant_content_found = True
                                print(f"   ✓ Contains '{term}' - relevant to NCERT unit")
                                break
                        
                        # Check question quality
                        if len(question_text) > 30:
                            print(f"   ✓ Substantial question content")
                        else:
                            print(f"   ⚠️ Question may be too short")
                    
                    if relevant_content_found:
                        successful_tests += 1
                        print(f"✅ {scenario['name']}: PASSED - Generated relevant NCERT content")
                    else:
                        print(f"⚠️ {scenario['name']}: Generated questions but may lack NCERT-specific content")
                else:
                    print(f"❌ {scenario['name']}: No questions generated")
            else:
                print(f"❌ {scenario['name']}: API call failed - {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ {scenario['name']}: Exception - {str(e)}")
    
    # Calculate success rate
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n📊 NCERT Units Integration Test Results:")
    print(f"   Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    print(f"   Successful Tests: {successful_tests}")
    print(f"   Failed Tests: {total_tests - successful_tests}")
    
    if success_rate >= 80:
        print("🎉 NCERT Units Integration: EXCELLENT")
        return True
    elif success_rate >= 60:
        print("✅ NCERT Units Integration: GOOD")
        return True
    else:
        print("❌ NCERT Units Integration: NEEDS IMPROVEMENT")
        return False

def main():
    print("🚀 NCERT Units Integration Testing")
    print("=" * 50)
    
    # Register test student
    print("🔐 Registering test student...")
    token = register_test_student()
    
    if token:
        print("✅ Student registered successfully")
        
        # Test NCERT units integration
        success = test_ncert_units_integration(token)
        
        if success:
            print("\n🎉 NCERT Units Integration Testing: PASSED")
        else:
            print("\n❌ NCERT Units Integration Testing: FAILED")
    else:
        print("❌ Failed to register test student")

if __name__ == "__main__":
    main()
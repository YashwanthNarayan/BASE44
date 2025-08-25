#!/usr/bin/env python3
"""
FOCUSED GEMINI API TEST - Quick verification of AI-powered question generation
"""
import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🎯 FOCUSED GEMINI API VERIFICATION")
print(f"Testing: {API_URL}")
print("="*60)

def setup_student():
    """Quick student setup"""
    payload = {
        "email": f"quick_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Quick Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def test_ai_generation(token, subject, topics):
    """Test AI generation for a specific subject"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "subject": subject,
        "topics": topics,
        "difficulty": "medium",
        "question_count": 2
    }
    
    response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        questions = data.get("questions", [])
        
        if questions:
            # Check if questions look AI-generated
            sample_q = questions[0]
            question_text = sample_q.get("question_text", "")
            explanation = sample_q.get("explanation", "")
            
            # Simple heuristics for AI vs fallback
            is_ai = (
                len(question_text) > 50 and
                len(explanation) > 30 and
                "fundamental concept" not in question_text.lower() and
                "basic principle" not in question_text.lower()
            )
            
            return {
                "success": True,
                "is_ai": is_ai,
                "question": question_text[:100] + "..." if len(question_text) > 100 else question_text,
                "explanation_length": len(explanation)
            }
    
    return {"success": False, "error": response.status_code}

def main():
    # Setup
    print("🔧 Setting up test account...")
    token = setup_student()
    if not token:
        print("❌ Failed to create student account")
        return
    
    print("✅ Student account created")
    
    # Test subjects
    test_cases = [
        ("math", ["Algebra"]),
        ("physics", ["Mechanics"]),
        ("chemistry", ["Organic Chemistry"]),
        ("biology", ["Cell Biology"]),
        ("english", ["Grammar"])
    ]
    
    ai_count = 0
    total_count = len(test_cases)
    
    print(f"\n🧪 Testing AI generation across {total_count} subjects...")
    
    for subject, topics in test_cases:
        print(f"\n   Testing {subject}...")
        result = test_ai_generation(token, subject, topics)
        
        if result["success"]:
            if result["is_ai"]:
                ai_count += 1
                print(f"   ✅ AI-generated: {result['question']}")
                print(f"      Explanation length: {result['explanation_length']} chars")
            else:
                print(f"   ⚠️ Fallback detected: {result['question']}")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Summary
    print(f"\n" + "="*60)
    print(f"📊 RESULTS SUMMARY")
    print(f"="*60)
    
    ai_percentage = (ai_count / total_count) * 100
    print(f"AI Generation: {ai_count}/{total_count} subjects ({ai_percentage:.0f}%)")
    
    if ai_count >= 4:
        print("🎉 GEMINI API KEY IS WORKING EXCELLENTLY!")
        print("✅ AI-powered questions are being generated")
        print("✅ Ready for demo with dynamic content")
    elif ai_count >= 2:
        print("⚠️ GEMINI API KEY IS PARTIALLY WORKING")
        print("🔄 Some subjects using AI, others using fallback")
    else:
        print("❌ GEMINI API KEY MAY NOT BE WORKING")
        print("🚨 Mostly fallback questions detected")
    
    return ai_count >= 4

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
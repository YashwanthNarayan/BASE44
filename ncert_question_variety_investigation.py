#!/usr/bin/env python3
"""
Investigation into NCERT Question Variety Issue
The test showed only 5 unique questions out of 15 generated (33% variety)
This suggests caching or AI generation issues
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

def setup_test_user():
    """Create a test student account"""
    url = f"{API_URL}/auth/register"
    payload = {
        "email": f"variety_test_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "Variety Test Student",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

def investigate_question_variety():
    """Investigate why question variety is low"""
    print("🔍 INVESTIGATING QUESTION VARIETY ISSUE")
    print("="*60)
    
    token = setup_test_user()
    if not token:
        print("❌ Failed to create test user")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with Math Real Numbers - the unit that showed repetition
    payload = {
        "subject": "math",
        "topics": ["Real Numbers"],
        "difficulty": "medium",
        "question_count": 5
    }
    
    print("\n📚 Testing Math Real Numbers - Multiple Generations")
    print("Looking for caching issues or AI generation problems...")
    
    all_questions = []
    question_hashes = set()
    
    for attempt in range(5):  # Generate 5 times
        print(f"\n🔄 Generation Attempt {attempt + 1}")
        
        try:
            response = requests.post(f"{API_URL}/practice/generate", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                
                print(f"   Generated {len(questions)} questions")
                
                for i, question in enumerate(questions):
                    question_text = question.get("question_text", "")
                    question_id = question.get("id", "")
                    
                    # Create hash of question text to detect duplicates
                    question_hash = hashlib.md5(question_text.encode()).hexdigest()[:8]
                    
                    print(f"   Q{i+1} (ID: {question_id}): {question_text[:50]}...")
                    print(f"        Hash: {question_hash}")
                    
                    all_questions.append({
                        "text": question_text,
                        "hash": question_hash,
                        "id": question_id,
                        "attempt": attempt + 1
                    })
                    
                    question_hashes.add(question_hash)
            else:
                print(f"   ❌ Generation failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Analyze the results
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"Total questions generated: {len(all_questions)}")
    print(f"Unique question hashes: {len(question_hashes)}")
    print(f"Variety percentage: {len(question_hashes) / len(all_questions) * 100:.1f}%")
    
    # Group questions by hash to see duplicates
    hash_groups = {}
    for question in all_questions:
        hash_key = question["hash"]
        if hash_key not in hash_groups:
            hash_groups[hash_key] = []
        hash_groups[hash_key].append(question)
    
    print(f"\n🔍 DUPLICATE ANALYSIS:")
    for hash_key, questions in hash_groups.items():
        if len(questions) > 1:
            print(f"\n   Hash {hash_key} appears {len(questions)} times:")
            for q in questions:
                print(f"     Attempt {q['attempt']}: {q['text'][:60]}...")
    
    # Check if questions are identical or just similar
    print(f"\n🔍 EXACT DUPLICATE CHECK:")
    exact_duplicates = 0
    seen_texts = set()
    for question in all_questions:
        if question["text"] in seen_texts:
            exact_duplicates += 1
            print(f"   EXACT DUPLICATE: {question['text'][:60]}...")
        else:
            seen_texts.add(question["text"])
    
    print(f"\nExact duplicates found: {exact_duplicates}")
    
    # Test with different parameters to see if it affects variety
    print(f"\n🔄 TESTING WITH DIFFERENT PARAMETERS")
    
    # Test with different difficulty
    payload_hard = {
        "subject": "math",
        "topics": ["Real Numbers"],
        "difficulty": "hard",
        "question_count": 3
    }
    
    print(f"\n   Testing with 'hard' difficulty...")
    response = requests.post(f"{API_URL}/practice/generate", json=payload_hard, headers=headers)
    if response.status_code == 200:
        data = response.json()
        questions = data.get("questions", [])
        print(f"   Generated {len(questions)} questions with hard difficulty")
        for i, q in enumerate(questions):
            print(f"     Q{i+1}: {q.get('question_text', '')[:50]}...")
    
    # Test with different topic
    payload_different = {
        "subject": "math",
        "topics": ["Quadratic Equations"],
        "difficulty": "medium",
        "question_count": 3
    }
    
    print(f"\n   Testing with different topic (Quadratic Equations)...")
    response = requests.post(f"{API_URL}/practice/generate", json=payload_different, headers=headers)
    if response.status_code == 200:
        data = response.json()
        questions = data.get("questions", [])
        print(f"   Generated {len(questions)} questions for Quadratic Equations")
        for i, q in enumerate(questions):
            print(f"     Q{i+1}: {q.get('question_text', '')[:50]}...")

if __name__ == "__main__":
    investigate_question_variety()
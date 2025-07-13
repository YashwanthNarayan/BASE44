#!/usr/bin/env python3
"""
Database Investigation for NULL subjects issue
"""
import requests
import json
import uuid

API_URL = "http://localhost:8001/api"

def investigate_null_subjects():
    """Check for NULL subjects in the database"""
    print("🔍 Investigating NULL subjects in database...")
    
    # Register a student to get access
    register_url = f"{API_URL}/auth/register"
    register_payload = {
        "email": f"db_investigator_{uuid.uuid4()}@example.com",
        "password": "SecurePass123!",
        "name": "DB Investigator",
        "user_type": "student",
        "grade_level": "10th"
    }
    
    try:
        response = requests.post(register_url, json=register_payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get all results
                results_url = f"{API_URL}/practice/results"
                results_response = requests.get(results_url, headers=headers)
                
                if results_response.status_code == 200:
                    results = results_response.json()
                    
                    print(f"📊 Total results found: {len(results)}")
                    
                    # Analyze subjects
                    subject_analysis = {}
                    null_subjects = 0
                    
                    for result in results:
                        subject = result.get('subject')
                        if subject is None or subject == '' or subject == 'null':
                            null_subjects += 1
                            subject = 'NULL/EMPTY'
                        
                        if subject not in subject_analysis:
                            subject_analysis[subject] = 0
                        subject_analysis[subject] += 1
                    
                    print("\n📊 SUBJECT DISTRIBUTION:")
                    for subject, count in subject_analysis.items():
                        percentage = (count / len(results)) * 100 if results else 0
                        print(f"  {subject}: {count} attempts ({percentage:.1f}%)")
                    
                    if null_subjects > 0:
                        print(f"\n❌ CRITICAL: {null_subjects} attempts have NULL/empty subjects!")
                        print(f"   This represents {(null_subjects/len(results)*100):.1f}% of all attempts")
                    else:
                        print(f"\n✅ No NULL subjects found in current data")
                        
                    # Test each subject's stats
                    print("\n🔍 Testing subject stats APIs:")
                    subjects_to_test = ['math', 'physics', 'chemistry', 'biology', 'english']
                    
                    for subject in subjects_to_test:
                        stats_url = f"{API_URL}/practice/stats/{subject}"
                        stats_response = requests.get(stats_url, headers=headers)
                        
                        if stats_response.status_code == 200:
                            stats_data = stats_response.json()
                            total_tests = stats_data.get('total_tests', 0)
                            print(f"  {subject}: {total_tests} tests")
                        else:
                            print(f"  {subject}: API error {stats_response.status_code}")
                
                else:
                    print(f"❌ Failed to get results: {results_response.status_code}")
            else:
                print("❌ No token received")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    investigate_null_subjects()
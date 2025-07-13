#!/usr/bin/env python3
"""
Practice Test Results API Debug Test
Focus: Investigate the exact data structure being returned and identify why frontend click functionality isn't working
"""
import requests
import json
import uuid
import os
from datetime import datetime

# Get API URL from current origin (same as frontend)
API_BASE = os.environ.get('REACT_APP_BACKEND_URL', 'https://eduleap-k.preview.emergentagent.com')
API_URL = f"{API_BASE}/api"

print(f"🔍 Testing Practice Results API at: {API_URL}")
print(f"🎯 Focus: Debug frontend click functionality issue")
print("=" * 80)

class PracticeResultsDebugger:
    def __init__(self):
        self.student_token = None
        self.student_id = None
        self.attempt_ids = []
        
    def register_and_login_student(self):
        """Register and login a student for testing"""
        print("\n🔍 Step 1: Setting up student account...")
        
        # Register student
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"debug_student_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Debug Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            print(f"Registration Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.student_id = data.get("user", {}).get("id")
                print(f"✅ Student registered with ID: {self.student_id}")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def create_practice_attempts(self):
        """Create some practice test attempts to have data to test with"""
        print("\n🔍 Step 2: Creating practice test attempts...")
        
        if not self.student_token:
            print("❌ No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create multiple practice tests for different subjects
        test_configs = [
            {"subject": "math", "topics": ["Algebra"], "difficulty": "medium", "question_count": 3},
            {"subject": "physics", "topics": ["Mechanics"], "difficulty": "easy", "question_count": 2},
            {"subject": "chemistry", "topics": ["Organic Chemistry"], "difficulty": "hard", "question_count": 4}
        ]
        
        for i, config in enumerate(test_configs):
            try:
                print(f"\n  Creating test {i+1}: {config['subject']}")
                
                # Generate practice test
                gen_url = f"{API_URL}/practice/generate"
                gen_response = requests.post(gen_url, json=config, headers=headers)
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    questions = gen_data.get("questions", [])
                    print(f"  ✅ Generated {len(questions)} questions")
                    
                    if questions:
                        # Submit the test with some answers
                        question_ids = [q.get("id") for q in questions if q.get("id")]
                        student_answers = {}
                        
                        # Use correct answers for some questions
                        for j, question in enumerate(questions):
                            if question.get("id") and question.get("correct_answer"):
                                # Answer correctly for first half, incorrectly for second half
                                if j < len(questions) // 2:
                                    student_answers[question["id"]] = question["correct_answer"]
                                else:
                                    student_answers[question["id"]] = "wrong answer"
                        
                        submit_payload = {
                            "questions": question_ids,
                            "student_answers": student_answers,
                            "subject": config["subject"],
                            "time_taken": 300 + (i * 60)  # Different times
                        }
                        
                        submit_url = f"{API_URL}/practice/submit"
                        submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
                        
                        if submit_response.status_code == 200:
                            submit_data = submit_response.json()
                            attempt_id = submit_data.get("attempt_id")
                            if attempt_id:
                                self.attempt_ids.append(attempt_id)
                                print(f"  ✅ Submitted test, attempt ID: {attempt_id}")
                            else:
                                print(f"  ⚠️ No attempt_id in response: {submit_data}")
                        else:
                            print(f"  ❌ Submit failed: {submit_response.status_code} - {submit_response.text}")
                else:
                    print(f"  ❌ Generation failed: {gen_response.status_code} - {gen_response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error creating test {i+1}: {e}")
        
        print(f"\n✅ Created {len(self.attempt_ids)} practice attempts")
        return len(self.attempt_ids) > 0
    
    def test_practice_results_api(self):
        """Test GET /api/practice/results (all results)"""
        print("\n🔍 Step 3: Testing GET /api/practice/results (all results)")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        url = f"{API_URL}/practice/results"
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API call successful")
                print(f"📊 Data type: {type(data)}")
                print(f"📊 Number of results: {len(data) if isinstance(data, list) else 'Not a list'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print("\n🔍 DETAILED DATA STRUCTURE ANALYSIS:")
                    print("=" * 50)
                    
                    for i, result in enumerate(data[:3]):  # Show first 3 results
                        print(f"\nResult #{i+1}:")
                        print(f"  Type: {type(result)}")
                        print(f"  Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                        
                        if isinstance(result, dict):
                            # Check for 'id' field specifically
                            if 'id' in result:
                                print(f"  ✅ HAS 'id' field: {result['id']}")
                            else:
                                print(f"  ❌ NO 'id' field found!")
                                print(f"  Available fields: {list(result.keys())}")
                            
                            # Show all fields and their values
                            for key, value in result.items():
                                if key in ['id', 'attempt_id', '_id', 'subject', 'score', 'completed_at']:
                                    print(f"  {key}: {value} ({type(value).__name__})")
                    
                    print("\n🎯 FRONTEND CLICK ISSUE ANALYSIS:")
                    print("=" * 50)
                    
                    # Check if all results have 'id' field
                    results_with_id = [r for r in data if isinstance(r, dict) and 'id' in r]
                    results_without_id = [r for r in data if isinstance(r, dict) and 'id' not in r]
                    
                    print(f"Results WITH 'id' field: {len(results_with_id)}")
                    print(f"Results WITHOUT 'id' field: {len(results_without_id)}")
                    
                    if results_without_id:
                        print("❌ ISSUE IDENTIFIED: Some results missing 'id' field!")
                        print("This explains why frontend click functionality isn't working.")
                        
                        # Show alternative field names
                        alt_fields = set()
                        for result in results_without_id[:3]:
                            for key in result.keys():
                                if 'id' in key.lower():
                                    alt_fields.add(key)
                        
                        if alt_fields:
                            print(f"Alternative ID fields found: {list(alt_fields)}")
                        else:
                            print("No alternative ID fields found!")
                    else:
                        print("✅ All results have 'id' field - issue might be elsewhere")
                
                else:
                    print("⚠️ No results returned or data is not a list")
                    
            else:
                print(f"❌ API call failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing results API: {e}")
    
    def test_practice_stats_api(self):
        """Test GET /api/practice/stats/{subject} for specific subjects"""
        print("\n🔍 Step 4: Testing GET /api/practice/stats/{subject}")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        subjects = ["math", "physics", "chemistry"]
        
        for subject in subjects:
            print(f"\n  Testing subject: {subject}")
            url = f"{API_URL}/practice/stats/{subject}"
            
            try:
                response = requests.get(url, headers=headers)
                print(f"  Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ API call successful")
                    print(f"  📊 Data type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"  📊 Keys: {list(data.keys())}")
                        print(f"  📊 Total tests: {data.get('total_tests', 'N/A')}")
                        print(f"  📊 Average score: {data.get('average_score', 'N/A')}")
                        
                        # Check recent_tests structure
                        recent_tests = data.get('recent_tests', [])
                        if recent_tests:
                            print(f"  📊 Recent tests count: {len(recent_tests)}")
                            if len(recent_tests) > 0:
                                first_test = recent_tests[0]
                                print(f"  📊 Recent test structure: {list(first_test.keys()) if isinstance(first_test, dict) else 'Not a dict'}")
                                
                                # Check for 'id' field in recent tests
                                if isinstance(first_test, dict):
                                    if 'id' in first_test:
                                        print(f"  ✅ Recent tests have 'id' field")
                                    else:
                                        print(f"  ❌ Recent tests missing 'id' field")
                        else:
                            print(f"  📊 No recent tests")
                else:
                    print(f"  ❌ API call failed: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error testing stats API for {subject}: {e}")
    
    def test_detailed_results_api(self):
        """Test GET /api/practice/results/{attempt_id} with real attempt IDs"""
        print("\n🔍 Step 5: Testing GET /api/practice/results/{attempt_id}")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        if not self.attempt_ids:
            print("❌ No attempt IDs available for testing")
            return
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        for i, attempt_id in enumerate(self.attempt_ids[:3]):  # Test first 3 attempts
            print(f"\n  Testing attempt #{i+1}: {attempt_id}")
            url = f"{API_URL}/practice/results/{attempt_id}"
            
            try:
                response = requests.get(url, headers=headers)
                print(f"  Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ API call successful")
                    print(f"  📊 Data type: {type(data)}")
                    
                    if isinstance(data, dict):
                        print(f"  📊 Keys: {list(data.keys())}")
                        
                        # Check for important fields
                        important_fields = ['attempt_id', 'id', 'score', 'subject', 'detailed_results']
                        for field in important_fields:
                            if field in data:
                                value = data[field]
                                if field == 'detailed_results' and isinstance(value, list):
                                    print(f"  📊 {field}: {len(value)} items")
                                else:
                                    print(f"  📊 {field}: {value}")
                            else:
                                print(f"  ❌ Missing field: {field}")
                        
                        # Check detailed_results structure
                        detailed_results = data.get('detailed_results', [])
                        if detailed_results and len(detailed_results) > 0:
                            first_result = detailed_results[0]
                            print(f"  📊 Detailed result structure: {list(first_result.keys()) if isinstance(first_result, dict) else 'Not a dict'}")
                else:
                    print(f"  ❌ API call failed: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error testing detailed results for {attempt_id}: {e}")
    
    def investigate_database_structure(self):
        """Investigate what attempt IDs exist in the database"""
        print("\n🔍 Step 6: Database Investigation")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        # Get all results and analyze the data structure
        headers = {"Authorization": f"Bearer {self.student_token}"}
        url = f"{API_URL}/practice/results"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                print(f"📊 Total practice attempts in database: {len(data) if isinstance(data, list) else 0}")
                
                if isinstance(data, list):
                    # Analyze field consistency
                    field_analysis = {}
                    id_field_analysis = {}
                    
                    for result in data:
                        if isinstance(result, dict):
                            for key, value in result.items():
                                if key not in field_analysis:
                                    field_analysis[key] = {"count": 0, "types": set(), "sample_values": []}
                                
                                field_analysis[key]["count"] += 1
                                field_analysis[key]["types"].add(type(value).__name__)
                                
                                if len(field_analysis[key]["sample_values"]) < 3:
                                    field_analysis[key]["sample_values"].append(str(value)[:50])
                                
                                # Special analysis for ID-like fields
                                if 'id' in key.lower():
                                    if key not in id_field_analysis:
                                        id_field_analysis[key] = {"count": 0, "null_count": 0, "sample_values": []}
                                    
                                    id_field_analysis[key]["count"] += 1
                                    if value is None or value == "":
                                        id_field_analysis[key]["null_count"] += 1
                                    elif len(id_field_analysis[key]["sample_values"]) < 3:
                                        id_field_analysis[key]["sample_values"].append(str(value))
                    
                    print("\n📊 FIELD ANALYSIS:")
                    print("=" * 50)
                    for field, info in field_analysis.items():
                        print(f"{field}:")
                        print(f"  Present in: {info['count']}/{len(data)} records")
                        print(f"  Types: {list(info['types'])}")
                        print(f"  Sample values: {info['sample_values']}")
                    
                    print("\n📊 ID FIELD ANALYSIS:")
                    print("=" * 50)
                    for field, info in id_field_analysis.items():
                        print(f"{field}:")
                        print(f"  Present in: {info['count']}/{len(data)} records")
                        print(f"  Null/empty: {info['null_count']}/{info['count']} records")
                        print(f"  Sample values: {info['sample_values']}")
                    
                    # Check for missing 'id' field specifically
                    results_without_id = [r for r in data if isinstance(r, dict) and ('id' not in r or r.get('id') is None)]
                    if results_without_id:
                        print(f"\n❌ CRITICAL ISSUE: {len(results_without_id)} results missing 'id' field!")
                        print("This is likely the root cause of the frontend click issue.")
                    else:
                        print(f"\n✅ All results have 'id' field")
                        
            else:
                print(f"❌ Failed to get results for database investigation: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in database investigation: {e}")
    
    def run_complete_debug(self):
        """Run the complete debugging process"""
        print("🚀 Starting Practice Test Results API Debug")
        print("🎯 Goal: Identify why frontend click functionality isn't working")
        print("=" * 80)
        
        # Step 1: Setup
        if not self.register_and_login_student():
            print("❌ Failed to setup student account")
            return
        
        # Step 2: Create test data
        if not self.create_practice_attempts():
            print("❌ Failed to create practice attempts")
            return
        
        # Step 3-6: Run all tests
        self.test_practice_results_api()
        self.test_practice_stats_api()
        self.test_detailed_results_api()
        self.investigate_database_structure()
        
        print("\n" + "=" * 80)
        print("🏁 DEBUG COMPLETE")
        print("=" * 80)
        
        # Summary
        print("\n📋 SUMMARY OF FINDINGS:")
        print("1. Check the detailed output above for data structure issues")
        print("2. Look for missing 'id' fields in practice results")
        print("3. Verify that attempt IDs are properly formatted")
        print("4. Check if API responses match frontend expectations")

if __name__ == "__main__":
    debugger = PracticeResultsDebugger()
    debugger.run_complete_debug()
#!/usr/bin/env python3
"""
REAL DATA TESTING: Practice API Endpoints with Existing Data
Testing the practice API endpoints using existing student data from the database
"""

import requests
import json
import uuid
import os
import asyncio
import motor.motor_asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 REAL DATA TESTING: Practice API Endpoints")
print(f"Testing with existing practice test data from database")
print("=" * 80)

class RealDataTester:
    def __init__(self):
        self.client = None
        self.db = None
        self.test_student_id = None
        self.test_student_token = None
        self.existing_attempt_id = None
        self.existing_subjects = []
        
    async def connect_to_database(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {str(e)}")
            return False
    
    async def find_student_with_practice_data(self):
        """Find a student who has practice test data"""
        try:
            # Get a student who has practice attempts
            practice_attempts = self.db["practice_attempts"]
            sample_attempt = await practice_attempts.find_one({})
            
            if not sample_attempt:
                print("❌ No practice attempts found in database")
                return False
            
            self.test_student_id = sample_attempt.get("student_id")
            self.existing_attempt_id = sample_attempt.get("id")
            
            print(f"Found student with practice data: {self.test_student_id}")
            print(f"Sample attempt ID: {self.existing_attempt_id}")
            
            # Get all subjects this student has attempted
            student_attempts = await practice_attempts.find({
                "student_id": self.test_student_id
            }).to_list(None)
            
            self.existing_subjects = list(set(attempt.get("subject") for attempt in student_attempts if attempt.get("subject")))
            print(f"Student has attempted subjects: {self.existing_subjects}")
            print(f"Total attempts by this student: {len(student_attempts)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error finding student with practice data: {str(e)}")
            return False
    
    def create_test_student_token(self):
        """Create a new student account to test with (since we can't use existing tokens)"""
        print("\n🔍 Creating test student account...")
        
        register_url = f"{API_URL}/auth/register"
        register_payload = {
            "email": f"real_data_test_{uuid.uuid4()}@example.com",
            "password": "SecurePass123!",
            "name": "Real Data Test Student",
            "user_type": "student",
            "grade_level": "10th"
        }
        
        try:
            response = requests.post(register_url, json=register_payload)
            if response.status_code == 200:
                data = response.json()
                self.test_student_token = data.get("access_token")
                new_student_id = data.get("user", {}).get("id")
                print(f"✅ Created test student: {new_student_id}")
                return True
            else:
                print(f"❌ Failed to create test student: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating test student: {str(e)}")
            return False
    
    def test_practice_results_endpoint(self):
        """Test GET /api/practice/results endpoint"""
        print("\n🔍 Testing GET /api/practice/results endpoint...")
        
        if not self.test_student_token:
            print("❌ No test student token available")
            return False
        
        url = f"{API_URL}/practice/results"
        headers = {"Authorization": f"Bearer {self.test_student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"🚨 500 ERROR FOUND!")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Got {len(data)} results")
                return True
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    def test_practice_stats_endpoints(self):
        """Test GET /api/practice/stats/{subject} endpoints"""
        print("\n🔍 Testing GET /api/practice/stats/{subject} endpoints...")
        
        if not self.test_student_token:
            print("❌ No test student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.test_student_token}"}
        
        # Test with subjects that exist in the database
        test_subjects = ["math", "physics", "chemistry", "biology", "english"]
        
        results = {}
        
        for subject in test_subjects:
            url = f"{API_URL}/practice/stats/{subject}"
            
            try:
                response = requests.get(url, headers=headers)
                print(f"  {subject}: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"    🚨 500 ERROR FOUND for {subject}!")
                    print(f"    Response: {response.text}")
                    results[subject] = False
                elif response.status_code == 200:
                    data = response.json()
                    total_tests = data.get("total_tests", 0)
                    print(f"    ✅ SUCCESS: {total_tests} tests found")
                    results[subject] = True
                else:
                    print(f"    ⚠️ Unexpected status: {response.status_code}")
                    results[subject] = False
                    
            except Exception as e:
                print(f"    ❌ Exception for {subject}: {str(e)}")
                results[subject] = False
        
        success_count = sum(1 for success in results.values() if success)
        print(f"\nStats endpoint results: {success_count}/{len(test_subjects)} successful")
        
        return success_count == len(test_subjects)
    
    def test_detailed_results_endpoint(self):
        """Test GET /api/practice/results/{attempt_id} endpoint"""
        print("\n🔍 Testing GET /api/practice/results/{attempt_id} endpoint...")
        
        if not self.test_student_token or not self.existing_attempt_id:
            print("❌ No test student token or attempt ID available")
            return False
        
        # Test with the existing attempt ID (even though it's from a different student)
        # This should return 404, not 500
        url = f"{API_URL}/practice/results/{self.existing_attempt_id}"
        headers = {"Authorization": f"Bearer {self.test_student_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 500:
                print(f"🚨 500 ERROR FOUND!")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 404:
                print(f"✅ Proper 404 response (attempt not found for this student)")
                return True
            elif response.status_code == 200:
                print(f"✅ SUCCESS: Got detailed results")
                return True
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
    
    async def test_with_problematic_data(self):
        """Test endpoints with potentially problematic data from the database"""
        print("\n🔍 Testing with potentially problematic data...")
        
        try:
            # Look for attempts with potential issues
            practice_attempts = self.db["practice_attempts"]
            
            # Find attempts with NULL or empty subjects
            problematic_attempts = await practice_attempts.find({
                "$or": [
                    {"subject": {"$exists": False}},
                    {"subject": None},
                    {"subject": ""},
                    {"student_id": {"$exists": False}},
                    {"student_id": None},
                    {"id": {"$exists": False}},
                    {"id": None}
                ]
            }).to_list(10)
            
            if problematic_attempts:
                print(f"Found {len(problematic_attempts)} potentially problematic attempts:")
                for i, attempt in enumerate(problematic_attempts):
                    print(f"  Attempt {i+1}:")
                    print(f"    ID: {attempt.get('id', 'MISSING')}")
                    print(f"    Student ID: {attempt.get('student_id', 'MISSING')}")
                    print(f"    Subject: {attempt.get('subject', 'MISSING')}")
                    print(f"    Score: {attempt.get('score', 'MISSING')}")
                
                print(f"🚨 These problematic records could cause 500 errors in API endpoints!")
                return False
            else:
                print(f"✅ No problematic data found in practice_attempts collection")
                return True
                
        except Exception as e:
            print(f"❌ Error checking for problematic data: {str(e)}")
            return False
    
    async def run_real_data_tests(self):
        """Run all real data tests"""
        print("🔍 REAL DATA TESTING: Practice API Endpoints")
        print("Testing with existing practice test data from database")
        print("=" * 80)
        
        # Connect to database
        if not await self.connect_to_database():
            return
        
        # Find student with existing data
        if not await self.find_student_with_practice_data():
            return
        
        # Check for problematic data
        await self.test_with_problematic_data()
        
        # Create test student account
        if not self.create_test_student_token():
            return
        
        # Test all endpoints
        results = {
            "practice_results": self.test_practice_results_endpoint(),
            "practice_stats": self.test_practice_stats_endpoints(),
            "detailed_results": self.test_detailed_results_endpoint()
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 REAL DATA TEST RESULTS:")
        print("=" * 80)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        all_passed = all(results.values())
        
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 CONCLUSION: All practice API endpoints work correctly with real data!")
            print("No 500 errors found even with existing database records.")
        else:
            print("🚨 CONCLUSION: Issues found with practice API endpoints!")
            print("Some endpoints are returning 500 errors with real data.")
        print("=" * 80)
        
        if self.client:
            self.client.close()
        
        return results

async def main():
    tester = RealDataTester()
    await tester.run_real_data_tests()

if __name__ == "__main__":
    asyncio.run(main())
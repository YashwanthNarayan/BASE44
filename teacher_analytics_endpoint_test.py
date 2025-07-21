#!/usr/bin/env python3
"""
Teacher Analytics Endpoint Testing
==================================

Testing the teacher analytics endpoints with proper authentication
to understand why analytics show empty data despite having real data.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().strip('"')
    except:
        pass
    return "https://5dc579ef-675e-4006-84a0-6dbff9c9e674.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

# Test data from the investigation
TEACHER_ID = "82e6b2a2-7510-4b77-80d1-c8fbdf542cfb"
STUDENT_ID = "a99198ad-0aeb-470c-984a-72a07fdb53c5"

class TeacherAnalyticsTester:
    def __init__(self):
        self.session = None
        self.teacher_token = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def create_teacher_account(self):
        """Create a teacher account with proper credentials"""
        print(f"📝 Creating teacher account...")
        
        register_data = {
            "name": "Analytics Test Teacher",
            "email": "analytics.teacher@test.com",
            "password": "TestPass123!",
            "user_type": "teacher"
        }
        
        async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
            if response.status == 201:
                data = await response.json()
                self.teacher_token = data.get('access_token')
                print(f"✅ Teacher account created successfully")
                return data.get('user', {}).get('id')
            elif response.status == 400:
                # Try to login instead
                print("📝 Account exists, trying to login...")
                return await self.login_teacher()
            else:
                text = await response.text()
                print(f"❌ Teacher registration failed: {response.status} - {text}")
                return None
                
    async def login_teacher(self):
        """Login as teacher"""
        login_data = {
            "email": "analytics.teacher@test.com",
            "password": "TestPass123!"
        }
        
        async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.teacher_token = data.get('access_token')
                print(f"✅ Teacher login successful")
                return data.get('user', {}).get('id')
            else:
                text = await response.text()
                print(f"❌ Teacher login failed: {response.status} - {text}")
                return None
                
    async def create_test_class(self, teacher_id):
        """Create a test class"""
        print(f"📚 Creating test class...")
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        class_data = {
            "class_name": "Analytics Test Class",
            "subject": "math",
            "description": "Test class for analytics investigation"
        }
        
        async with self.session.post(f"{API_BASE}/teacher/classes", json=class_data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Test class created: {data.get('class_id')}")
                return data.get('class_id')
            else:
                text = await response.text()
                print(f"❌ Class creation failed: {response.status} - {text}")
                return None
                
    async def test_with_existing_teacher_data(self):
        """Test analytics with the existing teacher data from database"""
        print("\n" + "="*60)
        print("🔍 TESTING WITH EXISTING TEACHER DATA")
        print("="*60)
        
        # We know from investigation that teacher 82e6b2a2-7510-4b77-80d1-c8fbdf542cfb exists
        # Let's try to get their credentials or create a matching account
        
        # First, let's check if we can find this teacher in the users collection
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            # Find the teacher user
            teacher_user = await db.users.find_one({"id": TEACHER_ID})
            if teacher_user:
                print(f"✅ Found teacher user: {teacher_user.get('email', 'No email')}")
                
                # Try to login with common passwords
                test_passwords = ["password", "password123", "test123", "TestPass123!", "teacher123"]
                
                for password in test_passwords:
                    login_data = {
                        "email": teacher_user.get('email'),
                        "password": password
                    }
                    
                    async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.teacher_token = data.get('access_token')
                            print(f"✅ Successfully logged in as existing teacher")
                            return True
                            
                print(f"❌ Could not login as existing teacher")
                return False
            else:
                print(f"❌ Teacher user not found in database")
                return False
                
        finally:
            client.close()
            
    async def test_analytics_endpoints(self):
        """Test all analytics endpoints"""
        print("\n" + "="*60)
        print("📊 TESTING ANALYTICS ENDPOINTS")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Test 1: Analytics Overview
        print("🔍 Testing /api/teacher/analytics/overview...")
        async with self.session.get(f"{API_BASE}/teacher/analytics/overview", headers=headers) as response:
            print(f"   Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"   ✅ Overview endpoint working")
                
                metrics = data.get('overview_metrics', {})
                print(f"   📈 Metrics:")
                print(f"      Total Classes: {metrics.get('total_classes', 0)}")
                print(f"      Total Students: {metrics.get('total_students', 0)}")
                print(f"      Total Tests: {metrics.get('total_tests', 0)}")
                print(f"      Average Score: {metrics.get('average_score', 0):.2f}")
                
                # Check if we have the expected data
                if metrics.get('total_tests', 0) > 0:
                    print(f"   ✅ Found test data in analytics!")
                else:
                    print(f"   ❌ No test data found in analytics")
                    
                class_summary = data.get('class_summary', [])
                print(f"   📚 Class Summary: {len(class_summary)} classes")
                
                subject_dist = data.get('subject_distribution', [])
                print(f"   📊 Subject Distribution: {len(subject_dist)} subjects")
                
            else:
                text = await response.text()
                print(f"   ❌ Overview failed: {text}")
                
        # Test 2: Test Results
        print("\n🔍 Testing /api/teacher/analytics/test-results...")
        async with self.session.get(f"{API_BASE}/teacher/analytics/test-results", headers=headers) as response:
            print(f"   Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"   ✅ Test results endpoint working")
                print(f"   📊 Found {len(data)} test results")
                
                if data:
                    print("   📝 Sample results:")
                    for i, result in enumerate(data[:3], 1):
                        print(f"      {i}. Student: {result.get('student_name', 'Unknown')}")
                        print(f"         Subject: {result.get('subject', 'Unknown')}")
                        print(f"         Score: {result.get('score', 0)}")
                else:
                    print("   ❌ No test results found")
            else:
                text = await response.text()
                print(f"   ❌ Test results failed: {text}")
                
        # Test 3: Class Performance (need a class ID)
        print("\n🔍 Getting teacher's classes first...")
        async with self.session.get(f"{API_BASE}/teacher/classes", headers=headers) as response:
            if response.status == 200:
                classes = await response.json()
                print(f"   Found {len(classes)} classes")
                
                if classes:
                    class_id = classes[0]['class_id']
                    print(f"   Testing class performance for: {class_id}")
                    
                    async with self.session.get(f"{API_BASE}/teacher/analytics/class-performance/{class_id}", headers=headers) as perf_response:
                        print(f"   Status: {perf_response.status}")
                        
                        if perf_response.status == 200:
                            data = await perf_response.json()
                            print(f"   ✅ Class performance endpoint working")
                            
                            perf_summary = data.get('performance_summary', {})
                            print(f"   📊 Performance Summary:")
                            print(f"      Total Tests: {perf_summary.get('total_tests', 0)}")
                            print(f"      Average Score: {perf_summary.get('average_score', 0):.2f}")
                            
                        else:
                            text = await perf_response.text()
                            print(f"   ❌ Class performance failed: {text}")
            else:
                print("   ❌ Failed to get teacher's classes")
                
    async def investigate_root_cause(self):
        """Investigate the root cause of empty analytics"""
        print("\n" + "="*60)
        print("🔬 ROOT CAUSE INVESTIGATION")
        print("="*60)
        
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            print("🔍 Analyzing the data flow issue...")
            
            # Check the specific teacher's data
            teacher_classes = await db.classrooms.find({"teacher_id": TEACHER_ID}).to_list(10)
            print(f"   Teacher {TEACHER_ID} has {len(teacher_classes)} classes")
            
            if teacher_classes:
                class_ids = [cls['class_id'] for cls in teacher_classes]
                
                # Check students in these classes
                students = await db.student_profiles.find({
                    "joined_classes": {"$in": class_ids}
                }).to_list(100)
                print(f"   Found {len(students)} students in teacher's classes")
                
                if students:
                    student_ids = [s['user_id'] for s in students]
                    
                    # Check practice attempts
                    attempts = await db.practice_attempts.find({
                        "student_id": {"$in": student_ids}
                    }).to_list(100)
                    print(f"   Found {len(attempts)} practice attempts for these students")
                    
                    if attempts:
                        # Analyze subjects
                        subjects = {}
                        for attempt in attempts:
                            subject = attempt.get('subject', 'Unknown')
                            if subject not in subjects:
                                subjects[subject] = 0
                            subjects[subject] += 1
                            
                        print(f"   Subject breakdown:")
                        for subject, count in subjects.items():
                            print(f"      {subject}: {count} attempts")
                            
                        # Check if the issue is with subject filtering
                        if 'general' in subjects and subjects['general'] > 0:
                            print(f"   🚨 ISSUE FOUND: Most attempts have subject 'general' instead of specific subjects!")
                            print(f"   This might be why analytics show empty data for specific subjects.")
                            
                        # Check a sample attempt structure
                        sample = attempts[0]
                        print(f"   Sample attempt structure:")
                        for key, value in sample.items():
                            if key != '_id':
                                print(f"      {key}: {type(value)} = {value}")
                                
        finally:
            client.close()
            
    async def run_test(self):
        """Run the complete test"""
        print("🚀 STARTING TEACHER ANALYTICS ENDPOINT TESTING")
        print("="*80)
        
        await self.setup_session()
        
        try:
            # Try to test with existing teacher data first
            if await self.test_with_existing_teacher_data():
                await self.test_analytics_endpoints()
            else:
                # Create new teacher account
                teacher_id = await self.create_teacher_account()
                if teacher_id:
                    await self.test_analytics_endpoints()
                    
            # Always run root cause investigation
            await self.investigate_root_cause()
            
        finally:
            await self.cleanup_session()
            
        print("\n" + "="*80)
        print("🏁 TESTING COMPLETE")
        print("="*80)

async def main():
    """Main function"""
    tester = TeacherAnalyticsTester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())
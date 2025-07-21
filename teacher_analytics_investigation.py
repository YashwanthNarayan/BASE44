#!/usr/bin/env python3
"""
Teacher Analytics Investigation Test
===================================

This test investigates why teacher analytics endpoints are showing empty data
despite having real data in the database. Specifically testing with:
- Teacher ID: 82e6b2a2-7510-4b77-80d1-c8fbdf542cfb
- Student ID: a99198ad-0aeb-470c-984a-72a07fdb53c5
- Expected: 37 practice attempts for this student
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
EXPECTED_ATTEMPTS = 37

class TeacherAnalyticsInvestigator:
    def __init__(self):
        self.session = None
        self.teacher_token = None
        self.student_token = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_as_teacher(self):
        """Authenticate as the specific teacher"""
        print(f"🔐 Authenticating as teacher {TEACHER_ID}...")
        
        # First, try to login with existing teacher credentials
        login_data = {
            "email": "teacher@test.com",
            "password": "password123"
        }
        
        async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.teacher_token = data.get('access_token')
                print(f"✅ Teacher login successful")
                return True
            else:
                print(f"❌ Teacher login failed: {response.status}")
                # Try to register the teacher
                return await self.register_teacher()
                
    async def register_teacher(self):
        """Register the specific teacher"""
        print(f"📝 Registering teacher {TEACHER_ID}...")
        
        register_data = {
            "name": "Test Teacher",
            "email": "teacher@test.com",
            "password": "password123",
            "user_type": "teacher"
        }
        
        async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
            if response.status == 201:
                data = await response.json()
                self.teacher_token = data.get('access_token')
                print(f"✅ Teacher registration successful")
                return True
            else:
                text = await response.text()
                print(f"❌ Teacher registration failed: {response.status} - {text}")
                return False
                
    async def get_auth_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
        
    async def investigate_database_data(self):
        """Investigate the actual database data"""
        print("\n" + "="*60)
        print("🔍 DATABASE DATA INVESTIGATION")
        print("="*60)
        
        # Connect to MongoDB directly to check data
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            # Check practice attempts collection
            print(f"📊 Checking PRACTICE_ATTEMPTS collection...")
            total_attempts = await db.practice_attempts.count_documents({})
            print(f"   Total practice attempts in database: {total_attempts}")
            
            # Check for specific student
            student_attempts = await db.practice_attempts.count_documents({"student_id": STUDENT_ID})
            print(f"   Practice attempts for student {STUDENT_ID}: {student_attempts}")
            
            # Get sample attempts for this student
            if student_attempts > 0:
                sample_attempts = await db.practice_attempts.find({"student_id": STUDENT_ID}).limit(3).to_list(3)
                print(f"   Sample attempts for student:")
                for i, attempt in enumerate(sample_attempts, 1):
                    print(f"     {i}. ID: {attempt.get('id', 'N/A')}")
                    print(f"        Subject: {attempt.get('subject', 'N/A')}")
                    print(f"        Score: {attempt.get('score', 'N/A')}")
                    print(f"        Date: {attempt.get('completed_at', 'N/A')}")
            
            # Check classrooms collection
            print(f"\n📚 Checking CLASSROOMS collection...")
            total_classrooms = await db.classrooms.count_documents({})
            print(f"   Total classrooms in database: {total_classrooms}")
            
            # Check for teacher's classes
            teacher_classes = await db.classrooms.find({"teacher_id": TEACHER_ID}).to_list(10)
            print(f"   Classes for teacher {TEACHER_ID}: {len(teacher_classes)}")
            
            for i, classroom in enumerate(teacher_classes, 1):
                print(f"     {i}. Class ID: {classroom.get('class_id', 'N/A')}")
                print(f"        Name: {classroom.get('class_name', 'N/A')}")
                print(f"        Subject: {classroom.get('subject', 'N/A')}")
                print(f"        Students: {len(classroom.get('student_ids', []))}")
            
            # Check student profiles
            print(f"\n👥 Checking STUDENT_PROFILES collection...")
            student_profile = await db.student_profiles.find_one({"user_id": STUDENT_ID})
            if student_profile:
                print(f"   Student profile found for {STUDENT_ID}")
                print(f"   Joined classes: {student_profile.get('joined_classes', [])}")
            else:
                print(f"   No student profile found for {STUDENT_ID}")
                
            # Check if student is in any of teacher's classes
            if teacher_classes and student_profile:
                teacher_class_ids = [cls['class_id'] for cls in teacher_classes]
                student_classes = student_profile.get('joined_classes', [])
                common_classes = set(teacher_class_ids) & set(student_classes)
                print(f"   Common classes between teacher and student: {list(common_classes)}")
                
        finally:
            client.close()
            
    async def test_analytics_overview(self):
        """Test the analytics overview endpoint"""
        print("\n" + "="*60)
        print("📊 TESTING ANALYTICS OVERVIEW ENDPOINT")
        print("="*60)
        
        headers = await self.get_auth_headers(self.teacher_token)
        
        async with self.session.get(f"{API_BASE}/teacher/analytics/overview", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Overview endpoint working")
                print(f"📈 Overview Metrics:")
                metrics = data.get('overview_metrics', {})
                print(f"   Total Classes: {metrics.get('total_classes', 0)}")
                print(f"   Total Students: {metrics.get('total_students', 0)}")
                print(f"   Total Tests: {metrics.get('total_tests', 0)}")
                print(f"   Average Score: {metrics.get('average_score', 0):.2f}")
                
                print(f"\n📚 Class Summary:")
                class_summary = data.get('class_summary', [])
                if class_summary:
                    for i, cls in enumerate(class_summary, 1):
                        class_info = cls.get('class_info', {})
                        print(f"   {i}. {class_info.get('class_name', 'Unknown')}")
                        print(f"      Subject: {class_info.get('subject', 'Unknown')}")
                        print(f"      Students: {cls.get('student_count', 0)}")
                        print(f"      Tests: {cls.get('total_tests', 0)}")
                        print(f"      Avg Score: {cls.get('average_score', 0):.2f}")
                else:
                    print("   ❌ No class summary data found")
                    
                print(f"\n📊 Subject Distribution:")
                subject_dist = data.get('subject_distribution', [])
                if subject_dist:
                    for subject in subject_dist:
                        print(f"   {subject.get('subject', 'Unknown')}: {subject.get('test_count', 0)} tests, avg {subject.get('average_score', 0):.2f}")
                else:
                    print("   ❌ No subject distribution data found")
                    
            else:
                text = await response.text()
                print(f"❌ Overview endpoint failed: {text}")
                
    async def test_test_results_endpoint(self):
        """Test the test results endpoint"""
        print("\n" + "="*60)
        print("📋 TESTING TEST RESULTS ENDPOINT")
        print("="*60)
        
        headers = await self.get_auth_headers(self.teacher_token)
        
        # Test without filters
        print("🔍 Testing without filters...")
        async with self.session.get(f"{API_BASE}/teacher/analytics/test-results", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Test results endpoint working")
                print(f"📊 Found {len(data)} test results")
                
                if data:
                    print("📝 Sample results:")
                    for i, result in enumerate(data[:3], 1):
                        print(f"   {i}. Student: {result.get('student_name', 'Unknown')}")
                        print(f"      Subject: {result.get('subject', 'Unknown')}")
                        print(f"      Score: {result.get('score', 0)}")
                        print(f"      Date: {result.get('completed_at', 'Unknown')}")
                else:
                    print("   ❌ No test results found")
            else:
                text = await response.text()
                print(f"❌ Test results endpoint failed: {text}")
                
        # Test with subject filter
        print("\n🔍 Testing with subject filter (math)...")
        async with self.session.get(f"{API_BASE}/teacher/analytics/test-results?subject=math", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"✅ Math filter working - found {len(data)} results")
            else:
                text = await response.text()
                print(f"❌ Math filter failed: {text}")
                
    async def test_class_performance_endpoint(self):
        """Test the class performance endpoint"""
        print("\n" + "="*60)
        print("🎯 TESTING CLASS PERFORMANCE ENDPOINT")
        print("="*60)
        
        headers = await self.get_auth_headers(self.teacher_token)
        
        # First get teacher's classes to find a class ID
        async with self.session.get(f"{API_BASE}/teacher/classes", headers=headers) as response:
            if response.status == 200:
                classes = await response.json()
                if classes:
                    class_id = classes[0]['class_id']
                    print(f"🔍 Testing with class ID: {class_id}")
                    
                    async with self.session.get(f"{API_BASE}/teacher/analytics/class-performance/{class_id}", headers=headers) as perf_response:
                        print(f"Status: {perf_response.status}")
                        
                        if perf_response.status == 200:
                            data = await perf_response.json()
                            print(f"✅ Class performance endpoint working")
                            
                            class_info = data.get('class_info', {})
                            print(f"📚 Class: {class_info.get('class_name', 'Unknown')}")
                            print(f"   Subject: {class_info.get('subject', 'Unknown')}")
                            print(f"   Students: {class_info.get('student_count', 0)}")
                            
                            perf_summary = data.get('performance_summary', {})
                            print(f"📊 Performance Summary:")
                            print(f"   Total Tests: {perf_summary.get('total_tests', 0)}")
                            print(f"   Average Score: {perf_summary.get('average_score', 0):.2f}")
                            print(f"   Highest Score: {perf_summary.get('highest_score', 0)}")
                            print(f"   Lowest Score: {perf_summary.get('lowest_score', 0)}")
                            
                            student_perf = data.get('student_performance', [])
                            print(f"👥 Student Performance ({len(student_perf)} students):")
                            for student in student_perf[:3]:
                                print(f"   {student.get('student_name', 'Unknown')}: {student.get('total_tests', 0)} tests, avg {student.get('average_score', 0):.2f}")
                                
                        else:
                            text = await perf_response.text()
                            print(f"❌ Class performance failed: {text}")
                else:
                    print("❌ No classes found for teacher")
            else:
                print("❌ Failed to get teacher's classes")
                
    async def diagnose_data_flow_issue(self):
        """Diagnose the specific data flow issue"""
        print("\n" + "="*60)
        print("🔬 DIAGNOSING DATA FLOW ISSUE")
        print("="*60)
        
        # Connect to MongoDB to trace the data flow
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            print("🔍 Step 1: Check if teacher exists and has classes")
            teacher_classes = await db.classrooms.find({"teacher_id": TEACHER_ID}).to_list(10)
            print(f"   Teacher has {len(teacher_classes)} classes")
            
            if teacher_classes:
                class_ids = [cls['class_id'] for cls in teacher_classes]
                print(f"   Class IDs: {class_ids}")
                
                print("\n🔍 Step 2: Check if students are in these classes")
                students_in_classes = await db.student_profiles.find({
                    "joined_classes": {"$in": class_ids}
                }).to_list(100)
                print(f"   Found {len(students_in_classes)} students in teacher's classes")
                
                if students_in_classes:
                    student_ids = [s['user_id'] for s in students_in_classes]
                    print(f"   Student IDs: {student_ids[:5]}...")  # Show first 5
                    
                    print("\n🔍 Step 3: Check practice attempts for these students")
                    practice_attempts = await db.practice_attempts.find({
                        "student_id": {"$in": student_ids}
                    }).to_list(100)
                    print(f"   Found {len(practice_attempts)} practice attempts")
                    
                    if practice_attempts:
                        print("   Sample attempts:")
                        for i, attempt in enumerate(practice_attempts[:3], 1):
                            print(f"     {i}. Student: {attempt.get('student_id', 'N/A')}")
                            print(f"        Subject: {attempt.get('subject', 'N/A')}")
                            print(f"        Score: {attempt.get('score', 'N/A')}")
                            
                        # Check field names
                        print("\n🔍 Step 4: Check field name consistency")
                        sample_attempt = practice_attempts[0]
                        print("   Practice attempt fields:")
                        for key in sample_attempt.keys():
                            print(f"     - {key}: {type(sample_attempt[key])}")
                            
                    else:
                        print("   ❌ No practice attempts found for students in teacher's classes")
                        
                        # Check if there are practice attempts with different field names
                        print("\n🔍 Checking for practice attempts with different field names...")
                        all_attempts = await db.practice_attempts.find({}).limit(5).to_list(5)
                        if all_attempts:
                            print("   Sample practice attempts from database:")
                            for i, attempt in enumerate(all_attempts, 1):
                                print(f"     {i}. Fields: {list(attempt.keys())}")
                                if 'student_id' in attempt:
                                    print(f"        student_id: {attempt['student_id']}")
                                if 'user_id' in attempt:
                                    print(f"        user_id: {attempt['user_id']}")
                else:
                    print("   ❌ No students found in teacher's classes")
                    
                    # Check if students exist but with different field structure
                    print("\n🔍 Checking student profile structure...")
                    sample_student = await db.student_profiles.find_one({})
                    if sample_student:
                        print("   Sample student profile fields:")
                        for key in sample_student.keys():
                            print(f"     - {key}: {type(sample_student[key])}")
            else:
                print("   ❌ Teacher has no classes")
                
        finally:
            client.close()
            
    async def run_investigation(self):
        """Run the complete investigation"""
        print("🚀 STARTING TEACHER ANALYTICS INVESTIGATION")
        print("="*80)
        
        await self.setup_session()
        
        try:
            # Step 1: Investigate database data
            await self.investigate_database_data()
            
            # Step 2: Authenticate as teacher
            if await self.authenticate_as_teacher():
                # Step 3: Test analytics endpoints
                await self.test_analytics_overview()
                await self.test_test_results_endpoint()
                await self.test_class_performance_endpoint()
                
            # Step 4: Diagnose data flow issue
            await self.diagnose_data_flow_issue()
            
        finally:
            await self.cleanup_session()
            
        print("\n" + "="*80)
        print("🏁 INVESTIGATION COMPLETE")
        print("="*80)

async def main():
    """Main function"""
    investigator = TeacherAnalyticsInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
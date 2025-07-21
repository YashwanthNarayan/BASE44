#!/usr/bin/env python3
"""
Teacher Analytics Final Test
============================

Testing teacher analytics endpoints with proper authentication
to verify the root cause of empty analytics data.
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

# Test data
TEACHER_ID = "82e6b2a2-7510-4b77-80d1-c8fbdf542cfb"
STUDENT_ID = "a99198ad-0aeb-470c-984a-72a07fdb53c5"

class TeacherAnalyticsFinalTest:
    def __init__(self):
        self.session = None
        self.teacher_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZDkxOGRjZi03MTEwLTQ5MGQtOTUzZC1iM2U3YzkxYWM0NTUiLCJlbWFpbCI6ImFuYWx5dGljcy50ZWFjaGVyQHRlc3QuY29tIiwidXNlcl90eXBlIjoidGVhY2hlciIsImV4cCI6MTc1MzY4MDI1OH0.wYK5eOR5g6yKaLRP9CfXpaDjgbLVtFndOJiQmgB5sPE"
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def create_test_class_and_add_student(self):
        """Create a test class and add the existing student to it"""
        print("📚 Setting up test environment...")
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        # Create a test class
        class_data = {
            "class_name": "Analytics Test Math Class",
            "subject": "math",
            "description": "Test class for analytics investigation"
        }
        
        async with self.session.post(f"{API_BASE}/teacher/classes", json=class_data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                class_id = data.get('class_id')
                join_code = data.get('join_code')
                print(f"✅ Test class created: {class_id}")
                print(f"   Join code: {join_code}")
                
                # Now we need to manually add the student to this class in the database
                # since we can't authenticate as the existing student
                await self.add_student_to_class_directly(class_id, STUDENT_ID)
                
                return class_id
            else:
                text = await response.text()
                print(f"❌ Class creation failed: {response.status} - {text}")
                return None
                
    async def add_student_to_class_directly(self, class_id, student_id):
        """Add student to class directly in database"""
        print(f"👥 Adding student {student_id} to class {class_id}...")
        
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            # Add student to class's student_ids array
            await db.classrooms.update_one(
                {"class_id": class_id},
                {"$addToSet": {"student_ids": student_id}}
            )
            
            # Add class to student's joined_classes array
            await db.student_profiles.update_one(
                {"user_id": student_id},
                {"$addToSet": {"joined_classes": class_id}}
            )
            
            print(f"✅ Student added to class successfully")
            
        finally:
            client.close()
            
    async def test_analytics_with_real_data(self):
        """Test analytics endpoints with real data"""
        print("\n" + "="*60)
        print("📊 TESTING ANALYTICS WITH REAL DATA")
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
                print(f"   📈 Overview Metrics:")
                print(f"      Total Classes: {metrics.get('total_classes', 0)}")
                print(f"      Total Students: {metrics.get('total_students', 0)}")
                print(f"      Total Tests: {metrics.get('total_tests', 0)}")
                print(f"      Average Score: {metrics.get('average_score', 0):.2f}")
                
                class_summary = data.get('class_summary', [])
                print(f"   📚 Class Summary ({len(class_summary)} classes):")
                for i, cls in enumerate(class_summary, 1):
                    class_info = cls.get('class_info', {})
                    print(f"      {i}. {class_info.get('class_name', 'Unknown')}")
                    print(f"         Subject: {class_info.get('subject', 'Unknown')}")
                    print(f"         Students: {cls.get('student_count', 0)}")
                    print(f"         Tests: {cls.get('total_tests', 0)}")
                    print(f"         Avg Score: {cls.get('average_score', 0):.2f}")
                
                subject_dist = data.get('subject_distribution', [])
                print(f"   📊 Subject Distribution ({len(subject_dist)} subjects):")
                for subject in subject_dist:
                    print(f"      {subject.get('subject', 'Unknown')}: {subject.get('test_count', 0)} tests, avg {subject.get('average_score', 0):.2f}")
                    
                # Check if we found the expected data
                if metrics.get('total_tests', 0) >= 37:
                    print(f"   ✅ FOUND EXPECTED DATA: {metrics.get('total_tests')} tests found!")
                elif metrics.get('total_tests', 0) > 0:
                    print(f"   ⚠️  PARTIAL DATA: {metrics.get('total_tests')} tests found (expected 37)")
                else:
                    print(f"   ❌ NO DATA FOUND: Analytics still showing empty")
                    
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
                    for i, result in enumerate(data[:5], 1):
                        print(f"      {i}. Student: {result.get('student_name', 'Unknown')}")
                        print(f"         Subject: {result.get('subject', 'Unknown')}")
                        print(f"         Score: {result.get('score', 0)}")
                        print(f"         Date: {result.get('completed_at', 'Unknown')}")
                        
                    # Check for our specific student
                    student_results = [r for r in data if r.get('student_id') == STUDENT_ID]
                    if student_results:
                        print(f"   ✅ FOUND STUDENT DATA: {len(student_results)} results for student {STUDENT_ID}")
                    else:
                        print(f"   ❌ Student {STUDENT_ID} not found in results")
                else:
                    print("   ❌ No test results found")
            else:
                text = await response.text()
                print(f"   ❌ Test results failed: {text}")
                
        # Test 3: Subject filtering
        print("\n🔍 Testing subject filtering...")
        for subject in ['math', 'general', 'physics']:
            async with self.session.get(f"{API_BASE}/teacher/analytics/test-results?subject={subject}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   {subject}: {len(data)} results")
                else:
                    print(f"   {subject}: Failed ({response.status})")
                    
        # Test 4: Class Performance
        print("\n🔍 Testing class performance...")
        async with self.session.get(f"{API_BASE}/teacher/classes", headers=headers) as response:
            if response.status == 200:
                classes = await response.json()
                if classes:
                    for cls in classes:
                        class_id = cls['class_id']
                        print(f"   Testing class: {cls['class_name']} ({class_id})")
                        
                        async with self.session.get(f"{API_BASE}/teacher/analytics/class-performance/{class_id}", headers=headers) as perf_response:
                            if perf_response.status == 200:
                                perf_data = await perf_response.json()
                                perf_summary = perf_data.get('performance_summary', {})
                                print(f"      Tests: {perf_summary.get('total_tests', 0)}")
                                print(f"      Avg Score: {perf_summary.get('average_score', 0):.2f}")
                                
                                student_perf = perf_data.get('student_performance', [])
                                print(f"      Students: {len(student_perf)}")
                            else:
                                print(f"      Failed: {perf_response.status}")
                                
    async def analyze_the_issue(self):
        """Analyze why analytics might be empty"""
        print("\n" + "="*60)
        print("🔬 ANALYZING THE ANALYTICS ISSUE")
        print("="*60)
        
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "test_database")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        try:
            # Get the new teacher's ID
            teacher_user = await db.users.find_one({"email": "analytics.teacher@test.com"})
            if teacher_user:
                new_teacher_id = teacher_user['id']
                print(f"📝 New teacher ID: {new_teacher_id}")
                
                # Check new teacher's classes
                new_teacher_classes = await db.classrooms.find({"teacher_id": new_teacher_id}).to_list(10)
                print(f"   New teacher has {len(new_teacher_classes)} classes")
                
                if new_teacher_classes:
                    class_ids = [cls['class_id'] for cls in new_teacher_classes]
                    
                    # Check students in these classes
                    students = await db.student_profiles.find({
                        "joined_classes": {"$in": class_ids}
                    }).to_list(100)
                    print(f"   Found {len(students)} students in new teacher's classes")
                    
                    if students:
                        student_ids = [s['user_id'] for s in students]
                        print(f"   Student IDs: {student_ids}")
                        
                        # Check practice attempts for these students
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
                                
                            print(f"   ✅ CONCLUSION: Analytics should show {len(attempts)} total tests")
                        else:
                            print(f"   ❌ No practice attempts found for students in new teacher's classes")
                    else:
                        print(f"   ❌ No students found in new teacher's classes")
                        
                        # Check if the student was actually added
                        student_profile = await db.student_profiles.find_one({"user_id": STUDENT_ID})
                        if student_profile:
                            print(f"   Student's joined classes: {student_profile.get('joined_classes', [])}")
                            
                            # Check if any of the new teacher's classes are in the student's joined classes
                            common = set(class_ids) & set(student_profile.get('joined_classes', []))
                            if common:
                                print(f"   ✅ Student is in teacher's classes: {list(common)}")
                            else:
                                print(f"   ❌ Student is NOT in any of teacher's classes")
                else:
                    print(f"   ❌ New teacher has no classes")
                    
        finally:
            client.close()
            
    async def run_final_test(self):
        """Run the final comprehensive test"""
        print("🚀 STARTING TEACHER ANALYTICS FINAL TEST")
        print("="*80)
        
        await self.setup_session()
        
        try:
            # Set up test environment
            class_id = await self.create_test_class_and_add_student()
            
            if class_id:
                # Test analytics endpoints
                await self.test_analytics_with_real_data()
                
            # Analyze the issue
            await self.analyze_the_issue()
            
        finally:
            await self.cleanup_session()
            
        print("\n" + "="*80)
        print("🏁 FINAL TEST COMPLETE")
        print("="*80)

async def main():
    """Main function"""
    tester = TeacherAnalyticsFinalTest()
    await tester.run_final_test()

if __name__ == "__main__":
    asyncio.run(main())
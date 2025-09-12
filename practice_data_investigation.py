#!/usr/bin/env python3
"""
Practice Test Data Storage and Retrieval Investigation
=====================================================

This script investigates why only math domain shows data in the progress tracker
while other domains don't have data. It will:

1. Check what practice test attempts exist in the database
2. Verify what subjects/domains have been tested
3. Test practice test generation for different subjects
4. Test practice test submission for different subjects
5. Verify data is being stored correctly in PRACTICE_ATTEMPTS collection
6. Test progress API endpoints
7. Check for filtering issues or subject name inconsistencies
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
BACKEND_URL = "https://learnlab-k.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

class PracticeDataInvestigator:
    def __init__(self):
        self.session = None
        self.student_token = None
        self.student_id = None
        self.db = None
        self.client = None
        
    async def setup(self):
        """Setup HTTP session and database connection"""
        self.session = aiohttp.ClientSession()
        
        # Connect to MongoDB
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
        print("🔧 Setup completed - HTTP session and database connection established")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        if self.client:
            self.client.close()
    
    async def create_test_student(self):
        """Create a test student account"""
        student_data = {
            "email": f"test_student_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com",
            "password": "TestPassword123!",
            "name": "Practice Test Student",
            "user_type": "student",
            "grade_level": "10th",
            "school_name": "Test School"
        }
        
        async with self.session.post(f"{BACKEND_URL}/auth/register", json=student_data) as response:
            if response.status == 200:
                result = await response.json()
                self.student_token = result["access_token"]
                self.student_id = result["user"]["id"]
                print(f"✅ Created test student: {student_data['email']}")
                print(f"   Student ID: {self.student_id}")
                return True
            else:
                error = await response.text()
                print(f"❌ Failed to create student: {response.status} - {error}")
                return False
    
    async def check_database_state(self):
        """Check current state of practice test data in database"""
        print("\n" + "="*60)
        print("📊 DATABASE STATE INVESTIGATION")
        print("="*60)
        
        # Check practice attempts collection
        attempts_count = await self.db.practice_attempts.count_documents({})
        print(f"📈 Total practice attempts in database: {attempts_count}")
        
        if attempts_count > 0:
            # Get all attempts
            attempts = await self.db.practice_attempts.find({}).to_list(None)
            
            # Analyze by subject
            subjects = {}
            for attempt in attempts:
                subject = attempt.get("subject", "unknown")
                if subject not in subjects:
                    subjects[subject] = {
                        "count": 0,
                        "scores": [],
                        "student_ids": set()
                    }
                subjects[subject]["count"] += 1
                subjects[subject]["scores"].append(attempt.get("score", 0))
                subjects[subject]["student_ids"].add(attempt.get("student_id", "unknown"))
            
            print("\n📋 PRACTICE ATTEMPTS BY SUBJECT:")
            for subject, data in subjects.items():
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
                print(f"   {subject.upper()}: {data['count']} attempts, avg score: {avg_score:.1f}%, {len(data['student_ids'])} students")
            
            # Show recent attempts
            recent_attempts = await self.db.practice_attempts.find({}).sort("completed_at", -1).limit(5).to_list(None)
            print("\n🕒 RECENT PRACTICE ATTEMPTS:")
            for attempt in recent_attempts:
                print(f"   {attempt.get('completed_at', 'Unknown time')}: {attempt.get('subject', 'Unknown')} - Score: {attempt.get('score', 0)}%")
        
        # Check practice questions collection
        questions_count = await self.db.practice_questions.count_documents({})
        print(f"\n❓ Total practice questions in database: {questions_count}")
        
        if questions_count > 0:
            # Analyze questions by subject
            pipeline = [
                {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            question_subjects = await self.db.practice_questions.aggregate(pipeline).to_list(None)
            
            print("\n📝 PRACTICE QUESTIONS BY SUBJECT:")
            for item in question_subjects:
                print(f"   {item['_id'].upper()}: {item['count']} questions")
    
    async def test_practice_generation_all_subjects(self):
        """Test practice test generation for all subjects"""
        print("\n" + "="*60)
        print("🧪 PRACTICE TEST GENERATION TESTING")
        print("="*60)
        
        subjects_to_test = [
            ("math", ["Algebra", "Geometry"]),
            ("physics", ["Mechanics", "Electricity"]),
            ("chemistry", ["Atomic Structure", "Organic Chemistry"]),
            ("biology", ["Cell Biology", "Genetics"]),
            ("english", ["Grammar", "Literature"])
        ]
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        generation_results = {}
        
        for subject, topics in subjects_to_test:
            print(f"\n🔬 Testing {subject.upper()} practice test generation...")
            
            test_request = {
                "subject": subject,
                "topics": topics,
                "difficulty": "medium",
                "question_count": 3,
                "question_types": ["mcq", "short_answer"]
            }
            
            try:
                async with self.session.post(
                    f"{BACKEND_URL}/practice/generate",
                    json=test_request,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        questions = result.get("questions", [])
                        print(f"   ✅ Generated {len(questions)} questions for {subject}")
                        generation_results[subject] = {
                            "success": True,
                            "questions": questions,
                            "count": len(questions)
                        }
                        
                        # Show sample question
                        if questions:
                            sample = questions[0]
                            print(f"   📝 Sample question: {sample.get('question_text', 'N/A')[:60]}...")
                    else:
                        error = await response.text()
                        print(f"   ❌ Failed to generate {subject} questions: {response.status} - {error}")
                        generation_results[subject] = {
                            "success": False,
                            "error": error,
                            "status": response.status
                        }
            except Exception as e:
                print(f"   ❌ Exception generating {subject} questions: {str(e)}")
                generation_results[subject] = {
                    "success": False,
                    "error": str(e)
                }
        
        return generation_results
    
    async def test_practice_submission_all_subjects(self, generation_results):
        """Test practice test submission for all subjects"""
        print("\n" + "="*60)
        print("📤 PRACTICE TEST SUBMISSION TESTING")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        submission_results = {}
        
        for subject, gen_result in generation_results.items():
            if not gen_result.get("success"):
                print(f"⏭️  Skipping {subject} submission - generation failed")
                continue
            
            print(f"\n📋 Testing {subject.upper()} practice test submission...")
            
            questions = gen_result["questions"]
            if not questions:
                print(f"   ⏭️  No questions to submit for {subject}")
                continue
            
            # Create sample answers
            student_answers = {}
            question_ids = []
            for question in questions:
                q_id = question["id"]
                question_ids.append(q_id)
                # Provide sample answers based on question type
                if question.get("question_type") == "mcq":
                    student_answers[q_id] = "A"  # Sample MCQ answer
                else:
                    student_answers[q_id] = "Sample answer"  # Sample text answer
            
            submission_data = {
                "questions": question_ids,
                "student_answers": student_answers,
                "time_taken": 300  # 5 minutes
            }
            
            try:
                async with self.session.post(
                    f"{BACKEND_URL}/practice/submit",
                    json=submission_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Successfully submitted {subject} test")
                        print(f"   📊 Score: {result.get('score', 0)}% ({result.get('correct_answers', 0)}/{result.get('total_questions', 0)})")
                        submission_results[subject] = {
                            "success": True,
                            "attempt_id": result.get("attempt_id"),
                            "score": result.get("score", 0)
                        }
                    else:
                        error = await response.text()
                        print(f"   ❌ Failed to submit {subject} test: {response.status} - {error}")
                        submission_results[subject] = {
                            "success": False,
                            "error": error,
                            "status": response.status
                        }
            except Exception as e:
                print(f"   ❌ Exception submitting {subject} test: {str(e)}")
                submission_results[subject] = {
                    "success": False,
                    "error": str(e)
                }
        
        return submission_results
    
    async def test_progress_apis(self):
        """Test progress API endpoints"""
        print("\n" + "="*60)
        print("📈 PROGRESS API TESTING")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Test GET /api/practice/results (all results)
        print("\n🔍 Testing GET /api/practice/results (all results)...")
        try:
            async with self.session.get(f"{BACKEND_URL}/practice/results", headers=headers) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"   ✅ Retrieved {len(results)} practice results")
                    
                    # Analyze by subject
                    subjects_found = {}
                    for result in results:
                        subject = result.get("subject", "unknown")
                        if subject not in subjects_found:
                            subjects_found[subject] = []
                        subjects_found[subject].append(result)
                    
                    print("   📊 Results by subject:")
                    for subject, subject_results in subjects_found.items():
                        avg_score = sum(r.get("score", 0) for r in subject_results) / len(subject_results)
                        print(f"      {subject.upper()}: {len(subject_results)} tests, avg: {avg_score:.1f}%")
                else:
                    error = await response.text()
                    print(f"   ❌ Failed to get all results: {response.status} - {error}")
        except Exception as e:
            print(f"   ❌ Exception getting all results: {str(e)}")
        
        # Test GET /api/practice/stats/{subject} for different subjects
        subjects_to_test = ["math", "physics", "chemistry", "biology", "english"]
        
        print("\n🔍 Testing GET /api/practice/stats/{subject} for different subjects...")
        for subject in subjects_to_test:
            try:
                async with self.session.get(f"{BACKEND_URL}/practice/stats/{subject}", headers=headers) as response:
                    if response.status == 200:
                        stats = await response.json()
                        total_tests = stats.get("total_tests", 0)
                        avg_score = stats.get("average_score", 0)
                        print(f"   📊 {subject.upper()}: {total_tests} tests, avg: {avg_score}%")
                    else:
                        error = await response.text()
                        print(f"   ❌ Failed to get {subject} stats: {response.status} - {error}")
            except Exception as e:
                print(f"   ❌ Exception getting {subject} stats: {str(e)}")
    
    async def verify_data_completeness(self):
        """Verify that practice attempts include all required fields"""
        print("\n" + "="*60)
        print("🔍 DATA COMPLETENESS VERIFICATION")
        print("="*60)
        
        attempts = await self.db.practice_attempts.find({}).to_list(None)
        
        if not attempts:
            print("❌ No practice attempts found in database")
            return
        
        print(f"📊 Analyzing {len(attempts)} practice attempts...")
        
        required_fields = ["student_id", "subject", "score", "total_questions", "completed_at"]
        field_analysis = {field: {"present": 0, "missing": 0, "values": set()} for field in required_fields}
        
        for attempt in attempts:
            for field in required_fields:
                if field in attempt and attempt[field] is not None:
                    field_analysis[field]["present"] += 1
                    if field == "subject":
                        field_analysis[field]["values"].add(attempt[field])
                else:
                    field_analysis[field]["missing"] += 1
        
        print("\n📋 FIELD COMPLETENESS ANALYSIS:")
        for field, analysis in field_analysis.items():
            total = analysis["present"] + analysis["missing"]
            percentage = (analysis["present"] / total * 100) if total > 0 else 0
            print(f"   {field}: {analysis['present']}/{total} ({percentage:.1f}%) present")
            
            if field == "subject" and analysis["values"]:
                print(f"      Subject values found: {sorted(analysis['values'])}")
        
        # Check for subject name consistency
        print("\n🔍 SUBJECT NAME CONSISTENCY CHECK:")
        subject_variations = {}
        for attempt in attempts:
            subject = attempt.get("subject", "").strip().lower()
            if subject:
                if subject not in subject_variations:
                    subject_variations[subject] = []
                subject_variations[subject].append(attempt.get("subject", ""))
        
        for normalized, variations in subject_variations.items():
            unique_variations = set(variations)
            if len(unique_variations) > 1:
                print(f"   ⚠️  Subject '{normalized}' has variations: {unique_variations}")
            else:
                print(f"   ✅ Subject '{normalized}' is consistent")
    
    async def check_frontend_backend_subject_mapping(self):
        """Check if subject names in database match what frontend expects"""
        print("\n" + "="*60)
        print("🔗 FRONTEND-BACKEND SUBJECT MAPPING CHECK")
        print("="*60)
        
        # Expected subjects from backend models
        expected_subjects = ["math", "physics", "chemistry", "biology", "english", "history", "geography"]
        
        # Get actual subjects from database
        pipeline = [
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        actual_subjects = await self.db.practice_attempts.aggregate(pipeline).to_list(None)
        actual_subject_names = [item["_id"] for item in actual_subjects if item["_id"]]
        
        print("📋 EXPECTED SUBJECTS (from backend models):")
        for subject in expected_subjects:
            print(f"   - {subject}")
        
        print(f"\n📋 ACTUAL SUBJECTS (from database):")
        for item in actual_subjects:
            print(f"   - {item['_id']}: {item['count']} attempts")
        
        print(f"\n🔍 MAPPING ANALYSIS:")
        missing_subjects = set(expected_subjects) - set(actual_subject_names)
        unexpected_subjects = set(actual_subject_names) - set(expected_subjects)
        
        if missing_subjects:
            print(f"   ⚠️  Missing subjects (expected but not found): {missing_subjects}")
        else:
            print("   ✅ All expected subjects have data")
        
        if unexpected_subjects:
            print(f"   ⚠️  Unexpected subjects (found but not expected): {unexpected_subjects}")
        else:
            print("   ✅ No unexpected subjects found")
    
    async def run_investigation(self):
        """Run the complete investigation"""
        print("🚀 STARTING PRACTICE TEST DATA INVESTIGATION")
        print("=" * 80)
        
        try:
            await self.setup()
            
            # Step 1: Check initial database state
            await self.check_database_state()
            
            # Step 2: Create test student
            if not await self.create_test_student():
                print("❌ Cannot proceed without test student")
                return
            
            # Step 3: Test practice generation for all subjects
            generation_results = await self.test_practice_generation_all_subjects()
            
            # Step 4: Test practice submission for all subjects
            submission_results = await self.test_practice_submission_all_subjects(generation_results)
            
            # Step 5: Test progress APIs
            await self.test_progress_apis()
            
            # Step 6: Check database state after tests
            print("\n" + "="*60)
            print("📊 DATABASE STATE AFTER TESTING")
            print("="*60)
            await self.check_database_state()
            
            # Step 7: Verify data completeness
            await self.verify_data_completeness()
            
            # Step 8: Check frontend-backend subject mapping
            await self.check_frontend_backend_subject_mapping()
            
            # Final summary
            print("\n" + "="*80)
            print("📋 INVESTIGATION SUMMARY")
            print("="*80)
            
            successful_generations = sum(1 for result in generation_results.values() if result.get("success"))
            successful_submissions = sum(1 for result in submission_results.values() if result.get("success"))
            
            print(f"✅ Practice test generation: {successful_generations}/{len(generation_results)} subjects successful")
            print(f"✅ Practice test submission: {successful_submissions}/{len(submission_results)} subjects successful")
            
            if successful_generations < len(generation_results):
                print("\n⚠️  GENERATION ISSUES:")
                for subject, result in generation_results.items():
                    if not result.get("success"):
                        print(f"   - {subject}: {result.get('error', 'Unknown error')}")
            
            if successful_submissions < len(submission_results):
                print("\n⚠️  SUBMISSION ISSUES:")
                for subject, result in submission_results.items():
                    if not result.get("success"):
                        print(f"   - {subject}: {result.get('error', 'Unknown error')}")
            
            print("\n🎯 CONCLUSION:")
            if successful_generations == len(generation_results) and successful_submissions == len(submission_results):
                print("   All subjects are working correctly for practice test generation and submission.")
                print("   If only math shows in progress tracker, the issue is likely in the frontend")
                print("   filtering or display logic, not in the backend data storage.")
            else:
                print("   Some subjects have issues with practice test generation or submission.")
                print("   This could explain why only certain subjects show data in the progress tracker.")
        
        except Exception as e:
            print(f"❌ Investigation failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup()

async def main():
    """Main function"""
    investigator = PracticeDataInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
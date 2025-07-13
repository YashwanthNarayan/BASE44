#!/usr/bin/env python3
"""
Practice Test Data Analysis - Root Cause Investigation
=====================================================

Based on initial database investigation, I found:
- 151 total practice attempts in database
- 140 attempts have subject "UNKNOWN" (92.7%)
- Only 11 attempts have subject "math" (7.3%)

This explains why only math shows in progress tracker!

Root Cause Analysis:
The issue is that most practice attempts are being stored with subject "UNKNOWN"
instead of the actual subject name. This suggests a problem in the practice
test submission process where the subject field is not being properly set.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Configuration
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

class PracticeDataAnalyzer:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def setup(self):
        """Setup database connection"""
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        print("🔧 Database connection established")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            self.client.close()
    
    async def analyze_unknown_subject_issue(self):
        """Analyze why most attempts have subject 'UNKNOWN'"""
        print("\n" + "="*60)
        print("🔍 ANALYZING 'UNKNOWN' SUBJECT ISSUE")
        print("="*60)
        
        # Get all attempts with UNKNOWN subject
        unknown_attempts = await self.db.practice_attempts.find({"subject": "unknown"}).to_list(None)
        print(f"📊 Found {len(unknown_attempts)} attempts with subject 'unknown'")
        
        if unknown_attempts:
            # Analyze the structure of unknown attempts
            sample_attempt = unknown_attempts[0]
            print(f"\n📋 SAMPLE 'UNKNOWN' ATTEMPT STRUCTURE:")
            for key, value in sample_attempt.items():
                if key == "_id":
                    continue
                if isinstance(value, list) and len(value) > 3:
                    print(f"   {key}: [{len(value)} items] - {value[:2]}...")
                elif isinstance(value, dict) and len(str(value)) > 100:
                    print(f"   {key}: {{dict with {len(value)} keys}}")
                else:
                    print(f"   {key}: {value}")
            
            # Check if these attempts have questions associated
            if "questions" in sample_attempt:
                question_ids = sample_attempt["questions"]
                if question_ids:
                    print(f"\n🔍 CHECKING ASSOCIATED QUESTIONS:")
                    questions = await self.db.practice_questions.find({
                        "id": {"$in": question_ids[:3]}  # Check first 3 questions
                    }).to_list(None)
                    
                    if questions:
                        print(f"   Found {len(questions)} associated questions")
                        for q in questions:
                            print(f"   Question subject: {q.get('subject', 'NOT SET')}")
                            print(f"   Question topic: {q.get('topic', 'NOT SET')}")
                    else:
                        print("   ❌ No associated questions found in database")
        
        # Compare with math attempts
        math_attempts = await self.db.practice_attempts.find({"subject": "math"}).to_list(None)
        print(f"\n📊 Found {len(math_attempts)} attempts with subject 'math'")
        
        if math_attempts:
            sample_math = math_attempts[0]
            print(f"\n📋 SAMPLE 'MATH' ATTEMPT STRUCTURE:")
            for key, value in sample_math.items():
                if key == "_id":
                    continue
                if isinstance(value, list) and len(value) > 3:
                    print(f"   {key}: [{len(value)} items] - {value[:2]}...")
                elif isinstance(value, dict) and len(str(value)) > 100:
                    print(f"   {key}: {{dict with {len(value)} keys}}")
                else:
                    print(f"   {key}: {value}")
    
    async def analyze_question_subject_distribution(self):
        """Analyze the subject distribution in practice questions"""
        print("\n" + "="*60)
        print("📝 PRACTICE QUESTIONS SUBJECT ANALYSIS")
        print("="*60)
        
        # Get subject distribution from questions
        pipeline = [
            {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        question_subjects = await self.db.practice_questions.aggregate(pipeline).to_list(None)
        
        print("📊 QUESTIONS BY SUBJECT:")
        total_questions = 0
        for item in question_subjects:
            print(f"   {item['_id'].upper()}: {item['count']} questions")
            total_questions += item['count']
        
        print(f"\n📈 Total questions: {total_questions}")
        
        # Check if questions have proper subject field
        sample_questions = await self.db.practice_questions.find({}).limit(5).to_list(None)
        print(f"\n🔍 SAMPLE QUESTION STRUCTURES:")
        for i, q in enumerate(sample_questions, 1):
            print(f"   Question {i}:")
            print(f"      Subject: {q.get('subject', 'NOT SET')}")
            print(f"      Topic: {q.get('topic', 'NOT SET')}")
            print(f"      ID: {q.get('id', 'NOT SET')}")
    
    async def investigate_subject_assignment_logic(self):
        """Investigate how subjects are assigned during practice test submission"""
        print("\n" + "="*60)
        print("🔬 SUBJECT ASSIGNMENT LOGIC INVESTIGATION")
        print("="*60)
        
        # Find attempts that have questions and analyze the subject assignment
        attempts_with_questions = await self.db.practice_attempts.find({
            "questions": {"$exists": True, "$ne": []}
        }).limit(10).to_list(None)
        
        print(f"📊 Analyzing {len(attempts_with_questions)} attempts with questions...")
        
        subject_assignment_analysis = {
            "correct_assignment": 0,
            "incorrect_assignment": 0,
            "missing_questions": 0,
            "examples": []
        }
        
        for attempt in attempts_with_questions:
            attempt_subject = attempt.get("subject", "unknown")
            question_ids = attempt.get("questions", [])
            
            if not question_ids:
                subject_assignment_analysis["missing_questions"] += 1
                continue
            
            # Get the first question to check its subject
            first_question = await self.db.practice_questions.find_one({"id": question_ids[0]})
            
            if first_question:
                question_subject = first_question.get("subject", "unknown")
                
                if attempt_subject == question_subject:
                    subject_assignment_analysis["correct_assignment"] += 1
                else:
                    subject_assignment_analysis["incorrect_assignment"] += 1
                    subject_assignment_analysis["examples"].append({
                        "attempt_id": attempt.get("id", "unknown"),
                        "attempt_subject": attempt_subject,
                        "question_subject": question_subject,
                        "completed_at": attempt.get("completed_at", "unknown")
                    })
        
        print(f"\n📋 SUBJECT ASSIGNMENT ANALYSIS:")
        print(f"   ✅ Correct assignments: {subject_assignment_analysis['correct_assignment']}")
        print(f"   ❌ Incorrect assignments: {subject_assignment_analysis['incorrect_assignment']}")
        print(f"   ⚠️  Missing questions: {subject_assignment_analysis['missing_questions']}")
        
        if subject_assignment_analysis["examples"]:
            print(f"\n🔍 EXAMPLES OF INCORRECT ASSIGNMENTS:")
            for example in subject_assignment_analysis["examples"][:3]:
                print(f"   Attempt: {example['attempt_id']}")
                print(f"      Attempt subject: {example['attempt_subject']}")
                print(f"      Question subject: {example['question_subject']}")
                print(f"      Date: {example['completed_at']}")
    
    async def check_backend_code_logic(self):
        """Analyze the backend code logic for subject assignment"""
        print("\n" + "="*60)
        print("💻 BACKEND CODE LOGIC ANALYSIS")
        print("="*60)
        
        print("📋 ANALYZING PRACTICE SUBMISSION LOGIC:")
        print("   From /app/backend/routes/practice.py line 119:")
        print('   "subject": questions[0]["subject"] if questions else "general"')
        print("")
        print("🔍 POTENTIAL ISSUES:")
        print("   1. If questions array is empty, subject defaults to 'general'")
        print("   2. Subject is taken from first question only")
        print("   3. If first question doesn't have subject field, it could be None/undefined")
        print("   4. Case sensitivity issues (backend expects lowercase, questions might have uppercase)")
        print("")
        print("🎯 ROOT CAUSE HYPOTHESIS:")
        print("   The 'unknown' subject in attempts suggests that:")
        print("   - questions[0]['subject'] is returning 'unknown' or None")
        print("   - There's a mismatch between question generation and storage")
        print("   - Questions are being generated with proper subjects but stored incorrectly")
    
    async def propose_solution(self):
        """Propose solution based on analysis"""
        print("\n" + "="*60)
        print("💡 PROPOSED SOLUTION")
        print("="*60)
        
        print("🔧 IMMEDIATE FIXES NEEDED:")
        print("   1. Fix subject assignment in practice test submission")
        print("   2. Ensure questions are stored with correct subject field")
        print("   3. Add validation to prevent 'unknown' subjects")
        print("   4. Update existing 'unknown' attempts with correct subjects")
        print("")
        print("📝 CODE CHANGES REQUIRED:")
        print("   1. In practice.py submit endpoint:")
        print("      - Add validation for question subjects")
        print("      - Handle case where questions[0]['subject'] is None/undefined")
        print("      - Add logging to track subject assignment")
        print("")
        print("   2. In AI service question generation:")
        print("      - Ensure all generated questions have proper subject field")
        print("      - Add validation before storing questions")
        print("")
        print("   3. Database cleanup:")
        print("      - Update existing 'unknown' attempts with correct subjects")
        print("      - Add database constraints to prevent future issues")
    
    async def run_analysis(self):
        """Run the complete analysis"""
        print("🚀 STARTING PRACTICE TEST DATA ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        try:
            await self.setup()
            
            await self.analyze_unknown_subject_issue()
            await self.analyze_question_subject_distribution()
            await self.investigate_subject_assignment_logic()
            await self.check_backend_code_logic()
            await self.propose_solution()
            
            print("\n" + "="*80)
            print("🎯 CONCLUSION")
            print("="*80)
            print("ROOT CAUSE IDENTIFIED: Most practice attempts are stored with subject 'unknown'")
            print("instead of the actual subject. This is why only math (11 attempts) shows in")
            print("the progress tracker while 140 'unknown' attempts are ignored.")
            print("")
            print("IMPACT: 92.7% of practice test data is not showing in progress tracker")
            print("due to incorrect subject assignment during test submission.")
            print("")
            print("NEXT STEPS: Fix the subject assignment logic in practice test submission")
            print("and update existing 'unknown' attempts with correct subjects.")
        
        except Exception as e:
            print(f"❌ Analysis failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.cleanup()

async def main():
    """Main function"""
    analyzer = PracticeDataAnalyzer()
    await analyzer.run_analysis()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
DATABASE INVESTIGATION: Practice API Endpoints
Investigating the actual database state to understand if there are data conditions
that might cause 500 errors in the practice endpoints.
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio

# Load environment variables
load_dotenv('/app/backend/.env')

# Get database connection details
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Get API URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

print(f"🔍 DATABASE INVESTIGATION: Practice API Endpoints")
print(f"Database: {MONGO_URL}/{DB_NAME}")
print(f"API URL: {API_URL}")
print("=" * 80)

class DatabaseInvestigator:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect_to_database(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {str(e)}")
            return False
    
    async def investigate_practice_attempts_collection(self):
        """Investigate the PRACTICE_ATTEMPTS collection"""
        print("\n🔍 INVESTIGATING PRACTICE_ATTEMPTS COLLECTION")
        
        try:
            collection = self.db["PRACTICE_ATTEMPTS"]
            
            # Get total count
            total_count = await collection.count_documents({})
            print(f"Total practice attempts: {total_count}")
            
            if total_count == 0:
                print("⚠️ No practice attempts found in database")
                return
            
            # Get sample documents
            sample_docs = await collection.find({}).limit(5).to_list(None)
            
            print(f"\nSample documents structure:")
            for i, doc in enumerate(sample_docs):
                print(f"\nDocument {i+1}:")
                print(f"  ID: {doc.get('id', 'MISSING')}")
                print(f"  Student ID: {doc.get('student_id', 'MISSING')}")
                print(f"  Subject: {doc.get('subject', 'MISSING')}")
                print(f"  Score: {doc.get('score', 'MISSING')}")
                print(f"  Total Questions: {doc.get('total_questions', 'MISSING')}")
                print(f"  Completed At: {doc.get('completed_at', 'MISSING')}")
                print(f"  Fields: {list(doc.keys())}")
            
            # Check for NULL subjects (the issue mentioned in test_result.md)
            null_subject_count = await collection.count_documents({
                "$or": [
                    {"subject": {"$exists": False}},
                    {"subject": None},
                    {"subject": ""}
                ]
            })
            
            print(f"\nNULL subject analysis:")
            print(f"  Attempts with NULL/missing subjects: {null_subject_count}")
            print(f"  Attempts with valid subjects: {total_count - null_subject_count}")
            
            if null_subject_count > 0:
                print(f"  🚨 POTENTIAL ISSUE: {null_subject_count} attempts have NULL subjects")
                print(f"  This could cause issues in subject-based queries")
            
            # Check subject distribution
            pipeline = [
                {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            subject_distribution = await collection.aggregate(pipeline).to_list(None)
            print(f"\nSubject distribution:")
            for item in subject_distribution:
                subject = item["_id"] if item["_id"] is not None else "NULL"
                count = item["count"]
                print(f"  {subject}: {count} attempts")
            
            # Check for missing required fields
            print(f"\nField completeness check:")
            required_fields = ["id", "student_id", "subject", "score", "total_questions", "completed_at"]
            
            for field in required_fields:
                missing_count = await collection.count_documents({field: {"$exists": False}})
                null_count = await collection.count_documents({field: None})
                print(f"  {field}: {missing_count} missing, {null_count} null")
                
                if missing_count > 0 or null_count > 0:
                    print(f"    🚨 POTENTIAL ISSUE: {field} has missing/null values")
            
        except Exception as e:
            print(f"❌ Error investigating PRACTICE_ATTEMPTS: {str(e)}")
    
    async def test_with_existing_data(self):
        """Test API endpoints with existing database data"""
        print("\n🔍 TESTING WITH EXISTING DATABASE DATA")
        
        try:
            collection = self.db["PRACTICE_ATTEMPTS"]
            
            # Get a sample of existing attempts
            existing_attempts = await collection.find({}).limit(3).to_list(None)
            
            if not existing_attempts:
                print("⚠️ No existing attempts to test with")
                return
            
            print(f"Found {len(existing_attempts)} existing attempts to test with")
            
            # Try to find a student with existing data
            for attempt in existing_attempts:
                student_id = attempt.get("student_id")
                attempt_id = attempt.get("id")
                subject = attempt.get("subject")
                
                if not student_id:
                    print(f"⚠️ Attempt {attempt_id} has no student_id")
                    continue
                
                print(f"\nTesting with existing data:")
                print(f"  Student ID: {student_id}")
                print(f"  Attempt ID: {attempt_id}")
                print(f"  Subject: {subject}")
                
                # We can't test with existing student tokens since we don't have them
                # But we can check if the data structure would cause issues
                
                # Check for data integrity issues
                issues = []
                
                if not attempt_id:
                    issues.append("Missing attempt ID")
                
                if not student_id:
                    issues.append("Missing student ID")
                
                if subject is None or subject == "":
                    issues.append("NULL/empty subject")
                
                if "score" not in attempt:
                    issues.append("Missing score")
                
                if "total_questions" not in attempt:
                    issues.append("Missing total_questions")
                
                if "completed_at" not in attempt:
                    issues.append("Missing completed_at")
                
                if issues:
                    print(f"  🚨 DATA INTEGRITY ISSUES FOUND:")
                    for issue in issues:
                        print(f"    - {issue}")
                    print(f"  These issues could cause 500 errors in API endpoints!")
                else:
                    print(f"  ✅ Data structure looks good")
                
        except Exception as e:
            print(f"❌ Error testing with existing data: {str(e)}")
    
    async def check_database_indexes(self):
        """Check if proper database indexes exist"""
        print("\n🔍 CHECKING DATABASE INDEXES")
        
        try:
            collection = self.db["PRACTICE_ATTEMPTS"]
            
            indexes = await collection.list_indexes().to_list(None)
            
            print(f"Existing indexes:")
            for index in indexes:
                print(f"  {index.get('name', 'unnamed')}: {index.get('key', {})}")
            
            # Check if we have indexes on commonly queried fields
            index_fields = [idx.get('key', {}) for idx in indexes]
            
            important_fields = ['student_id', 'subject', 'completed_at']
            
            for field in important_fields:
                has_index = any(field in idx_key for idx_key in index_fields)
                if has_index:
                    print(f"  ✅ Index exists for {field}")
                else:
                    print(f"  ⚠️ No index for {field} (could cause performance issues)")
            
        except Exception as e:
            print(f"❌ Error checking indexes: {str(e)}")
    
    async def run_investigation(self):
        """Run the complete database investigation"""
        print("🔍 DATABASE INVESTIGATION: Practice API Endpoints")
        print("Investigating database state for potential causes of 500 errors")
        print("=" * 80)
        
        if not await self.connect_to_database():
            return
        
        await self.investigate_practice_attempts_collection()
        await self.test_with_existing_data()
        await self.check_database_indexes()
        
        print("\n" + "=" * 80)
        print("🔍 DATABASE INVESTIGATION COMPLETED")
        print("Check above for any data integrity issues that could cause 500 errors")
        print("=" * 80)
        
        if self.client:
            self.client.close()

async def main():
    investigator = DatabaseInvestigator()
    await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())
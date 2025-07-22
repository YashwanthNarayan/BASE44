#!/usr/bin/env python3
"""
COMPREHENSIVE DATABASE SCAN: All Collections
Scanning all collections in the database to find practice test data
"""

import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

print(f"🔍 COMPREHENSIVE DATABASE SCAN")
print(f"Database: {MONGO_URL}/{DB_NAME}")
print("=" * 80)

async def scan_all_collections():
    """Scan all collections in the database"""
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # List all collections
        collections = await db.list_collection_names()
        print(f"Found {len(collections)} collections:")
        
        for collection_name in collections:
            print(f"\n📁 Collection: {collection_name}")
            
            collection = db[collection_name]
            count = await collection.count_documents({})
            print(f"   Documents: {count}")
            
            if count > 0:
                # Get a sample document to understand structure
                sample = await collection.find_one({})
                if sample:
                    print(f"   Sample fields: {list(sample.keys())}")
                    
                    # Check if this might be practice test related
                    practice_indicators = ['practice', 'test', 'attempt', 'score', 'question', 'subject']
                    has_practice_fields = any(indicator in str(sample.keys()).lower() for indicator in practice_indicators)
                    
                    if has_practice_fields:
                        print(f"   🎯 POTENTIAL PRACTICE DATA FOUND!")
                        
                        # Show more details for practice-related collections
                        if 'subject' in sample:
                            print(f"   Subject: {sample.get('subject')}")
                        if 'score' in sample:
                            print(f"   Score: {sample.get('score')}")
                        if 'student_id' in sample:
                            print(f"   Student ID: {sample.get('student_id')}")
                        if 'completed_at' in sample:
                            print(f"   Completed: {sample.get('completed_at')}")
                            
                        # Check for NULL subjects in this collection
                        null_subjects = await collection.count_documents({
                            "$or": [
                                {"subject": {"$exists": False}},
                                {"subject": None},
                                {"subject": ""}
                            ]
                        })
                        
                        if null_subjects > 0:
                            print(f"   🚨 NULL SUBJECTS: {null_subjects}/{count} documents")
                        else:
                            print(f"   ✅ All documents have valid subjects")
            else:
                print(f"   (Empty collection)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error scanning database: {str(e)}")

if __name__ == "__main__":
    asyncio.run(scan_all_collections())
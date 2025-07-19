from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "air_project_k")

# Global database client
client = None
db = None

async def connect_to_database():
    """Initialize database connection"""
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"Connected to MongoDB database: {DB_NAME}")

async def close_database_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db

# Custom JSON encoder for MongoDB ObjectId
def convert_objectid_to_str(data):
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

# Database collection helpers
class Collections:
    """Database collection names"""
    USERS = "users"
    STUDENT_PROFILES = "student_profiles"
    TEACHER_PROFILES = "teacher_profiles"
    CLASSROOMS = "classrooms"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"
    PRACTICE_QUESTIONS = "practice_questions"
    PRACTICE_ATTEMPTS = "practice_attempts"
    STUDENT_QUESTION_HISTORY = "student_question_history"
    STUDENT_NOTES = "student_notes"
    CALENDAR_EVENTS = "calendar_events"
    MINDFULNESS_ACTIVITIES = "mindfulness_activities"
    NOTIFICATIONS = "notifications"
    STUDY_PLANS = "study_plans"
    SCHEDULED_TESTS = "scheduled_tests"

async def create_indexes():
    """Create database indexes for better performance"""
    # User indexes
    await db[Collections.USERS].create_index("email", unique=True)
    await db[Collections.USERS].create_index("user_type")
    
    # Profile indexes
    await db[Collections.STUDENT_PROFILES].create_index("user_id", unique=True)
    await db[Collections.TEACHER_PROFILES].create_index("user_id", unique=True)
    
    # Classroom indexes
    await db[Collections.CLASSROOMS].create_index("join_code", unique=True)
    await db[Collections.CLASSROOMS].create_index("teacher_id")
    
    # Chat indexes
    await db[Collections.CHAT_SESSIONS].create_index([("user_id", 1), ("subject", 1)])
    await db[Collections.CHAT_MESSAGES].create_index("session_id")
    
    # Practice test indexes
    await db[Collections.PRACTICE_QUESTIONS].create_index([("subject", 1), ("topic", 1)])
    await db[Collections.PRACTICE_ATTEMPTS].create_index("student_id")
    
    # Content indexes
    await db[Collections.STUDENT_NOTES].create_index("user_id")
    await db[Collections.CALENDAR_EVENTS].create_index([("user_id", 1), ("start_time", 1)])
    await db[Collections.NOTIFICATIONS].create_index([("user_id", 1), ("created_at", -1)])
    
    # Study planner indexes
    await db[Collections.STUDY_PLANS].create_index([("user_id", 1), ("created_at", -1)])
    await db[Collections.STUDY_PLANS].create_index("plan_id", unique=True)
    
    print("Database indexes created successfully")
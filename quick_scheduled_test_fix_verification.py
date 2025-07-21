#!/usr/bin/env python3
"""
QUICK SCHEDULED TEST COMPLETION FIX VERIFICATION
===============================================

Quick test to verify the key fix is working:
- POST request body {"score": 85.5} is accepted
- Returns 200 OK instead of 422 Unprocessable Entity
"""

import asyncio
import aiohttp
import json
import uuid

API_BASE = "http://localhost:8001"

async def quick_test():
    """Quick test of the fix"""
    print("🚀 QUICK SCHEDULED TEST COMPLETION FIX VERIFICATION")
    print("=" * 60)
    
    session = aiohttp.ClientSession()
    
    try:
        # Register student
        student_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123!",
            "name": "Test Student",
            "user_type": "student"
        }
        
        async with session.post(f"{API_BASE}/api/auth/register", json=student_data) as response:
            if response.status == 200:
                register_data = await response.json()
                token = register_data.get("access_token")
                print("✅ Student registered successfully")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test the FIXED endpoint directly
                test_id = "test-id-123"  # Use fake ID to test format
                completion_data = {"score": 85.5}
                
                print(f"\n🎯 Testing POST /api/practice-scheduler/complete-scheduled-test/{test_id}")
                print(f"Request body: {json.dumps(completion_data)}")
                
                async with session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                       json=completion_data, headers=headers) as response:
                    response_text = await response.text()
                    
                    print(f"Response status: {response.status}")
                    print(f"Response body: {response_text}")
                    
                    if response.status == 404:
                        print("✅ SUCCESS: 404 (test not found) means request format is accepted")
                        print("✅ The CompleteTestRequest Pydantic model is working")
                        print("✅ No 422 Unprocessable Entity error")
                    elif response.status == 422:
                        print("❌ FAILURE: Still getting 422 Unprocessable Entity")
                        print("❌ The fix is not working")
                    elif response.status == 200:
                        print("✅ SUCCESS: 200 OK - request format accepted")
                    else:
                        print(f"⚠️  Unexpected status: {response.status}")
                
                # Test wrong format for comparison
                print(f"\n🔍 Testing wrong format (query parameter):")
                async with session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}?score=85.5", 
                                       headers=headers) as response:
                    response_text = await response.text()
                    
                    print(f"Response status: {response.status}")
                    
                    if response.status == 422:
                        print("✅ SUCCESS: 422 error correctly rejects query parameter format")
                    else:
                        print(f"⚠️  Unexpected: Should reject query parameter format")
                
                # Test empty body
                print(f"\n🔍 Testing empty request body:")
                async with session.post(f"{API_BASE}/api/practice-scheduler/complete-scheduled-test/{test_id}", 
                                       json={}, headers=headers) as response:
                    response_text = await response.text()
                    
                    print(f"Response status: {response.status}")
                    
                    if response.status == 422 and "score" in response_text:
                        print("✅ SUCCESS: 422 error correctly requires score field")
                    else:
                        print(f"⚠️  Unexpected: Should require score field")
                
            else:
                print(f"❌ Failed to register student: {response.status}")
    
    finally:
        await session.close()
    
    print(f"\n📊 CONCLUSION:")
    print("If you see '✅ SUCCESS: 404 (test not found) means request format is accepted'")
    print("Then the fix is working correctly!")

if __name__ == "__main__":
    asyncio.run(quick_test())
#!/usr/bin/env python3
"""
Script to delete 261 users from the Samastu database
Targets users with @samastu.com email addresses (test users)
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def delete_users():
    """Delete 261 test users from the database"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 60)
    print("DELETING 261 USERS FROM SAMASTU DATABASE")
    print("=" * 60)
    print()
    
    # Get current user count
    total_users = await db.users.count_documents({})
    print(f"📊 Current total users: {total_users}")
    
    # Find test users (emails with @samastu.com)
    test_users = await db.users.find(
        {"email": {"$regex": "@samastu.com$"}},
        {"_id": 0, "id": 1, "email": 1, "name": 1}
    ).to_list(1000)
    
    print(f"📧 Found {len(test_users)} test users with @samastu.com email")
    
    if len(test_users) < 261:
        print(f"⚠️  Warning: Only {len(test_users)} test users available, will delete all of them")
        users_to_delete = test_users
    else:
        # Delete first 261 test users
        users_to_delete = test_users[:261]
    
    print(f"🗑️  Deleting {len(users_to_delete)} users...")
    print()
    
    # Delete users and their associated data
    deleted_count = 0
    for i, user in enumerate(users_to_delete, 1):
        user_id = user['id']
        
        try:
            # Delete user
            await db.users.delete_one({"id": user_id})
            
            # Delete associated data
            await db.progress.delete_many({"user_id": user_id})
            await db.workout_sessions.delete_many({"user_id": user_id})
            await db.scheduled_workouts.delete_many({"user_id": user_id})
            await db.ai_workout_plans.delete_many({"user_id": user_id})
            
            deleted_count += 1
            
            if i % 50 == 0:
                print(f"✅ Deleted {i}/{len(users_to_delete)} users...")
        
        except Exception as e:
            print(f"❌ Error deleting user {user['email']}: {str(e)}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Get final user count
    final_count = await db.users.count_documents({})
    
    print(f"✅ Successfully deleted: {deleted_count} users")
    print(f"📊 Previous total: {total_users} users")
    print(f"📊 Current total: {final_count} users")
    print(f"📉 Reduction: {total_users - final_count} users")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(delete_users())

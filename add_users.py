#!/usr/bin/env python3
"""
Script to add 200 users to the Samastu database
"""

import requests
import random
from faker import Faker

fake = Faker()

BASE_URL = "https://fitgame-app-1.preview.emergentagent.com/api"

def create_user(index):
    """Create a single user"""
    # Generate realistic user data
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    user_data = {
        "email": f"user{index}_{first_name.lower()}.{last_name.lower()}@samastu.com",
        "password": "FitnessUser123!",
        "name": f"{first_name} {last_name}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ User {index}/200: {user_data['name']} created")
            return True
        else:
            print(f"❌ User {index}/200 failed: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ User {index}/200 error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("ADDING 200 USERS TO SAMASTU DATABASE")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for i in range(1, 201):
        if create_user(i):
            success_count += 1
        else:
            fail_count += 1
        
        # Small delay to avoid overwhelming the server
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/200 users processed ---\n")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully created: {success_count} users")
    print(f"❌ Failed: {fail_count} users")
    print(f"📊 Total: {success_count + fail_count} users")
    print("=" * 60)

if __name__ == "__main__":
    main()

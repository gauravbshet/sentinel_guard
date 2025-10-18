#!/usr/bin/env python3
"""
Test MongoDB connection for SentinelGuard AI
Run this to verify your local MongoDB is working
"""

from app.database import get_db, test_connection
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def main():
    print("🧪 Testing MongoDB Connection...")
    print("=" * 50)

    try:
        # Test connection
        success = await test_connection()

        if success:
            print("\n📊 Testing Supabase operations...")
            db = get_db()

            # Use a test table name 'test_collection' (create the table in Supabase if needed)
            table = db.table("test_collection")

            # Test inserting a test document
            test_doc = {
                "test": True,
                "message": "SentinelGuard AI connection test",
                "timestamp": "2024-01-01T00:00:00Z"
            }

            result = await table.insert_one(test_doc)
            print(f"✅ Test document inserted with ID: {result.inserted_id}")

            # Clean up test document
            await table.delete_one({"_id": result.inserted_id})
            print("🧹 Test document cleaned up")

            print("\n🎉 Supabase connection test PASSED!")
            print("✅ Your Supabase database is ready for SentinelGuard AI!")

        else:
            print("\n❌ Supabase connection test FAILED!")
            print("🔧 Please check:")
            print("   1. SUPABASE_URL and SUPABASE_KEY are set in .env or environment")
            print("   2. Your Supabase project is reachable")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("🔧 Make sure MongoDB is running and accessible")

if __name__ == "__main__":
    asyncio.run(main())

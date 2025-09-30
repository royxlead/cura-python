#!/usr/bin/env python3
"""
Simple database connection test script
Run this to verify MongoDB connection before starting the main server
"""

import asyncio
import sys
from app.core.database import DatabaseManager
from app.core.config import settings

async def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    print(f"MongoDB URL: {settings.mongodb_url[:50]}...")
    
    db_manager = DatabaseManager()
    
    try:
        await db_manager.connect()
        print("✅ Database connection successful!")
        
        # Test health check
        health = await db_manager.health_check()
        print(f"✅ Health check passed: {health}")
        
        await db_manager.disconnect()
        print("✅ Database disconnected cleanly")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
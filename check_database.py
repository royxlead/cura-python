#!/usr/bin/env python3
"""
Quick MongoDB connection troubleshooting guide and test
"""

import asyncio
import socket
from app.core.database import DatabaseManager
from app.core.config import settings

async def main():
    print("🔧 MongoDB Connection Troubleshooting")
    print("=" * 50)
    
    # Check DNS resolution
    print("1️⃣ Testing DNS resolution...")
    try:
        hostname = "cura.6oiwqd2.mongodb.net"
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip}")
        dns_ok = True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print("💡 Possible solutions:")
        print("   - Check internet connectivity")
        print("   - Try using Google DNS (8.8.8.8, 8.8.4.4)")
        print("   - Check firewall/antivirus settings")
        print("   - Try connecting from a different network")
        dns_ok = False
    
    # Test database connection
    print(f"\n2️⃣ Testing database connection...")
    if not dns_ok:
        print("⚠️  Skipping Atlas connection test due to DNS issues")
        print("📝 Will use development fallback instead")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        
        health = await db_manager.health_check()
        print(f"✅ Database connected successfully!")
        print(f"📊 Health status: {health}")
        
        if health.get('mode') == 'development':
            print("\n⚠️  IMPORTANT: Running in development mode!")
            print("📝 This means:")
            print("   - Data is stored in memory only")
            print("   - Data will be lost when server restarts")
            print("   - Some features may not work as expected")
            print("\n💡 To fix MongoDB Atlas connection:")
            print("   1. Check your internet connection")
            print("   2. Verify MongoDB Atlas cluster is running")
            print("   3. Check network access whitelist in Atlas")
            print("   4. Verify credentials in .env file")
        
        await db_manager.disconnect()
        
    except Exception as e:
        print(f"❌ Database connection failed completely: {e}")
        return False
    
    print(f"\n🚀 You can now start the server with: python run_server.py")
    return True

if __name__ == "__main__":
    asyncio.run(main())
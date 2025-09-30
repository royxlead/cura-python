#!/usr/bin/env python3
"""
Detailed MongoDB Atlas connection diagnostic tool
This will help identify the specific issue with MongoDB Atlas connection
"""

import asyncio
import sys
import ssl
import socket
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
from app.core.config import settings

async def test_mongodb_atlas():
    """Comprehensive MongoDB Atlas connection test"""
    print("🔍 MongoDB Atlas Connection Diagnostics")
    print("=" * 50)
    
    # Extract connection details
    mongodb_url = settings.mongodb_url
    print(f"📍 Connection URL: {mongodb_url[:50]}...")
    
    # Test 1: Basic network connectivity
    print("\n1️⃣ Testing network connectivity...")
    try:
        hostname = "cura.6oiwqd2.mongodb.net"
        port = 27017
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print("✅ Network connectivity: OK")
        else:
            print(f"❌ Network connectivity: FAILED (Error code: {result})")
            return False
    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False
    
    # Test 2: SSL/TLS connectivity
    print("\n2️⃣ Testing SSL/TLS connectivity...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print("✅ SSL/TLS connectivity: OK")
                print(f"📋 SSL version: {ssock.version()}")
    except Exception as e:
        print(f"❌ SSL/TLS connectivity: FAILED - {e}")
    
    # Test 3: MongoDB connection with different configurations
    print("\n3️⃣ Testing MongoDB connection configurations...")
    
    configs = [
        {
            "name": "Standard configuration",
            "params": {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
                "socketTimeoutMS": 5000,
            }
        },
        {
            "name": "With retryWrites disabled",
            "params": {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
                "socketTimeoutMS": 5000,
                "retryWrites": False
            }
        },
        {
            "name": "With TLS settings",
            "params": {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
                "socketTimeoutMS": 5000,
                "tls": True,
                "tlsAllowInvalidCertificates": True
            }
        },
        {
            "name": "Minimal configuration",
            "params": {
                "serverSelectionTimeoutMS": 10000,
            }
        }
    ]
    
    for config in configs:
        print(f"\n🔧 Testing: {config['name']}")
        try:
            client = AsyncIOMotorClient(mongodb_url, **config['params'])
            
            # Test connection
            await asyncio.wait_for(
                client.admin.command('ping'),
                timeout=10.0
            )
            
            print(f"✅ {config['name']}: SUCCESS")
            
            # Get server info
            server_info = await client.admin.command('buildInfo')
            print(f"📊 MongoDB version: {server_info.get('version', 'Unknown')}")
            
            # Test database access
            db = client[settings.mongo_database]
            collections = await db.list_collection_names()
            print(f"📁 Database accessible, collections: {len(collections)}")
            
            client.close()
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ {config['name']}: TIMEOUT")
        except ServerSelectionTimeoutError as e:
            print(f"❌ {config['name']}: SERVER SELECTION TIMEOUT - {e}")
        except ConnectionFailure as e:
            print(f"❌ {config['name']}: CONNECTION FAILURE - {e}")
        except ConfigurationError as e:
            print(f"❌ {config['name']}: CONFIGURATION ERROR - {e}")
        except Exception as e:
            print(f"❌ {config['name']}: UNEXPECTED ERROR - {e}")
    
    # Test 4: Check MongoDB Atlas IP whitelist
    print("\n4️⃣ Testing IP whitelist configuration...")
    try:
        import requests
        response = requests.get('https://httpbin.org/ip', timeout=10)
        public_ip = response.json()['origin']
        print(f"🌐 Your public IP: {public_ip}")
        print("💡 Ensure this IP is whitelisted in MongoDB Atlas Network Access")
    except Exception as e:
        print(f"❓ Could not determine public IP: {e}")
    
    print("\n" + "=" * 50)
    print("❌ All MongoDB Atlas connection attempts failed")
    print("\n💡 Possible solutions:")
    print("1. Check MongoDB Atlas cluster status")
    print("2. Verify network access whitelist (add 0.0.0.0/0 for testing)")
    print("3. Check username/password credentials")
    print("4. Verify cluster endpoint URL")
    print("5. Check firewall/antivirus blocking connections")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_mongodb_atlas())
    sys.exit(0 if success else 1)
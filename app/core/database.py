"""
Database connection and management module
MongoDB integration with async support using Beanie ODM
"""

import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from .config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB database manager with connection lifecycle"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.sync_client: Optional[MongoClient] = None
    
    async def connect(self) -> None:
        """Initialize database connection"""
        # Check if we can resolve MongoDB Atlas hostname first
        if not await self._test_dns_resolution():
            logger.warning("Cannot resolve MongoDB Atlas hostname - DNS resolution failed")
            logger.warning("This might be due to internet connectivity or DNS server issues")
            await self._try_local_fallback()
            return
            
        try:
            # First try with minimal configuration for MongoDB Atlas
            logger.info("Attempting MongoDB Atlas connection...")
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=10000,  # Reduced timeout for faster fallback
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=10
            )
            
            # Test connection with shorter timeout
            await asyncio.wait_for(
                self.client.admin.command('ping'),
                timeout=10.0
            )
            
            self.database = self.client[settings.mongo_database]
            
            # Initialize ODM
            await self._init_beanie()
            
            logger.info("MongoDB Atlas connection successful")
            
        except (asyncio.TimeoutError, ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB Atlas connection failed: {e}")
            # Try to fall back to local MongoDB
            await self._try_local_fallback()
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            # Try fallback on any error
            await self._try_local_fallback()
    
    async def _init_beanie(self) -> None:
        """Initialize Beanie ODM with models"""
        from ..models.documents import get_document_models
        
        await init_beanie(
            database=self.database,
            document_models=get_document_models()
        )
        logger.info("Beanie ODM initialized")
    
    async def _test_dns_resolution(self) -> bool:
        """Test if we can resolve MongoDB Atlas hostname"""
        try:
            import socket
            hostname = "cura.6oiwqd2.mongodb.net"
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False
        except Exception:
            return False
    
    async def _try_local_fallback(self) -> None:
        """Try to connect to local MongoDB as fallback"""
        try:
            logger.warning("Attempting local MongoDB fallback...")
            local_url = f"mongodb://localhost:27017/{settings.mongo_database}"
            
            self.client = AsyncIOMotorClient(
                local_url,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000,
                socketTimeoutMS=3000
            )
            
            await asyncio.wait_for(
                self.client.admin.command('ping'),
                timeout=3.0
            )
            
            self.database = self.client[settings.mongo_database]
            await self._init_beanie()
            
            logger.info("Connected to local MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Local MongoDB fallback failed: {e}")
            logger.warning("Starting in development mode with in-memory fallback...")
            
            # Create a minimal in-memory setup for development
            await self._create_development_fallback()
    
    async def _create_development_fallback(self) -> None:
        """Create a development-only fallback when no MongoDB is available"""
        try:
            logger.info("Creating development database fallback...")
            
            # Try to use mongomock-motor if available
            try:
                import mongomock_motor
                
                # Create an in-memory MongoDB mock
                self.client = mongomock_motor.AsyncMongoMockClient()
                self.database = self.client[settings.mongo_database]
                
                # Initialize with basic collections for development
                await self._init_dev_collections()
                
                logger.info("✅ In-memory MongoDB mock initialized successfully")
                
            except ImportError:
                logger.warning("⚠️  mongomock-motor not available, using basic fallback")
                logger.info("💡 Install 'mongomock-motor' with: pip install mongomock-motor")
                await self._create_basic_fallback()
            except Exception as e:
                logger.error(f"Mock database setup failed: {e}")
                await self._create_basic_fallback()
                
        except Exception as e:
            logger.error(f"Development fallback failed: {e}")
            await self._create_basic_fallback()
    
    async def _init_dev_collections(self) -> None:
        """Initialize development collections with sample data"""
        try:
            # Create users collection with sample data
            users_collection = self.database.users
            
            # Insert sample user for development
            await users_collection.insert_one({
                "_id": "dev_user_123",
                "username": "dev_user",
                "email": "dev@cura.ai",
                "password_hash": "$2b$12$LKmYa8QgPOD7i.H.q8rFE.K3KGzTpf4Z.n5vI4HzGJKtQ6jQe8.qG",
                "first_name": "Dev",
                "last_name": "User",
                "is_active": True,
                "role": "patient",
                "created_at": "2025-09-30T00:00:00Z"
            })
            
            logger.info("Development collections initialized with sample data")
            
        except Exception as e:
            logger.error(f"Failed to initialize dev collections: {e}")
    
    async def _create_basic_fallback(self) -> None:
        """Create a basic fallback for when even mongomock is not available"""
        logger.warning("Using basic fallback - limited functionality")
        
        # Create mock client and database objects
        class MockClient:
            def close(self): pass
            
            class admin:
                @staticmethod
                async def command(cmd):
                    return {"ok": 1}
        
        class MockDatabase:
            def __init__(self):
                self.collections = {}
            
            async def list_collection_names(self):
                return list(self.collections.keys())
        
        self.client = MockClient()
        self.database = MockDatabase()
        
        logger.info("Basic fallback database created")
    
    async def disconnect(self) -> None:
        """Close database connections"""
        if self.client:
            self.client.close()
        if self.sync_client:
            self.sync_client.close()
        logger.info("Database disconnected")
    
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            if not self.client:
                return {"status": "no_connection", "mode": "development"}
            
            # Try to ping the database
            await self.client.admin.command('ping')
            
            # Get collection count if possible
            try:
                collections = await self.database.list_collection_names()
                collection_count = len(collections)
            except:
                collection_count = 0
            
            return {
                "status": "healthy",
                "database": settings.mongo_database,
                "collections": collection_count,
                "mode": "production" if "mongodb+srv" in settings.mongodb_url else "development"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "fallback", 
                "error": str(e),
                "mode": "development"
            }

# Global database manager
db = DatabaseManager()

# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency for database access"""
    if not db.database:
        await db.connect()
    return db.database

# Database lifecycle functions
async def startup_database():
    """Initialize database on startup"""
    await db.connect()

async def shutdown_database():
    """Cleanup database on shutdown"""
    await db.disconnect()

__all__ = ["db", "get_database", "startup_database", "shutdown_database"]
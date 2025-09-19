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
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[settings.mongo_database]
            
            # Initialize ODM
            await self._init_beanie()
            
            logger.info("Database connected successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def _init_beanie(self) -> None:
        """Initialize Beanie ODM with models"""
        from ..models.documents import get_document_models
        
        await init_beanie(
            database=self.database,
            document_models=get_document_models()
        )
        logger.info("Beanie ODM initialized")
    
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
                return {"status": "disconnected"}
            
            await self.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": settings.mongo_database,
                "collections": len(await self.database.list_collection_names())
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

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
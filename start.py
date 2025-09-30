#!/usr/bin/env python3
"""
Cura Medical AI Assistant - Startup Script
Handles initialization and startup of the complete application
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_environment():
    """Check if .env file exists"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found")
            print("📋 Please copy .env.example to .env and configure your settings:")
            print(f"   cp {env_example} {env_file}")
        else:
            print("❌ No environment configuration found")
        return False
    
    print("✅ Environment configuration found")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pymongo
        import langchain
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False

def check_data_directory():
    """Check if data directory exists"""
    data_dir = project_root / "data" / "pdfs"
    if not data_dir.exists():
        print("⚠️  PDF data directory not found")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created data directory: {data_dir}")
    else:
        pdf_count = len(list(data_dir.glob("*.pdf")))
        print(f"✅ Data directory found with {pdf_count} PDF files")

def check_faiss_index():
    """Check if FAISS index exists"""
    index_dir = project_root / "faiss_index"
    if not index_dir.exists() or not list(index_dir.glob("*.faiss")):
        print("⚠️  FAISS vector index not found")
        print("🔧 You may need to build the vector index first")
        print("   This will be done automatically on first run")
    else:
        print("✅ FAISS vector index found")

async def initialize_database():
    """Initialize database connection and setup"""
    try:
        from app.core.database import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.connect()
        print("✅ Database connection successful")
        await db_manager.disconnect()
        return True
    except Exception as e:
        print(f"⚠️  Database connection issue: {e}")
        print("📋 Make sure MongoDB is running and configured correctly")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Cura Medical AI Assistant...")
    print("=" * 50)
    
    try:
        # Import and start the server
        import uvicorn
        uvicorn.run(
            "run_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Cura Medical AI Assistant stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🏥 Cura Medical AI Assistant")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Environment Config", check_environment),
        ("Dependencies", check_dependencies),
        ("Data Directory", check_data_directory),
        ("Vector Index", check_faiss_index),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if result is False:
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            failed_checks.append(check_name)
    
    # Check database connection
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        db_ok = loop.run_until_complete(initialize_database())
        loop.close()
        
        if not db_ok:
            failed_checks.append("Database Connection")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        failed_checks.append("Database Connection")
    
    if failed_checks:
        print(f"\n⚠️  Some checks failed: {', '.join(failed_checks)}")
        print("🔧 Please fix the issues above before starting the server")
        
        # Ask if user wants to continue anyway
        response = input("\nDo you want to continue anyway? (y/N): ").lower()
        if response != 'y':
            print("👋 Startup cancelled")
            sys.exit(1)
    
    print("\n✅ All checks passed! Starting server...")
    print("\n📍 Access the application at:")
    print("   🌐 Web App: http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("   ⚡ API Status: http://localhost:8000/api/status")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
import asyncio
from app.services.simple_ai_service import ai_service

async def test_ai():
    print("Testing AI Service with updated prompt...")
    await ai_service.initialize()
    
    if ai_service.is_initialized:
        print("✅ AI Service initialized successfully")
        
        # Test a simple query
        response = await ai_service.generate_response("What is alopecia?")
        print(f"✅ Response generated: {len(response.get('message', ''))} characters")
        print(f"Error status: {response.get('error', False)}")
        print("Response preview:")
        print("=" * 50)
        print(response.get('message', '')[:500] + "...")
        print("=" * 50)
    else:
        print("❌ Failed to initialize AI Service")

if __name__ == "__main__":
    asyncio.run(test_ai())
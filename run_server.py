from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api import router as chatbot_router
import uvicorn
from colorama import init, Fore, Style

init()  # Initialize colorama

app = FastAPI(title="Cura API")

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Cura backend is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=str(exc)
    )

if __name__ == "__main__":
    print(f"\n{Fore.CYAN}Starting Cura Server...{Style.RESET_ALL}")
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=True)

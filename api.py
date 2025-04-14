from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from chat import load_vector_store
from models.llm_loader import initialize_llm
from chains.rag_pipeline import setup_rag
from fastapi.responses import JSONResponse
from halo import Halo

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatHistory(BaseModel):
    messages: List[Message]

class Query(BaseModel):
    question: str
    conversationId: Optional[str] = None

chat_histories = {}

# Initialize components with spinner
spinner = Halo(text='Initializing Cura...', spinner='dots')
spinner.start()
try:
    vector_store = load_vector_store()
    llm = initialize_llm()
    qa_chain = setup_rag(vector_store, llm)
    spinner.succeed("Cura initialized successfully")
except Exception as e:
    spinner.fail(f"Initialization failed: {str(e)}")
    raise e

@router.post("/ask")
async def ask_question(query: Query):
    try:
        result = qa_chain.invoke({"query": query.question})
        timestamp = datetime.now().isoformat()
        
        user_message = Message(
            role="user",
            content=query.question,
            timestamp=timestamp
        )
        
        bot_message = Message(
            role="assistant",
            content=result["result"].strip(),
            timestamp=timestamp
        )
        
        if query.conversationId not in chat_histories:
            chat_histories[query.conversationId] = ChatHistory(messages=[])
        
        chat_histories[query.conversationId].messages.extend([user_message, bot_message])
        
        return {
            "answer": result["result"].strip(),
            "timestamp": timestamp,
            "conversationId": query.conversationId
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    if conversation_id not in chat_histories:
        return {"messages": []}
    return chat_histories[conversation_id]

@router.delete("/history/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    if conversation_id in chat_histories:
        del chat_histories[conversation_id]
    return {"status": "ok"}

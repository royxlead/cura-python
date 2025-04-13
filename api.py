from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chat import load_vector_store
from models.llm_loader import initialize_llm
from chains.rag_pipeline import setup_rag
from fastapi.responses import JSONResponse
from halo import Halo

router = APIRouter()

class Query(BaseModel):
    question: str

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
        return {"answer": result["result"].strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

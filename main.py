from config import PDF_DIR
from utils import pdf_utils, vector_store
from models.llm_loader import initialize_llm
from chains.rag_pipeline import setup_rag
from chatbot.interactive_chat import medical_chatbot

def main():
    print("Initializing the medical chatbot...")
    print("Loading PDF documents...")
    texts = pdf_utils.extract_text_from_pdfs(PDF_DIR)
    if not texts:
        raise RuntimeError("No PDF text extracted.")

    vector = vector_store.build_vector_store(texts)
    llm = initialize_llm()
    qa = setup_rag(vector, llm)

    medical_chatbot(qa)

if __name__ == "__main__":
    main()
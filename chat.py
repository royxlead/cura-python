from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import VECTOR_STORE_PATH, EMBEDDING_MODEL, DEVICE
from models.llm_loader import initialize_llm
from chains.rag_pipeline import setup_rag
from utils.prompts import DEFAULT_SYSTEM_PROMPT
import os
from colorama import init, Fore, Style
from halo import Halo
from datetime import datetime

# Initialize colorama
init()

def load_vector_store():
    spinner = Halo(text='Loading vector store...', spinner='dots')
    spinner.start()
    try:
        if os.path.exists(VECTOR_STORE_PATH):
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": DEVICE})
            store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
            spinner.succeed(f"Vector store loaded from {VECTOR_STORE_PATH}")
            return store
        else:
            spinner.fail("Vector store not found")
            raise FileNotFoundError(f"Vector store not found at {VECTOR_STORE_PATH}. Please run the initial setup.")
    except Exception as e:
        spinner.fail("Error loading vector store")
        raise e

def save_chat_to_markdown(chat_history):
    chat_dir = "chat_logs"
    os.makedirs(chat_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{chat_dir}/chat_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Cura Chat Log\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for entry in chat_history:
            f.write(f"### 👤 User\n{entry['question']}\n\n")
            f.write(f"### 🤖 Cura\n{entry['answer']}\n\n")
    return filename

def medical_chatbot(qa_chain):
    print(f"\n{Fore.GREEN}🩺 Cura is ready!{Style.RESET_ALL} Type 'exit' to quit.\n")
    chat_history = []
    
    while True:
        query = input(f"{Fore.BLUE}You:{Style.RESET_ALL} ").strip()
        if not query:
            print(f"{Fore.YELLOW}⚠️  Please enter a question.{Style.RESET_ALL}")
            continue
        if query.lower() == "exit":
            if chat_history:
                filename = save_chat_to_markdown(chat_history)
                print(f"\n{Fore.GREEN}💾 Chat saved to: {filename}{Style.RESET_ALL}")
            print(f"\n{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}")
            break
        
        spinner = Halo(text='Thinking...', spinner='dots')
        spinner.start()
        try:
            result = qa_chain.invoke({"query": query})
            answer = result.get("result", "").strip()
            spinner.stop()
            print(f"\n{Fore.GREEN}🤖 Cura:{Style.RESET_ALL} {answer}\n")
            chat_history.append({"question": query, "answer": answer})
        except Exception as e:
            spinner.fail(f"Error: {str(e)}")

def main():
    print(f"\n{Fore.CYAN}=== Cura Medical Assistant ==={Style.RESET_ALL}\n")
    
    # Load the vector store and model
    vector_store = load_vector_store()
    
    spinner = Halo(text='Initializing AI model...', spinner='dots')
    spinner.start()
    llm = initialize_llm()
    spinner.succeed("AI model initialized")

    # Set up the RAG pipeline
    spinner = Halo(text='Setting up RAG pipeline...', spinner='dots')
    spinner.start()
    qa_chain = setup_rag(vector_store, llm)
    spinner.succeed("RAG pipeline ready")

    # Start chatbot interaction
    medical_chatbot(qa_chain)

if __name__ == "__main__":
    main()

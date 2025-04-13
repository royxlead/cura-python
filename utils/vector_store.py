from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import DEVICE, EMBEDDING_MODEL, VECTOR_STORE_PATH

def build_vector_store(texts):
    print("Building vector store...")

    # Set chunk size and overlap
    chunk_size = 800
    chunk_overlap = 256

    # Initialize the text splitter with the chunk size and overlap
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.create_documents(texts)

    # Log the results
    print(f"Splitting into {len(chunks)} chunks")
    print(f"Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": DEVICE})

    # Create the FAISS vector store
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Save the vector store locally
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector store saved at {VECTOR_STORE_PATH}.")

    return vector_store

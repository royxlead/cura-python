import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PDF_DIR = "data/pdfs"
VECTOR_STORE_PATH = "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "TinyLLaMA/TinyLLaMA-1.1B-Chat-v1.0"

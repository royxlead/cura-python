import os
from typing import List
import PyPDF2

def extract_text_from_pdfs(pdf_directory: str) -> List[str]:
    print(f"[+] Extracting text from PDFs in {pdf_directory}...")
    documents = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            with open(os.path.join(pdf_directory, filename), "rb") as f:
                try:
                    reader = PyPDF2.PdfReader(f)
                    text = " ".join(page.extract_text() or "" for page in reader.pages)
                    if text.strip():
                        documents.append(text)
                except Exception as e:
                    print(f"[!] Error reading {filename}: {e}")
    return documents

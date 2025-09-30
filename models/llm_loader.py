# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# from langchain_huggingface import HuggingFacePipeline
# from config import LLM_MODEL

# def initialize_llm():
    
#     print("Loading model...")

#     tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
#     model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, device_map="auto", low_cpu_mem_usage=True)

#     # Initialize the pipeline
#     print("Initializing pipeline...")
#     pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample=True,
#                     max_new_tokens=256, temperature=0.9, top_k=50, top_p=0.95,
#                     num_return_sequences=1, repetition_penalty=1.1, return_full_text=False)

#     return HuggingFacePipeline(pipeline=pipe)

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_llm():
    """
    Initialize the Google Gemini LLM using the langchain-google-genai integration.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    if not gemini_api_key:
        raise EnvironmentError("❌ GEMINI_API_KEY or GOOGLE_API_KEY is not set. Check your .env file or environment variables.")

    print(f"🔗 Initializing Google Gemini LLM: {gemini_model}")

    # Configure the Gemini API
    genai.configure(api_key=gemini_api_key)

    # Initialize the LangChain wrapper for Gemini
    llm = ChatGoogleGenerativeAI(
        model=gemini_model,
        temperature=0.7,
        max_tokens=1000,
        top_k=40,
        top_p=0.95,
        google_api_key=gemini_api_key,
        verbose=True
    )

    print("✅ Gemini LLM initialized successfully.\n")
    return llm

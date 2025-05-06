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

from langchain_together import Together  # ✅ New import from updated package
from config import TOGETHER_API_KEY, LLM_MODEL


def initialize_llm():
    """
    Initialize the Together AI LLM using the updated langchain-together integration.
    """
    if not TOGETHER_API_KEY:
        raise EnvironmentError("❌ TOGETHER_API_KEY is not set. Check your .env file or environment variables.")

    print(f"🔗 Initializing Together AI LLM: {LLM_MODEL}")

    llm = Together(
        model=LLM_MODEL,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        max_tokens=800,
        repetition_penalty=1.1,
        api_key=TOGETHER_API_KEY,   
        verbose=True
    )

    print("✅ LLM initialized successfully.\n")
    return llm

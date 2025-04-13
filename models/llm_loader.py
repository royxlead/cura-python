from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from config import LLM_MODEL

def initialize_llm():
    
    print("Loading model...")

    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, device_map="auto", low_cpu_mem_usage=True)

    # Initialize the pipeline
    print("Initializing pipeline...")
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, do_sample=True,
                    max_new_tokens=256, temperature=0.9, top_k=50, top_p=0.95,
                    num_return_sequences=1, repetition_penalty=1.1, return_full_text=False)

    return HuggingFacePipeline(pipeline=pipe)

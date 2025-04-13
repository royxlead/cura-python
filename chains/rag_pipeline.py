from langchain.chains import RetrievalQA

def setup_rag(vector_store, llm):
    print("Setting up RAG pipeline...")
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 5})
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

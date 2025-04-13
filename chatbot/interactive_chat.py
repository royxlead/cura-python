import textwrap

def medical_chatbot(qa_chain):
    print("🩺 Cura is ready! Type 'exit' to quit.")
    while True:
        query = input("\nYou: ").strip()
        if not query:
            print("⚠️  Please enter a question.")
            continue
        if query.lower() == "exit":
            print("👋 Goodbye!")
            break
        try:
            result = qa_chain({"query": query})
            answer = result.get("result", "").strip()
            print(f"\n🤖 Cura: {textwrap.fill(answer, width=100)}")
        except Exception as e:
            print(f"❌ Error: {e}")

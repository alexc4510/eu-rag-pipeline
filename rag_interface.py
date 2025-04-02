from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import VECTORSTORE_DIR, PROCESSED_DOCUMENTS, OPENAI_MODEL, OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


# ---------- Load the persisted vector DB ----------
def load_retriever():
    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=str(VECTORSTORE_DIR), embedding_function=embedding
    )
    return vectordb.as_retriever(search_kwargs={"k": 5})


# ---------- Step 1: Retrieve context and generate raw answer ----------
def get_answer(question: str, retriever):
    relevant_docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = (
        "You are an expert in European regulations. Use only the context to answer the user's question. "
        "The answer may be spread across the whole document. "
        "If the answer is not in the context, say: 'The information is not available in the provided documents.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
    )
    return response.choices[0].message.content.strip()


# ---------- Step 2: Refine the raw answer ----------
def refine_answer(raw_answer: str, question: str) -> str:
    prompt = (
        "You are a professional legal assistant helping a user understand European Union regulations. "
        "Your task is to take the following raw answer and rewrite it in a clear, organized, and formal tone.\n\n"
        "Guidelines:\n"
        "- Structure the response in full sentences.\n"
        "- Use formal language but keep it easy to understand.\n"
        "- Highlight legal points, actions, or obligations where relevant.\n"
        "- Use bullet points or paragraphs only if it improves clarity.\n"
        "- Remove any phrasing artifacts from the LLM that generated the raw answer.\n"
        "- Do NOT add new facts or assumptions.\n"
        "- The final response must only be based on the raw answer and the user question.\n\n"
        "- Answer in the language of the user question.\n\n"
        f"User Question: {question}\n\n"
        f"Raw Answer: {raw_answer}\n\n"
        f"Formatted Answer:"
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


# ---------- Run full QA pipeline (for CLI) ----------
def main():
    retriever = load_retriever()
    question = input("Ask a question about EU regulations:\n> ")

    print("\n🧠 Searching for answer...")
    raw_answer = get_answer(question, retriever)

    print("\n🪄 Polishing answer...")
    final_answer = refine_answer(raw_answer, question)

    print("\n✅ Final Answer:")
    print(final_answer)


if __name__ == "__main__":
    main()

# rag_interface.py

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import VECTORSTORE_DIR, SUMMARY_DIR, OPENAI_MODEL, OPENAI_API_KEY
from openai import OpenAI
import os

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- Category list ----------
CATEGORIES = sorted(
    name for name in os.listdir(SUMMARY_DIR) if (SUMMARY_DIR / name).is_dir()
)

print("Available categories:", CATEGORIES)


# ---------- Load the persisted vector DB ----------
def load_retriever():
    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=str(VECTORSTORE_DIR), embedding_function=embedding
    )
    return vectordb.as_retriever(search_kwargs={"k": 5})


# ---------- Step 1: First model - Detect category ----------
def detect_category(question: str) -> str:
    formatted_categories = "\n- " + "\n- ".join(CATEGORIES)
    system_prompt = (
        "You are a classifier that determines the correct category of a user's question about European regulations.\n"
        "Choose exactly one category from the following list:\n"
        f"{formatted_categories}\n\n"
        "Respond ONLY with the category name. Do not add any explanation or formatting."
    )

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        max_tokens=15,
        temperature=0,
    )

    category = response.choices[0].message.content.strip()
    if category not in CATEGORIES:
        print(
            f"⚠️ Unknown category detected: {category}. Defaulting to 'Others/Unidentified'."
        )
        category = "Others/Unidentified"
    return category


# ---------- Step 2: Retrieve context and generate raw answer ----------
def get_answer(question: str, category: str, retriever):
    relevant_docs = retriever.invoke(question, filter={"category": category})
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = (
        f"You are an expert in European regulations. The following context belongs to the '{category}' category. "
        "Use only the context to answer the user's question. The answer may be spread across the whole document. "
        "Before answering the question, read the document thoroughly. "
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


# ---------- Step 3: Refine the raw answer ----------
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


# ---------- Run full QA pipeline ----------
def main():
    retriever = load_retriever()
    question = input("Ask a question about EU regulations:\n> ")

    print("\n🔍 Detecting category...")
    category = detect_category(question)
    print(f"📂 Category detected: {category}")

    print("\n🧠 Searching for answer...")
    raw_answer = get_answer(question, category, retriever)

    print("\n🪄 Polishing answer...")
    final_answer = refine_answer(raw_answer, question)

    print("\n✅ Final Answer:")
    print(final_answer)


if __name__ == "__main__":
    main()

# scripts/build_vector_db.py

from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import tiktoken
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import PROCESSED_DOCUMENTS, VECTORSTORE_DIR, OPENAI_API_KEY


def build_vector_db(
    root_directory: Path = PROCESSED_DOCUMENTS, persist_dir: Path = VECTORSTORE_DIR
):
    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # Token-based length function using tiktoken for OpenAI model
    encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
    length_function = lambda text: len(encoding.encode(text))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,  # ~600 tokens per chunk
        chunk_overlap=100,  # ~100 tokens overlap
        length_function=length_function,
        add_start_index=True,
    )

    documents = []

    for txt_file in root_directory.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": str(txt_file.name),
                        },
                    )
                )

    os.makedirs(persist_dir, exist_ok=True)

    db = Chroma.from_documents(
        documents,
        embedding=embedding,
        persist_directory=str(persist_dir),
    )

    print(f"✅ Vector database built and saved at: {persist_dir}")


if __name__ == "__main__":
    build_vector_db()

# scripts/build_vector_db.py

from pathlib import Path
from config import SUMMARY_DIR, VECTORSTORE_DIR, OPENAI_API_KEY
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os


def build_vector_db(
    root_directory: Path = SUMMARY_DIR, persist_dir: Path = VECTORSTORE_DIR
):
    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=0,
        length_function=len,
        add_start_index=True,
    )

    documents = []

    for category_dir in root_directory.iterdir():
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        for txt_file in category_dir.rglob("*.txt"):
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read()
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "category": category,
                                "source": str(txt_file.relative_to(root_directory)),
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

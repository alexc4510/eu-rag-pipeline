# scripts/summarize.py

from openai import OpenAI
from config import (
    MAX_SUMMARY_TOKENS,
    TRUNCATE_WORDS,
    OPENAI_MODEL,
    OPENAI_API_KEY,
    PROCESSED_DOCUMENTS,
)
from pathlib import Path

client = OpenAI(api_key=OPENAI_API_KEY)


def summarize_texts(sanitized_data: dict[str, str]) -> dict[str, str]:
    summarized = {}
    for relative_path, content in sanitized_data.items():
        celex_filename = Path(relative_path).name

        # ✅ Skip if already summarized
        already_exists = any(
            (subdir / celex_filename).exists()
            for subdir in PROCESSED_DOCUMENTS.iterdir()
            if subdir.is_dir()
        )
        if already_exists:
            print(f"⏭️ Skipping summarization for {celex_filename} (already summarized)")
            continue

        truncated = " ".join(content.split()[:TRUNCATE_WORDS])
        summary = (
            client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Your task is to summarize the following European regulation while maintaining high clarity and relevance. "
                            "The summary must capture the regulation’s title, main objectives, scope, and essential details. "
                            "Follow these strict formatting rules: "
                            "1️⃣ Begin with the **title of the regulation**. "
                            "2️⃣ Use clear, structured sentences for **core legal points**. "
                            "3️⃣ Avoid introductory phrases. "
                            "4️⃣ The summary **must be exactly 600 tokens**. "
                            "5️⃣ Adjust sentence length if needed to reach token count."
                        ),
                    },
                    {"role": "user", "content": f"Text:\n{truncated}\n\nSummary:"},
                ],
                max_tokens=MAX_SUMMARY_TOKENS,
                temperature=0.0,
            )
            .choices[0]
            .message.content.strip()
        )
        summarized[relative_path] = summary
    return summarized

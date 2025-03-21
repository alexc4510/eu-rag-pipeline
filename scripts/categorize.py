# scripts/categorize.py

from openai import OpenAI
from config import DOMAINS, OPENAI_MODEL, OPENAI_API_KEY, SUMMARY_DIR
from pathlib import Path

client = OpenAI(api_key=OPENAI_API_KEY)


def categorize_texts(raw_texts: dict[str, str]) -> dict[str, dict[str, str]]:
    categorized = {domain: {} for domain in DOMAINS}
    for relative_path, content in raw_texts.items():
        celex_filename = Path(relative_path).name

        # ✅ Skip if already summarized
        already_summarized = any(
            (subdir / celex_filename).exists()
            for subdir in SUMMARY_DIR.iterdir()
            if subdir.is_dir()
        )
        if already_summarized:
            print(
                f"⏭️ Skipping categorization for {celex_filename} (already summarized)"
            )
            continue

        text_excerpt = " ".join(content.split()[:800])
        category = (
            client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that carefully analyzes text files containing European regulations "
                            "and decides in which category they belong (what is the area of the regulation), based on their content. "
                            "Your response must be only the name of the category."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Categorize into one of: {', '.join(DOMAINS)}.\n\nText: {text_excerpt}",
                    },
                ],
                max_tokens=50,
                temperature=0.0,
            )
            .choices[0]
            .message.content.strip()
        )

        if category in categorized:
            categorized[category][relative_path] = content
        else:
            categorized["Others/Unidentified"][relative_path] = content
    return categorized

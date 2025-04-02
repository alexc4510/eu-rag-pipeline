# EU Regulation Processing & Retrieval Pipeline

A modular pipeline for scraping, processing, summarizing, vectorizing, and querying European Union regulations.

## 🧩 Project Structure

```
Project/
├── data/                    # All input/output files
│   ├── pdfs/                # Downloaded PDF files
│   ├── processed_documents/ # Final summarized and sanitized .txt files 
│   ├── raw/                 # Raw text files from EUR-Lex
│   ├── vectorstore/         # Chroma DB files
│   ├── eurlex_results.json  # Metadata with CELEX ID, title, date, and link
│   └── eurlex_ro.json       # Metadata with CELEX ID, title, date, and link for PDF files
├── scripts/                 # Modular processing scripts
│   ├── build_vector_db.py
│   ├── clean_pdfs.py
│   ├── extract_pdf.py
│   ├── extract_result_text.py
│   ├── parse_all_results.py
│   ├── parse_romanian_results.py
│   ├── sanitize.py
│   └── summarize.py
├── config.py                # Central config for paths, API keys, constants
├── main_pipeline.py         # Runs the full pipeline from scrape to vector DB
├── gui.py                   # Streamlit interface
├── rag_interface.py         # Loads vector DB, allows user to ask questions
├── readme.md                # You are reading me right now!
└── requirements.txt         # Python dependencies
```

## ⚙️ Setup

1. **Create environment**

```bash
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

2. **Set your OpenAI API key**
- Set it inside `config.py` as `OPENAI_API_KEY = "sk-..."`


## 🚀 How to Use

### Option 1: Use the interface
### Step 1: Run the interface
```bash
streamlit run gui.py
```
This will:
- Launch the interace in the browser
- Either build/update the database by pressing "Run Processing Pipeline"
- Or start prompting the chatbot directly

### Step 2:
- Enjoy!

### Option 2: Use the terminal
### Step 1: Build or update the dataset
```bash
python main_pipeline.py
```
This will:
- Scrape new metadata from EUR-Lex
- Extract HTML content
- Scrape PDF Documents
- Extract the text content of the PDFs
- Sanitize and summarize documents (skips already processed ones)
- Save outputs in the folder processed_documents
- Build or update the vector database

### Step 2: Query the knowledge base
```bash
python rag_interface.py
```
- Prompts the user for a question
- Automatically detects the correct category
- Retrieves context and generates an answer using OpenAI


## 🧠 Features
- **Skips already processed files** to minimize API usage
- **Modular scripts** for each step
- **Token-aware summarization** (600 tokens)
- **Filtered context retrieval** using Chroma and LangChain


## 📦 Dependencies
- `openai`
- `langchain`
- `langchain-chroma`
- `beautifulsoup4`
- `selenium`
- `webdriver-manager`


## 📌 Notes
- The scraping target is the EUR-Lex website filtered to show only regulations.
- The system assumes filenames are based on CELEX IDs (e.g. `32021R0123.txt`).



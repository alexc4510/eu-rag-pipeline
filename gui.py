import streamlit as st
from pathlib import Path
from rag_interface import detect_category, get_answer, refine_answer, load_retriever
from main_pipeline import load_raw_texts, save_summaries

# Import processing functions
from scripts.parse_all_results import parse_all_results
from scripts.extract_result_text import extract_result_text
from scripts.categorize import categorize_texts
from scripts.sanitize import sanitize_texts
from scripts.summarize import summarize_texts
from scripts.build_vector_db import build_vector_db
from config import RAW_DIR, SUMMARY_DIR


# Initialize retriever
retriever = load_retriever()

# Streamlit page settings
st.set_page_config(page_title="EU Regulations", layout="wide")

# Session state for history and UI management
if "history" not in st.session_state:
    st.session_state.history = []

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "answer_given" not in st.session_state:
    st.session_state.answer_given = False

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# Custom CSS for styling
st.markdown("""
    <style>
        h1 { font-size: 50px; color: #2E3A59; font-weight: bold; margin-bottom: 10px; }
        .divider { margin: 30px 0; border-bottom: 2px solid #2E3A59; }
        .stButton button {
            background-color: #2E3A59; color: white; font-size: 16px;
            font-weight: bold; padding: 12px; border-radius: 5px;
        }
        .stButton button:hover { background-color: #1D2A47; }
    </style>
""", unsafe_allow_html=True)

# Layout: Main column for Q&A, Sidebar for controls
col1, col2 = st.columns([3, 1], gap="small")

# Left Column (Question & Answer)
with col1:
    st.markdown("<h1>EU Regulations Compliance Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 24px; font-weight: bold;'>Enter your question:</h3>", unsafe_allow_html=True)

    # Clear input if needed
    if st.session_state.clear_input:
        st.session_state.question_input = ""
        st.session_state.clear_input = False

    question = st.text_area("Question", key="question_input", label_visibility="hidden")

    if st.button("Get Answer", use_container_width=True):
        if question.strip():
            with st.spinner("Detecting category..."):
                category = detect_category(question)
                st.markdown(f"<h4>📂 <b>Detected Category:</b> {category}</h4>", unsafe_allow_html=True)

            with st.spinner("Retrieving relevant documents..."):
                raw_answer = get_answer(question, category, retriever)

            with st.spinner("Refining the answer..."):
                final_answer = refine_answer(raw_answer, question)

            st.subheader("Answer:")
            st.write(final_answer)

            # Save to history and update session state
            st.session_state.history.append((question, final_answer))
            st.session_state.answer_given = True

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # "Ask Another Question" button
    if st.session_state.answer_given:
        if st.button("Ask Another Question", use_container_width=True):
            st.session_state.clear_input = True
            st.session_state.answer_given = False
            st.rerun()

# Sidebar for pipeline execution and history toggle
with st.sidebar:
    # Section for running the pipeline
    st.markdown("### Build Database")

    # Year selection input
    target_year = st.number_input("Select Year", min_value=2000, max_value=2030, value=2025, step=1)

    if st.button("Run Processing Pipeline"):
        with st.status("Processing...", expanded=True) as status:
            st.write("🔍 Parsing metadata from EUR-Lex...")
            parse_all_results(target_year=target_year)

            st.write("🌐 Downloading full regulation text from links...")
            extract_result_text_generator = extract_result_text()
            for update in extract_result_text_generator:
                st.write(update)  # Display progress in UI

            st.write("📂 Loading raw files from disk...")
            raw_data = load_raw_texts(RAW_DIR)

            st.write("🏷️ Categorizing documents...")
            categorized = categorize_texts(raw_data)

            st.write("🧼 Sanitizing text...")
            sanitized = sanitize_texts(categorized)

            st.write("🧠 Summarizing content...")
            summarized = summarize_texts(sanitized)

            st.write("💾 Saving summaries to disk...")
            save_summaries(summarized, SUMMARY_DIR)

            st.write("📚 Building vector database...")
            build_vector_db()

            status.update(label="✅ Database built successfully!", state="complete")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    # History toggle button
    if st.button("➤ Show Previous Questions" if not st.session_state.show_history else "❌ Hide Previous Questions"):
        st.session_state.show_history = not st.session_state.show_history

# Right Column (History Panel, if toggled ON)
if st.session_state.show_history:
    with col2:
        st.markdown("<h3>Previous Questions</h3>", unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        if st.session_state.history:
            for q, a in st.session_state.history:
                with st.expander(q):
                    st.write(a)


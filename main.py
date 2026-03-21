import streamlit as st
from rag import process_urls, generate_answer
from fpdf import FPDF
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Assistant",
    page_icon="💬",
    layout="centered"
)

# ------------------ CUSTOM CSS (CHATGPT STYLE) ------------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
    color: white;
}

.chat-container {
    max-width: 800px;
    margin: auto;
}

.user-msg {
    background-color: #2b313e;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.assistant-msg {
    background-color: #444654;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}

.stTextInput > div > div > input {
    background-color: #1e1e1e;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("<h2 style='text-align: center;'>💬 AI Real Estate Assistant</h2>", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("⚙️ Settings")

    urls_input = st.text_area("🌐 Enter URLs (one per line)")
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    if st.button("📥 Load Knowledge"):
        with st.spinner("Processing URLs..."):
            process_urls(urls)
        st.success("✅ Knowledge loaded!")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.success("Chat cleared!")

# ------------------ CHAT DISPLAY ------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ CHAT INPUT ------------------
prompt = st.chat_input("Ask anything about the loaded data...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message instantly
    st.markdown(f'<div class="user-msg">🧑 {prompt}</div>', unsafe_allow_html=True)

    # Generate response
    with st.spinner("Thinking..."):
        answer, sources = generate_answer(prompt)
        response = f"{answer}\n\n📌 Sources:\n{sources}"

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant message
    st.markdown(f'<div class="assistant-msg">🤖 {response}</div>', unsafe_allow_html=True)

# ------------------ PDF EXPORT ------------------
if st.sidebar.button("📄 Export Chat"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "AI Chat Report", ln=True)
    pdf.ln(5)

    for msg in st.session_state.messages:
        role = msg["role"].upper()
        content = msg["content"]

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, role, ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, content)
        pdf.ln(2)

    pdf_file = "chat_report.pdf"
    pdf.output(pdf_file)

    st.download_button(
        "Download PDF",
        data=open(pdf_file, "rb").read(),
        file_name=pdf_file
    )
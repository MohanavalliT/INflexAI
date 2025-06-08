import streamlit as st
import requests
import PyPDF2
import os
import base64
from io import BytesIO
from dotenv import load_dotenv
import docx

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="INflexAI", layout="wide", initial_sidebar_state="expanded")

# ---------------------- STYLE -------------------------
st.markdown("""
    <style>
    body {
        background-color: #0e0e0e;
        color: #f1f1f1;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    .welcome-text {
        font-size: 3.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0px;
    }
    .credit-text {
        text-align: right;
        font-size: 1rem;
        margin-top: 5px;
        margin-right: 50px;
        color: #cccccc;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- SIDEBAR -----------------------
with st.sidebar:
    st.title(" AI Assistant Hub")
    app_mode = st.radio("Choose Mode", ["🏠 Home", "💬 Chat Assistant", "📄 Resume Analyzer", "📚 RapidRevision"])
    st.markdown("---")

# ---------------------- UTILS -------------------------
def truncate_text(text, max_chars=800):
    return text[:max_chars] + "..." if len(text) > max_chars else text

# ---------------------- HOME PAGE ---------------------
if app_mode == "🏠 Home":
    st.markdown("""
        <div class="main-container">
            <div class="welcome-text">WELCOME TO INflexAI</div>
            <div class="credit-text">Created by <strong>MOHANAVALLI</strong></div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------- CHAT ASSISTANT ----------------
elif app_mode == "💬 Chat Assistant":
    st.title("💬 INflexAI Chat Assistant")
    st.markdown("Ask anything! You’ll get answers with voice.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

    user_input = st.chat_input("Type your question or message")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    GROQ_CHAT_URL,
                    headers=HEADERS,
                    json={
                        "model": "llama3-8b-8192",
                        "messages": st.session_state.messages,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    reply = response.json()["choices"][0]["message"]["content"]
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    short_reply = truncate_text(reply)
                    tts = requests.post(
                        TTS_URL,
                        headers=HEADERS,
                        json={
                            "model": "playai-tts",
                            "input": short_reply,
                            "voice": "Celeste-PlayAI",
                            "response_format": "wav"
                        }
                    )
                    if tts.status_code == 200:
                        with open("reply.wav", "wb") as f:
                            f.write(tts.content)
                        with open("reply.wav", "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/wav")
                        os.remove("reply.wav")
                    else:
                        st.warning("🔈 Voice generation failed.")
                else:
                    st.error("❌ Chat API error.")

# ---------------------- RESUME ANALYZER ----------------
elif app_mode == "📄 Resume Analyzer":
    st.title("📄 Resume Analyzer")
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

    if uploaded_file:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            extracted_text = "".join([page.extract_text() for page in pdf_reader.pages])
            st.subheader("📄 Extracted Text")
            st.text_area("Resume Content", extracted_text, height=250)

            if st.button("🧠 Analyze"):
                with st.spinner("Analyzing..."):
                    response = requests.post(
                        GROQ_CHAT_URL,
                        headers=HEADERS,
                        json={
                            "model": "llama3-8b-8192",
                            "messages": [
                                {"role": "system", "content": "You are a resume analysis assistant."},
                                {"role": "user", "content": extracted_text}
                            ],
                            "temperature": 0.5
                        }
                    )
                    if response.status_code == 200:
                        result = response.json()["choices"][0]["message"]["content"]
                        st.subheader("📊 Resume Feedback")
                        st.markdown(result)
                    else:
                        st.error("❌ API Error")
        except Exception as e:
            st.error(f"❌ PDF error: {e}")

# ---------------------- SYLLABUS SIMPLIFIER ----------------
elif app_mode == "📚 RapidRevision":
    st.title("📚 RapidRevise with INflexAI")
    st.markdown("Upload your syllabus and ask questions about it.")
    uploaded_file = st.file_uploader("Upload syllabus (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    file_text = ""
    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    file_text += page.extract_text()
            elif uploaded_file.type == "text/plain":
                file_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    file_text += para.text + "\n"
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

    if file_text.strip():
        st.subheader("📑 Extracted Syllabus")
        st.text_area("Text Content", file_text.strip(), height=250)

        st.markdown("---")
        st.subheader("💬 Ask Questions About Your Syllabus")

        if "syllabus_chat" not in st.session_state:
            st.session_state.syllabus_chat = []

        for msg in st.session_state.syllabus_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_question = st.chat_input("Ask something based on the uploaded syllabus")

        if user_question:
            st.session_state.syllabus_chat.append({"role": "user", "content": user_question})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    qa_response = requests.post(
                        GROQ_CHAT_URL,
                        headers=HEADERS,
                        json={
                            "model": "llama3-8b-8192",
                            "messages": [
                                {"role": "system", "content": "You are a helpful tutor. Use the document below to answer questions."},
                                {"role": "user", "content": f"Syllabus:\n{file_text}\n\nQuestion:\n{user_question}"}
                            ],
                            "temperature": 0.6
                        }
                    )
                    if qa_response.status_code == 200:
                        answer = qa_response.json()["choices"][0]["message"]["content"]
                        st.markdown(answer)
                        st.session_state.syllabus_chat.append({"role": "assistant", "content": answer})
                    else:
                        st.error("❌ Unable to fetch answer.")

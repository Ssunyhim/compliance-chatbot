# ============================================================
# app.py  ─  컴플라이언스 도우미 (Streamlit 웹 버전)
# 실행: python -m streamlit run app.py
# ============================================================

import os
import sys
import time
import json
import requests
import streamlit as st

# ── 페이지 기본 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="컴플라이언스 도우미",
    page_icon="⚖️",
    layout="centered",
)

# ── 스타일 ────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #fdf8f2; }
    .chat-header {
        background: linear-gradient(135deg, #c8392b, #e74c3c);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .chat-header h1 { font-size: 1.5rem; margin: 0; }
    .chat-header p  { font-size: 0.85rem; margin: 0.3rem 0 0 0; opacity: 0.9; }
    .msg-user {
        background: #c8392b;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0 0.5rem 15%;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .msg-bot {
        background: white;
        color: #333;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 15% 0.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #ecddd0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .msg-typing {
        background: white;
        color: #999;
        padding: 0.75rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 15% 0.5rem 0;
        font-size: 0.95rem;
        border: 1px solid #ecddd0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .dot {
        width: 8px; height: 8px;
        background: #c8392b;
        border-radius: 50%;
        display: inline-block;
        animation: bounce 1.2s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
        40%            { transform: translateY(-6px); opacity: 1; }
    }
    .msg-label { font-size: 0.72rem; color: #999; margin: 0.15rem 0; }
    .msg-label-user { text-align: right; margin-right: 0.3rem; }
    .msg-label-bot  { margin-left: 0.3rem; }
    .stTextInput input {
        border-radius: 25px !important;
        border: 1.5px solid #e0c8b8 !important;
        padding: 0.6rem 1.2rem !important;
    }
    .stButton button {
        border-radius: 25px !important;
        background: #c8392b !important;
        color: white !important;
        border: none !important;
        padding: 0.55rem 1.5rem !important;
        font-weight: 600 !important;
    }
    .stButton button:hover { background: #a93226 !important; }
    div[data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── API Key & 매뉴얼 로드 ─────────────────────────────────────
API_KEY = st.secrets.get("GEMINI_API_KEY", "여기에_API_KEY_입력")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key=" + API_KEY
)

@st.cache_resource
def load_manual():
    txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_text.txt")
    if os.path.exists(txt_path):
        for enc in ["utf-8", "cp949", "euc-kr", "latin-1"]:
            try:
                with open(txt_path, "r", encoding=enc, errors="ignore") as f:
                    return f.read()
            except Exception:
                continue
    return ""

MANUAL_TEXT = load_manual()

# ── 세션 상태 초기화 ──────────────────────────────────────────
if "history"   not in st.session_state:
    st.session_state.history   = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
  <h1>&#9878;&#65039; 컴플라이언스 도우미</h1>
  <p>컴플라이언스 관련 궁금한 점을 자유롭게 질문해 주세요</p>
</div>
""", unsafe_allow_html=True)

if not MANUAL_TEXT:
    st.warning("⚠️ manual_text.txt 파일이 없습니다.")

# ── 대화 출력 ─────────────────────────────────────────────────
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown('<div class="msg-label msg-label-user">나</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="msg-label msg-label-bot">⚖️ 컴플라이언스 도우미</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ── 타이핑 중 표시 ────────────────────────────────────────────
if st.session_state.is_typing:
    st.markdown('<div class="msg-label msg-label-bot">⚖️ 컴플라이언스 도우미</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="msg-typing">
        답변을 생성 중입니다&nbsp;
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    </div>
    """, unsafe_allow_html=True)

# ── AI 응답 함수 (requests 직접 호출) ────────────────────────
def ask_chatbot(user_question):
    history_text = ""
    for h in st.session_state.history[-8:]:
        role = "사용자" if h["role"] == "user" else "도우미"
        history_text += f"{role}: {h['content']}\n"

    prompt = (
        "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
        "아래 컴플라이언스 자료 전체를 꼼꼼히 읽고 질문에 답변해주세요.\n"
        "자료 안에 관련 내용이 조금이라도 있으면 반드시 찾아서 답변해주세요.\n"
        "정말로 자료에 없는 경우에만 '해당 내용은 자료에 없습니다. 담당 부서에 문의해 주세요'라고 안내하세요.\n"
        "답변은 항상 한국어로 해주세요.\n\n"
        "[컴플라이언스 자료]\n"
        + MANUAL_TEXT[:200000]
        + "\n\n[이전 대화]\n"
        + history_text
        + "\n\n[질문]\n"
        + user_question
    )

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=60
            )
            result = resp.json()
            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in result:
                err_msg = result["error"].get("message", "알 수 없는 오류")
                if "429" in str(result["error"].get("code", "")):
                    wait = (attempt + 1) * 15
                    time.sleep(wait)
                    continue
                return f"오류: {err_msg}"
        except Exception as e:
            if attempt == 2:
                return f"오류가 발생했습니다: {str(e)}"
            time.sleep(5)

    return "잠시 후 다시 질문해 주세요."

# ── 입력 영역 ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            label="질문 입력",
            placeholder="컴플라이언스 관련 질문을 입력하세요...",
            label_visibility="collapsed",
            disabled=st.session_state.is_typing
        )
    with col2:
        send = st.form_submit_button(
            "전송",
            use_container_width=True,
            disabled=st.session_state.is_typing
        )

if st.session_state.history:
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.history   = []
        st.session_state.is_typing = False
        st.rerun()

# ── 전송 처리 ─────────────────────────────────────────────────
if send and user_input.strip():
    question = user_input.strip()
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.is_typing = True
    st.rerun()

if st.session_state.is_typing:
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.history) if m["role"] == "user"),
        None
    )
    if last_user_msg:
        answer = ask_chatbot(last_user_msg)
        st.session_state.history.append({"role": "bot", "content": answer})
    st.session_state.is_typing = False
    st.rerun()

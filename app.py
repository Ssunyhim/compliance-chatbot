# ============================================================
# app.py  ─  컴플라이언스 도우미 (Paris Baguette)
# 실행: python -m streamlit run app.py
# ============================================================

import os, sys, time, json, requests
import streamlit as st

st.set_page_config(
    page_title="컴플라이언스 도우미",
    page_icon="⚖️",
    layout="centered",
)

# ── 스타일 ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

* { font-family: 'Noto Sans KR', sans-serif; box-sizing: border-box; }

.stApp { background: #F5F0EB; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
.block-container { padding: 0 !important; max-width: 720px !important; }
div[data-testid="stStatusWidget"] { display: none; }

/* ── 헤더 ── */
.pb-header {
    background: linear-gradient(135deg, #7B1818 0%, #C8392B 100%);
    padding: 18px 24px 14px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 12px rgba(139,26,26,0.25);
}
.pb-header-left h1 {
    color: white; font-size: 1.15rem; font-weight: 700;
    margin: 0; letter-spacing: -0.3px;
}
.pb-header-left p {
    color: rgba(255,255,255,0.75); font-size: 0.72rem;
    margin: 2px 0 0 0; letter-spacing: 0.2px;
}
.pb-online {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 4px 10px;
    color: white; font-size: 0.72rem; font-weight: 600;
    display: flex; align-items: center; gap: 5px;
}
.pb-online-dot {
    width: 7px; height: 7px; background: #4ADE80;
    border-radius: 50%; animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; } 50% { opacity: 0.4; }
}

/* ── 상태 바 ── */
.pb-status {
    background: #FDF8F2;
    border-bottom: 1px solid #EDD5C5;
    padding: 8px 24px;
    font-size: 0.75rem; color: #8B5E52;
    display: flex; align-items: center; gap: 6px;
}
.pb-status-dot { color: #C8392B; font-size: 0.8rem; }

/* ── 채팅 영역 ── */
.pb-chat { padding: 20px 24px 10px; }

/* ── 봇 메시지 ── */
.bot-row { display: flex; gap: 10px; margin-bottom: 14px; align-items: flex-start; }
.bot-avatar {
    width: 36px; height: 36px; min-width: 36px;
    background: linear-gradient(135deg, #7B1818, #C8392B);
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 1rem; color: white;
    box-shadow: 0 2px 8px rgba(200,57,43,0.3);
}
.bot-bubble {
    background: white; border-radius: 4px 16px 16px 16px;
    padding: 14px 16px; max-width: 85%;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    border: 1px solid #F0E0D6;
}
.bot-time { font-size: 0.65rem; color: #BBAA9E; margin-top: 4px; margin-left: 46px; }

/* ── 사용자 메시지 ── */
.user-row { display: flex; justify-content: flex-end; margin-bottom: 14px; }
.user-bubble {
    background: linear-gradient(135deg, #C8392B, #A93226);
    color: white; border-radius: 16px 4px 16px 16px;
    padding: 12px 16px; max-width: 75%;
    font-size: 0.9rem; line-height: 1.5;
    box-shadow: 0 2px 8px rgba(200,57,43,0.25);
}
.user-time { font-size: 0.65rem; color: #BBAA9E; margin-top: 4px; text-align: right; }

/* ── 환영 메시지 ── */
.welcome-text { font-size: 0.9rem; color: #3D2B26; line-height: 1.6; margin-bottom: 12px; }

/* ── 빠른 질문 버튼 ── */
.quick-q-wrap { display: flex; flex-direction: column; gap: 7px; margin-top: 4px; }
.quick-q-btn {
    background: #FDF8F2; border: 1px solid #EDD5C5;
    border-radius: 8px; padding: 9px 13px;
    font-size: 0.82rem; color: #7B1818; font-weight: 500;
    cursor: pointer; text-align: left;
    display: flex; align-items: center; gap: 8px;
    transition: all 0.15s ease;
}
.quick-q-btn:hover { background: #FAEAE2; border-color: #C8392B; }

/* ── 카드 응답 ── */
.card-summary {
    font-size: 0.88rem; color: #3D2B26; line-height: 1.6;
    margin-bottom: 10px; font-weight: 500;
}
.card-item {
    display: flex; align-items: flex-start; gap: 10px;
    background: #FDF8F2; border-radius: 8px;
    padding: 10px 12px; margin-bottom: 6px;
    border-left: 3px solid #C8392B;
}
.ci-icon { font-size: 1rem; min-width: 20px; margin-top: 1px; }
.ci-content { flex: 1; }
.ci-title { font-size: 0.85rem; font-weight: 600; color: #2C1810; }
.ci-arrow { color: #C8392B; font-weight: 700; margin: 0 4px; }
.ci-desc { font-size: 0.8rem; color: #7B5E56; margin-top: 2px; line-height: 1.4; }
.card-source {
    margin-top: 10px; padding-top: 8px;
    border-top: 1px solid #F0E0D6;
    font-size: 0.75rem; color: #C8392B; font-weight: 500;
}

/* ── 타이핑 ── */
.typing-wrap { display: flex; gap: 10px; align-items: center; margin-bottom: 14px; }
.typing-bubble {
    background: white; border-radius: 4px 16px 16px 16px;
    padding: 12px 16px; border: 1px solid #F0E0D6;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    display: flex; align-items: center; gap: 5px;
}
.typing-text { font-size: 0.82rem; color: #BBAA9E; margin-right: 6px; }
.dot {
    width: 7px; height: 7px; background: #C8392B; border-radius: 50%;
    display: inline-block; animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%,80%,100% { transform: translateY(0); opacity:0.35; }
    40% { transform: translateY(-5px); opacity:1; }
}

/* ── 빠른 답변 버튼 ── */
.quick-reply-wrap {
    padding: 8px 24px 4px;
    display: flex; flex-wrap: wrap; gap: 7px;
}
.qr-btn {
    background: white; border: 1px solid #EDD5C5;
    border-radius: 20px; padding: 6px 14px;
    font-size: 0.78rem; color: #7B1818; font-weight: 500;
    cursor: pointer; transition: all 0.15s;
    white-space: nowrap;
}
.qr-btn:hover { background: #FAEAE2; border-color: #C8392B; }

/* ── 입력 영역 ── */
.pb-input-wrap {
    background: white; border-top: 1px solid #EDD5C5;
    padding: 12px 16px; position: sticky; bottom: 0;
}
.stTextInput input {
    border-radius: 25px !important; border: 1.5px solid #EDD5C5 !important;
    padding: 10px 18px !important; font-size: 0.9rem !important;
    background: #FDF8F2 !important; color: #2C1810 !important;
}
.stTextInput input:focus { border-color: #C8392B !important; box-shadow: 0 0 0 3px rgba(200,57,43,0.1) !important; }
.stButton>button {
    border-radius: 25px !important; background: #C8392B !important;
    color: white !important; border: none !important;
    padding: 10px 20px !important; font-weight: 600 !important;
    font-size: 0.88rem !important; height: 44px !important;
}
.stButton>button:hover { background: #A93226 !important; }
.stFormSubmitButton>button {
    border-radius: 25px !important; background: #C8392B !important;
    color: white !important; border: none !important;
    padding: 10px 20px !important; font-weight: 600 !important;
    height: 44px !important;
}
.stFormSubmitButton>button:hover { background: #A93226 !important; }
.stForm { border: none !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── 설정 ─────────────────────────────────────────────────────
API_KEY    = st.secrets.get("GEMINI_API_KEY", "여기에_API_KEY_입력")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key=" + API_KEY
)

QUICK_QUESTIONS = [
    ("📋", "공정거래법·가맹사업법 해석", "공정거래법과 가맹사업법에 대해 설명해줘"),
    ("⚠️", "위반 시 제재사항 안내",     "위반 시 제재사항에 대해 알려줘"),
    ("📝", "내부신고 절차 및 CP 교육",  "내부신고 절차와 CP 교육에 대해 알려줘"),
]
QUICK_REPLIES = ["↺ 처음으로", "CP 교육 일정", "내부신고 절차", "관련 법령 보기"]

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

MANUAL_TEXT  = load_manual()
MANUAL_CHARS = f"{len(MANUAL_TEXT):,}"

# ── 세션 초기화 ───────────────────────────────────────────────
for k, v in [("history",[]), ("is_typing",False), ("pending",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="pb-header">
  <div class="pb-header-left">
    <h1>⚖️ 컴플라이언스 도우미</h1>
    <p>사내 CP 자료 기반 &nbsp;·&nbsp; 임직원 전용</p>
  </div>
  <div class="pb-online">
    <span class="pb-online-dot"></span> 온라인
  </div>
</div>
<div class="pb-status">
  <span class="pb-status-dot">●</span>
  자료 로드 완료 &nbsp; 총 <strong>{MANUAL_CHARS}자</strong>
</div>
""", unsafe_allow_html=True)

# ── 응답 파싱 함수 ────────────────────────────────────────────
def parse_response(raw):
    clean = raw.strip()
    for fence in ["```json", "```"]:
        if clean.startswith(fence):
            clean = clean[len(fence):]
    clean = clean.rstrip("`").strip()
    try:
        data = json.loads(clean)
        html = ""
        if data.get("summary"):
            html += f'<div class="card-summary">{data["summary"]}</div>'
        for item in data.get("items", []):
            icon  = item.get("icon",  "•")
            title = item.get("title", "")
            desc  = item.get("desc",  "")
            html += f"""
            <div class="card-item">
              <span class="ci-icon">{icon}</span>
              <div class="ci-content">
                <div class="ci-title">{title}</div>
                {'<div class="ci-desc">'+desc+'</div>' if desc else ''}
              </div>
            </div>"""
        if data.get("source"):
            html += f'<div class="card-source">📄 출처: {data["source"]}</div>'
        return html
    except Exception:
        # fallback: plain text
        return f'<div style="font-size:0.9rem;line-height:1.7;color:#3D2B26">{raw}</div>'

# ── AI 호출 함수 ──────────────────────────────────────────────
def ask_chatbot(user_question):
    history_text = ""
    for h in st.session_state.history[-8:]:
        role = "사용자" if h["role"] == "user" else "도우미"
        history_text += f"{role}: {h['content']}\n"

    prompt = (
        "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
        "아래 컴플라이언스 자료를 꼼꼼히 읽고 질문에 답변해주세요.\n"
        "자료에 내용이 있으면 반드시 찾아서 답변하고, 없으면 담당부서 문의를 안내하세요.\n\n"
        "★ 응답 형식: 반드시 아래 JSON만 출력하세요. 다른 텍스트는 절대 포함하지 마세요.\n"
        "{\n"
        '  "summary": "1~2줄 핵심 요약 (한국어)",\n'
        '  "items": [\n'
        '    {"icon": "관련이모지", "title": "항목제목", "desc": "항목설명"}\n'
        "  ],\n"
        '  "source": "출처명 또는 null"\n'
        "}\n\n"
        "[컴플라이언스 자료]\n"
        + MANUAL_TEXT[:200000]
        + "\n\n[이전 대화]\n" + history_text
        + "\n\n[질문]\n" + user_question
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(3):
        try:
            resp   = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=60,
            )
            result = resp.json()
            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            err = result.get("error", {})
            if err.get("code") == 429:
                time.sleep((attempt+1)*15); continue
            return json.dumps({"summary": f"오류: {err.get('message','알 수 없는 오류')}", "items": [], "source": None}, ensure_ascii=False)
        except Exception as e:
            if attempt == 2:
                return json.dumps({"summary": f"오류가 발생했습니다: {str(e)}", "items": [], "source": None}, ensure_ascii=False)
            time.sleep(5)
    return json.dumps({"summary": "잠시 후 다시 시도해 주세요.", "items": [], "source": None}, ensure_ascii=False)

# ── 채팅 렌더링 ───────────────────────────────────────────────
import datetime
now_str = datetime.datetime.now().strftime("%H:%M")

st.markdown('<div class="pb-chat">', unsafe_allow_html=True)

# 환영 메시지 + 빠른 질문 (대화 없을 때)
if not st.session_state.history:
    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">⚖️</div>
      <div class="bot-bubble">
        <div class="welcome-text">
          안녕하세요! 컴플라이언스 도우미입니다.<br>
          궁금한 점을 질문해 주세요.
        </div>
      </div>
    </div>
    <div class="bot-time">{now_str}</div>
    """, unsafe_allow_html=True)

    for icon, label, _ in QUICK_QUESTIONS:
        if st.button(f"{icon}  {label}", key=f"qq_{label}", use_container_width=False):
            st.session_state.pending = label
            st.rerun()

# 대화 기록 출력
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-row">
          <div class="user-bubble">{msg["content"]}</div>
        </div>
        <div class="user-time">{now_str}</div>
        """, unsafe_allow_html=True)
    else:
        card_html = parse_response(msg["content"])
        st.markdown(f"""
        <div class="bot-row">
          <div class="bot-avatar">⚖️</div>
          <div class="bot-bubble">{card_html}</div>
        </div>
        <div class="bot-time">{now_str}</div>
        """, unsafe_allow_html=True)

# 타이핑 중 표시
if st.session_state.is_typing:
    st.markdown(f"""
    <div class="typing-wrap">
      <div class="bot-avatar">⚖️</div>
      <div class="typing-bubble">
        <span class="typing-text">답변 생성 중</span>
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── 빠른 답변 버튼 (마지막 봇 메시지 이후) ───────────────────
if (st.session_state.history and
        st.session_state.history[-1]["role"] == "bot" and
        not st.session_state.is_typing):
    cols = st.columns(len(QUICK_REPLIES))
    for i, (col, label) in enumerate(zip(cols, QUICK_REPLIES)):
        with col:
            if st.button(label, key=f"qr_{i}"):
                if "처음으로" in label:
                    st.session_state.history = []
                    st.rerun()
                else:
                    st.session_state.pending = label
                    st.rerun()

# ── 입력 폼 ──────────────────────────────────────────────────
st.markdown('<div class="pb-input-wrap">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            label="질문",
            placeholder="궁금한 점을 입력하세요...",
            label_visibility="collapsed",
            disabled=st.session_state.is_typing,
        )
    with col2:
        send = st.form_submit_button("전송", use_container_width=True,
                                     disabled=st.session_state.is_typing)
st.markdown('</div>', unsafe_allow_html=True)

# ── 전송 처리 ─────────────────────────────────────────────────
question = None
if send and user_input.strip():
    question = user_input.strip()
if st.session_state.pending:
    question = st.session_state.pending
    st.session_state.pending = None

if question:
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.is_typing = True
    st.rerun()

if st.session_state.is_typing:
    last_q = next(
        (m["content"] for m in reversed(st.session_state.history) if m["role"] == "user"),
        None,
    )
    if last_q:
        answer = ask_chatbot(last_q)
        st.session_state.history.append({"role": "bot", "content": answer})
    st.session_state.is_typing = False
    st.rerun()

# ============================================================
# app.py  ─  컴플라이언스 도우미 (Paris Baguette)
# 실행: python -m streamlit run app.py
# ============================================================

import os, time, json, requests, datetime, threading
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="컴플라이언스 도우미",
    page_icon="🛡️",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

/* ── 리셋 ── */
*, *::before, *::after { box-sizing: border-box; margin:0; padding:0; }
html, body, .stApp { font-family: 'Noto Sans KR', sans-serif !important; }

/* ── Streamlit 기본 UI 정리 ── */
header[data-testid="stHeader"]          { display: none !important; }
div[data-testid="stStatusWidget"]       { display: none !important; }
div[data-testid="stToolbar"]            { display: none !important; }
.stApp                                  { background: #E8EDF5 !important; }
section[data-testid="stMain"]           { padding: 0 !important; }
section[data-testid="stMain"] > div     { padding: 0 !important; }
.block-container                        { padding: 0 !important; max-width: 780px !important; }
.stForm                                 { border: none !important; }

/* ══════════════════════════════
   헤더 (두 번째 이미지 기준)
══════════════════════════════ */
.pb-header {
    background: linear-gradient(135deg, #071530 0%, #0B2461 60%, #0D3188 100%);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.pb-header-inner {
    display: flex;
    align-items: center;
    gap: 11px;
    flex: 1;
    min-width: 0;
}
.pb-icon-box {
    width: 38px; height: 38px; min-width: 38px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
}
.pb-header-texts { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.pb-title {
    color: white;
    font-size: clamp(0.9rem, 2.5vw, 1.08rem);
    font-weight: 800;
    letter-spacing: -0.3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pb-sub {
    color: rgba(255,255,255,0.60);
    font-size: 0.68rem;
    font-weight: 400;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.pb-online {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 4px 11px;
    color: white;
    font-size: 0.70rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
    flex-shrink: 0;
}
.pb-dot { width: 7px; height: 7px; background: #4ADE80; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.35;} }

/* 상태 바 */
.pb-status {
    background: #F5F8FF;
    border-bottom: 1px solid #C5D5EE;
    padding: 7px 20px;
    font-size: 0.73rem;
    color: #2A5298;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

/* ══════════════════════════════
   채팅 영역 (공백 제거)
══════════════════════════════ */
.pb-chat { padding: 14px 18px 6px; }

/* 봇 메시지 */
.bot-row { display:flex; gap:9px; margin-bottom:6px; align-items:flex-start; }
.bot-avatar {
    width:36px; height:36px; min-width:36px;
    background: linear-gradient(135deg, #071530, #0D3188);
    border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:0.95rem;
    box-shadow:0 2px 8px rgba(13,49,136,0.3);
}
.bot-bubble {
    background:white;
    border-radius:4px 14px 14px 14px;
    padding:12px 15px;
    max-width:84%;
    box-shadow:0 1px 5px rgba(0,0,0,0.07);
    border:1px solid #D4E3F7;
}
.msg-time      { font-size:0.62rem; color:#A0AABF; margin-top:3px; margin-left:45px; }
.msg-time-right{ font-size:0.62rem; color:#A0AABF; margin-top:3px; text-align:right; }

/* 사용자 메시지 */
.user-row { display:flex; justify-content:flex-end; margin-bottom:6px; }
.user-bubble {
    background: linear-gradient(135deg, #0B2461, #1A56C4);
    color:white;
    border-radius:14px 4px 14px 14px;
    padding:11px 15px;
    max-width:72%;
    font-size:0.88rem;
    line-height:1.55;
    box-shadow:0 2px 8px rgba(13,49,136,0.25);
}

/* 환영 */
.welcome-text { font-size:0.88rem; color:#1A2B5F; line-height:1.65; }

/* ── 빠른 질문 버튼 (Streamlit) ── */
.stButton > button {
    border-radius: 22px !important;
    border: 1.5px solid #0D3188 !important;
    background: white !important;
    color: #0D3188 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 7px 15px !important;
    transition: all 0.15s !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    margin-bottom: 2px !important;
    margin-top: 0 !important;
}
.stButton > button:hover {
    background: #0D3188 !important;
    color: white !important;
}

/* ── 카드형 응답 (불렛) ── */
.card-summary {
    font-size:0.86rem; color:#1A2B5F; line-height:1.6;
    margin-bottom:9px; font-weight:600;
    padding-bottom:8px; border-bottom:1px solid #D4E3F7;
}
.card-item {
    display:flex; align-items:flex-start; gap:9px;
    padding:7px 0;
    border-bottom: 1px dashed #E8EFF9;
}
.card-item:last-of-type { border-bottom: none; }
.ci-icon { font-size:0.95rem; min-width:20px; margin-top:1px; }
.ci-title { font-size:0.83rem; font-weight:600; color:#0B2461; line-height:1.45; }
.ci-desc  { font-size:0.77rem; color:#4A6899; margin-top:2px; line-height:1.4; }
.card-source {
    margin-top:9px; padding-top:7px;
    border-top:1px solid #D4E3F7;
    font-size:0.73rem; color:#0D3188; font-weight:600;
}

/* 타이핑 */
.typing-wrap { display:flex; gap:9px; align-items:center; margin-bottom:6px; }
.typing-text { font-size:0.79rem; color:#A0AABF; margin-right:4px; }
.dot {
    width:6px; height:6px; background:#0D3188; border-radius:50%;
    display:inline-block; animation:bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2){animation-delay:0.2s;}
.dot:nth-child(3){animation-delay:0.4s;}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.3;}40%{transform:translateY(-5px);opacity:1;}}

/* 빠른 답변 */
.quick-reply-area {
    padding: 2px 0 0;
    margin-bottom: -8px;
    display: flex;
    justify-content: center;
}
.quick-reply-area .stButton > button {
    padding: 6px 10px !important;
    font-size: 0.76rem !important;
    margin: 0 2px !important;
}

/* 입력 영역 */
.stTextInput input {
    border-radius:22px !important; border:1.5px solid #C5D5EE !important;
    padding:9px 17px !important; font-size:0.88rem !important;
    background:#F0F5FF !important; color:#1A2B5F !important;
    font-family:'Noto Sans KR',sans-serif !important;
}
.stTextInput input:focus {
    border-color:#0D3188 !important;
    box-shadow:0 0 0 3px rgba(13,49,136,0.10) !important;
}
.stFormSubmitButton > button {
    border-radius:22px !important;
    background:linear-gradient(135deg, #0B2461, #1A56C4) !important;
    color:white !important; border:none !important;
    padding:9px 20px !important; font-weight:700 !important;
    font-size:0.86rem !important; height:44px !important;
    font-family:'Noto Sans KR',sans-serif !important;
    box-shadow:0 2px 8px rgba(13,49,136,0.28) !important;
}
.stFormSubmitButton > button:hover {
    background:linear-gradient(135deg, #071530, #0B2461) !important;
}

/* 입력 폼 래퍼 - 여백 제거 */
div[data-testid="stForm"] {
    background: white !important;
    border-top: 1px solid #C5D5EE !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    position: sticky !important;
    bottom: 0 !important;
    z-index: 100 !important;
}
div[data-testid="stForm"] > div { gap: 0 !important; }
.stForm { padding: 0 !important; }

/* ── 워터마크 ── */
.pb-watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    z-index: 0;
    pointer-events: none;
    user-select: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    opacity: 0.045;
}
.pb-watermark-text {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: clamp(2rem, 6vw, 3.8rem);
    font-weight: 800;
    color: #0B2461;
    letter-spacing: 0.25em;
    white-space: nowrap;
    line-height: 1.1;
}
.pb-watermark-sub {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: clamp(0.6rem, 1.8vw, 1rem);
    font-weight: 500;
    color: #0B2461;
    letter-spacing: 0.5em;
    white-space: nowrap;
}
.pb-watermark-line {
    width: 100%;
    height: 1.5px;
    background: #0B2461;
    margin: 2px 0;
}

/* ── 실시간 타이머 ── */
.timer-tag {
    font-size: 0.72rem;
    color: #6B8CBF;
    margin-left: 8px;
    font-weight: 500;
    white-space: nowrap;
}

/* ── 타이핑 + 중지 버튼 인라인 ── */
.typing-bubble {
    background:white;
    border-radius:4px 14px 14px 14px;
    padding:10px 15px;
    border:1px solid #D4E3F7;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
    display:inline-flex;
    align-items:center;
    gap:5px;
    white-space:nowrap;
    width:fit-content;
}
/* 중지 버튼 - 버블과 동일한 높이/폰트 */
.stop-col {
    display: flex;
    align-items: center;
    height: 100%;
}
.stop-col .stButton { display:flex; align-items:center; }
.stop-col .stButton > button {
    background: transparent !important;
    border: 1px solid #D4E3F7 !important;
    color: #dc2626 !important;
    border-radius: 4px 14px 14px 14px !important;
    padding: 10px 14px !important;
    font-size: 0.79rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    margin: 0 !important;
    height: auto !important;
    line-height: 1.4 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
.stop-col .stButton > button:hover {
    background: #fff0f0 !important;
    border-color: #dc2626 !important;
}

/* TOP 버튼 */
.top-btn {
    position:fixed; bottom:80px; right:20px;
    width:40px; height:40px;
    background:linear-gradient(135deg, #0B2461, #1A56C4);
    border-radius:50%; border:none; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    color:white; font-size:1rem; font-weight:700;
    box-shadow:0 3px 12px rgba(13,49,136,0.35);
    z-index:9999; transition:all 0.2s; text-decoration:none;
}
.top-btn:hover { transform:translateY(-2px); box-shadow:0 5px 16px rgba(13,49,136,0.45); }

/* 반응형 */
@media(max-width:640px){
    .block-container { max-width:100% !important; }
    .pb-header { padding:11px 14px; }
    .pb-title  { font-size:0.88rem; }
    .pb-chat   { padding:10px 10px 4px; }
    .bot-bubble,.user-bubble { max-width:92%; }
    .quick-reply-area { padding:4px 10px 2px; }
    .top-btn { right:12px; bottom:72px; }
}
@media(min-width:641px) and (max-width:1024px){
    .block-container { max-width:680px !important; }
}
</style>

<!-- 워터마크 -->
<div class="pb-watermark" aria-hidden="true">
  <div class="pb-watermark-text">PARIS</div>
  <div class="pb-watermark-line"></div>
  <div class="pb-watermark-text">BAGUETTE</div>
  <div class="pb-watermark-sub">COMPLIANCE</div>
</div>

<a class="top-btn" onclick="(window.parent||window).scrollTo({top:0,behavior:'smooth'})" title="맨 위로">↑</a>
""", unsafe_allow_html=True)

# ── 설정 ─────────────────────────────────────────────────────
API_KEY    = st.secrets.get("GEMINI_API_KEY", "여기에_API_KEY_입력")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key=" + API_KEY
)

QUICK_QUESTIONS = [
    ("📋", "공정거래법·가맹사업법 해석",  "공정거래법과 가맹사업법에 대해 핵심만 알려줘"),
    ("⚠️", "위반 시 제재사항 안내",      "위반 시 제재사항 핵심 내용을 알려줘"),
    ("📝", "내부신고 절차 및 CP 교육",   "내부신고 절차와 CP 교육 핵심 내용을 알려줘"),
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
NOW_STR      = datetime.datetime.now().strftime("%H:%M")

for k, v in [("history",[]),("is_typing",False),("pending",None),
              ("_api_done",False),("_api_result",None),("_api_started",False),("_stopped",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="pb-header">
  <div class="pb-header-inner">
    <div class="pb-icon-box">🛡️</div>
    <div class="pb-header-texts">
      <div class="pb-title">컴플라이언스 FAQ 도우미</div>
      <div class="pb-sub">사내 CP 자료 기반 &nbsp;·&nbsp; 임직원 전용</div>
    </div>
  </div>
  <div class="pb-online"><span class="pb-dot"></span> 온라인</div>
</div>
<div class="pb-status">
  ✅ &nbsp;FAQ 자료 로드 완료 &nbsp; 총 <strong>&nbsp;{MANUAL_CHARS}자</strong>
</div>
""", unsafe_allow_html=True)

# ── 응답 파싱 ─────────────────────────────────────────────────
def parse_response(raw):
    clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        data = json.loads(clean)
        html = ""
        if data.get("summary"):
            html += f'<div class="card-summary">{data["summary"]}</div>'
        for item in data.get("items", []):
            icon  = item.get("icon","▪")
            title = item.get("title","")
            desc  = item.get("desc","")
            html += f"""<div class="card-item">
              <span class="ci-icon">{icon}</span>
              <div><div class="ci-title">{title}</div>{'<div class="ci-desc">'+desc+'</div>' if desc else ''}</div>
            </div>"""
        if data.get("source"):
            html += f'<div class="card-source">📄 출처: {data["source"]}</div>'
        return html
    except Exception:
        # 일반 텍스트 → 줄 단위 불렛 변환
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        html = ""
        for l in lines:
            prefix = "▪" if not l.startswith(("•","▪","·","-","*")) else ""
            html += f'<div class="card-item"><span class="ci-icon">{prefix}</span><div class="ci-title">{l}</div></div>'
        return html

# ── AI 호출 ───────────────────────────────────────────────────
def ask_chatbot(user_question):
    history_text = "".join(
        f"{'사용자' if h['role']=='user' else '도우미'}: {h['content']}\n"
        for h in st.session_state.history[-8:]
    )
    prompt = (
        "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
        "아래 컴플라이언스 자료에서 질문과 관련된 핵심 내용만 찾아 답변하세요.\n"
        "자료에 없으면 '담당 부서에 문의해 주세요'로 안내하세요.\n\n"
        "★ 응답 규칙:\n"
        "1. 반드시 아래 JSON 형식으로만 출력 (다른 텍스트 금지)\n"
        "2. summary: 한 줄 핵심 요약\n"
        "3. items: 핵심 내용을 간결한 불렛 3~6개로 정리. desc는 꼭 필요할 때만 한 줄로.\n"
        "4. 서술형 문장 금지. 명사형·단문 위주로 작성.\n"
        '{"summary":"한줄요약","items":[{"icon":"이모지","title":"핵심항목","desc":"보충설명(선택)"}],"source":"출처명 또는 null"}\n\n'
        "[자료]\n" + MANUAL_TEXT[:50000]
        + "\n\n[이전대화]\n" + history_text
        + "\n\n[질문]\n" + user_question
    )
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    for attempt in range(3):
        try:
            resp   = requests.post(
                GEMINI_URL,
                headers={"Content-Type":"application/json; charset=utf-8"},
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=90,
            )
            result = resp.json()
            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            err = result.get("error", {})
            code = err.get("code", "")
            msg  = err.get("message", "알 수 없음")
            if code == 429:
                time.sleep((attempt+1)*15); continue
            return json.dumps({
                "summary": f"API 오류 ({code}): {msg}",
                "items": [{"icon":"⚠️","title":"오류 내용","desc": msg},
                          {"icon":"🔑","title":"API 키 또는 모델 확인","desc":"Streamlit Secrets의 키가 올바른지 확인해 주세요"}],
                "source": None
            }, ensure_ascii=False)
        except requests.exceptions.Timeout:
            if attempt == 2:
                return json.dumps({"summary":"응답 시간 초과 — 질문을 더 짧게 해보세요","items":[{"icon":"⏱️","title":"타임아웃","desc":"90초가 지나도 응답이 없습니다. 질문을 간단하게 줄여 다시 시도해 주세요"}],"source":None}, ensure_ascii=False)
            time.sleep(5)
        except Exception as e:
            if attempt == 2:
                return json.dumps({"summary":f"연결 오류: {str(e)}","items":[{"icon":"🔄","title":"잠시 후 재시도","desc":str(e)}],"source":None}, ensure_ascii=False)
            time.sleep(5)
    return json.dumps({"summary":"요청 실패 — 잠시 후 다시 시도해 주세요","items":[],"source":None}, ensure_ascii=False)

# ── 채팅 렌더링 ───────────────────────────────────────────────
# 봇 응답이 아직 없으면 → 환영 + 빠른 질문 항상 노출 (타이핑 중도 포함)
bot_replied = any(m["role"]=="bot" for m in st.session_state.history)

st.markdown('<div class="pb-chat">', unsafe_allow_html=True)

# 환영 메시지 + 빠른 질문 버튼 (봇이 한 번도 답변 안 했을 때 항상 표시)
if not bot_replied:
    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">🛡️</div>
      <div class="bot-bubble">
        <div class="welcome-text">
          안녕하세요! 컴플라이언스 도우미입니다.<br>궁금한 점을 질문해 주세요.
        </div>
      </div>
    </div>
    <div class="msg-time">{NOW_STR}</div>
    """, unsafe_allow_html=True)
    for icon, label, _ in QUICK_QUESTIONS:
        if st.button(f"{icon}  {label}", key=f"qq_{label}"):
            st.session_state.pending = label
            st.rerun()

# 대화 기록
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-row"><div class="user-bubble">{msg["content"]}</div></div>
        <div class="msg-time-right">{NOW_STR}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-row">
          <div class="bot-avatar">🛡️</div>
          <div class="bot-bubble">{parse_response(msg["content"])}</div>
        </div>
        <div class="msg-time">{NOW_STR}</div>
        """, unsafe_allow_html=True)

# 타이핑 중 + 실시간 경과 타이머 + 중지 버튼
if st.session_state.is_typing:
    elapsed = int(time.time() - st.session_state.get("_start_time", time.time()))
    if elapsed < 5:
        timer_text = "· 잠시만 기다려 주세요"
    elif elapsed < 20:
        timer_text = f"· {elapsed}초 경과"
    elif elapsed < 40:
        timer_text = f"· {elapsed}초 경과 (거의 완료)"
    else:
        timer_text = f"· {elapsed}초 경과 (복잡한 질문이에요)"

    # avatar + bubble + stop 버튼을 하나의 columns 행에
    col_av, col_bub, col_stop, col_empty = st.columns([0.45, 3.8, 1.4, 4.35])
    with col_av:
        st.markdown('<div class="bot-avatar" style="margin-top:2px">🛡️</div>', unsafe_allow_html=True)
    with col_bub:
        st.markdown(f"""<div class="typing-bubble">
          <span class="typing-text">답변 생성 중</span>
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          <span class="timer-tag">{timer_text}</span>
        </div>""", unsafe_allow_html=True)
    with col_stop:
        st.markdown('<div class="stop-col">', unsafe_allow_html=True)
        if st.button("⏹ 중지", key="stop_btn"):
            st.session_state.is_typing    = False
            st.session_state._api_started = False
            st.session_state._api_done    = False
            st.session_state._stopped     = True
            if st.session_state.history and st.session_state.history[-1]["role"] == "user":
                st.session_state.history.pop()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 빠른 답변 버튼
if (bot_replied and not st.session_state.is_typing
        and st.session_state.history[-1]["role"]=="bot"):
    st.markdown('<div class="quick-reply-area">', unsafe_allow_html=True)
    # 좌우 여백 columns으로 중앙 정렬
    _, c1, c2, c3, c4, _ = st.columns([0.3, 1, 1, 1, 1, 0.3])
    for col, label, i in zip([c1,c2,c3,c4], QUICK_REPLIES, range(4)):
        with col:
            if st.button(label, key=f"qr_{i}", use_container_width=True):
                if "처음으로" in label:
                    st.session_state.history=[]
                    st.rerun()
                else:
                    st.session_state.pending=label
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 입력 폼
with st.form(key="chat_form", clear_on_submit=True):
    c1,c2 = st.columns([5,1])
    with c1:
        user_input = st.text_input(
            label="질문", placeholder="궁금한 점을 입력하세요...",
            label_visibility="collapsed", disabled=st.session_state.is_typing)
    with c2:
        send = st.form_submit_button("전송", use_container_width=True,
                                     disabled=st.session_state.is_typing)
# 전송 처리
question = None
if send and user_input.strip():
    question = user_input.strip()
if st.session_state.pending:
    question = st.session_state.pending
    st.session_state.pending = None

if question:
    st.session_state.history.append({"role":"user","content":question})
    st.session_state.is_typing = True
    st.rerun()

if st.session_state.is_typing:
    if not st.session_state._api_started:
        last_q = next((m["content"] for m in reversed(st.session_state.history) if m["role"]=="user"), None)
        if last_q:
            st.session_state._api_started = True
            st.session_state._start_time  = time.time()
            def _worker(q=last_q):
                result = ask_chatbot(q)
                st.session_state["_api_result"] = result
                st.session_state["_api_done"]   = True
            threading.Thread(target=_worker, daemon=True).start()

    if st.session_state._api_done:
        if st.session_state.is_typing:
            st.session_state.history.append({"role":"bot","content":st.session_state._api_result})
        st.session_state.is_typing    = False
        st.session_state._api_started = False
        st.session_state._api_done    = False
        st.session_state._api_result  = None
        st.rerun()
    else:
        time.sleep(0.8)
        st.rerun()

# ============================================================
# app.py  ─  컴플라이언스 도우미 v2.0 (Paris Baguette)
# 새 기능: 로그인, RAG, 피드백, 대화내보내기, 관리자페이지, 감사로그
# ============================================================
import os, time, json, requests, datetime, threading, io
import streamlit as st

st.set_page_config(page_title="컴플라이언스 도우미", page_icon="🛡️", layout="centered")

# ══════════════════════════════════════════════════════════════
#  공통 CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,.stApp{font-family:'Noto Sans KR',sans-serif!important}
.stApp{background:#E8EDF5!important}
header[data-testid="stHeader"]{display:none!important}
div[data-testid="stStatusWidget"]{display:none!important}
section[data-testid="stMain"]{padding:0!important}
section[data-testid="stMain"]>div{padding:0!important}
.block-container{padding:0!important;max-width:780px!important}
.stForm{border:none!important}

/* 헤더 */
.pb-header{background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%);padding:14px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.pb-header-inner{display:flex;align-items:center;gap:11px;flex:1;min-width:0}
.pb-icon-box{width:38px;height:38px;min-width:38px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.15rem}
.pb-title{color:white;font-size:clamp(.9rem,2.5vw,1.08rem);font-weight:800;letter-spacing:-.3px;white-space:nowrap}
.pb-sub{color:rgba(255,255,255,.60);font-size:.68rem;font-weight:400;white-space:nowrap}
.pb-online{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:4px 11px;color:white;font-size:.70rem;font-weight:600;display:flex;align-items:center;gap:5px;white-space:nowrap;flex-shrink:0}
.pb-dot{width:7px;height:7px;background:#4ADE80;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.pb-status{background:#F5F8FF;border-bottom:1px solid #C5D5EE;padding:7px 20px;font-size:.73rem;color:#2A5298;display:flex;align-items:center;gap:6px;font-weight:500}

/* 채팅 */
.pb-chat{padding:14px 18px 6px}
.bot-row{display:flex;gap:9px;margin-bottom:6px;align-items:flex-start}
.bot-avatar{width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#071530,#0D3188);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.95rem;box-shadow:0 2px 8px rgba(13,49,136,.3)}
.bot-bubble{background:white;border-radius:4px 14px 14px 14px;padding:12px 15px;max-width:84%;box-shadow:0 1px 5px rgba(0,0,0,.07);border:1px solid #D4E3F7}
.msg-time{font-size:.62rem;color:#A0AABF;margin-top:3px;margin-left:45px}
.msg-time-right{font-size:.62rem;color:#A0AABF;margin-top:3px;text-align:right}
.user-row{display:flex;justify-content:flex-end;margin-bottom:6px}
.user-bubble{background:linear-gradient(135deg,#0B2461,#1A56C4);color:white;border-radius:14px 4px 14px 14px;padding:11px 15px;max-width:72%;font-size:.88rem;line-height:1.55;box-shadow:0 2px 8px rgba(13,49,136,.25)}
.welcome-text{font-size:.88rem;color:#1A2B5F;line-height:1.65}

/* 카드 응답 */
.card-summary{font-size:.86rem;color:#1A2B5F;line-height:1.6;margin-bottom:9px;font-weight:600;padding-bottom:8px;border-bottom:1px solid #D4E3F7}
.card-item{display:flex;align-items:flex-start;gap:9px;padding:7px 0;border-bottom:1px dashed #E8EFF9}
.card-item:last-of-type{border-bottom:none}
.ci-icon{font-size:.95rem;min-width:20px;margin-top:1px}
.ci-title{font-size:.83rem;font-weight:600;color:#0B2461;line-height:1.45}
.ci-desc{font-size:.77rem;color:#4A6899;margin-top:2px;line-height:1.4}
.card-source{margin-top:9px;padding-top:7px;border-top:1px solid #D4E3F7;font-size:.73rem;color:#0D3188;font-weight:600}

/* 피드백 버튼 */
.feedback-row{display:flex;align-items:center;gap:6px;margin-top:6px;margin-left:45px}
.feedback-label{font-size:.68rem;color:#A0AABF}
.stButton.fb-btn>button{background:transparent!important;border:1px solid #D4E3F7!important;border-radius:12px!important;padding:2px 8px!important;font-size:.78rem!important;color:#4A6899!important;min-width:0!important;height:auto!important;margin:0!important}
.stButton.fb-btn>button:hover{border-color:#0D3188!important;color:#0D3188!important}
.fb-active{color:#0D3188!important;border-color:#0D3188!important;font-weight:700!important}

/* 타이핑 */
.typing-bubble{background:white;border-radius:4px 14px 14px 14px;padding:10px 15px;border:1px solid #D4E3F7;box-shadow:0 1px 4px rgba(0,0,0,.06);display:inline-flex;align-items:center;gap:5px;white-space:nowrap;width:fit-content}
.typing-text{font-size:.79rem;color:#A0AABF;margin-right:4px}
.timer-tag{font-size:.72rem;color:#6B8CBF;margin-left:4px;font-weight:500}
.dot{width:6px;height:6px;background:#0D3188;border-radius:50%;display:inline-block;animation:bounce 1.2s infinite ease-in-out}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.3}40%{transform:translateY(-5px);opacity:1}}

/* 중지 버튼 */
.typing-col-wrap [data-testid="stHorizontalBlock"]{display:flex!important;align-items:center!important;gap:6px!important;flex-wrap:nowrap!important}
.typing-col-wrap [data-testid="column"]:nth-child(1){flex:0 0 auto!important;width:auto!important;min-width:0!important;padding:0!important}
.typing-col-wrap [data-testid="column"]:nth-child(2){flex:0 0 auto!important;width:auto!important;min-width:0!important;padding:0!important}
.typing-col-wrap [data-testid="column"]:nth-child(3){flex:0 0 auto!important;width:auto!important;min-width:0!important;padding:0!important}
.typing-col-wrap [data-testid="column"]:nth-child(4){flex:1 1 auto!important}
.stop-col{display:flex;align-items:center}
.stop-col .stButton{display:flex;align-items:center;margin:0}
.stop-col .stButton>button{background:white!important;border:1px solid #D4E3F7!important;color:#dc2626!important;border-radius:4px 14px 14px 14px!important;padding:10px 14px!important;font-size:.79rem!important;font-weight:600!important;white-space:nowrap!important;margin:0!important;height:auto!important;line-height:1.4!important;box-shadow:0 1px 4px rgba(0,0,0,.06)!important}
.stop-col .stButton>button:hover{background:#fff0f0!important;border-color:#dc2626!important}

/* 빠른질문 / 빠른답변 */
.stButton>button{border-radius:22px!important;border:1.5px solid #0D3188!important;background:white!important;color:#0D3188!important;font-size:.82rem!important;font-weight:600!important;padding:7px 15px!important;transition:all .15s!important;font-family:'Noto Sans KR',sans-serif!important;margin-bottom:4px!important}
.stButton>button:hover{background:#0D3188!important;color:white!important}
.quick-reply-area{padding:2px 0 0;margin-bottom:-8px;display:flex;justify-content:center}
.quick-reply-area .stButton>button{padding:6px 10px!important;font-size:.76rem!important;margin:0 2px!important}

/* 입력창 */
div[data-testid="stForm"]{background:white!important;border-top:1px solid #C5D5EE!important;padding:10px 14px!important;margin:0!important;position:sticky!important;bottom:0!important;z-index:100!important}
.stTextInput input{border-radius:22px!important;border:1.5px solid #C5D5EE!important;padding:9px 17px!important;font-size:.88rem!important;background:#F0F5FF!important;color:#1A2B5F!important;font-family:'Noto Sans KR',sans-serif!important}
.stTextInput input:focus{border-color:#0D3188!important;box-shadow:0 0 0 3px rgba(13,49,136,.10)!important}
.stFormSubmitButton>button{border-radius:22px!important;background:linear-gradient(135deg,#0B2461,#1A56C4)!important;color:white!important;border:none!important;padding:9px 20px!important;font-weight:700!important;font-size:.86rem!important;height:44px!important;font-family:'Noto Sans KR',sans-serif!important;box-shadow:0 2px 8px rgba(13,49,136,.28)!important}
.stFormSubmitButton>button:hover{background:linear-gradient(135deg,#071530,#0B2461)!important}

/* 로그인 */
.login-wrap{max-width:420px;margin:80px auto;background:white;border-radius:20px;padding:40px;box-shadow:0 8px 32px rgba(13,49,136,.12)}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo h1{font-size:1.3rem;font-weight:800;color:#0B2461;margin-top:10px}
.login-logo p{font-size:.8rem;color:#6B8CBF;margin-top:4px}
.login-wrap .stTextInput input{border-radius:12px!important;border:1.5px solid #C5D5EE!important;background:#F5F8FF!important}
.login-wrap .stFormSubmitButton>button{width:100%;border-radius:12px!important;height:48px!important}

/* 워터마크 */
.pb-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);z-index:0;pointer-events:none;user-select:none;display:flex;flex-direction:column;align-items:center;gap:6px;opacity:.045}
.pb-watermark-text{font-family:'Noto Sans KR',sans-serif;font-size:clamp(2rem,6vw,3.8rem);font-weight:800;color:#0B2461;letter-spacing:.25em;white-space:nowrap;line-height:1.1}
.pb-watermark-sub{font-family:'Noto Sans KR',sans-serif;font-size:clamp(.6rem,1.8vw,1rem);font-weight:500;color:#0B2461;letter-spacing:.5em;white-space:nowrap}
.pb-watermark-line{width:100%;height:1.5px;background:#0B2461;margin:2px 0}

/* TOP 버튼 */
.top-btn{position:fixed;bottom:80px;right:20px;width:40px;height:40px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;color:white;font-size:1rem;font-weight:700;box-shadow:0 3px 12px rgba(13,49,136,.35);z-index:9999;transition:all .2s;text-decoration:none}
.top-btn:hover{transform:translateY(-2px)}

/* 관리자 */
.admin-card{background:white;border-radius:14px;padding:20px;margin-bottom:16px;border:1px solid #D4E3F7;box-shadow:0 1px 6px rgba(0,0,0,.06)}
.admin-stat{text-align:center}
.admin-stat .num{font-size:2rem;font-weight:800;color:#0D3188}
.admin-stat .lbl{font-size:.78rem;color:#6B8CBF;margin-top:2px}

/* 반응형 */
@media(max-width:640px){
  .block-container{max-width:100%!important}
  .pb-header{padding:11px 14px}
  .pb-title{font-size:.88rem}
  .pb-chat{padding:10px 10px 4px}
  .bot-bubble,.user-bubble{max-width:92%}
  .login-wrap{margin:40px 16px;padding:28px 20px}
  .quick-reply-area .stButton>button{font-size:.7rem!important;padding:5px 7px!important}
  .top-btn{right:12px;bottom:72px}
}
</style>

<a class="top-btn" onclick="(window.parent||window).scrollTo({top:0,behavior:'smooth'})" title="맨 위로">↑</a>
<div class="pb-watermark" aria-hidden="true">
  <div class="pb-watermark-text">PARIS</div>
  <div class="pb-watermark-line"></div>
  <div class="pb-watermark-text">BAGUETTE</div>
  <div class="pb-watermark-sub">COMPLIANCE</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  설정 & 데이터 로드
# ══════════════════════════════════════════════════════════════
API_KEY   = st.secrets.get("GEMINI_API_KEY", "")
LOGIN_PW  = st.secrets.get("LOGIN_PASSWORD",  "pb2024")
ADMIN_PW  = st.secrets.get("ADMIN_PASSWORD",  "pbadmin2024")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

QUICK_QUESTIONS = [
    ("📋", "공정거래법·가맹사업법 해석",  "공정거래법과 가맹사업법에 대해 알려줘"),
    ("⚠️", "위반 시 제재사항 안내",      "위반 시 제재사항을 알려줘"),
    ("📝", "내부신고 절차 및 CP 교육",   "내부신고 절차와 CP 교육을 알려줘"),
]
QUICK_REPLIES = ["↺ 처음으로", "CP 교육 일정", "내부신고 절차", "관련 법령 보기"]

@st.cache_resource
def load_and_chunk():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_text.txt")
    if not os.path.exists(path):
        return "", []
    for enc in ["utf-8","cp949","euc-kr","latin-1"]:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                text = f.read()
            chunks, i = [], 0
            while i < len(text):
                c = text[i:i+800].strip()
                if len(c) > 50:
                    chunks.append(c)
                i += 650
            return text, chunks
        except Exception:
            continue
    return "", []

MANUAL_TEXT, MANUAL_CHUNKS = load_and_chunk()
MANUAL_CHARS = f"{len(MANUAL_TEXT):,}"

def get_relevant_chunks(query, top_k=7):
    """RAG: 한국어 n-gram 키워드 매칭"""
    if not MANUAL_CHUNKS:
        return []
    clean_q = query.replace(" ", "")
    ngrams = {clean_q[i:i+n] for n in [2,3,4] for i in range(len(clean_q)-n+1)}
    scored = sorted(((sum(1 for ng in ngrams if ng in c), c) for c in MANUAL_CHUNKS), reverse=True)
    result = [c for s,c in scored[:top_k] if s > 0]
    return result or MANUAL_CHUNKS[:3]

# ══════════════════════════════════════════════════════════════
#  세션 초기화
# ══════════════════════════════════════════════════════════════
for k,v in [("logged_in",False),("is_admin",False),("user_id",""),
            ("history",[]),("is_typing",False),("pending",None),
            ("_api_done",False),("_api_result",None),
            ("_api_started",False),("_stopped",False),("_start_time",0),
            ("feedback",{}),("audit_log",[])]:
    if k not in st.session_state:
        st.session_state[k] = v

NOW_STR = datetime.datetime.now().strftime("%H:%M")

# ══════════════════════════════════════════════════════════════
#  AI 호출
# ══════════════════════════════════════════════════════════════
def ask_chatbot(question):
    context = "\n\n---\n".join(get_relevant_chunks(question))
    hist = "".join(f"{'사용자' if h['role']=='user' else '도우미'}: {h['content']}\n"
                   for h in st.session_state.history[-6:])
    prompt = (
        "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
        "아래 자료에서 질문과 관련된 핵심 내용을 찾아 답변하세요.\n"
        "자료에 없으면 '담당 부서에 문의해 주세요'로 안내하세요.\n"
        "★ 응답: 반드시 JSON만 출력 (다른 텍스트 금지)\n"
        '{"summary":"한줄요약","items":[{"icon":"이모지","title":"항목","desc":"설명(선택)"}],"source":"출처 또는 null"}\n\n'
        f"[관련 자료]\n{context}\n\n[이전 대화]\n{hist}\n\n[질문]\n{question}"
    )
    payload = {"contents":[{"parts":[{"text":prompt}]}]}
    for attempt in range(3):
        try:
            r = requests.post(GEMINI_URL,
                headers={"Content-Type":"application/json; charset=utf-8"},
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=90)
            res = r.json()
            if "candidates" in res:
                return res["candidates"][0]["content"]["parts"][0]["text"]
            err = res.get("error",{})
            if err.get("code")==429:
                time.sleep((attempt+1)*15); continue
            return json.dumps({"summary":f"API 오류: {err.get('message','')}","items":[],"source":None},ensure_ascii=False)
        except requests.exceptions.Timeout:
            if attempt==2:
                return json.dumps({"summary":"응답 시간 초과 — 질문을 짧게 해보세요","items":[],"source":None},ensure_ascii=False)
            time.sleep(3)
        except Exception as e:
            if attempt==2:
                return json.dumps({"summary":f"오류: {e}","items":[],"source":None},ensure_ascii=False)
            time.sleep(3)
    return json.dumps({"summary":"요청 실패 — 잠시 후 재시도해 주세요","items":[],"source":None},ensure_ascii=False)

def parse_response(raw):
    clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        data = json.loads(clean)
        html = ""
        if data.get("summary"):
            html += f'<div class="card-summary">{data["summary"]}</div>'
        for item in data.get("items",[]):
            icon,title,desc = item.get("icon","▪"),item.get("title",""),item.get("desc","")
            html += f'<div class="card-item"><span class="ci-icon">{icon}</span><div><div class="ci-title">{title}</div>{"<div class=\"ci-desc\">"+desc+"</div>" if desc else ""}</div></div>'
        if data.get("source"):
            html += f'<div class="card-source">📄 출처: {data["source"]}</div>'
        return html
    except Exception:
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        return "".join(f'<div class="card-item"><span class="ci-icon">▪</span><div class="ci-title">{l}</div></div>' for l in lines) or f'<div style="font-size:.88rem;line-height:1.7;color:#1A2B5F">{raw}</div>'

def log_audit(question, resp_time):
    st.session_state.audit_log.append({
        "시간": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "사번": st.session_state.user_id,
        "질문": question[:80],
        "응답시간(초)": round(resp_time, 1),
    })

# ══════════════════════════════════════════════════════════════
#  로그인 페이지
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-wrap">
      <div class="login-logo">
        <div style="font-size:2.5rem">🛡️</div>
        <h1>컴플라이언스 도우미</h1>
        <p>사내 CP 자료 기반 · 임직원 전용</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        emp_id = st.text_input("사번", placeholder="사번을 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        submitted = st.form_submit_button("로그인", use_container_width=True)
        if submitted:
            if password == ADMIN_PW:
                st.session_state.logged_in = True
                st.session_state.is_admin  = True
                st.session_state.user_id   = emp_id or "admin"
                st.rerun()
            elif password == LOGIN_PW:
                st.session_state.logged_in = True
                st.session_state.user_id   = emp_id or "unknown"
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  관리자 페이지
# ══════════════════════════════════════════════════════════════
if st.session_state.is_admin:
    st.markdown(f"""
    <div class="pb-header">
      <div class="pb-header-inner">
        <div class="pb-icon-box">⚙️</div>
        <div><div class="pb-title">관리자 대시보드</div>
        <div class="pb-sub">Paris Baguette Compliance Admin</div></div>
      </div>
      <div class="pb-online"><span class="pb-dot"></span> 관리자</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 사용 통계", "📁 문서 관리", "📋 감사 로그"])

    with tab1:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        audit = st.session_state.audit_log
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="admin-stat"><div class="num">{len(audit)}</div><div class="lbl">총 질문 수</div></div>', unsafe_allow_html=True)
        with col2:
            avg_t = round(sum(a["응답시간(초)"] for a in audit)/len(audit),1) if audit else 0
            st.markdown(f'<div class="admin-stat"><div class="num">{avg_t}s</div><div class="lbl">평균 응답 시간</div></div>', unsafe_allow_html=True)
        with col3:
            users = len(set(a["사번"] for a in audit))
            st.markdown(f'<div class="admin-stat"><div class="num">{users}</div><div class="lbl">사용 인원</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if audit:
            st.markdown("**최근 질문 현황**")
            import pandas as pd
            df = pd.DataFrame(audit[-20:][::-1])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # CSV 다운로드
            csv = pd.DataFrame(audit).to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 전체 로그 다운로드 (CSV)", csv, "audit_log.csv", "text/csv")
        else:
            st.info("아직 사용 데이터가 없습니다.")

    with tab2:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown("**현재 문서 상태**")
        st.info(f"📄 manual_text.txt — 총 {MANUAL_CHARS}자 ({len(MANUAL_CHUNKS)}개 청크)")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown("**새 문서 업로드**")
        st.caption("PDF, DOCX, PPTX, XLSX, TXT 파일을 업로드하면 내용을 추출해 미리보기를 제공합니다.")
        uploaded = st.file_uploader("문서 파일 선택", accept_multiple_files=True,
                                     type=["pdf","docx","pptx","xlsx","txt"])
        if uploaded:
            texts = []
            for f in uploaded:
                try:
                    if f.name.endswith(".txt"):
                        texts.append(f"[{f.name}]\n{f.read().decode('utf-8',errors='ignore')}")
                    else:
                        texts.append(f"[{f.name}] — 바이너리 파일 (로컬에서 convert_docs.py 실행 후 업로드)")
                except Exception as e:
                    texts.append(f"[{f.name}] 오류: {e}")
            combined = "\n\n".join(texts)
            st.text_area("추출 결과 미리보기", combined[:3000], height=200)
            st.download_button("📥 manual_text.txt 다운로드 후 GitHub에 업로드", combined, "manual_text.txt")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        if st.session_state.audit_log:
            import pandas as pd
            st.dataframe(pd.DataFrame(st.session_state.audit_log[::-1]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("감사 로그가 없습니다.")

    st.markdown("---")
    if st.button("🚪 로그아웃"):
        st.session_state.logged_in = False
        st.session_state.is_admin  = False
        st.rerun()

    if st.button("💬 채팅으로 이동"):
        st.session_state.is_admin = False
        st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════
#  메인 채팅
# ══════════════════════════════════════════════════════════════
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
  &nbsp;&nbsp;|&nbsp;&nbsp; 👤 {st.session_state.user_id}
</div>
""", unsafe_allow_html=True)

bot_replied = any(m["role"]=="bot" for m in st.session_state.history)

st.markdown('<div class="pb-chat">', unsafe_allow_html=True)

# 환영 + 빠른 질문
if not bot_replied:
    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">🛡️</div>
      <div class="bot-bubble">
        <div class="welcome-text">안녕하세요! 컴플라이언스 도우미입니다.<br>궁금한 점을 질문해 주세요.</div>
      </div>
    </div>
    <div class="msg-time">{NOW_STR}</div>
    """, unsafe_allow_html=True)
    for icon, label, _ in QUICK_QUESTIONS:
        if st.button(f"{icon}  {label}", key=f"qq_{label}"):
            st.session_state.pending = label
            st.rerun()

# 대화 기록
for i, msg in enumerate(st.session_state.history):
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

        # 피드백 버튼
        fb = st.session_state.feedback.get(i)
        st.markdown('<div class="feedback-row"><span class="feedback-label">도움이 됐나요?</span>', unsafe_allow_html=True)
        fc1, fc2, _ = st.columns([0.4, 0.4, 8])
        with fc1:
            liked = fb == "positive"
            if st.button(f"👍{'✓' if liked else ''}", key=f"like_{i}"):
                st.session_state.feedback[i] = "positive"
                st.rerun()
        with fc2:
            disliked = fb == "negative"
            if st.button(f"👎{'✓' if disliked else ''}", key=f"dislike_{i}"):
                st.session_state.feedback[i] = "negative"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 타이핑 중 + 중지
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

    st.markdown('<div class="typing-col-wrap">', unsafe_allow_html=True)
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

st.markdown('</div>', unsafe_allow_html=True)

# 빠른 답변 버튼
if bot_replied and not st.session_state.is_typing and st.session_state.history[-1]["role"]=="bot":
    st.markdown('<div class="quick-reply-area">', unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.3,1,1,1,1,0.3])
    for col, label, i in zip([c1,c2,c3,c4], QUICK_REPLIES, range(4)):
        with col:
            if st.button(label, key=f"qr_{i}", use_container_width=True):
                if "처음으로" in label:
                    st.session_state.history = []
                    st.rerun()
                else:
                    st.session_state.pending = label
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 사이드 버튼 (내보내기 + 로그아웃)
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.user_id}**")
    if st.session_state.history:
        # 대화 내보내기
        export = f"컴플라이언스 도우미 대화 이력\n날짜: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n" + "="*40 + "\n\n"
        for m in st.session_state.history:
            role = "나" if m["role"]=="user" else "도우미"
            export += f"[{role}]\n{m['content']}\n\n"
        st.download_button("📥 대화 내보내기", export, f"compliance_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt", use_container_width=True)
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# 입력 폼
with st.form(key="chat_form", clear_on_submit=True):
    c1, c2 = st.columns([5,1])
    with c1:
        user_input = st.text_input("질문", placeholder="궁금한 점을 입력하세요...",
                                   label_visibility="collapsed", disabled=st.session_state.is_typing)
    with c2:
        send = st.form_submit_button("전송", use_container_width=True, disabled=st.session_state.is_typing)

# 전송 처리
question = None
if send and user_input.strip():
    question = user_input.strip()
if st.session_state.pending:
    question = st.session_state.pending
    st.session_state.pending = None

if question:
    st.session_state.history.append({"role":"user","content":question})
    st.session_state.is_typing    = True
    st.session_state._api_started = False
    st.rerun()

# 스레딩 API 호출
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
            answer = st.session_state._api_result
            resp_time = time.time() - st.session_state._start_time
            st.session_state.history.append({"role":"bot","content":answer})
            log_audit(st.session_state.history[-2]["content"], resp_time)
        st.session_state.is_typing    = False
        st.session_state._api_started = False
        st.session_state._api_done    = False
        st.session_state._api_result  = None
        st.rerun()
    else:
        time.sleep(0.8)
        st.rerun()

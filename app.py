# ============================================================
# app.py  ─  파리크라상 컴플라이언스 가이드 v2.0 (Paris Baguette)
# 새 기능: 로그인, RAG, 피드백, 대화내보내기, 관리자페이지, 감사로그
# ============================================================
import os, time, json, requests, datetime, threading, base64, io
from zoneinfo import ZoneInfo
import streamlit as st
from PIL import Image


_FAVICON_B64 = "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"
_FAVICON = Image.open(io.BytesIO(base64.b64decode(_FAVICON_B64)))
st.set_page_config(page_title="파리크라상 컴플라이언스 가이드", page_icon=_FAVICON, layout="centered")

# ══════════════════════════════════════════════════════════════
#  공통 CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

:root{
  --pb-navy:#0A1F44;        /* 딥 네이비 */
  --pb-navy-2:#12305F;
  --pb-blue:#1B4A8F;
  --pb-gold:#C9A227;        /* 골드 액센트 */
  --pb-gold-soft:#E9D8A6;
  --pb-ink:#1C2A45;         /* 본문 텍스트 */
  --pb-ink-soft:#54658A;    /* 보조 텍스트 */
  --pb-line:#E7E2D6;        /* 따뜻한 보더 */
  --pb-line-cool:#DCE4F0;
  --pb-card:#FFFFFF;
  --pb-shadow:0 4px 24px rgba(10,31,68,.07);
  --pb-shadow-sm:0 1px 3px rgba(10,31,68,.06);
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,.stApp{font-family:'Noto Sans KR',sans-serif!important}

/* 배경: 차가운 회청 → 따뜻한 아이보리 그라데이션 */
.stApp{
  background:
    radial-gradient(1200px 500px at 50% -10%, #F4EFE2 0%, rgba(244,239,226,0) 60%),
    linear-gradient(180deg,#FBFAF6 0%,#F3F1EA 100%)!important;
}
header[data-testid="stHeader"]{display:none!important}
div[data-testid="stStatusWidget"]{display:none!important}
section[data-testid="stMain"]{padding:0!important}
section[data-testid="stMain"]>div{padding:0!important}
.block-container{padding:0!important;max-width:760px!important}
.stForm{border:none!important}

/* ───────── 헤더 ───────── */
.pb-header{
  background:
    linear-gradient(135deg,var(--pb-navy) 0%,var(--pb-navy-2) 55%,var(--pb-blue) 100%);
  padding:18px 26px;display:flex;align-items:center;justify-content:space-between;gap:12px;
  position:relative;border-bottom:2px solid var(--pb-gold);
  box-shadow:0 6px 22px rgba(10,31,68,.18);
}
.pb-header::after{
  content:"";position:absolute;left:0;right:0;bottom:-2px;height:2px;
  background:linear-gradient(90deg,transparent,var(--pb-gold),transparent);opacity:.9;
}
.pb-header-inner{display:flex;align-items:center;gap:14px;flex:1;min-width:0}
.pb-icon-box{
  width:44px;height:44px;min-width:44px;
  background:linear-gradient(145deg,rgba(201,162,39,.22),rgba(255,255,255,.06));
  border:1px solid rgba(201,162,39,.45);border-radius:13px;
  display:flex;align-items:center;justify-content:center;font-size:1.2rem;
  box-shadow:inset 0 1px 2px rgba(255,255,255,.15);
}
.pb-title{color:#fff;font-size:clamp(1rem,2.6vw,1.18rem);font-weight:800;letter-spacing:-.2px;white-space:nowrap}
.pb-sub{color:var(--pb-gold-soft);font-size:.7rem;font-weight:500;letter-spacing:.04em;white-space:nowrap;margin-top:2px;opacity:.85}
.pb-online{
  background:rgba(255,255,255,.08);border:1px solid rgba(201,162,39,.4);
  border-radius:20px;padding:5px 13px;color:#fff;font-size:.7rem;font-weight:600;
  display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0;
  backdrop-filter:blur(4px);
}
.pb-dot{width:7px;height:7px;background:#4ADE80;border-radius:50%;box-shadow:0 0 6px #4ADE80;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}

/* 상태바 */
.pb-status{
  background:linear-gradient(180deg,#FFFFFF,#FBFAF5);
  border-bottom:1px solid var(--pb-line);
  padding:9px 26px;font-size:.74rem;color:var(--pb-navy);
  display:flex;align-items:center;gap:6px;font-weight:600;letter-spacing:.01em;
}

/* ───────── 채팅 ───────── */
.pb-chat{padding:20px 22px 8px}
.date-badge-wrap{text-align:center;margin:2px 0 18px;position:relative}
.date-badge-wrap::before{
  content:"";position:absolute;top:50%;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--pb-line),transparent);z-index:0;
}
.date-badge{
  position:relative;z-index:1;background:#FBFAF5;color:var(--pb-ink-soft);
  font-size:.7rem;font-weight:600;padding:5px 16px;border-radius:20px;
  border:1px solid var(--pb-line);letter-spacing:.02em;
}
.bot-row{display:flex;gap:11px;margin-bottom:7px;align-items:flex-start}
.bot-avatar{
  width:38px;height:38px;min-width:38px;
  background:linear-gradient(145deg,var(--pb-navy),var(--pb-blue));
  border:1.5px solid var(--pb-gold);border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:.95rem;
  box-shadow:0 3px 10px rgba(10,31,68,.28);
}
.bot-bubble{
  background:var(--pb-card);border-radius:5px 16px 16px 16px;
  padding:15px 18px;max-width:85%;box-shadow:var(--pb-shadow);
  border:1px solid var(--pb-line);
}
.msg-time{font-size:.62rem;color:#A9B2C6;margin-top:4px;margin-left:49px;letter-spacing:.02em}
.msg-time-right{font-size:.62rem;color:#A9B2C6;margin-top:4px;text-align:right;letter-spacing:.02em}
.user-row{display:flex;justify-content:flex-end;margin-bottom:7px}
.user-bubble{
  background:linear-gradient(135deg,var(--pb-navy) 0%,var(--pb-blue) 100%);
  color:#fff;border-radius:16px 5px 16px 16px;padding:13px 17px;max-width:74%;
  font-size:.88rem;line-height:1.6;box-shadow:0 4px 14px rgba(10,31,68,.22);
  border:1px solid rgba(201,162,39,.25);
}
.welcome-text{font-size:.9rem;color:var(--pb-ink);line-height:1.7}

/* ───────── 카드 응답 ───────── */
.card-summary{
  font-size:.92rem;color:var(--pb-navy);line-height:1.65;margin-bottom:13px;
  font-weight:700;padding-bottom:13px;border-bottom:2px solid var(--pb-line);
  position:relative;
}
.card-summary::after{
  content:"";position:absolute;left:0;bottom:-2px;width:48px;height:2px;background:var(--pb-gold);
}
.card-item{display:flex;align-items:flex-start;gap:11px;padding:11px 0;border-bottom:1px solid #F1EEE4}
.card-item:last-of-type{border-bottom:none;padding-bottom:2px}
.ci-icon{
  font-size:.9rem;min-width:26px;height:26px;margin-top:1px;
  display:flex;align-items:center;justify-content:center;
  background:linear-gradient(145deg,#FBF6E8,#F4ECD4);
  border:1px solid var(--pb-gold-soft);border-radius:8px;
}
.ci-title{font-size:.85rem;font-weight:700;color:var(--pb-navy);line-height:1.5;letter-spacing:-.1px}
.ci-desc{font-size:.79rem;color:var(--pb-ink-soft);margin-top:3px;line-height:1.6}
.card-source{
  margin-top:13px;padding-top:11px;border-top:1px solid var(--pb-line);
  font-size:.74rem;color:var(--pb-navy);font-weight:600;
  display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;
}
.source-web{color:#0369A1;background:#E0F2FE;border:1px solid #BAE6FD;border-radius:6px;padding:2px 8px;font-size:.68rem;font-weight:700}
.attach-link{
  background:linear-gradient(135deg,var(--pb-navy),var(--pb-blue));border:1px solid var(--pb-gold);
  color:#fff;border-radius:8px;padding:5px 12px;font-size:.72rem;font-weight:700;
  text-decoration:none;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;
  box-shadow:0 2px 8px rgba(10,31,68,.2);transition:all .18s;
}
.attach-link:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(10,31,68,.3)}
.card-disclaimer{
  margin-top:12px;padding:10px 13px;
  background:linear-gradient(135deg,#FDF8EE,#FBF3DF);
  border:1px solid var(--pb-gold-soft);border-left:3px solid var(--pb-gold);
  border-radius:9px;font-size:.74rem;color:#8A6D1B;font-weight:600;
  display:flex;align-items:center;gap:7px;
}

/* 피드백 버튼 */
[class*="st-key-like_"] button,
[class*="st-key-dislike_"] button{
  background:#FBFAF5!important;border:1px solid var(--pb-line)!important;
  color:var(--pb-ink-soft)!important;box-shadow:none!important;
  padding:3px 13px!important;font-size:.74rem!important;font-weight:600!important;
  min-width:0!important;width:auto!important;height:auto!important;margin:0!important;
  line-height:1.5!important;border-radius:16px!important;
}
[class*="st-key-like_"] button:hover{background:#F4ECD4!important;border-color:var(--pb-gold)!important;color:var(--pb-navy)!important}
[class*="st-key-dislike_"] button:hover{background:#FFF0F0!important;border-color:#dc2626!important;color:#dc2626!important}

/* 타이핑 */
.typing-bubble{
  background:var(--pb-card);border-radius:5px 16px 16px 16px;padding:13px 17px;
  border:1px solid var(--pb-line);box-shadow:var(--pb-shadow-sm);
  display:inline-flex;align-items:center;gap:6px;white-space:nowrap;width:fit-content;
}
.typing-text{font-size:.8rem;color:var(--pb-ink-soft);margin-right:4px}
.timer-tag{font-size:.72rem;color:#6B8CBF;margin-left:4px;font-weight:500}
.dot{width:6px;height:6px;background:var(--pb-gold);border-radius:50%;display:inline-block;animation:bounce 1.2s infinite ease-in-out}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.3}40%{transform:translateY(-5px);opacity:1}}

/* 중지 버튼 */
.typing-col-wrap [data-testid="stHorizontalBlock"]{display:flex!important;align-items:center!important;gap:6px!important;flex-wrap:nowrap!important}
.typing-col-wrap [data-testid="column"]:nth-child(1),
.typing-col-wrap [data-testid="column"]:nth-child(2),
.typing-col-wrap [data-testid="column"]:nth-child(3){flex:0 0 auto!important;width:auto!important;min-width:0!important;padding:0!important}
.typing-col-wrap [data-testid="column"]:nth-child(4){flex:1 1 auto!important}
.stop-col{display:flex;align-items:center}
.stop-col .stButton{display:flex;align-items:center;margin:0}
.stop-col .stButton>button{background:#fff!important;border:1px solid var(--pb-line)!important;color:#dc2626!important;border-radius:5px 16px 16px 16px!important;padding:10px 14px!important;font-size:.79rem!important;font-weight:600!important;white-space:nowrap!important;margin:0!important;height:auto!important;line-height:1.4!important;box-shadow:var(--pb-shadow-sm)!important}
.stop-col .stButton>button:hover{background:#fff0f0!important;border-color:#dc2626!important}

/* ───────── 빠른질문 / 빠른답변 버튼 ───────── */
.stButton>button{
  border-radius:24px!important;border:1.5px solid var(--pb-line-cool)!important;
  background:#FFFFFF!important;color:var(--pb-navy)!important;
  font-size:.83rem!important;font-weight:600!important;padding:9px 18px!important;
  transition:all .2s cubic-bezier(.4,0,.2,1)!important;
  font-family:'Noto Sans KR',sans-serif!important;margin-bottom:5px!important;
  box-shadow:var(--pb-shadow-sm)!important;
}
.stButton>button:hover{
  background:linear-gradient(135deg,var(--pb-navy),var(--pb-blue))!important;
  color:#fff!important;border-color:var(--pb-gold)!important;
  transform:translateY(-2px)!important;box-shadow:0 6px 16px rgba(10,31,68,.22)!important;
}
.quick-reply-area{padding:8px 0 0;margin-bottom:-4px;display:flex;justify-content:center}
.quick-reply-area .stButton>button{padding:8px 14px!important;font-size:.78rem!important;margin:0 3px!important}

/* ───────── 입력창 ───────── */
div[data-testid="stForm"]{
  background:linear-gradient(180deg,#FFFFFF,#FBFAF5)!important;
  border-top:1px solid var(--pb-line)!important;
  padding:14px 18px!important;margin:0!important;
  position:sticky!important;bottom:0!important;z-index:100!important;
  box-shadow:0 -4px 18px rgba(10,31,68,.05)!important;
}
.stTextInput input{
  border-radius:24px!important;border:1.5px solid var(--pb-line-cool)!important;
  padding:11px 19px!important;font-size:.9rem!important;background:#FFFFFF!important;
  color:var(--pb-ink)!important;font-family:'Noto Sans KR',sans-serif!important;
  box-shadow:inset 0 1px 2px rgba(10,31,68,.04)!important;
}
.stTextInput input::placeholder{color:#A9B2C6!important}
.stTextInput input:focus{border-color:var(--pb-gold)!important;box-shadow:0 0 0 3px rgba(201,162,39,.14)!important}
.stFormSubmitButton>button{
  border-radius:24px!important;
  background:linear-gradient(135deg,var(--pb-navy) 0%,var(--pb-blue) 100%)!important;
  color:#fff!important;border:1px solid var(--pb-gold)!important;padding:11px 24px!important;
  font-weight:700!important;font-size:.88rem!important;height:46px!important;
  font-family:'Noto Sans KR',sans-serif!important;box-shadow:0 3px 12px rgba(10,31,68,.25)!important;
  transition:all .2s!important;
}
.stFormSubmitButton>button:hover{
  background:linear-gradient(135deg,#071833,var(--pb-navy))!important;
  transform:translateY(-1px)!important;box-shadow:0 6px 16px rgba(10,31,68,.32)!important;
}

/* ───────── 로그인 ───────── */
.login-wrap{max-width:420px;margin:80px auto;background:var(--pb-card);border-radius:22px;padding:42px;box-shadow:var(--pb-shadow);border:1px solid var(--pb-line)}
.login-logo{text-align:center;margin-bottom:28px}
.login-logo h1{font-size:1.34rem;font-weight:800;color:var(--pb-navy);margin-top:10px;letter-spacing:-.3px}
.login-logo p{font-size:.8rem;color:var(--pb-ink-soft);margin-top:5px}
.login-wrap .stTextInput input{border-radius:13px!important;border:1.5px solid var(--pb-line-cool)!important;background:#FBFAF5!important}
.login-wrap .stFormSubmitButton>button{width:100%;border-radius:13px!important;height:48px!important}

/* 워터마크 */
.pb-watermark{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);z-index:0;pointer-events:none;user-select:none;display:flex;flex-direction:column;align-items:center;gap:6px;opacity:.04}
.pb-watermark-text{font-family:'Noto Sans KR',sans-serif;font-size:clamp(2rem,6vw,3.8rem);font-weight:800;color:var(--pb-navy);letter-spacing:.25em;white-space:nowrap;line-height:1.1}
.pb-watermark-sub{font-family:'Noto Sans KR',sans-serif;font-size:clamp(.6rem,1.8vw,1rem);font-weight:500;color:var(--pb-navy);letter-spacing:.5em;white-space:nowrap}
.pb-watermark-line{width:100%;height:1.5px;background:var(--pb-navy);margin:2px 0}

/* TOP 버튼 */
.top-btn{
  position:fixed;bottom:84px;right:22px;width:44px;height:44px;
  background:linear-gradient(135deg,var(--pb-navy),var(--pb-blue));
  border-radius:50%;border:1.5px solid var(--pb-gold);cursor:pointer;
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.05rem;font-weight:700;
  box-shadow:0 4px 14px rgba(10,31,68,.32);z-index:9999;transition:all .2s;text-decoration:none;
}
.top-btn:hover{transform:translateY(-3px);box-shadow:0 8px 20px rgba(10,31,68,.4)}

/* 관리자 */
.admin-card{background:var(--pb-card);border-radius:16px;padding:22px;margin-bottom:16px;border:1px solid var(--pb-line);box-shadow:var(--pb-shadow-sm)}
.admin-stat{text-align:center}
.admin-stat .num{font-size:2.1rem;font-weight:800;color:var(--pb-navy)}
.admin-stat .lbl{font-size:.78rem;color:var(--pb-ink-soft);margin-top:3px}

/* 상단 로그아웃 버튼: 떠있는 느낌 제거 → 미니멀 텍스트형 */
[class*="st-key-top_logout"] button{
  background:transparent!important;border:1px solid var(--pb-line-cool)!important;
  color:var(--pb-ink-soft)!important;border-radius:20px!important;
  font-size:.76rem!important;font-weight:600!important;padding:5px 14px!important;
  box-shadow:none!important;margin:6px 0 0!important;
}
[class*="st-key-top_logout"] button:hover{
  background:#FBFAF5!important;border-color:var(--pb-gold)!important;
  color:var(--pb-navy)!important;transform:none!important;
}

/* 반응형 */
@media(max-width:640px){
  .block-container{max-width:100%!important}
  .pb-header{padding:14px 16px}
  .pb-title{font-size:.95rem}
  .pb-chat{padding:14px 12px 6px}
  .bot-bubble,.user-bubble{max-width:92%}
  .login-wrap{margin:40px 16px;padding:30px 22px}
  .quick-reply-area .stButton>button{font-size:.72rem!important;padding:6px 9px!important}
  .top-btn{right:12px;bottom:74px}
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
LOGIN_PW  = st.secrets.get("LOGIN_PASSWORD",  "1111")
ADMIN_PW  = st.secrets.get("ADMIN_PASSWORD",  "pbadmin2024")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

QUICK_QUESTIONS = [
    ("🏢", "가맹금이란?",              "가맹금이 무엇인지 알려줘"),
    ("⚖️", "공정거래법 위반 시 제재는?", "공정거래법 위반 시 제재사항을 알려줘"),
    ("📋", "CP란 무엇인가요?",          "컴플라이언스 프로그램(CP)이 무엇인지 알려줘"),
]
QUICK_REPLIES = ["↺ 처음으로", "CP 교육 일정", "관련 법령 보기"]

MASCOT_SVG = """<svg width="100%" height="100%" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
<ellipse cx="100" cy="115" rx="78" ry="58" fill="#F0C36A"/>
<path d="M28 120 Q35 60 100 50 Q165 60 172 120 Q160 145 100 152 Q40 145 28 120 Z" fill="#F6D795"/>
<path d="M45 100 Q55 75 80 70" stroke="#E0AE56" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M120 70 Q145 75 155 100" stroke="#E0AE56" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M55 130 Q65 110 90 105" stroke="#E0AE56" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M110 105 Q135 110 145 130" stroke="#E0AE56" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="78" cy="108" r="7" fill="#3A2B1A"/>
<circle cx="122" cy="108" r="7" fill="#3A2B1A"/>
<circle cx="80" cy="105" r="2.2" fill="#FFFFFF"/>
<circle cx="124" cy="105" r="2.2" fill="#FFFFFF"/>
<ellipse cx="64" cy="124" rx="10" ry="6" fill="#F4A693" opacity="0.55"/>
<ellipse cx="136" cy="124" rx="10" ry="6" fill="#F4A693" opacity="0.55"/>
<path d="M82 128 Q100 142 118 128" stroke="#3A2B1A" stroke-width="3.5" fill="none" stroke-linecap="round"/>
<circle cx="100" cy="156" r="17" fill="#0D3B8E"/>
<circle cx="100" cy="156" r="17" fill="none" stroke="#FFFFFF" stroke-width="2"/>
<path d="M92 156 L98 163 L110 147" stroke="#FFFFFF" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

_mascot_b64 = base64.b64encode(MASCOT_SVG.encode("utf-8")).decode("ascii")
MASCOT_SVG = f'<img src="data:image/svg+xml;base64,{_mascot_b64}" style="width:100%;height:100%;display:block;object-fit:contain" alt="mascot"/>'


@st.cache_resource
def load_and_chunk():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual_text.txt")
    if not os.path.exists(path):
        return "", []
    for enc in ["utf-8","cp949","euc-kr","latin-1"]:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                text = f.read()
            # 문서 제목 추출: [출처: 파일명] 또는 파일명 구분자 파싱
            import re
            chunks = []
            current_title = "파리바게뜨 CP 매뉴얼"
            i = 0
            lines = text.split("\n")
            # 문서 제목 후보 패턴: [출처: xxx], ===xxx=== 안의 파일명
            for line in lines:
                m = re.search(r'\[출처[:\s:：]+([^\]]+)\]', line)
                if m:
                    raw = m.group(1).strip()
                    # 확장자 제거하고 깔끔하게
                    title = re.sub(r'\.(pdf|docx|pptx|xlsx|txt)$', '', raw, flags=re.IGNORECASE).strip()
                    if title:
                        current_title = title
            # 청크 생성 시 현재 문서 제목 추적
            current_title = "파리바게뜨 CP 매뉴얼"
            i = 0
            while i < len(text):
                # 이 위치에서 가장 가까운 출처 헤더 찾기
                snippet = text[max(0,i-200):i]
                m = re.search(r'\[출처[:\s:：]+([^\]]+)\]', snippet)
                if m:
                    raw = m.group(1).strip()
                    title = re.sub(r'\.(pdf|docx|pptx|xlsx|txt)$', '', raw, flags=re.IGNORECASE).strip()
                    if title:
                        current_title = title
                c = text[i:i+800].strip()
                if len(c) > 30:
                    # 청크를 "【문서제목】내용" 형태로 저장
                    chunks.append(f"【{current_title}】{c}")
                i += 600
            return text, chunks
        except Exception:
            continue
    return "", []

MANUAL_TEXT, MANUAL_CHUNKS = load_and_chunk()
MANUAL_CHARS = f"{len(MANUAL_TEXT):,}"

# 약어 확장 사전
ABBR_MAP = {
    "CP": "컴플라이언스 프로그램 CP 준법",
    "cp": "컴플라이언스 프로그램 CP 준법",
    "공정위": "공정거래위원회",
    "가맹법": "가맹사업법 가맹거래법",
    "내부신고": "내부신고 공익신고 신고채널 신고센터",
    "제재": "제재 처벌 과징금 시정조치 형사고발",
    "위약금": "위약금 손해배상액 계약해지 산정",
    "손해액": "손해액 산정 손해배상액 무단폐점",
}

# ── 첨부파일 자동 안내 설정 ──
ATTACHMENT_FILE = "[컴플FAQ Q3.답변첨부파일]무단폐점 점포로 인한 가맹본부의 손해액 산정 방법.xlsx"
ATTACHMENT_KEYWORDS = ["손해액", "위약금", "무단폐점", "손해배상", "산정 방법", "산정방법"]

def needs_attachment(text):
    return any(k in text for k in ATTACHMENT_KEYWORDS)

@st.cache_resource(show_spinner=False)
def get_attachment_bytes():
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, ATTACHMENT_FILE)
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return None

@st.cache_resource(show_spinner=False)
def get_attachment_b64():
    data = get_attachment_bytes()
    return base64.b64encode(data).decode("ascii") if data else None

def get_folder_files():
    """진단용: 현재 폴더의 파일 목록 (xlsx만)"""
    folder = os.path.dirname(os.path.abspath(__file__))
    try:
        return [f for f in os.listdir(folder) if f.lower().endswith((".xlsx",".xls"))]
    except Exception:
        return []

def get_relevant_chunks(query, top_k=20):
    chunks, _ = get_relevant_chunks_with_score(query, top_k)
    return chunks

# ══════════════════════════════════════════════════════════════
#  세션 초기화
# ══════════════════════════════════════════════════════════════
for k,v in [("logged_in",False),("is_admin",False),("user_id",""),
            ("history",[]),("is_typing",False),("pending",None),
            ("_api_done",False),("_api_result",None),
            ("_api_started",False),("_stopped",False),("_start_time",0),
            ("feedback",{}),("audit_log",[]),("login_mode","user")]:
    if k not in st.session_state:
        st.session_state[k] = v

NOW_STR = datetime.datetime.now().strftime("%H:%M")

# ══════════════════════════════════════════════════════════════
#  AI 호출
# ══════════════════════════════════════════════════════════════
def get_relevant_chunks_with_score(query, top_k=20):
    """RAG 검색 + 최고 점수 반환"""
    if not MANUAL_CHUNKS:
        return [], 0
    expanded = query
    for abbr, full in ABBR_MAP.items():
        if abbr in query:
            expanded += " " + full
    clean_q = expanded.replace(" ", "")
    ngrams = {clean_q[i:i+n] for n in [1,2,3,4] for i in range(len(clean_q)-n+1)}
    scored = sorted(((sum(1 for ng in ngrams if ng in c), c) for c in MANUAL_CHUNKS), reverse=True)
    best_score = scored[0][0] if scored else 0
    result = [c for s,c in scored[:top_k] if s > 0]
    if len(result) < 3:
        result = [c for _,c in scored[:25]]
    return result, best_score

def ask_chatbot(question):
    chunks, best_score = get_relevant_chunks_with_score(question)
    hist = "".join(f"{'사용자' if h['role']=='user' else '도우미'}: {h['content']}\n"
                   for h in st.session_state.history[-6:])

    # ── 매뉴얼에 관련 내용이 충분한지 판단 ──
    # 최고 점수가 낮고 유의미 청크가 적으면 웹 검색 모드
    USE_WEB = best_score < 4 or len([c for c in chunks if c]) < 3
    context = "\n\n---\n".join(chunks)

    if USE_WEB:
        # ── 웹 검색 모드: Gemini 내장 Google Search 활용 ──
        prompt = (
            "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
            "내부 매뉴얼에서 관련 정보를 찾지 못했습니다. "
            "Google 검색을 통해 공정거래법, 가맹사업법, 컴플라이언스 관련 최신 정보를 찾아 답변하세요.\n"
            "반드시 신뢰할 수 있는 공식 출처(법제처, 공정거래위원회 등)를 우선 참고하세요.\n"
            "★ 응답: 반드시 JSON만 출력 (다른 텍스트 금지)\n"
            '{"summary":"한줄요약","items":[{"icon":"이모지","title":"항목","desc":"설명"}],"source":"🌐 외부 검색"}\n\n'
            f"[이전 대화]\n{hist}\n\n[질문]\n{question}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
        }
    else:
        # ── 매뉴얼 모드: 내부 자료 기반 답변 ──
        prompt = (
            "당신은 파리바게뜨 컴플라이언스 전문 도우미입니다.\n"
            "아래 자료를 읽고 질문과 관련된 내용을 찾아 답변하세요.\n"
            "자료에 없으면 '담당 부서에 문의해 주세요'로 안내하세요.\n"
            "각 자료 앞에는 【문서제목】이 표시되어 있습니다. source 필드에는 답변에 사용한 문서의 제목만 쓰세요. 페이지 번호는 쓰지 마세요.\n"
            "★ 응답: 반드시 JSON만 출력 (다른 텍스트 금지)\n"
            '{"summary":"한줄요약","items":[{"icon":"이모지","title":"항목","desc":"설명(선택)"}],"source":"문서제목 또는 null"}\n\n'
            f"[관련 자료]\n{context}\n\n[이전 대화]\n{hist}\n\n[질문]\n{question}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # ── 공통 API 호출 ──
    try:
        r = requests.post(GEMINI_URL,
            headers={"Content-Type":"application/json; charset=utf-8"},
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=90)
        res = r.json()
        if "candidates" in res:
            return res["candidates"][0]["content"]["parts"][0]["text"]
        err  = res.get("error", {})
        code = err.get("code", "코드없음")
        stat = err.get("status", "")
        msg  = err.get("message", "메시지없음")
        key_preview = (API_KEY[:6] + "..." + API_KEY[-4:]) if API_KEY else "(비어있음)"
        return json.dumps({
            "summary": f"🔧 [진단] HTTP {r.status_code} / code {code} {stat}",
            "items": [
                {"icon":"📩","title":"구글 원본 메시지","desc":str(msg)[:400]},
                {"icon":"🔑","title":"사용 중인 키","desc":f"{key_preview} (길이 {len(API_KEY)}자)"},
            ],
            "source": None
        }, ensure_ascii=False)
    except requests.exceptions.Timeout:
        return json.dumps({"summary":"🔧 [진단] 네트워크 타임아웃 (90초 초과)","items":[],"source":None}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"summary":"🔧 [진단] 예외 발생","items":[{"icon":"⚠️","title":"오류 종류","desc":f"{type(e).__name__}: {str(e)[:300]}"}],"source":None}, ensure_ascii=False)

def parse_response(raw, attachment=False):
    DISCLAIMER = '<div class="card-disclaimer">⚠️ 최종 법적 판단은 반드시 법무팀에 문의하세요.</div>'

    attach_html = ""
    if attachment:
        b64 = get_attachment_b64()
        if b64:
            attach_html = (
                f'<a class="attach-link" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" '
                f'download="{ATTACHMENT_FILE}">📎 손해액 산정 엑셀</a>'
            )

    clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        data = json.loads(clean)
        html = ""
        if data.get("summary"):
            html += f'<div class="card-summary">{data["summary"]}</div>'
        for item in data.get("items",[]):
            icon,title,desc = item.get("icon","▪"),item.get("title",""),item.get("desc","")
            html += f'<div class="card-item"><span class="ci-icon">{icon}</span><div><div class="ci-title">{title}</div>{"<div class=\"ci-desc\">"+desc+"</div>" if desc else ""}</div></div>'
        if data.get("source") or attach_html:
            src = data.get("source","")
            if src and "외부 검색" in src:
                src_html = '<span class="source-web">🌐 외부 검색 (Google)</span>'
            elif src:
                src_html = f'📄 출처: {src}'
            else:
                src_html = ""
            html += f'<div class="card-source"><span>{src_html}</span>{attach_html}</div>'
        html += DISCLAIMER
        return html
    except Exception:
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        body = "".join(f'<div class="card-item"><span class="ci-icon">▪</span><div class="ci-title">{l}</div></div>' for l in lines) or f'<div style="font-size:.88rem;line-height:1.7;color:#1A2B5F">{raw}</div>'
        if attach_html:
            body += f'<div class="card-source"><span></span>{attach_html}</div>'
        return body + DISCLAIMER

def log_audit(question, resp_time):
    st.session_state.audit_log.append({
        "시간": datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
        "사번": st.session_state.user_id,
        "질문": question[:80],
        "응답시간(초)": round(resp_time, 1),
    })

# ══════════════════════════════════════════════════════════════
#  로그인 페이지
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    # 로그인 모드 토글 CSS
    st.markdown("""
    <style>
    .login-outer{max-width:440px;margin:60px auto 0}
    .login-card{background:white;border-radius:20px;padding:36px 32px 28px;box-shadow:0 8px 32px rgba(13,49,136,.13);margin-bottom:0}
    .login-logo-area{text-align:center;margin-bottom:24px}
    .login-logo-area h1{font-size:1.25rem;font-weight:800;color:#0B2461;margin-top:10px}
    .login-logo-area p{font-size:.78rem;color:#6B8CBF;margin-top:3px}
    .mode-toggle{display:flex;background:#EEF2FF;border-radius:12px;padding:4px;margin-bottom:22px;gap:4px}
    .mode-btn{flex:1;text-align:center;padding:9px;border-radius:9px;font-size:.83rem;font-weight:600;cursor:pointer;transition:all .2s;color:#6B8CBF}
    .mode-btn.active{background:white;color:#0B2461;box-shadow:0 2px 8px rgba(13,49,136,.12)}
    .cred-hint{background:#F0F5FF;border:1px solid #C5D5EE;border-radius:10px;padding:10px 14px;margin-bottom:16px;font-size:.78rem;color:#3B5EA6}
    .cred-hint b{color:#0B2461}
    .login-card .stTextInput input{border-radius:12px!important;border:1.5px solid #C5D5EE!important;background:#F5F8FF!important;height:46px!important}
    .login-card .stFormSubmitButton>button{width:100%;border-radius:12px!important;height:48px!important;font-size:.95rem!important}
    </style>
    <div class="login-outer">
      <div class="login-card">
        <div class="login-logo-area">
          <div style="width:64px;height:64px;margin:0 auto">👾</div>
          <h1>파리크라상 컴플라이언스 가이드</h1>
          <p>사내 CP 자료 기반 &nbsp;·&nbsp; 임직원 전용</p>
        </div>
      </div>
    </div>
    """.replace("👾", MASCOT_SVG), unsafe_allow_html=True)

    # 모드 선택 버튼
    col_u, col_a = st.columns(2)
    with col_u:
        if st.button("👤 일반 사용자", use_container_width=True,
                     type="primary" if st.session_state.login_mode=="user" else "secondary",
                     key="mode_user"):
            st.session_state.login_mode = "user"
            st.rerun()
    with col_a:
        if st.button("⚙️ 관리자", use_container_width=True,
                     type="primary" if st.session_state.login_mode=="admin" else "secondary",
                     key="mode_admin"):
            st.session_state.login_mode = "admin"
            st.rerun()

    is_admin_mode = st.session_state.login_mode == "admin"

    # 로그인 안내
    if is_admin_mode:
        st.info("🔐 **관리자 전용** — 통계 · 문서 관리 · 감사 로그에 접근할 수 있습니다.")
    else:
        st.info("💡 **일반 사용자** — ID: 사번 입력 / PW: **1111**")

    # 입력칸 콤팩트 CSS
    st.markdown("""
    <style>
    .login-form-narrow { max-width: 230px; }
    .login-form-narrow .stTextInput input {
        max-width: 180px !important;
        font-size: .85rem !important;
        height: 38px !important;
        padding: 6px 12px !important;
    }
    .login-form-narrow [data-testid="stForm"] {
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
    }
    .login-form-narrow .stFormSubmitButton > button {
        max-width: 180px !important;
        border-radius: 10px !important;
        height: 40px !important;
        font-size: .85rem !important;
        padding: 6px 14px !important;
    }
    .field-label {
        font-size: .8rem; font-weight: 700;
        color: #0B2461; margin-bottom: 2px; margin-top: 8px;
    }
    </style>
    <div class="login-form-narrow">
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown('<div class="field-label">ID (사번)</div>', unsafe_allow_html=True)
        emp_id = st.text_input("ID", placeholder="사번 입력",
                               label_visibility="collapsed")
        st.markdown(
            '<div class="field-label">PW (관리자 비밀번호)</div>' if is_admin_mode
            else '<div class="field-label">PW (1111)</div>',
            unsafe_allow_html=True)
        password = st.text_input(
            "PW", type="password",
            placeholder="비밀번호 입력" if is_admin_mode else "1111",
            label_visibility="collapsed")
        submitted = st.form_submit_button(
            "⚙️ 관리자 로그인" if is_admin_mode else "👤 로그인",
            use_container_width=False)

        if submitted:
            if is_admin_mode and password == ADMIN_PW:
                st.session_state.logged_in = True
                st.session_state.is_admin  = True
                st.session_state.user_id   = emp_id or "admin"
                st.rerun()
            elif not is_admin_mode and password == LOGIN_PW:
                st.session_state.logged_in = True
                st.session_state.user_id   = emp_id or "unknown"
                st.rerun()
            else:
                st.error("ID 또는 비밀번호가 올바르지 않습니다.")

    st.markdown('</div>', unsafe_allow_html=True)
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

    # 탭 메뉴 글자색 (안 보이는 문제 해결)
    st.markdown("""
    <style>
    /* 관리자 탭 글자 */
    .stTabs [data-baseweb="tab"] { color: #1A2B5F !important; font-weight: 600 !important; font-size:.9rem !important; }
    .stTabs [aria-selected="true"] { color: #0D3188 !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #0D3188 !important; }
    /* 관리자 페이지 전체 글자색 */
    .admin-card p, .admin-card div, .admin-card span,
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] label,
    section[data-testid="stMain"] span { color: #1A2B5F !important; }
    section[data-testid="stMain"] h1,
    section[data-testid="stMain"] h2,
    section[data-testid="stMain"] h3 { color: #0B2461 !important; }
    /* 문서관리 탭 텍스트 */
    [data-testid="stMarkdownContainer"] p { color: #1A2B5F !important; }
    [data-testid="stMarkdownContainer"] strong { color: #0B2461 !important; }
    .stFileUploader label, .stFileUploader span { color: #1A2B5F !important; }
    .stTextArea label { color: #1A2B5F !important; }
    .stInfo { color: #1A2B5F !important; }
    </style>
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
        # 현재 문서 상태
        st.markdown(f"""
        <div style="background:#F0F5FF;border:1px solid #C5D5EE;border-radius:10px;padding:14px 18px;margin-bottom:14px">
          <div style="font-size:.8rem;font-weight:700;color:#0B2461;margin-bottom:6px">현재 문서 상태</div>
          <div style="font-size:.85rem;color:#1A2B5F">📄 manual_text.txt &nbsp;—&nbsp; 총 {MANUAL_CHARS}자 &nbsp;/&nbsp; {len(MANUAL_CHUNKS)}개 청크</div>
        </div>
        <div style="background:#F0F5FF;border:1px solid #C5D5EE;border-radius:10px;padding:14px 18px">
          <div style="font-size:.8rem;font-weight:700;color:#0B2461;margin-bottom:4px">새 문서 업로드</div>
          <div style="font-size:.78rem;color:#4A6899;margin-bottom:10px">PDF, DOCX, PPTX, XLSX, TXT 파일을 업로드하면 내용을 추출해 미리보기를 제공합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        # 파일 업로더 글자색
        st.markdown("""
        <style>
        /* 파일 업로더 전체 */
        [data-testid="stFileUploader"] { background: transparent !important; }
        [data-testid="stFileUploader"] label p { color: #1A2B5F !important; font-weight:600 !important; }
        [data-testid="stFileUploader"] section {
            border: 1.5px dashed #0D3188 !important;
            background: #EEF2FF !important;
        }
        /* Upload 버튼 - 흰 배경 + 파란 글자 */
        [data-testid="stFileUploader"] section button,
        [data-testid="stFileUploader"] section > button {
            background-color: white !important;
            background: white !important;
            color: #0D3188 !important;
            border: 1.5px solid #0D3188 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }
        [data-testid="stFileUploader"] section button *,
        [data-testid="stFileUploader"] section button span,
        [data-testid="stFileUploader"] section button p,
        [data-testid="stFileUploader"] section button div {
            color: #0D3188 !important;
            fill: #0D3188 !important;
        }
        [data-testid="stFileUploader"] section button svg {
            fill: #0D3188 !important;
            stroke: #0D3188 !important;
        }
        /* 안내 텍스트 */
        [data-testid="stFileUploaderDropzoneInstructions"],
        [data-testid="stFileUploaderDropzoneInstructions"] *,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stFileUploaderDropzone"] p {
            color: #1A2B5F !important;
        }
        </style>
        """, unsafe_allow_html=True)
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
    <div class="pb-icon-box">👾</div>
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
""".replace("👾", MASCOT_SVG), unsafe_allow_html=True)

# 로그아웃 버튼 (헤더 바로 아래 우측)
hcol1, hcol2 = st.columns([7, 1.3])
with hcol2:
    if st.button("🚪 로그아웃", use_container_width=True, key="top_logout"):
        st.session_state.logged_in = False
        st.session_state.history   = []
        st.rerun()

bot_replied = any(m["role"]=="bot" for m in st.session_state.history)
TODAY_STR = datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y년 %m월 %d일 (%a)")

st.markdown('<div class="pb-chat">', unsafe_allow_html=True)

# 상단 날짜 배지
st.markdown(f'<div class="date-badge-wrap"><span class="date-badge">{TODAY_STR}</span></div>', unsafe_allow_html=True)

# 환영 + 빠른 질문
if not bot_replied:
    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">👾</div>
      <div class="bot-bubble">
        <div class="welcome-text">안녕하세요! 파리크라상 컴플라이언스 가이드입니다.<br>궁금한 점을 질문해 주세요.</div>
      </div>
    </div>
    <div class="msg-time">{NOW_STR}</div>
    """.replace("👾", MASCOT_SVG), unsafe_allow_html=True)
    for icon, label, _ in QUICK_QUESTIONS:
        if st.button(f"{icon}  {label}", key=f"qq_{label}"):
            st.session_state.pending = label
            st.rerun()

# 대화 기록
for i, msg in enumerate(st.session_state.history):
    msg_time = msg.get("time", NOW_STR)
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-row"><div class="user-bubble">{msg["content"]}</div></div>
        <div class="msg-time-right">{msg_time}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-row">
          <div class="bot-avatar">👾</div>
          <div class="bot-bubble">{parse_response(msg["content"], msg.get("attachment", False))}</div>
        </div>
        <div class="msg-time">{msg_time}</div>
        """.replace("👾", MASCOT_SVG), unsafe_allow_html=True)

        if msg.get("attachment") and not get_attachment_b64():
            found = get_folder_files()
            st.markdown(
                '<div style="margin:4px 0 6px 45px;font-size:.74rem;color:#9A3412;background:#FFF7ED;'
                'border:1px solid #FED7AA;border-radius:8px;padding:8px 12px">'
                '⚠️ 첨부 엑셀 파일을 찾을 수 없어요. 파일이 GitHub 저장소(app.py와 같은 폴더)에 '
                '업로드되어 있는지 확인해주세요.<br>'
                f'기대한 파일명: <code>{ATTACHMENT_FILE}</code><br>'
                f'폴더에서 발견된 xlsx 파일: {found if found else "없음"}'
                '</div>', unsafe_allow_html=True)

        # 피드백 버튼 (한글 텍스트)


# 타이핑 중 표시
if st.session_state.is_typing:
    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">👾</div>
      <div class="typing-bubble">
        <span class="typing-text">답변 생성 중</span>
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>
    """.replace("👾", MASCOT_SVG), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 빠른 답변 버튼
if bot_replied and not st.session_state.is_typing and st.session_state.history[-1]["role"]=="bot":
    st.markdown('<div class="quick-reply-area">', unsafe_allow_html=True)
    _, c1, c2, c3, _ = st.columns([0.5,1,1,1,0.5])
    for col, label, i in zip([c1,c2,c3], QUICK_REPLIES, range(3)):
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
        export = f"파리크라상 컴플라이언스 가이드 대화 이력\n날짜: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n" + "="*40 + "\n\n"
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
    st.session_state.history.append({"role":"user","content":question,"time":datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H:%M")})
    st.session_state.is_typing = True
    st.rerun()

# ── API 직접 호출 (스레드 없이) ──
# 스레드 방식은 Streamlit에서 session_state 전달이 불안정해 답변이 사라지는
# 문제가 있어, 질문을 받으면 그 자리에서 바로 API를 호출하도록 단순화함.
if st.session_state.is_typing:
    last_q = next((m["content"] for m in reversed(st.session_state.history) if m["role"]=="user"), None)
    if last_q:
        start = time.time()
        answer = ask_chatbot(last_q)            # 여기서 동기 호출 (스피너는 이미 위에 표시됨)
        resp_time = time.time() - start
        st.session_state.history.append({
            "role": "bot",
            "content": answer,
            "time": datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H:%M"),
            "attachment": needs_attachment(last_q),
        })
        log_audit(last_q, resp_time)
    st.session_state.is_typing = False
    st.rerun()

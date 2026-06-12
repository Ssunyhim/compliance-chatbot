# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
# ============================================================
import streamlit as st
import streamlit.components.v1 as components
import datetime, json, requests, pandas as pd, time, calendar, base64, io
from zoneinfo import ZoneInfo
from PIL import Image


_FAVICON_B64 = "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"
_FAVICON = Image.open(io.BytesIO(base64.b64decode(_FAVICON_B64)))
st.set_page_config(
    page_title="CP 컴플라이언스 대시보드",
    page_icon=_FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
KST   = ZoneInfo("Asia/Seoul")
NOW   = datetime.datetime.now(KST)
TODAY = NOW.strftime("%Y년 %m월 %d일 (%a)")

# ══════════════════════════════════════════════════════════════
#  1. 사이드바 설정 (진짜 st.sidebar)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { background:#F7FAFF !important; }
    section[data-testid="stSidebar"] label { color:#0D3B8E !important; font-weight:600 !important; font-size:.82rem !important; }
    section[data-testid="stSidebar"] p { color:#1A2B5F !important; font-size:.82rem !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 { color:#0B2461 !important; }
    section[data-testid="stSidebar"] .stNumberInput input { color:#1A2B5F !important; background:white !important; border:1.5px solid #BEE3F8 !important; border-radius:6px !important; }
    section[data-testid="stSidebar"] .stTextInput input { color:#1A2B5F !important; background:white !important; border:1.5px solid #BEE3F8 !important; border-radius:6px !important; }
    section[data-testid="stSidebar"] .stButton button { background:#0D3B8E !important; color:white !important; border:none !important; border-radius:8px !important; font-weight:600 !important; }
    section[data-testid="stSidebar"] .stButton button p { color:white !important; }

    /* expander (📌 구글 시트 설정 방법) */
    section[data-testid="stSidebar"] .stExpander details summary {
        background:#EBF4FF !important;
        border:1.5px solid #BEE3F8 !important;
        border-radius:8px !important;
        padding:8px 12px !important;
    }
    section[data-testid="stSidebar"] .stExpander details summary p,
    section[data-testid="stSidebar"] .stExpander details summary span {
        color:#0D3B8E !important;
        font-weight:700 !important;
    }
    section[data-testid="stSidebar"] .stExpander [data-testid="stExpanderToggleIcon"] {
        color:#0D3B8E !important;
    }
    section[data-testid="stSidebar"] .stExpander details[open] summary {
        border-radius:8px 8px 0 0 !important;
    }
    section[data-testid="stSidebar"] .stExpander details > div {
        background:white !important;
        border:1.5px solid #BEE3F8 !important;
        border-top:none !important;
        border-radius:0 0 8px 8px !important;
        padding:10px 12px !important;
    }
    section[data-testid="stSidebar"] .stExpander details > div p,
    section[data-testid="stSidebar"] .stExpander details > div li {
        color:#1A2B5F !important;
        font-size:.78rem !important;
    }
    section[data-testid="stSidebar"] .stExpander details > div code {
        color:#0D3B8E !important;
        background:#EBF4FF !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display:none !important; }

    /* ── 사이드바 접기/펼치기 버튼 ── */
    /* 펼쳐진 상태: 사이드바 헤더의 << 버튼 */
    [data-testid="stSidebarCollapseButton"] button,
    section[data-testid="stSidebar"] button[kind="header"] {
        background:#EBF4FF !important;
        border:1.5px solid #BEE3F8 !important;
        border-radius:8px !important;
        z-index:1000000 !important;
    }
    [data-testid="stSidebarCollapseButton"] button svg,
    section[data-testid="stSidebar"] button[kind="header"] svg {
        fill:#0D3B8E !important;
        color:#0D3B8E !important;
    }
    /* 접힌 상태: 화면 좌측 상단 > 버튼 */
    [data-testid="collapsedControl"] {
        z-index:1000000 !important;
        background:#0D3B8E !important;
        border-radius:8px !important;
        box-shadow:0 2px 8px rgba(13,59,142,.35) !important;
    }
    [data-testid="collapsedControl"] svg {
        fill:white !important;
        color:white !important;
    }
    [data-testid="collapsedControl"]:hover {
        background:#1A56C4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## ⚙️ 데이터 설정")
    st.caption("숫자 변경 → Enter 치면 자동 반영돼요")
    st.divider()

    st.markdown("#### 📋 KPI 직접 입력")
    kpi_goal   = st.number_input("CP 목표 건수",  value=40,  min_value=1)
    kpi_actual = st.number_input("CP 실적 건수",  value=19,  min_value=0)
    kpi_sign   = st.number_input("내부신고 건수", value=12,  min_value=0)
    kpi_law    = st.number_input("법령검토 누적", value=350, min_value=0)
    kpi_ftc    = st.number_input("공정거래 검토", value=761, min_value=0)
    st.divider()

    st.markdown("#### 📰 뉴스 키워드")
    news_kw  = st.text_input("뉴스 검색어",         value="가맹사업 법령위반")
    press_kw = st.text_input("공정위/식약처 키워드", value="가맹 공정거래")
    st.divider()

    st.markdown("#### 📊 구글 시트 연동")
    st.caption("시트 → 파일 → 웹에 게시 → CSV URL")
    gs_cp   = st.text_input("CP 운영현황",    placeholder="...export?format=csv")
    gs_sign = st.text_input("내부신고 현황",  placeholder="...export?format=csv")
    gs_law  = st.text_input("법령검토 건수",  placeholder="...export?format=csv")
    gs_ftc  = st.text_input("공정거래 법령별",placeholder="...export?format=csv")
    gs_tl   = st.text_input("타임라인",       placeholder="...export?format=csv")
    st.divider()

    if st.button("🔄 캐시 초기화", use_container_width=True):
        st.cache_data.clear()
        st.success("완료!")

    with st.expander("📌 구글 시트 설정 방법"):
        st.markdown("""
1. 구글 시트 열기  
2. **파일 → 공유 → 웹에 게시**  
3. 형식: **CSV** → 게시  
4. URL 복사 → 위 입력칸에 붙여넣기  

**컬럼 형식**  
`구분,내용,목표,실적,달성률,상태,주요활동`  
`월,신고건수,처리완료,진행중`  
`월,누적건수` / `법령명,건수`  
`구분,날짜,내용`
        """)

kpi_pct = int(kpi_actual / kpi_goal * 100) if kpi_goal else 0

# 귀여운 크루아상 캐릭터 (파리크라상)
_MASCOT_SVG_RAW = """<svg width="100%" height="100%" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
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
_mascot_b64 = base64.b64encode(_MASCOT_SVG_RAW.encode("utf-8")).decode("ascii")
MASCOT_IMG = f'<img src="data:image/svg+xml;base64,{_mascot_b64}" style="width:30px;height:30px;display:block;object-fit:contain;border-radius:6px" alt="mascot"/>'

# 뉴스/보도자료 새로고침 & 정렬 상태
for k, v in [("news_refresh",0),("press_refresh",0),("news_sort","관련도순"),("press_sort","관련도순")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
#  2. 데이터 로딩 — 매일 오전 10시(KST) 기준 갱신
# ══════════════════════════════════════════════════════════════
def get_news_cache_key():
    """오전 10시 이전이면 전날 날짜, 이후면 당일 날짜를 캐시 키로 반환"""
    cutoff = NOW.replace(hour=10, minute=0, second=0, microsecond=0)
    ref = NOW if NOW >= cutoff else NOW - datetime.timedelta(days=1)
    return ref.strftime("%Y-%m-%d")

NEWS_CACHE_KEY = get_news_cache_key()
NEWS_UPDATE_LABEL = f"{NEWS_CACHE_KEY} 10:00 기준"

@st.cache_data(ttl=25*3600, show_spinner=False)
def fetch_news(keyword, cache_key, refresh_token):
    try:
        import feedparser
        q = requests.utils.quote(keyword)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko")
        res = []
        for e in feed.entries[:8]:
            t = e.get("title",""); p = t.rsplit(" - ",1)
            pp = e.get("published_parsed")
            ts = calendar.timegm(pp) if pp else 0
            res.append({
                "title":p[0].strip(),
                "link":e.get("link","#"),
                "source":p[1].strip() if len(p)>1 else "",
                "ts": ts,
                "date": e.get("published","")[:16],
            })
        label = NEWS_UPDATE_LABEL if refresh_token == 0 else NOW.strftime("%Y-%m-%d %H:%M") + " 즉시갱신"
        return res, label
    except: return [], None

@st.cache_data(ttl=25*3600, show_spinner=False)
def fetch_press(keyword, cache_key, refresh_token):
    try:
        import feedparser
        res = []
        for q_txt, src in [("공정거래위원회 "+keyword,"공정거래위원회"),("식품의약품안전처 가맹","식품의약품안전처")]:
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={requests.utils.quote(q_txt)}&hl=ko&gl=KR&ceid=KR:ko")
            for e in feed.entries[:5]:
                t = e.get("title","").rsplit(" - ",1)[0].strip()
                pp = e.get("published_parsed")
                ts = calendar.timegm(pp) if pp else 0
                res.append({
                    "title":t,
                    "link":e.get("link","#"),
                    "date":e.get("published","")[:10],
                    "source":src,
                    "ts": ts,
                })
        label = NEWS_UPDATE_LABEL if refresh_token == 0 else NOW.strftime("%Y-%m-%d %H:%M") + " 즉시갱신"
        return res, label
    except: return [], None

@st.cache_data(ttl=3600, show_spinner=False)
def load_gs(url):
    if not url or not url.startswith("http"): return None
    try: return pd.read_csv(url)
    except: return None

DEFAULT_CP = [
    {"구분":"구축","내용":"대표이사 의지표명","목표":4,"실적":5,"달성률":125,"상태":"완료","주요활동":"자율준수 선서식, 컨퍼런스"},
    {"구분":"구축","내용":"CP 확산활동","목표":4,"실적":4,"달성률":100,"상태":"완료","주요활동":"대표이사 CP 영상 제작"},
    {"구분":"교육","내용":"CP 교육","목표":20,"실적":6,"달성률":30,"상태":"진행","주요활동":"신입·입직IP 교육 예정"},
    {"구분":"교육","내용":"CP 규정","목표":2,"실적":None,"달성률":None,"상태":"계획","주요활동":"개정 진행중"},
    {"구분":"운영","내용":"위험성평가","목표":4,"실적":1,"달성률":25,"상태":"진행","주요활동":"개선방안 도출(04/22)"},
    {"구분":"운영","내용":"자율준수협의회","목표":2,"실적":1,"달성률":50,"상태":"완료","주요활동":"공정거래실신 서"},
    {"구분":"평가","내용":"효과성평가","목표":2,"실적":2,"달성률":100,"상태":"완료","주요활동":"개선방안 도출(04/27)"},
    {"구분":"평가","내용":"사업부 현장컨설팅","목표":2,"실적":None,"달성률":None,"상태":"계획","주요활동":"진행 협의 중"},
]
DEFAULT_SIGN = [{"월":"1월","신고건수":2,"처리완료":2,"진행중":0},{"월":"2월","신고건수":3,"처리완료":3,"진행중":0},{"월":"3월","신고건수":4,"처리완료":4,"진행중":0},{"월":"4월","신고건수":3,"처리완료":2,"진행중":1}]
DEFAULT_LAW  = [{"월":"1월","누적건수":82},{"월":"2월","누적건수":175},{"월":"3월","누적건수":268},{"월":"4월","누적건수":350}]
DEFAULT_FTC  = [{"법령명":"가맹사업법","건수":594},{"법령명":"약관법","건수":78},{"법령명":"공정거래법","건수":35},{"법령명":"하도급법","건수":27}]
DEFAULT_TL   = [
    {"구분":"구축/확산","날짜":"01/30","내용":"자율준수 선서식"},
    {"구분":"구축/확산","날짜":"04/20","내용":"CP 영상 배포"},
    {"구분":"구축/확산","날짜":"04/16","내용":"컨퍼런스 참가"},
    {"구분":"교육","날짜":"04/16","내용":"임원 교육"},
    {"구분":"교육","날짜":"04/23","내용":"사전업무협의체 교육"},
    {"구분":"교육","날짜":"04/29","내용":"IP 실무자 교육"},
    {"구분":"운영/평가","날짜":"04/22","내용":"위험성평가 결과보고"},
    {"구분":"운영/평가","날짜":"04/27","내용":"효과성평가 결과보고"},
    {"구분":"운영/평가","날짜":"04/11","내용":"1분기 CP 서비스 보고"},
]

df_cp  = load_gs(gs_cp);  cp_data  = df_cp.to_dict("records")  if df_cp  is not None else DEFAULT_CP
df_sign= load_gs(gs_sign);sign_data= df_sign.to_dict("records")if df_sign is not None else DEFAULT_SIGN
df_law = load_gs(gs_law); law_data = df_law.to_dict("records") if df_law  is not None else DEFAULT_LAW
df_ftc = load_gs(gs_ftc); ftc_data = df_ftc.to_dict("records") if df_ftc  is not None else DEFAULT_FTC
df_tl  = load_gs(gs_tl);  tl_data  = df_tl.to_dict("records")  if df_tl   is not None else DEFAULT_TL

# ══════════════════════════════════════════════════════════════
#  3. 전체 CSS + 고정 네비 (가장 핵심)
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,.stApp{{font-family:'Noto Sans KR',sans-serif!important}}
.stApp{{background:#F0F4F8!important}}
header[data-testid="stHeader"]{{display:none!important}}
div[data-testid="stStatusWidget"]{{display:none!important}}
.block-container{{padding:20px 24px 40px!important;max-width:100%!important}}

/* ── 핵심: stMain을 overflow visible로 해서 fixed 가능하게 ── */
/* 기본 Streamlit 스크롤 유지 - overflow 건드리지 않음 */

/* ── 상단 네비 (JS로 body 최상위로 이동시켜 진짜 고정) ── */
#pb-nav.dash-nav{{
    position:fixed!important;top:0!important;left:0!important;right:0!important;
    z-index:100!important;
    background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%)!important;
    padding:0 24px!important;
    display:flex!important;align-items:center!important;justify-content:space-between!important;
    height:52px!important;
    box-shadow:0 2px 12px rgba(6,27,74,.3)!important;
    margin:0!important;
}}
.nav-left{{display:flex;align-items:center;gap:12px}}
.nav-title{{color:white;font-size:1rem;font-weight:800}}
.nav-badge{{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 10px;color:rgba(255,255,255,.85);font-size:.68rem;font-weight:600}}
.nav-links{{display:flex;gap:2px}}
.nav-btn{{background:transparent;border:none;color:rgba(255,255,255,.7);padding:7px 14px;border-radius:6px;font-size:.76rem;font-weight:600;cursor:pointer;font-family:'Noto Sans KR',sans-serif;transition:all .15s;white-space:nowrap;text-decoration:none;display:inline-block}}
.nav-btn:hover{{background:rgba(255,255,255,.15);color:white}}
.nav-settings{{background:#FFD700!important;color:#0B2461!important;font-weight:800!important;border-radius:6px!important;}}
.nav-settings:hover{{background:#FFC400!important;color:#0B2461!important}}
.nav-date{{color:rgba(255,255,255,.55);font-size:.7rem;white-space:nowrap}}

/* 네비가 가리는 만큼 본문 위쪽 여백 */
.nav-spacer{{height:60px}}

/* 섹션 */
.sec-anchor{{display:block;position:relative;top:-66px;visibility:hidden}}
.sec-title{{font-size:.95rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:8px;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #E2E8F0;margin-top:20px}}
.card{{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;margin-bottom:16px}}
.card-head{{font-size:.84rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:7px;border-bottom:1px solid #EDF2F7;padding-bottom:10px;margin-bottom:12px}}
.insight{{background:linear-gradient(135deg,#1A365D,#2B6CB0);border-radius:12px;padding:18px 22px;margin-bottom:18px}}
.insight-t{{color:white;font-size:.92rem;font-weight:700;margin-bottom:6px}}
.insight-txt{{color:rgba(255,255,255,.82);font-size:.78rem;line-height:1.6;margin-bottom:10px}}
.chip{{display:inline-block;border-radius:20px;padding:3px 11px;font-size:.69rem;font-weight:600;margin:2px 3px 2px 0}}
.chip-warn{{background:rgba(255,87,51,.22);border:1px solid rgba(255,87,51,.45);color:#FED7CC}}
.chip-ok{{background:rgba(52,211,153,.18);border:1px solid rgba(52,211,153,.38);color:#C6F6D5}}
.kpi{{background:white;border-radius:12px;padding:18px 20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;position:relative;overflow:hidden}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px}}
.kpi.b::before{{background:linear-gradient(90deg,#0D3B8E,#1A56C4)}}
.kpi.g::before{{background:linear-gradient(90deg,#22863a,#28a745)}}
.kpi.o::before{{background:linear-gradient(90deg,#d45500,#f77f00)}}
.kpi.r::before{{background:linear-gradient(90deg,#c0392b,#e74c3c)}}
.kpi-lbl{{font-size:.68rem;font-weight:700;color:#718096;letter-spacing:.5px;margin-bottom:7px}}
.kpi-val{{font-size:2rem;font-weight:800;color:#1A2B5F;line-height:1;margin-bottom:5px}}
.kpi-val span{{font-size:.95rem;font-weight:600;color:#4A5568}}
.kpi-sub{{font-size:.71rem;color:#718096;margin-bottom:8px}}
.kpi-bar{{height:4px;background:#E8EDF5;border-radius:2px;overflow:hidden}}
.kpi-fill{{height:100%;border-radius:2px}}
.news-row{{display:flex;align-items:flex-start;gap:8px;padding:7px 0;border-bottom:1px dashed #EDF2F7}}
.news-row:last-child{{border-bottom:none}}
.news-n{{min-width:20px;height:20px;background:#EBF4FF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.6rem;font-weight:700;color:#0D3B8E;flex-shrink:0;margin-top:1px}}
.news-t{{font-size:.78rem;color:#1A2B5F;text-decoration:none;line-height:1.45;flex:1}}
.news-t:hover{{color:#0D3B8E;text-decoration:underline}}
.news-src{{font-size:.63rem;color:#A0AEC0;margin-top:2px}}
.press{{background:#F7FAFF;border:1px solid #BEE3F8;border-radius:8px;padding:11px 13px;margin-bottom:7px}}
.press-d{{font-size:.65rem;color:#3182CE;font-weight:600;margin-bottom:3px}}
.press-t{{font-size:.78rem;color:#1A2B5F;text-decoration:none;font-weight:600;line-height:1.4;display:block}}
.press-t:hover{{color:#0D3B8E}}
.badge{{display:inline-flex;align-items:center;gap:4px;border-radius:6px;padding:3px 8px;font-size:.63rem;font-weight:600;margin-bottom:8px;background:#FEEBC8;color:#744210}}
.no-data{{text-align:center;padding:20px;color:#A0AEC0;font-size:.8rem}}

/* 뉴스 툴바 (갱신/정렬) - 정렬 드롭다운과 동일한 크기/폰트 */
[class*="st-key-news_refresh_btn"] button,
[class*="st-key-press_refresh_btn"] button {{
    background:#EBF4FF!important;border:1px solid #BEE3F8!important;color:#0D3B8E!important;
    border-radius:6px!important;font-size:.68rem!important;font-weight:700!important;
    font-family:'Noto Sans KR',sans-serif!important;line-height:1!important;
    height:30px!important;min-height:30px!important;padding:0 6px!important;
    width:100%!important;min-width:0!important;
}}
[class*="st-key-news_refresh_btn"] button:hover,
[class*="st-key-press_refresh_btn"] button:hover {{
    background:#0D3B8E!important;color:#fff!important;border-color:#0D3B8E!important;
}}
[class*="st-key-news_sort_sel"] div[data-baseweb="select"]>div,
[class*="st-key-press_sort_sel"] div[data-baseweb="select"]>div {{
    background:#EBF4FF!important;border:1px solid #BEE3F8!important;border-radius:6px!important;
    min-height:30px!important;height:30px!important;
}}
[class*="st-key-news_sort_sel"] div[data-baseweb="select"] *,
[class*="st-key-press_sort_sel"] div[data-baseweb="select"] * {{
    color:#0D3B8E!important;font-size:.68rem!important;font-weight:700!important;
    font-family:'Noto Sans KR',sans-serif!important;line-height:1!important;
}}
[class*="st-key-news_refresh_btn"],[class*="st-key-press_refresh_btn"],
[class*="st-key-news_sort_sel"],[class*="st-key-press_sort_sel"] {{
    margin-top:0!important;margin-bottom:4px!important;
}}
.cp-table{{width:100%;border-collapse:collapse;font-size:13px}}
.cp-table th{{background:#EDF2F7;color:#4A5568;font-weight:700;padding:9px 10px;text-align:center;font-size:11px;border:1px solid #E2E8F0}}
.cp-table td{{padding:8px 10px;border:1px solid #E2E8F0;color:#2D3748;text-align:center;vertical-align:middle}}
.cat{{background:#F7FAFF;font-weight:700;color:#1A2B5F}}
.nm{{text-align:left}}.act{{text-align:left;color:#4A5568;font-size:12px}}
.done{{background:#C6F6D5;color:#22543D;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.ing{{background:#BEE3F8;color:#2C5282;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.plan{{background:#EDF2F7;color:#4A5568;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.hi{{color:#22543D;font-weight:700}}.md{{color:#2C5282;font-weight:700}}.lo{{color:#c0392b;font-weight:700}}
.cp-table tfoot td{{background:#EDF2F7;font-weight:700;color:#1A2B5F}}
.tl-item{{display:flex;align-items:flex-start;gap:7px;padding:5px 0;border-bottom:1px dashed #EDF2F7}}
.tl-item:last-child{{border-bottom:none}}
.tl-date{{font-size:.66rem;color:#3182CE;font-weight:700;white-space:nowrap;min-width:34px}}
.tl-dot{{width:6px;height:6px;background:#0D3B8E;border-radius:50%;margin-top:4px;flex-shrink:0}}
.tl-text{{font-size:.74rem;color:#2D3748;line-height:1.4}}
.tl-sec{{font-size:.74rem;font-weight:700;color:#4A5568;border-bottom:2px solid #E2E8F0;padding-bottom:5px;margin-bottom:8px}}
.nav-top{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:white;padding:6px 12px;border-radius:6px;font-size:.76rem;font-weight:700;cursor:pointer;font-family:'Noto Sans KR',sans-serif;margin-left:8px;text-decoration:none;white-space:nowrap}}
.nav-top:hover{{background:rgba(255,255,255,.22)}}
@media(max-width:900px){{.nav-links{{display:none}}}}
</style>

<!-- 상단 네비 (JS로 body로 이동되어 진짜 고정됨) -->
<span class="sec-anchor" id="sec-top"></span>
<div id="pb-nav" class="dash-nav">
  <div class="nav-left">
    {MASCOT_IMG}
    <span class="nav-title">CP 컴플라이언스 대시보드</span>
    <span class="nav-badge">Paris Baguette</span>
  </div>
  <div class="nav-links">
    <a class="nav-btn nav-settings" href="#" id="pb-settings-btn">⚙️ 설정 열기/닫기</a>
    <a class="nav-btn" href="#sec-overview">📈 전체 현황</a>
    <a class="nav-btn" href="#sec-news">📰 일일 뉴스</a>
    <a class="nav-btn" href="#sec-cp">📊 CP 운영</a>
    <a class="nav-btn" href="#sec-chart">🔍 차트 분석</a>
    <a class="nav-btn" href="#sec-tl">🗓️ 타임라인</a>
    <a class="nav-top" href="#sec-top">↑ TOP</a>
  </div>
  <span class="nav-date">📅 {TODAY} · 4월 기준</span>
</div>
<div class="nav-spacer"></div>
""", unsafe_allow_html=True)

# 네비를 진짜 body 최상위로 이동 + 설정버튼 클릭 핸들러 연결
components.html("""
<script>
(function(){
    var doc = window.parent.document;
    var nav = doc.getElementById('pb-nav');
    if (!nav) return;

    if (nav.parentElement !== doc.body) {
        // 이전에 옮겨진 중복 nav 제거
        var olds = doc.body.querySelectorAll('#pb-nav');
        olds.forEach(function(el){ if(el !== nav) el.remove(); });
        doc.body.insertBefore(nav, doc.body.firstChild);
    }

    // 설정(사이드바 토글) 버튼 클릭 핸들러
    var btn = nav.querySelector('#pb-settings-btn');
    if (btn) {
        btn.onclick = function(e){
            e.preventDefault();
            var b = doc.querySelector('[data-testid="collapsedControl"] button')
                 || doc.querySelector('[data-testid="collapsedControl"]')
                 || doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
                 || doc.querySelector('section[data-testid="stSidebar"] button[kind="header"]')
                 || doc.querySelector('button[aria-label*="sidebar" i]')
                 || doc.querySelector('button[title*="sidebar" i]');
            if (b) b.click();
        };
    }
})();
</script>
""", height=0)

# ══════════════════════════════════════════════════════════════
#  4. ① 전체 현황
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<span class="sec-anchor" id="sec-overview"></span>
<div class="insight">
  <div class="insight-t">💡 경영진 핵심 인사이트 — 4월 기준</div>
  <div class="insight-txt">전체 CP 활동 달성률 <strong style="color:#FFD700">{kpi_pct}%</strong>로 목표 대비 미흡.
  교육(30%)·운영(25%)이 주요 미달 영역. 내부신고 {kpi_sign}건 중 1건 처리 진행 중.</div>
  <div>
    <span class="chip chip-warn">⚠ 교육 목표 30%</span>
    <span class="chip chip-warn">⚠ 운영 목표 25%</span>
    <span class="chip chip-ok">✓ 대표이사 의지표명 125%</span>
    <span class="chip chip-ok">✓ 효과성평가 100%</span>
  </div>
</div>
""", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)
for col,lbl,val,unit,sub,cls,color,pct in [
    (k1,"달성률",      str(kpi_pct),"%",  f"목표 {kpi_goal}건 · 실적 {kpi_actual}건","b","#0D3B8E",kpi_pct),
    (k2,"내부신고",    str(kpi_sign),"건", "처리완료 11 · 진행중 1",                  "g","#22863a",min(kpi_sign*3,100)),
    (k3,"법령검토",    str(kpi_law),"건",  "평균 3.5일 · 미처리 2건",                 "o","#d45500",70),
    (k4,"공정거래검토",str(kpi_ftc),"건",  "가맹사업법 594건(78%)",                   "r","#c0392b",76),
]:
    with col:
        st.markdown(f"""<div class="kpi {cls}">
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-val">{val}<span>{unit}</span></div>
          <div class="kpi-sub">{sub}</div>
          <div class="kpi-bar"><div class="kpi-fill" style="width:{min(pct,100)}%;background:{color}"></div></div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  5. ② 일일 뉴스
# ══════════════════════════════════════════════════════════════
st.markdown('<span class="sec-anchor" id="sec-news"></span><div class="sec-title">📰 일일 뉴스 · 보도자료</div>', unsafe_allow_html=True)

with st.spinner("뉴스 로딩 중..."):
    news_list, news_ts   = fetch_news(news_kw, NEWS_CACHE_KEY, st.session_state.news_refresh)
    press_list, press_ts = fetch_press(press_kw, NEWS_CACHE_KEY, st.session_state.press_refresh)

if st.session_state.news_sort == "최신순":
    news_list = sorted(news_list, key=lambda x: x.get("ts",0), reverse=True)
if st.session_state.press_sort == "최신순":
    press_list = sorted(press_list, key=lambda x: x.get("ts",0), reverse=True)

nc1,nc2 = st.columns(2)
with nc1:
    _, grp1 = st.columns([2.4,1.6])
    b1, s1 = grp1.columns([1,1.5], gap="small")
    with b1:
        if st.button("갱신", key="news_refresh_btn", use_container_width=True):
            st.session_state.news_refresh += 1
            st.rerun()
    with s1:
        st.session_state.news_sort = st.selectbox(
            "정렬", ["관련도순","최신순"],
            index=["관련도순","최신순"].index(st.session_state.news_sort),
            key="news_sort_sel", label_visibility="collapsed")
    rows = "".join([f'<div class="news-row"><span class="news-n">{i+1}</span><div><a href="{n["link"]}" target="_blank" class="news-t">{n["title"]}</a><div class="news-src">{n.get("source","")} {("· "+n["date"]) if n.get("date") else ""}</div></div></div>' for i,n in enumerate(news_list)]) if news_list else '<div class="no-data">⚠️ 뉴스를 불러오지 못했어요.</div>'
    st.markdown(f'<div class="card"><div class="card-head">📰 일일 NEWS <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">법령/가맹사업</span></div><span class="badge">🕷️ Google News · {news_ts or "미수집"} · {st.session_state.news_sort}</span>{rows}</div>', unsafe_allow_html=True)
with nc2:
    _, grp2 = st.columns([2.4,1.6])
    b2, s2 = grp2.columns([1,1.5], gap="small")
    with b2:
        if st.button("갱신", key="press_refresh_btn", use_container_width=True):
            st.session_state.press_refresh += 1
            st.rerun()
    with s2:
        st.session_state.press_sort = st.selectbox(
            "정렬", ["관련도순","최신순"],
            index=["관련도순","최신순"].index(st.session_state.press_sort),
            key="press_sort_sel", label_visibility="collapsed")
    pr = "".join([f'<div class="press"><div class="press-d">{p.get("date","")} · {p.get("source","")}</div><a href="{p.get("link","#")}" target="_blank" class="press-t">{p.get("title","")}</a></div>' for p in press_list[:5]]) if press_list else '<div class="no-data">⚠️ 보도자료를 불러오지 못했어요.</div>'
    st.markdown(f'<div class="card"><div class="card-head">📋 공정위/식약처 보도자료 <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">업데이트</span></div><span class="badge">🕷️ Google News · {press_ts or "미수집"} · {st.session_state.press_sort}</span><div style="margin-top:8px">{pr}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  6. ③ CP 운영
# ══════════════════════════════════════════════════════════════
st.markdown('<span class="sec-anchor" id="sec-cp"></span><div class="sec-title">📊 CP 운영현황 <span style="font-size:.72rem;color:#A0AEC0;font-weight:400;margin-left:auto">4월 기준</span></div>', unsafe_allow_html=True)
rows_html=""; prev_cat=""
for row in cp_data:
    cat=str(row.get("구분",""))
    cc=""
    if cat!=prev_cat:
        cnt=sum(1 for r in cp_data if str(r.get("구분",""))==cat)
        cc=f'<td class="cat" rowspan="{cnt}">{cat}</td>'; prev_cat=cat
    pv=row.get("달성률")
    ph="—" if pv is None or str(pv) in ("","None","nan") else f'<span class="{"hi" if int(float(pv))>=100 else "md" if int(float(pv))>=50 else "lo"}">{int(float(pv))}%</span>'
    ss=str(row.get("상태",""))
    sc="done" if "완료" in ss else "ing" if "진행" in ss else "plan"
    rows_html+=f"<tr>{cc}<td class='nm'>{row.get('내용','')}</td><td>{row.get('목표','')}</td><td>{row.get('실적','') or '—'}</td><td>{ph}</td><td><span class='{sc}'>{ss}</span></td><td class='act'>{row.get('주요활동','')}</td></tr>"
tg=sum(int(r.get("목표",0)) for r in cp_data if r.get("목표"))
ta=sum(int(r.get("실적",0)) for r in cp_data if r.get("실적") and str(r.get("실적")) not in ("","None","nan"))
tp=int(ta/tg*100) if tg else 0
st.markdown(f'<div class="card" style="overflow-x:auto"><table class="cp-table"><thead><tr><th>구분</th><th>내용</th><th>목표</th><th>실적</th><th>달성률</th><th>상태</th><th>주요 활동</th></tr></thead><tbody>{rows_html}</tbody><tfoot><tr><td colspan="2">합계</td><td>{tg}</td><td>{ta}</td><td><span class="lo">{tp}%</span></td><td></td><td></td></tr></tfoot></table></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  7. ④ 차트
# ══════════════════════════════════════════════════════════════
st.markdown('<span class="sec-anchor" id="sec-chart"></span><div class="sec-title">🔍 차트 분석</div>', unsafe_allow_html=True)
months  = json.dumps([str(r.get("월","")) for r in sign_data], ensure_ascii=False)
sc_cnt  = [int(r.get("신고건수",0)) for r in sign_data]
sc_done = [int(r.get("처리완료",0)) for r in sign_data]
lm      = json.dumps([str(r.get("월","")) for r in law_data], ensure_ascii=False)
lc      = [int(r.get("누적건수",0)) for r in law_data]
fl      = json.dumps([str(r.get("법령명","")) for r in ftc_data], ensure_ascii=False)
fv      = [int(r.get("건수",0)) for r in ftc_data]
CH = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'
cc1,cc2,cc3 = st.columns(3)
with cc1:
    st.markdown('<div class="card"><div class="card-head">📥 내부신고 현황</div></div>', unsafe_allow_html=True)
    components.html(f"""{CH}<canvas id="c1" style="width:100%;height:200px"></canvas>
    <script>new Chart(document.getElementById('c1'),{{type:'bar',data:{{labels:{months},datasets:[
      {{label:'신고건수',data:{sc_cnt},backgroundColor:'rgba(13,59,142,0.75)',borderRadius:5}},
      {{label:'처리완료',data:{sc_done},backgroundColor:'rgba(52,211,153,0.75)',borderRadius:5}}
    ]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
    }});</script>""", height=220)
with cc2:
    st.markdown('<div class="card"><div class="card-head">📖 법령 검토건수</div></div>', unsafe_allow_html=True)
    components.html(f"""{CH}<canvas id="c2" style="width:100%;height:200px"></canvas>
    <script>new Chart(document.getElementById('c2'),{{type:'line',data:{{labels:{lm},datasets:[{{label:'누적 검토',data:{lc},borderColor:'#0D3B8E',backgroundColor:'rgba(13,59,142,0.08)',fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#0D3B8E'}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
    }});</script>""", height=220)
with cc3:
    st.markdown('<div class="card"><div class="card-head">⚖️ 공정거래 법령별</div></div>', unsafe_allow_html=True)
    components.html(f"""{CH}<canvas id="c3" style="width:100%;height:200px"></canvas>
    <script>new Chart(document.getElementById('c3'),{{type:'doughnut',data:{{labels:{fl},datasets:[{{data:{fv},backgroundColor:['#0D3B8E','#1A56C4','#3182CE','#63B3ED'],borderWidth:2,borderColor:'#fff'}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'right',labels:{{font:{{size:11}},boxWidth:10}}}},tooltip:{{callbacks:{{label:function(c){{return c.label+': '+c.raw+'건'}}}}}}}}}}
    }});</script>""", height=220)

# ══════════════════════════════════════════════════════════════
#  8. ⑤ 타임라인
# ══════════════════════════════════════════════════════════════
st.markdown('<span class="sec-anchor" id="sec-tl"></span><div class="sec-title">🗓️ 4월 주요 활동 타임라인</div>', unsafe_allow_html=True)
sections={}
for row in tl_data:
    sections.setdefault(str(row.get("구분","기타")),[]).append((str(row.get("날짜","")),str(row.get("내용",""))))
tlc = st.columns(min(len(sections),3))
for col,(sec,items) in zip(tlc,sections.items()):
    with col:
        rows="".join([f'<div class="tl-item"><span class="tl-date">{d}</span><span class="tl-dot"></span><span class="tl-text">{t}</span></div>' for d,t in items])
        st.markdown(f'<div class="card"><div class="tl-sec">{sec}</div>{rows}</div>', unsafe_allow_html=True)

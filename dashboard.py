# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
# 데이터 출처:
#   - 일일뉴스: 네이버 뉴스 크롤링 (주 1회)
#   - 보도자료: 공정위/식약처 크롤링 (주 1회)
#   - 달성률 등: 대시보드 내 직접 입력
#   - CP현황/신고/법령/타임라인: 구글 시트 연동
# ============================================================
import streamlit as st
import streamlit.components.v1 as components
import datetime, json, requests, re
import pandas as pd
from zoneinfo import ZoneInfo

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

st.set_page_config(
    page_title="CP 컴플라이언스 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

KST   = ZoneInfo("Asia/Seoul")

# 사이드바 토글 상태 초기화
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
NOW   = datetime.datetime.now(KST)
TODAY = NOW.strftime("%Y년 %m월 %d일 (%a)")

# ══════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&family=Noto+Serif+KR:wght@700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,.stApp{font-family:'Noto Sans KR',sans-serif!important}
.stApp{background:#F0F4F8!important}
header[data-testid="stHeader"]{display:none!important}
div[data-testid="stStatusWidget"]{display:none!important}
section[data-testid="stMain"]{padding:0!important}
section[data-testid="stMain"]>div{padding:0!important}
.block-container{padding:0!important;max-width:100%!important}
.stTabs [data-baseweb="tab-list"]{background:#1A365D!important;gap:0!important;padding:0 16px}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.65)!important;font-size:.82rem!important;font-weight:600!important;padding:14px 18px!important;border-radius:0!important}
.stTabs [aria-selected="true"]{color:white!important;border-bottom:3px solid white!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.stTabs [data-baseweb="tab-border"]{display:none!important}
.stTabs [data-baseweb="tab-panel"]{padding:0!important}
.card{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;margin-bottom:16px}
.card-title{font-size:.86rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:7px;border-bottom:1px solid #EDF2F7;padding-bottom:10px;margin-bottom:14px}
.card-title .sub{font-size:.7rem;color:#A0AEC0;margin-left:auto;font-weight:400}
.kpi{background:white;border-radius:12px;padding:18px 20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:12px 12px 0 0}
.kpi.b::before{background:linear-gradient(90deg,#0D3B8E,#1A56C4)}
.kpi.g::before{background:linear-gradient(90deg,#22863a,#28a745)}
.kpi.o::before{background:linear-gradient(90deg,#d45500,#f77f00)}
.kpi.r::before{background:linear-gradient(90deg,#c0392b,#e74c3c)}
.kpi-lbl{font-size:.7rem;font-weight:700;color:#718096;letter-spacing:.5px;text-transform:uppercase;margin-bottom:7px}
.kpi-val{font-size:2rem;font-weight:800;color:#1A2B5F;line-height:1;margin-bottom:5px}
.kpi-val span{font-size:1rem;font-weight:600;color:#4A5568}
.kpi-sub{font-size:.72rem;color:#718096;margin-bottom:8px}
.kpi-bar{height:4px;background:#E8EDF5;border-radius:2px;overflow:hidden}
.kpi-fill{height:100%;border-radius:2px}
.news-row{display:flex;align-items:flex-start;gap:8px;padding:8px 0;border-bottom:1px dashed #EDF2F7}
.news-row:last-child{border-bottom:none}
.news-n{min-width:20px;height:20px;background:#EBF4FF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.62rem;font-weight:700;color:#0D3B8E;flex-shrink:0;margin-top:1px}
.news-t{font-size:.79rem;color:#2D3748;line-height:1.5;flex:1}
.news-t a{color:#1A2B5F;text-decoration:none}
.news-t a:hover{color:#0D3B8E;text-decoration:underline}
.news-src{font-size:.65rem;color:#A0AEC0;margin-top:2px}
.press{background:#F7FAFF;border:1px solid #BEE3F8;border-radius:8px;padding:12px 14px;margin-bottom:8px}
.press-d{font-size:.67rem;color:#3182CE;font-weight:600;margin-bottom:3px}
.press-t{font-size:.79rem;color:#1A2B5F;font-weight:600;line-height:1.4;margin-bottom:6px}
.press-t a{color:#1A2B5F;text-decoration:none}
.press-t a:hover{color:#0D3B8E;text-decoration:underline}
.press-tag{display:inline-block;background:#EBF8FF;color:#2B6CB0;border-radius:10px;padding:2px 7px;font-size:.63rem;font-weight:600;margin:2px 2px 0 0}
.insight{background:linear-gradient(135deg,#1A365D,#2B6CB0);border-radius:12px;padding:18px 22px;margin-bottom:16px}
.insight-t{color:white;font-size:.9rem;font-weight:700;margin-bottom:6px}
.insight-txt{color:rgba(255,255,255,.82);font-size:.78rem;line-height:1.55;margin-bottom:10px}
.chip{display:inline-block;border-radius:20px;padding:3px 10px;font-size:.69rem;font-weight:600;margin:2px 3px 2px 0}
.chip-warn{background:rgba(255,87,51,.22);border:1px solid rgba(255,87,51,.45);color:#FED7CC}
.chip-ok{background:rgba(52,211,153,.18);border:1px solid rgba(52,211,153,.38);color:#C6F6D5}
.tl-item{display:flex;align-items:flex-start;gap:7px;padding:5px 0;border-bottom:1px dashed #EDF2F7}
.tl-item:last-child{border-bottom:none}
.tl-date{font-size:.67rem;color:#3182CE;font-weight:700;white-space:nowrap;min-width:34px}
.tl-dot{width:6px;height:6px;background:#0D3B8E;border-radius:50%;margin-top:4px;flex-shrink:0}
.tl-text{font-size:.75rem;color:#2D3748;line-height:1.4}
.tl-sec{font-size:.74rem;font-weight:700;color:#4A5568;border-bottom:2px solid #E2E8F0;padding-bottom:5px;margin-bottom:8px}
.src-badge{display:inline-flex;align-items:center;gap:4px;background:#EDF2F7;border-radius:6px;padding:3px 8px;font-size:.65rem;color:#4A5568;font-weight:600;margin-top:2px}
.src-badge.live{background:#C6F6D5;color:#22543D}
.src-badge.manual{background:#BEE3F8;color:#2C5282}
.src-badge.crawl{background:#FEEBC8;color:#744210}
/* 설정 버튼 */
[class*="st-key"] button[kind="secondary"],
div[data-testid="column"] .stButton button {
    border-radius:8px!important;
    font-size:.78rem!important;
    font-weight:600!important;
}
.top-btn{position:fixed;bottom:28px;right:24px;width:42px;height:42px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.1rem;font-weight:700;box-shadow:0 3px 14px rgba(13,59,142,.4);z-index:9999;cursor:pointer;text-decoration:none;border:none;transition:all .2s}
@media(max-width:768px){.block-container{padding:0 8px!important}}
</style>
<button class="top-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  사이드바 - 데이터 설정
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    if not st.session_state.get("sidebar_open", True):
        st.markdown("""
        <div style="text-align:center;padding:20px 10px;color:#A0AEC0">
          <div style="font-size:1.5rem;margin-bottom:8px">⚙️</div>
          <div style="font-size:.78rem">헤더의<br><strong>⚙️ 설정</strong> 버튼으로<br>열 수 있어요</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("## ⚙️ 데이터 설정")
        st.markdown("---")

        # ── 구글 시트 설정 ──
        st.markdown("### 📊 구글 시트 연동")
    st.caption("구글 시트를 '웹에 게시'(CSV)로 공개 후 URL을 입력하세요.")

    gs_cp    = st.text_input("CP 운영현황 시트 URL", placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv")
    gs_sign  = st.text_input("내부신고 현황 URL",   placeholder="https://docs.google.com/spreadsheets/d/...")
    gs_law   = st.text_input("법령검토 건수 URL",   placeholder="https://docs.google.com/spreadsheets/d/...")
    gs_ftc   = st.text_input("공정거래 법령별 URL",  placeholder="https://docs.google.com/spreadsheets/d/...")
    gs_tl    = st.text_input("타임라인 URL",        placeholder="https://docs.google.com/spreadsheets/d/...")

    st.markdown("---")

    # ── 뉴스 키워드 설정 ──
    st.markdown("### 📰 뉴스 크롤링 설정")
    news_keywords = st.text_input(
        "네이버 뉴스 검색 키워드",
        value="가맹사업 법령위반",
        help="스페이스로 구분된 키워드로 뉴스를 검색합니다"
    )
    press_keyword = st.text_input(
        "공정위/식약처 키워드",
        value="가맹 공정거래",
    )

    st.markdown("---")

    # ── 수동 데이터 입력 ──
    st.markdown("### 📋 KPI 직접 입력")
    kpi_goal    = st.number_input("CP 목표 건수",    value=40, min_value=1)
    kpi_actual  = st.number_input("CP 실적 건수",    value=19, min_value=0)
    kpi_sign    = st.number_input("내부신고 건수",    value=12, min_value=0)
    kpi_law     = st.number_input("법령검토 누적",    value=350, min_value=0)
    kpi_ftc     = st.number_input("공정거래 검토",    value=761, min_value=0)

    st.markdown("---")
    refresh = st.button("🔄 데이터 새로고침", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.success("캐시를 초기화했습니다!")

    st.markdown("---")
    st.markdown("### 📌 구글 시트 설정 방법")
    with st.expander("설정 가이드 보기"):
        st.markdown("""
**1단계.** 구글 시트 열기

**2단계.** 상단 메뉴 → **파일 → 공유 → 웹에 게시**

**3단계.** 형식을 **CSV**로 선택 후 게시

**4단계.** 생성된 URL을 위 입력칸에 붙여넣기

---
**시트 컬럼 형식:**

📊 CP 운영현황:
`구분, 내용, 목표, 실적, 달성률, 상태, 주요활동`

📥 내부신고:
`월, 신고건수, 처리완료, 진행중`

📖 법령검토:
`월, 월별건수, 누적건수`

⚖️ 공정거래법령별:
`법령명, 건수`

🗓️ 타임라인:
`구분, 날짜, 내용`
        """)


# ══════════════════════════════════════════════════════════════
#  데이터 로딩 함수
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=7*24*3600, show_spinner=False)  # 주 1회 캐시
def fetch_naver_news(keyword: str):
    """Google News RSS로 뉴스 가져오기 (주 1회)"""
    try:
        import feedparser
        q = requests.utils.quote(keyword)
        url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:6]:
            title = entry.get("title", "")
            # "제목 - 언론사" 형태 분리
            parts = title.rsplit(" - ", 1)
            t = parts[0].strip()
            src = parts[1].strip() if len(parts) > 1 else ""
            results.append({
                "title":  t,
                "link":   entry.get("link", "#"),
                "source": src,
            })
        ts = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M")
        return results, ts
    except Exception as e:
        return [], None


@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_ftc_news(keyword: str):
    """공정위/식약처 뉴스 RSS (주 1회)"""
    try:
        import feedparser
        results = []
        # 공정위 관련 뉴스
        q1 = requests.utils.quote("공정거래위원회 " + keyword)
        feed1 = feedparser.parse(f"https://news.google.com/rss/search?q={q1}&hl=ko&gl=KR&ceid=KR:ko")
        for entry in feed1.entries[:3]:
            title = entry.get("title","")
            parts = title.rsplit(" - ", 1)
            results.append({
                "title":  parts[0].strip(),
                "link":   entry.get("link","#"),
                "date":   entry.get("published","")[:10] if entry.get("published") else "",
                "source": "공정거래위원회"
            })
        # 식약처 관련 뉴스
        q2 = requests.utils.quote("식품의약품안전처 가맹")
        feed2 = feedparser.parse(f"https://news.google.com/rss/search?q={q2}&hl=ko&gl=KR&ceid=KR:ko")
        for entry in feed2.entries[:2]:
            title = entry.get("title","")
            parts = title.rsplit(" - ", 1)
            results.append({
                "title":  parts[0].strip(),
                "link":   entry.get("link","#"),
                "date":   entry.get("published","")[:10] if entry.get("published") else "",
                "source": "식품의약품안전처"
            })
        ts = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M")
        return results, ts
    except Exception:
        return [], None





@st.cache_data(ttl=3600, show_spinner=False)
def load_gsheet(url: str):
    """구글 시트 CSV 로딩"""
    if not url or not url.startswith("http"):
        return None
    try:
        df = pd.read_csv(url)
        return df
    except Exception:
        return None


# 기본 샘플 데이터 (구글 시트 미연동 시)
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
DEFAULT_SIGN   = [{"월":"1월","신고건수":2,"처리완료":2,"진행중":0},{"월":"2월","신고건수":3,"처리완료":3,"진행중":0},{"월":"3월","신고건수":4,"처리완료":4,"진행중":0},{"월":"4월","신고건수":3,"처리완료":2,"진행중":1}]
DEFAULT_LAW    = [{"월":"1월","월별건수":82,"누적건수":82},{"월":"2월","월별건수":93,"누적건수":175},{"월":"3월","월별건수":93,"누적건수":268},{"월":"4월","월별건수":82,"누적건수":350}]
DEFAULT_FTC    = [{"법령명":"가맹사업법","건수":594},{"법령명":"약관법","건수":78},{"법령명":"공정거래법","건수":35},{"법령명":"하도급법","건수":27}]
DEFAULT_TL     = [
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

# ── 구글 시트 or 기본값 ──
df_cp   = load_gsheet(gs_cp)   ; cp_data   = df_cp.to_dict("records")   if df_cp   is not None else DEFAULT_CP
df_sign = load_gsheet(gs_sign) ; sign_data = df_sign.to_dict("records") if df_sign is not None else DEFAULT_SIGN
df_law  = load_gsheet(gs_law)  ; law_data  = df_law.to_dict("records")  if df_law  is not None else DEFAULT_LAW
df_ftc  = load_gsheet(gs_ftc)  ; ftc_data  = df_ftc.to_dict("records")  if df_ftc  is not None else DEFAULT_FTC
df_tl   = load_gsheet(gs_tl)   ; tl_data   = df_tl.to_dict("records")   if df_tl   is not None else DEFAULT_TL

# KPI 계산
kpi_pct = int(kpi_actual / kpi_goal * 100) if kpi_goal else 0


# ══════════════════════════════════════════════════════════════
#  헤더
# ══════════════════════════════════════════════════════════════
col_h1, col_h2 = st.columns([10, 1])
with col_h1:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%);padding:14px 28px;display:flex;align-items:center;gap:14px">
      <span style="font-family:'Noto Serif KR',serif;color:white;font-size:1.08rem;font-weight:700">📊 CP 컴플라이언스 대시보드</span>
      <span style="background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 11px;color:rgba(255,255,255,.85);font-size:.7rem;font-weight:600">Paris Baguette</span>
      <span style="margin-left:auto;color:rgba(255,255,255,.65);font-size:.75rem">📅 {TODAY} &nbsp;·&nbsp; 4월 CP 운영현황 기준</span>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <style>
    [class*="st-key-sidebar_toggle"] button {
        background: linear-gradient(135deg,#0D3B8E,#1A56C4) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: .78rem !important;
        font-weight: 700 !important;
        height: 58px !important;
        width: 100% !important;
    }
    [class*="st-key-sidebar_toggle"] button:hover {
        background: linear-gradient(135deg,#061B4A,#0D3B8E) !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("⚙️\n설정", key="sidebar_toggle", use_container_width=True):
        st.session_state.sidebar_open = not st.session_state.get("sidebar_open", True)
        st.rerun()

# ══════════════════════════════════════════════════════════════
#  탭
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 전체 현황", "📰 일일 뉴스", "📊 CP 운영", "🔍 차트 분석", "🗓️ 활동 타임라인"
])

# ══════════════════════════════════════════════════
# TAB 1: 전체 현황
# ══════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight">
      <div class="insight-t">💡 경영진 핵심 인사이트 — 4월 기준</div>
      <div class="insight-txt">
        전체 CP 활동 달성률 <strong style="color:#FFD700">{kpi_pct}%</strong>로 목표 대비 미흡.
        교육 부문(30%)과 운영 부문(25%)이 주요 미달 영역.
        내부신고 {kpi_sign}건 중 1건 처리 진행 중이며, 법령 검토 미처리 2건 신속 처리 필요.
      </div>
      <div>
        <span class="chip chip-warn">⚠ 교육 목표 30% 달성</span>
        <span class="chip chip-warn">⚠ 운영 목표 25% 달성</span>
        <span class="chip chip-ok">✓ 대표이사 의지표명 125%</span>
        <span class="chip chip-ok">✓ 효과성평가 100%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    kpis = [
        (k1,"달성률",str(kpi_pct),"%",f"목표 {kpi_goal}건 · 실적 {kpi_actual}건","b","#0D3B8E",kpi_pct,"manual"),
        (k2,"내부신고",str(kpi_sign),"건","처리완료 11 · 진행중 1","g","#22863a",min(kpi_sign*3,100),"manual"),
        (k3,"법령검토",str(kpi_law),"건","평균 3.5일 · 미처리 2건","o","#d45500",70,"manual"),
        (k4,"공정거래검토",str(kpi_ftc),"건","가맹사업법 594건(78%)","r","#c0392b",76,"manual"),
    ]
    for col,lbl,val,unit,sub,cls,color,pct,src in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi {cls}">
              <div class="kpi-lbl">{lbl}</div>
              <div class="kpi-val">{val}<span>{unit}</span></div>
              <div class="kpi-sub">{sub}</div>
              <div class="kpi-bar"><div class="kpi-fill" style="width:{pct}%;background:{color}"></div></div>
              <span class="src-badge manual" style="margin-top:8px">✏️ 직접 입력</span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 2: 일일 뉴스 (크롤링)
# ══════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)

    with st.spinner("뉴스 데이터를 불러오는 중..."):
        news_list, news_ts  = fetch_naver_news(news_keywords)
        ftc_list,  ftc_ts   = fetch_ftc_news(press_keyword)

    c1, c2 = st.columns(2)

    with c1:
        # 네이버 뉴스
        badge = f'<span class="src-badge crawl">🕷️ 네이버 크롤링 · {news_ts or "미수집"}</span>'
        if news_list:
            rows = "".join([
                f'<div class="news-row"><span class="news-n">{i+1}</span>'
                f'<div><div class="news-t"><a href="{n["link"]}" target="_blank">{n["title"]}</a></div>'
                f'<div class="news-src">{n.get("source","")}</div></div></div>'
                for i,n in enumerate(news_list)
            ])
        else:
            rows = """
            <div style="padding:16px;text-align:center;color:#A0AEC0;font-size:.82rem">
              ⚠️ 뉴스를 불러오지 못했어요.<br>
              잠시 후 새로고침하거나 키워드를 변경해보세요.
            </div>"""
        st.markdown(f"""
        <div class="card">
          <div class="card-title">📰 일일 NEWS <span class="sub">법령/가맹사업 관련</span></div>
          {badge}
          <div style="margin-top:10px">{rows}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # 공정위 + 식약처
        all_press = ftc_list or []
        badge2 = f'<span class="src-badge crawl">🕷️ Google News RSS · {ftc_ts or "미수집"}</span>'
        if all_press:
            press_rows = "".join([
                f'<div class="press">'
                f'<div class="press-d">{p.get("date","")} · {p.get("source","")}</div>'
                f'<div class="press-t"><a href="{p.get("link","#")}" target="_blank">{p.get("title","")}</a></div>'
                f'</div>'
                for p in all_press[:5]
            ])
        else:
            press_rows = """
            <div style="padding:16px;text-align:center;color:#A0AEC0;font-size:.82rem">
              ⚠️ 보도자료를 불러오지 못했어요.<br>
              잠시 후 새로고침해보세요.
            </div>"""
        st.markdown(f"""
        <div class="card">
          <div class="card-title">📋 공정위 / 식약처 보도자료 <span class="sub">자료 업데이트</span></div>
          {badge2}
          <div style="margin-top:10px">{press_rows}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 3: CP 운영현황 (구글 시트 or 기본값)
# ══════════════════════════════════════════════════
with tab3:
    src_lbl = "🔗 구글 시트 연동" if df_cp is not None else "📋 샘플 데이터 (구글 시트 미연동)"
    src_cls = "live" if df_cp is not None else "manual"
    st.markdown(f'<div style="padding:16px 24px 4px"><span class="src-badge {src_cls}">{src_lbl}</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:4px 24px 30px">', unsafe_allow_html=True)

    # 테이블 HTML
    rows_html = ""
    prev_cat = ""
    for row in cp_data:
        cat = str(row.get("구분",""))
        cat_cell = ""
        if cat != prev_cat:
            cnt = sum(1 for r in cp_data if str(r.get("구분",""))==cat)
            cat_cell = f'<td class="cat" rowspan="{cnt}">{cat}</td>'
            prev_cat = cat
        pct = row.get("달성률")
        if pct is None or str(pct) in ("","None","nan"):
            pct_html = "—"
        else:
            p = int(float(pct))
            cls = "hi" if p>=100 else "md" if p>=50 else "lo"
            pct_html = f'<span class="{cls}">{p}%</span>'
        st_s = str(row.get("상태",""))
        scls = "done" if "완료" in st_s else "ing" if "진행" in st_s else "plan"
        rows_html += f"""<tr>
            {cat_cell}
            <td class="nm">{row.get("내용","")}</td>
            <td>{row.get("목표","")}</td>
            <td>{row.get("실적","") or "—"}</td>
            <td>{pct_html}</td>
            <td><span class="{scls}">{st_s}</span></td>
            <td class="act">{row.get("주요활동","")}</td>
        </tr>"""

    total_g = sum(int(r.get("목표",0)) for r in cp_data if r.get("목표"))
    total_a = sum(int(r.get("실적",0)) for r in cp_data if r.get("실적") and str(r.get("실적")) not in ("","None","nan"))
    total_p = int(total_a/total_g*100) if total_g else 0

    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    body{{font-family:'Noto Sans KR',sans-serif;margin:0;padding:4px 0}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}
    th{{background:#EDF2F7;color:#4A5568;font-weight:700;padding:9px 10px;text-align:center;font-size:11px;letter-spacing:.3px;border:1px solid #E2E8F0}}
    td{{padding:8px 10px;border:1px solid #E2E8F0;color:#2D3748;text-align:center;vertical-align:middle}}
    .cat{{background:#F7FAFF;font-weight:700;color:#1A2B5F}}
    .nm{{text-align:left}}.act{{text-align:left;color:#4A5568;font-size:12px}}
    .done{{background:#C6F6D5;color:#22543D;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
    .ing{{background:#BEE3F8;color:#2C5282;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
    .plan{{background:#EDF2F7;color:#4A5568;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
    .hi{{color:#22543D;font-weight:700}}.md{{color:#2C5282;font-weight:700}}.lo{{color:#c0392b;font-weight:700}}
    tfoot td{{background:#EDF2F7;font-weight:700;color:#1A2B5F}}
    </style>
    <table>
      <thead><tr><th>구분</th><th>내용</th><th>목표</th><th>실적</th><th>달성률</th><th>상태</th><th>주요 활동</th></tr></thead>
      <tbody>{rows_html}</tbody>
      <tfoot><tr><td colspan="2">합계</td><td>{total_g}</td><td>{total_a}</td><td><span class="lo">{total_p}%</span></td><td></td><td></td></tr></tfoot>
    </table>
    """, height=350)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 4: 차트 분석 (구글 시트 or 기본값)
# ══════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)

    months   = [str(r.get("월","")) for r in sign_data]
    sign_cnt = [int(r.get("신고건수",0)) for r in sign_data]
    sign_done= [int(r.get("처리완료",0)) for r in sign_data]
    law_cum  = [int(r.get("누적건수",0)) for r in law_data]
    law_months=[str(r.get("월","")) for r in law_data]
    ftc_lbl  = [str(r.get("법령명","")) for r in ftc_data]
    ftc_val  = [int(r.get("건수",0)) for r in ftc_data]

    c1,c2,c3 = st.columns(3)
    src_sign = "🔗 구글 시트" if df_sign is not None else "📋 샘플"
    src_law  = "🔗 구글 시트" if df_law  is not None else "📋 샘플"
    src_ftc  = "🔗 구글 시트" if df_ftc  is not None else "📋 샘플"

    with c1:
        st.markdown(f'<div class="card"><div class="card-title">📥 내부신고 현황 <span class="sub">{src_sign}</span></div>', unsafe_allow_html=True)
        components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch1" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch1'),{{
          type:'bar',
          data:{{labels:{json.dumps(months,ensure_ascii=False)},
            datasets:[
              {{label:'신고건수',data:{sign_cnt},backgroundColor:'rgba(13,59,142,0.75)',borderRadius:6}},
              {{label:'처리완료',data:{sign_done},backgroundColor:'rgba(52,211,153,0.75)',borderRadius:6}}
            ]}},
          options:{{responsive:true,maintainAspectRatio:false,
            plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},
            scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
        }});
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="card"><div class="card-title">📖 법령 검토건수 <span class="sub">{src_law}</span></div>', unsafe_allow_html=True)
        components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch2" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch2'),{{
          type:'line',
          data:{{labels:{json.dumps(law_months,ensure_ascii=False)},
            datasets:[{{label:'누적 검토',data:{law_cum},
              borderColor:'#0D3B8E',backgroundColor:'rgba(13,59,142,0.08)',
              fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#0D3B8E'}}]}},
          options:{{responsive:true,maintainAspectRatio:false,
            plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},
            scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
        }});
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="card"><div class="card-title">⚖️ 공정거래 법령별 <span class="sub">{src_ftc}</span></div>', unsafe_allow_html=True)
        components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch3" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch3'),{{
          type:'doughnut',
          data:{{labels:{json.dumps(ftc_lbl,ensure_ascii=False)},
            datasets:[{{data:{ftc_val},
              backgroundColor:['#0D3B8E','#1A56C4','#3182CE','#63B3ED'],
              borderWidth:2,borderColor:'#fff'}}]}},
          options:{{responsive:true,maintainAspectRatio:false,
            plugins:{{
              legend:{{position:'right',labels:{{font:{{size:11}},boxWidth:10}}}},
              tooltip:{{callbacks:{{label:function(c){{return c.label+': '+c.raw+'건'}}}}}}}}}}
        }});
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 5: 활동 타임라인 (구글 시트 or 기본값)
# ══════════════════════════════════════════════════
with tab5:
    src_tl = "🔗 구글 시트" if df_tl is not None else "📋 샘플"
    st.markdown(f'<div style="padding:16px 24px 4px"><span class="src-badge {"live" if df_tl is not None else "manual"}">{src_tl}</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:4px 24px 30px">', unsafe_allow_html=True)

    sections = {}
    for row in tl_data:
        sec = str(row.get("구분","기타"))
        sections.setdefault(sec, []).append((str(row.get("날짜","")), str(row.get("내용",""))))

    cols = st.columns(min(len(sections), 3))
    for col, (sec, items) in zip(cols, sections.items()):
        with col:
            rows = "".join([
                f'<div class="tl-item"><span class="tl-date">{d}</span><span class="tl-dot"></span><span class="tl-text">{t}</span></div>'
                for d, t in items
            ])
            st.markdown(f'<div class="card"><div class="tl-sec">{sec}</div>{rows}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

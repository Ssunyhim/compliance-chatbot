# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
# ============================================================
import streamlit as st
import streamlit.components.v1 as components
import datetime, json, requests, pandas as pd
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="CP 컴플라이언스 대시보드",
    page_icon="📊",
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
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display:none !important; }
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

# ══════════════════════════════════════════════════════════════
#  2. 데이터 로딩
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_news(keyword):
    try:
        import feedparser
        q = requests.utils.quote(keyword)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko")
        res = []
        for e in feed.entries[:6]:
            t = e.get("title",""); p = t.rsplit(" - ",1)
            res.append({"title":p[0].strip(),"link":e.get("link","#"),"source":p[1].strip() if len(p)>1 else ""})
        return res, NOW.strftime("%H:%M")
    except: return [], None

@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_press(keyword):
    try:
        import feedparser
        res = []
        for q_txt, src in [("공정거래위원회 "+keyword,"공정거래위원회"),("식품의약품안전처 가맹","식품의약품안전처")]:
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={requests.utils.quote(q_txt)}&hl=ko&gl=KR&ceid=KR:ko")
            for e in feed.entries[:3]:
                t = e.get("title","").rsplit(" - ",1)[0].strip()
                res.append({"title":t,"link":e.get("link","#"),"date":e.get("published","")[:10],"source":src})
        return res, NOW.strftime("%H:%M")
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
.block-container{{padding:0 24px 40px!important;max-width:100%!important;padding-top:68px!important}}

/* ── 핵심: stMain을 overflow visible로 해서 fixed 가능하게 ── */
.stApp{{overflow-y:auto!important;height:100vh!important}}
section[data-testid="stMain"]{{overflow:visible!important;height:auto!important;min-height:calc(100vh - 0px)!important}}
section[data-testid="stMain"]>div{{overflow:visible!important;height:auto!important}}
div[data-testid="stVerticalBlock"]{{overflow:visible!important;height:auto!important}}
div[data-testid="stVerticalBlockBorderWrapper"]{{overflow:visible!important}}

/* ── 고정 네비 ── */
.dash-nav{{
    position:fixed!important;top:0!important;
    right:0!important;
    left:var(--sidebar-width, 0px)!important;
    z-index:99999!important;
    background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%)!important;
    padding:0 24px!important;
    display:flex!important;align-items:center!important;justify-content:space-between!important;
    height:52px!important;
    box-shadow:0 2px 12px rgba(6,27,74,.3)!important;
}}
.nav-left{{display:flex;align-items:center;gap:12px}}
.nav-title{{color:white;font-size:1rem;font-weight:800}}
.nav-badge{{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 10px;color:rgba(255,255,255,.85);font-size:.68rem;font-weight:600}}
.nav-links{{display:flex;gap:2px}}
.nav-btn{{background:transparent;border:none;color:rgba(255,255,255,.7);padding:7px 14px;border-radius:6px;font-size:.76rem;font-weight:600;cursor:pointer;font-family:'Noto Sans KR',sans-serif;transition:all .15s;white-space:nowrap;text-decoration:none;display:inline-block}}
.nav-btn:hover{{background:rgba(255,255,255,.15);color:white}}
.nav-date{{color:rgba(255,255,255,.55);font-size:.7rem;white-space:nowrap}}

/* 섹션 */
.sec-anchor{{display:block;position:relative;top:-70px;visibility:hidden}}
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
.top-btn{{position:fixed;bottom:28px;right:18px;width:40px;height:40px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.1rem;font-weight:700;box-shadow:0 3px 14px rgba(13,59,142,.4);cursor:pointer;border:none;z-index:9998;text-decoration:none}}
@media(max-width:900px){{.nav-links{{display:none}}}}
</style>

<!-- 고정 네비 -->
<div class="dash-nav">
  <div class="nav-left">
    <span class="nav-title">📊 CP 컴플라이언스 대시보드</span>
    <span class="nav-badge">Paris Baguette</span>
  </div>
  <div class="nav-links">
    <a class="nav-btn" href="#sec-overview">📈 전체 현황</a>
    <a class="nav-btn" href="#sec-news">📰 일일 뉴스</a>
    <a class="nav-btn" href="#sec-cp">📊 CP 운영</a>
    <a class="nav-btn" href="#sec-chart">🔍 차트 분석</a>
    <a class="nav-btn" href="#sec-tl">🗓️ 타임라인</a>
  </div>
  <span class="nav-date">📅 {TODAY} · 4월 기준</span>
</div>
<button class="top-btn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
""", unsafe_allow_html=True)

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
    news_list, news_ts   = fetch_news(news_kw)
    press_list, press_ts = fetch_press(press_kw)
nc1,nc2 = st.columns(2)
with nc1:
    rows = "".join([f'<div class="news-row"><span class="news-n">{i+1}</span><div><a href="{n["link"]}" target="_blank" class="news-t">{n["title"]}</a><div class="news-src">{n.get("source","")}</div></div></div>' for i,n in enumerate(news_list)]) if news_list else '<div class="no-data">⚠️ 뉴스를 불러오지 못했어요.</div>'
    st.markdown(f'<div class="card"><div class="card-head">📰 일일 NEWS <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">법령/가맹사업</span></div><span class="badge">🕷️ Google News · {news_ts or "미수집"}</span>{rows}</div>', unsafe_allow_html=True)
with nc2:
    pr = "".join([f'<div class="press"><div class="press-d">{p.get("date","")} · {p.get("source","")}</div><a href="{p.get("link","#")}" target="_blank" class="press-t">{p.get("title","")}</a></div>' for p in press_list[:5]]) if press_list else '<div class="no-data">⚠️ 보도자료를 불러오지 못했어요.</div>'
    st.markdown(f'<div class="card"><div class="card-head">📋 공정위/식약처 보도자료 <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">업데이트</span></div><span class="badge">🕷️ Google News · {press_ts or "미수집"}</span><div style="margin-top:8px">{pr}</div></div>', unsafe_allow_html=True)

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

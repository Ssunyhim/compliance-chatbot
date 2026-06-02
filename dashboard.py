# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
# 한 페이지 스크롤 + 앵커 네비게이션
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
#  1. 사이드바 (최상단)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ 데이터 설정")
    st.caption("숫자 변경 후 Enter 치면 자동 반영돼요.")
    st.divider()
    st.markdown("### 📋 KPI 직접 입력")
    kpi_goal   = st.number_input("CP 목표 건수",  value=40,  min_value=1,  key="kg")
    kpi_actual = st.number_input("CP 실적 건수",  value=19,  min_value=0,  key="ka")
    kpi_sign   = st.number_input("내부신고 건수", value=12,  min_value=0,  key="ks")
    kpi_law    = st.number_input("법령검토 누적", value=350, min_value=0,  key="kl")
    kpi_ftc    = st.number_input("공정거래 검토", value=761, min_value=0,  key="kf")
    st.divider()
    st.markdown("### 📊 구글 시트 연동")
    st.caption("구글 시트 → 파일 → 웹에 게시 → CSV 형식 URL")
    gs_cp   = st.text_input("CP 운영현황",    placeholder="...export?format=csv", key="gs_cp")
    gs_sign = st.text_input("내부신고 현황",  placeholder="...export?format=csv", key="gs_sign")
    gs_law  = st.text_input("법령검토 건수",  placeholder="...export?format=csv", key="gs_law")
    gs_ftc  = st.text_input("공정거래 법령별",placeholder="...export?format=csv", key="gs_ftc")
    gs_tl   = st.text_input("타임라인",       placeholder="...export?format=csv", key="gs_tl")
    st.divider()
    st.markdown("### 📰 뉴스 키워드")
    news_kw  = st.text_input("뉴스 검색어",       value="가맹사업 법령위반", key="nkw")
    press_kw = st.text_input("공정위/식약처 키워드", value="가맹 공정거래",   key="pkw")
    st.divider()
    if st.button("🔄 캐시 초기화", use_container_width=True):
        st.cache_data.clear()
        st.success("완료!")
    st.divider()
    with st.expander("📌 구글 시트 설정 방법"):
        st.markdown("""
**1.** 구글 시트 열기  
**2.** 파일 → 공유 → **웹에 게시**  
**3.** 형식: **CSV** 선택 → 게시  
**4.** URL 복사 → 위 입력칸에 붙여넣기  

컬럼 형식  
`구분,내용,목표,실적,달성률,상태,주요활동`  
`월,신고건수,처리완료,진행중`  
`월,누적건수`  
`법령명,건수`  
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
        q    = requests.utils.quote(keyword)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko")
        res  = []
        for e in feed.entries[:6]:
            t = e.get("title","")
            p = t.rsplit(" - ", 1)
            res.append({"title": p[0].strip(), "link": e.get("link","#"), "source": p[1].strip() if len(p)>1 else ""})
        return res, NOW.strftime("%H:%M")
    except:
        return [], None

@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_press(keyword):
    try:
        import feedparser
        res = []
        for q_txt, src in [("공정거래위원회 "+keyword,"공정거래위원회"),("식품의약품안전처 가맹","식품의약품안전처")]:
            q    = requests.utils.quote(q_txt)
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko")
            for e in feed.entries[:3]:
                t = e.get("title","").rsplit(" - ",1)[0].strip()
                res.append({"title":t,"link":e.get("link","#"),"date":e.get("published","")[:10],"source":src})
        return res, NOW.strftime("%H:%M")
    except:
        return [], None

@st.cache_data(ttl=3600, show_spinner=False)
def load_gs(url):
    if not url or not url.startswith("http"): return None
    try: return pd.read_csv(url)
    except: return None

DEFAULT_CP   = [
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

df_cp   = load_gs(gs_cp)  ; cp_data   = df_cp.to_dict("records")   if df_cp   is not None else DEFAULT_CP
df_sign = load_gs(gs_sign); sign_data = df_sign.to_dict("records") if df_sign is not None else DEFAULT_SIGN
df_law  = load_gs(gs_law) ; law_data  = df_law.to_dict("records")  if df_law  is not None else DEFAULT_LAW
df_ftc  = load_gs(gs_ftc) ; ftc_data  = df_ftc.to_dict("records")  if df_ftc  is not None else DEFAULT_FTC
df_tl   = load_gs(gs_tl)  ; tl_data   = df_tl.to_dict("records")   if df_tl   is not None else DEFAULT_TL

# ══════════════════════════════════════════════════════════════
#  3. 전체 페이지 HTML (한 페이지 스크롤)
# ══════════════════════════════════════════════════════════════

# CP 테이블 HTML 생성
rows_html = ""
prev_cat  = ""
for row in cp_data:
    cat = str(row.get("구분",""))
    cat_cell = ""
    if cat != prev_cat:
        cnt = sum(1 for r in cp_data if str(r.get("구분",""))==cat)
        cat_cell = f'<td class="cat" rowspan="{cnt}">{cat}</td>'
        prev_cat = cat
    pct_v = row.get("달성률")
    if pct_v is None or str(pct_v) in ("","None","nan"):
        pct_h = "—"
    else:
        p = int(float(pct_v))
        c = "hi" if p>=100 else "md" if p>=50 else "lo"
        pct_h = f'<span class="{c}">{p}%</span>'
    st_s = str(row.get("상태",""))
    sc   = "done" if "완료" in st_s else "ing" if "진행" in st_s else "plan"
    rows_html += f"<tr>{cat_cell}<td class='nm'>{row.get('내용','')}</td><td>{row.get('목표','')}</td><td>{row.get('실적','') or '—'}</td><td>{pct_h}</td><td><span class='{sc}'>{st_s}</span></td><td class='act'>{row.get('주요활동','')}</td></tr>"

tg = sum(int(r.get("목표",0)) for r in cp_data if r.get("목표"))
ta = sum(int(r.get("실적",0)) for r in cp_data if r.get("실적") and str(r.get("실적")) not in ("","None","nan"))
tp = int(ta/tg*100) if tg else 0

# 뉴스 데이터
with st.spinner("뉴스 로딩 중..."):
    news_list, news_ts   = fetch_news(news_kw)
    press_list, press_ts = fetch_press(press_kw)

news_html = "".join([f'<div class="news-row"><span class="news-n">{i+1}</span><div><a href="{n["link"]}" target="_blank" class="news-t">{n["title"]}</a><div class="news-src">{n.get("source","")}</div></div></div>' for i,n in enumerate(news_list)]) if news_list else '<p class="no-data">⚠️ 뉴스를 불러오지 못했어요. 잠시 후 새로고침해보세요.</p>'
press_html= "".join([f'<div class="press"><div class="press-d">{p.get("date","")} · {p.get("source","")}</div><a href="{p.get("link","#")}" target="_blank" class="press-t">{p.get("title","")}</a></div>' for p in press_list[:5]]) if press_list else '<p class="no-data">⚠️ 보도자료를 불러오지 못했어요.</p>'

# 타임라인 HTML
sections = {}
for row in tl_data:
    sec = str(row.get("구분","기타"))
    sections.setdefault(sec, []).append((str(row.get("날짜","")), str(row.get("내용",""))))

tl_cols_html = ""
for sec, items in sections.items():
    rows_tl = "".join([f'<div class="tl-item"><span class="tl-date">{d}</span><span class="tl-dot"></span><span class="tl-text">{t}</span></div>' for d,t in items])
    tl_cols_html += f'<div class="tl-col"><div class="tl-sec">{sec}</div>{rows_tl}</div>'

# 차트 데이터
months    = json.dumps([str(r.get("월","")) for r in sign_data], ensure_ascii=False)
sign_cnt  = [int(r.get("신고건수",0)) for r in sign_data]
sign_done = [int(r.get("처리완료",0)) for r in sign_data]
law_months= json.dumps([str(r.get("월","")) for r in law_data], ensure_ascii=False)
law_cum   = [int(r.get("누적건수",0)) for r in law_data]
ftc_lbl   = json.dumps([str(r.get("법령명","")) for r in ftc_data], ensure_ascii=False)
ftc_val   = [int(r.get("건수",0)) for r in ftc_data]

# KPI 바 너비
kpi_bars = [min(kpi_pct,100), min(kpi_sign*3,100), 70, 76]

components.html(f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans KR',sans-serif;background:#F0F4F8;color:#2D3748;font-size:14px}}

/* ── 고정 네비 ── */
.nav{{position:sticky;top:0;z-index:999;background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%);padding:0 28px;display:flex;align-items:center;justify-content:space-between;height:52px;box-shadow:0 2px 12px rgba(6,27,74,.3)}}
.nav-left{{display:flex;align-items:center;gap:12px}}
.nav-title{{color:white;font-size:1rem;font-weight:800;letter-spacing:-.3px}}
.nav-badge{{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 10px;color:rgba(255,255,255,.85);font-size:.68rem;font-weight:600}}
.nav-links{{display:flex;gap:2px}}
.nav-btn{{background:transparent;border:none;color:rgba(255,255,255,.7);padding:7px 14px;border-radius:6px;font-size:.78rem;font-weight:600;cursor:pointer;font-family:'Noto Sans KR',sans-serif;transition:all .15s;white-space:nowrap}}
.nav-btn:hover{{background:rgba(255,255,255,.15);color:white}}
.nav-date{{color:rgba(255,255,255,.55);font-size:.7rem;white-space:nowrap}}

/* ── 컨텐츠 ── */
.wrap{{padding:20px 28px;max-width:1400px;margin:0 auto}}
.section{{margin-bottom:28px}}
.section-title{{font-size:.95rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:8px;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #E2E8F0}}
.card{{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5}}

/* ── 인사이트 ── */
.insight{{background:linear-gradient(135deg,#1A365D,#2B6CB0);border-radius:12px;padding:18px 22px;margin-bottom:20px}}
.insight-t{{color:white;font-size:.92rem;font-weight:700;margin-bottom:6px}}
.insight-txt{{color:rgba(255,255,255,.82);font-size:.78rem;line-height:1.6;margin-bottom:10px}}
.chips{{display:flex;flex-wrap:wrap;gap:6px}}
.chip{{border-radius:20px;padding:3px 11px;font-size:.69rem;font-weight:600}}
.chip-warn{{background:rgba(255,87,51,.22);border:1px solid rgba(255,87,51,.45);color:#FED7CC}}
.chip-ok{{background:rgba(52,211,153,.18);border:1px solid rgba(52,211,153,.38);color:#C6F6D5}}

/* ── KPI ── */
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}
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
.kpi-fill{{height:100%;border-radius:2px;transition:width .8s ease}}

/* ── 뉴스 ── */
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.card-head{{font-size:.84rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:7px;border-bottom:1px solid #EDF2F7;padding-bottom:10px;margin-bottom:12px}}
.badge{{display:inline-flex;align-items:center;gap:4px;border-radius:6px;padding:3px 8px;font-size:.63rem;font-weight:600;margin-bottom:8px}}
.badge.crawl{{background:#FEEBC8;color:#744210}}
.news-row{{display:flex;align-items:flex-start;gap:8px;padding:7px 0;border-bottom:1px dashed #EDF2F7}}
.news-row:last-child{{border-bottom:none}}
.news-n{{min-width:20px;height:20px;background:#EBF4FF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.6rem;font-weight:700;color:#0D3B8E;flex-shrink:0;margin-top:1px}}
.news-t{{font-size:.78rem;color:#1A2B5F;text-decoration:none;line-height:1.45;display:block}}
.news-t:hover{{color:#0D3B8E;text-decoration:underline}}
.news-src{{font-size:.63rem;color:#A0AEC0;margin-top:2px}}
.press{{background:#F7FAFF;border:1px solid #BEE3F8;border-radius:8px;padding:11px 13px;margin-bottom:7px}}
.press-d{{font-size:.65rem;color:#3182CE;font-weight:600;margin-bottom:3px}}
.press-t{{font-size:.78rem;color:#1A2B5F;text-decoration:none;font-weight:600;line-height:1.4;display:block}}
.press-t:hover{{color:#0D3B8E}}
.no-data{{text-align:center;padding:20px;color:#A0AEC0;font-size:.8rem}}

/* ── CP 테이블 ── */
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#EDF2F7;color:#4A5568;font-weight:700;padding:9px 10px;text-align:center;font-size:11px;border:1px solid #E2E8F0}}
td{{padding:8px 10px;border:1px solid #E2E8F0;color:#2D3748;text-align:center;vertical-align:middle}}
.cat{{background:#F7FAFF;font-weight:700;color:#1A2B5F}}
.nm{{text-align:left}}.act{{text-align:left;color:#4A5568;font-size:12px}}
.done{{background:#C6F6D5;color:#22543D;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.ing{{background:#BEE3F8;color:#2C5282;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.plan{{background:#EDF2F7;color:#4A5568;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}}
.hi{{color:#22543D;font-weight:700}}.md{{color:#2C5282;font-weight:700}}.lo{{color:#c0392b;font-weight:700}}
tfoot td{{background:#EDF2F7;font-weight:700;color:#1A2B5F}}

/* ── 차트 ── */
.chart-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}

/* ── 타임라인 ── */
.tl-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.tl-col{{background:white;border-radius:12px;padding:18px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5}}
.tl-sec{{font-size:.75rem;font-weight:700;color:#4A5568;border-bottom:2px solid #E2E8F0;padding-bottom:6px;margin-bottom:10px}}
.tl-item{{display:flex;align-items:flex-start;gap:7px;padding:5px 0;border-bottom:1px dashed #EDF2F7}}
.tl-item:last-child{{border-bottom:none}}
.tl-date{{font-size:.66rem;color:#3182CE;font-weight:700;white-space:nowrap;min-width:34px}}
.tl-dot{{width:6px;height:6px;background:#0D3B8E;border-radius:50%;margin-top:4px;flex-shrink:0}}
.tl-text{{font-size:.74rem;color:#2D3748;line-height:1.4}}

/* ── TOP 버튼 ── */
.top-btn{{position:fixed;bottom:28px;right:18px;width:40px;height:40px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.1rem;font-weight:700;box-shadow:0 3px 14px rgba(13,59,142,.4);cursor:pointer;border:none;z-index:999}}

/* ── 반응형 ── */
@media(max-width:900px){{
  .kpi-grid,.chart-grid,.tl-grid{{grid-template-columns:repeat(2,1fr)}}
  .two-col{{grid-template-columns:1fr}}
  .nav-links{{display:none}}
}}
@media(max-width:600px){{
  .kpi-grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>

<!-- 고정 네비 -->
<nav class="nav">
  <div class="nav-left">
    <span class="nav-title">📊 CP 컴플라이언스 대시보드</span>
    <span class="nav-badge">Paris Baguette</span>
  </div>
  <div class="nav-links">
    <button class="nav-btn" onclick="scrollTo('sec-overview')">📈 전체 현황</button>
    <button class="nav-btn" onclick="scrollTo('sec-news')">📰 일일 뉴스</button>
    <button class="nav-btn" onclick="scrollTo('sec-cp')">📊 CP 운영</button>
    <button class="nav-btn" onclick="scrollTo('sec-chart')">🔍 차트 분석</button>
    <button class="nav-btn" onclick="scrollTo('sec-tl')">🗓️ 타임라인</button>
  </div>
  <span class="nav-date">📅 {TODAY} · 4월 기준</span>
</nav>

<div class="wrap">

<!-- ① 전체 현황 -->
<div id="sec-overview" class="section" style="padding-top:8px">

  <!-- 인사이트 -->
  <div class="insight">
    <div class="insight-t">💡 경영진 핵심 인사이트 — 4월 기준</div>
    <div class="insight-txt">
      전체 CP 활동 달성률 <strong style="color:#FFD700">{kpi_pct}%</strong>로 목표 대비 미흡.
      교육 부문(30%)과 운영 부문(25%)이 주요 미달 영역.
      내부신고 {kpi_sign}건 중 1건 처리 진행 중이며, 법령 검토 미처리 2건 신속 처리 필요.
    </div>
    <div class="chips">
      <span class="chip chip-warn">⚠ 교육 목표 30% 달성</span>
      <span class="chip chip-warn">⚠ 운영 목표 25% 달성</span>
      <span class="chip chip-ok">✓ 대표이사 의지표명 125%</span>
      <span class="chip chip-ok">✓ 효과성평가 100%</span>
    </div>
  </div>

  <!-- KPI 카드 -->
  <div class="kpi-grid">
    <div class="kpi b">
      <div class="kpi-lbl">달성률</div>
      <div class="kpi-val">{kpi_pct}<span>%</span></div>
      <div class="kpi-sub">목표 {kpi_goal}건 · 실적 {kpi_actual}건</div>
      <div class="kpi-bar"><div class="kpi-fill" style="width:{kpi_bars[0]}%;background:#0D3B8E"></div></div>
    </div>
    <div class="kpi g">
      <div class="kpi-lbl">내부신고</div>
      <div class="kpi-val">{kpi_sign}<span>건</span></div>
      <div class="kpi-sub">처리완료 11 · 진행중 1</div>
      <div class="kpi-bar"><div class="kpi-fill" style="width:{kpi_bars[1]}%;background:#22863a"></div></div>
    </div>
    <div class="kpi o">
      <div class="kpi-lbl">법령검토</div>
      <div class="kpi-val">{kpi_law}<span>건</span></div>
      <div class="kpi-sub">평균 3.5일 · 미처리 2건</div>
      <div class="kpi-bar"><div class="kpi-fill" style="width:{kpi_bars[2]}%;background:#d45500"></div></div>
    </div>
    <div class="kpi r">
      <div class="kpi-lbl">공정거래검토</div>
      <div class="kpi-val">{kpi_ftc}<span>건</span></div>
      <div class="kpi-sub">가맹사업법 594건(78%)</div>
      <div class="kpi-bar"><div class="kpi-fill" style="width:{kpi_bars[3]}%;background:#c0392b"></div></div>
    </div>
  </div>
</div>

<!-- ② 일일 뉴스 -->
<div id="sec-news" class="section">
  <div class="section-title">📰 일일 뉴스 · 보도자료</div>
  <div class="two-col">
    <div class="card">
      <div class="card-head">📰 일일 NEWS <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">법령/가맹사업</span></div>
      <span class="badge crawl">🕷️ Google News · {news_ts or "미수집"}</span>
      {news_html}
    </div>
    <div class="card">
      <div class="card-head">📋 공정위/식약처 보도자료 <span style="margin-left:auto;font-size:.7rem;color:#A0AEC0;font-weight:400">자료업데이트</span></div>
      <span class="badge crawl">🕷️ Google News · {press_ts or "미수집"}</span>
      <div style="margin-top:8px">{press_html}</div>
    </div>
  </div>
</div>

<!-- ③ CP 운영현황 -->
<div id="sec-cp" class="section">
  <div class="section-title">📊 CP 운영현황 <span style="font-size:.72rem;color:#A0AEC0;font-weight:400;margin-left:auto">4월 기준</span></div>
  <div class="card" style="overflow-x:auto">
    <table>
      <thead><tr><th>구분</th><th>내용</th><th>목표</th><th>실적</th><th>달성률</th><th>상태</th><th>주요 활동</th></tr></thead>
      <tbody>{rows_html}</tbody>
      <tfoot><tr><td colspan="2">합계</td><td>{tg}</td><td>{ta}</td><td><span class="lo">{tp}%</span></td><td></td><td></td></tr></tfoot>
    </table>
  </div>
</div>

<!-- ④ 차트 분석 -->
<div id="sec-chart" class="section">
  <div class="section-title">🔍 차트 분석</div>
  <div class="chart-grid">
    <div class="card">
      <div class="card-head">📥 내부신고 현황</div>
      <canvas id="ch1" height="200"></canvas>
    </div>
    <div class="card">
      <div class="card-head">📖 법령 검토건수</div>
      <canvas id="ch2" height="200"></canvas>
    </div>
    <div class="card">
      <div class="card-head">⚖️ 공정거래 법령별</div>
      <canvas id="ch3" height="200"></canvas>
    </div>
  </div>
</div>

<!-- ⑤ 타임라인 -->
<div id="sec-tl" class="section">
  <div class="section-title">🗓️ 4월 주요 활동 타임라인</div>
  <div class="tl-grid">{tl_cols_html}</div>
</div>

</div><!-- /wrap -->

<!-- TOP 버튼 -->
<button class="top-btn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
// 앵커 스크롤
function scrollTo(id) {{
  var el = document.getElementById(id);
  if(el) el.scrollIntoView({{behavior:'smooth', block:'start'}});
}}

// 차트
new Chart(document.getElementById('ch1'),{{
  type:'bar',
  data:{{labels:{months},datasets:[
    {{label:'신고건수',data:{sign_cnt},backgroundColor:'rgba(13,59,142,0.75)',borderRadius:6}},
    {{label:'처리완료',data:{sign_done},backgroundColor:'rgba(52,211,153,0.75)',borderRadius:6}}
  ]}},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},
    scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
}});

new Chart(document.getElementById('ch2'),{{
  type:'line',
  data:{{labels:{law_months},datasets:[{{
    label:'누적 검토',data:{law_cum},
    borderColor:'#0D3B8E',backgroundColor:'rgba(13,59,142,0.08)',
    fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#0D3B8E'
  }}]}},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{legend:{{labels:{{font:{{size:11}},boxWidth:10}}}}}},
    scales:{{y:{{beginAtZero:true,ticks:{{font:{{size:11}}}}}},x:{{ticks:{{font:{{size:11}}}}}}}}}}
}});

new Chart(document.getElementById('ch3'),{{
  type:'doughnut',
  data:{{labels:{ftc_lbl},datasets:[{{
    data:{ftc_val},
    backgroundColor:['#0D3B8E','#1A56C4','#3182CE','#63B3ED'],
    borderWidth:2,borderColor:'#fff'
  }}]}},
  options:{{responsive:true,maintainAspectRatio:false,
    plugins:{{
      legend:{{position:'right',labels:{{font:{{size:11}},boxWidth:10}}}},
      tooltip:{{callbacks:{{label:function(c){{return c.label+': '+c.raw+'건'}}}}}}
    }}
  }}
}});

// 네비 활성화
window.addEventListener('scroll', function(){{
  var secs = ['sec-overview','sec-news','sec-cp','sec-chart','sec-tl'];
  var btns = document.querySelectorAll('.nav-btn');
  var cur = '';
  secs.forEach(function(id){{
    var el = document.getElementById(id);
    if(el && el.getBoundingClientRect().top <= 80) cur = id;
  }});
  btns.forEach(function(b,i){{
    b.style.background = (cur === secs[i]) ? 'rgba(255,255,255,.2)' : 'transparent';
    b.style.color = (cur === secs[i]) ? 'white' : 'rgba(255,255,255,.7)';
  }});
}});
</script>
</body>
</html>
""", height=4000, scrolling=True)

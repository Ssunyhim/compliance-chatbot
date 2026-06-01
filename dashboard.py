# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
# 실행: python -m streamlit run dashboard.py
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import datetime, json
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="CP 컴플라이언스 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")
NOW = datetime.datetime.now(KST)
TODAY = NOW.strftime("%Y년 %m월 %d일 (%a)")

# ══════════════════════════════════════════════════════════════
#  CSS + 구글 폰트 + Tailwind-like 커스텀
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800;900&family=Noto+Serif+KR:wght@700&display=swap');

/* ── 리셋 ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,.stApp{font-family:'Noto Sans KR',sans-serif!important}
.stApp{background:#F0F4F8!important}
header[data-testid="stHeader"]{display:none!important}
div[data-testid="stStatusWidget"]{display:none!important}
section[data-testid="stMain"]{padding:0!important}
section[data-testid="stMain"]>div{padding:0!important}
.block-container{padding:0!important;max-width:100%!important}
.stTabs [data-baseweb="tab-list"]{gap:0!important;background:#fff;border-bottom:2px solid #E2E8F0}
.stTabs [data-baseweb="tab"]{padding:12px 20px!important;font-size:.85rem!important;font-weight:600!important;color:#4A5568!important;border-radius:0!important}
.stTabs [aria-selected="true"]{color:#1A365D!important;border-bottom:3px solid #1A365D!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.stTabs [data-baseweb="tab-border"]{display:none!important}

/* ── 상단 네비 ── */
.dash-nav{
    background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%);
    padding:0 32px;
    display:flex;align-items:center;justify-content:space-between;
    height:58px;
    box-shadow:0 2px 12px rgba(6,27,74,0.3);
    position:sticky;top:0;z-index:999;
}
.dash-nav-left{display:flex;align-items:center;gap:16px}
.dash-nav-logo{font-family:'Noto Serif KR',serif;color:white;font-size:1.05rem;font-weight:700;letter-spacing:-.3px;white-space:nowrap}
.dash-nav-badge{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 10px;color:rgba(255,255,255,.85);font-size:.7rem;font-weight:600}
.dash-nav-right{display:flex;align-items:center;gap:6px}
.nav-btn{background:transparent;border:none;color:rgba(255,255,255,.75);padding:6px 12px;border-radius:6px;font-size:.78rem;font-weight:500;cursor:pointer;transition:all .15s;font-family:'Noto Sans KR',sans-serif;white-space:nowrap}
.nav-btn:hover{background:rgba(255,255,255,.12);color:white}
.nav-btn.active{background:rgba(255,255,255,.18);color:white;font-weight:700}

/* ── 서브 헤더 ── */
.dash-subheader{
    background:white;
    padding:10px 32px;
    display:flex;align-items:center;justify-content:space-between;
    border-bottom:1px solid #E2E8F0;
    flex-wrap:wrap;gap:8px;
}
.dash-subheader-left{font-size:.8rem;color:#4A5568;display:flex;align-items:center;gap:8px}
.dash-date{font-weight:700;color:#1A365D}
.dash-update{color:#A0AEC0;font-size:.72rem}
.dash-subheader-right{display:flex;gap:8px}

/* ── 컨텐츠 ── */
.dash-content{padding:20px 32px 40px}

/* ── KPI 카드 ── */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.kpi-card{background:white;border-radius:12px;padding:18px 20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;position:relative;overflow:hidden}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.kpi-card.blue::before{background:linear-gradient(90deg,#0D3B8E,#1A56C4)}
.kpi-card.green::before{background:linear-gradient(90deg,#22863a,#28a745)}
.kpi-card.orange::before{background:linear-gradient(90deg,#d45500,#f77f00)}
.kpi-card.red::before{background:linear-gradient(90deg,#c0392b,#e74c3c)}
.kpi-label{font-size:.72rem;font-weight:600;color:#718096;letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px}
.kpi-value{font-size:2rem;font-weight:800;color:#1A2B5F;line-height:1;margin-bottom:6px}
.kpi-value span{font-size:1rem;font-weight:600;color:#4A5568}
.kpi-sub{font-size:.75rem;color:#718096}
.kpi-bar{height:4px;background:#E8EDF5;border-radius:2px;margin-top:10px;overflow:hidden}
.kpi-bar-fill{height:100%;border-radius:2px;transition:width .8s ease}

/* ── 섹션 카드 ── */
.section-card{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;margin-bottom:18px}
.section-title{font-size:.88rem;font-weight:700;color:#1A2B5F;margin-bottom:14px;display:flex;align-items:center;gap:7px;border-bottom:1px solid #EDF2F7;padding-bottom:10px}
.section-title .icon{font-size:1rem}
.section-subtitle{font-size:.72rem;color:#A0AEC0;margin-left:auto;font-weight:400}

/* ── 뉴스 아이템 ── */
.news-item{padding:9px 0;border-bottom:1px dashed #EDF2F7;display:flex;align-items:flex-start;gap:8px;cursor:pointer}
.news-item:last-child{border-bottom:none}
.news-num{min-width:20px;height:20px;background:#EBF4FF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:700;color:#0D3B8E;margin-top:1px}
.news-text{font-size:.8rem;color:#2D3748;line-height:1.5;flex:1}
.news-text:hover{color:#0D3B8E}

/* ── 보도자료 카드 ── */
.press-card{background:#F7FAFF;border:1px solid #BEE3F8;border-radius:8px;padding:12px 14px;margin-bottom:8px}
.press-date{font-size:.68rem;color:#3182CE;font-weight:600;margin-bottom:3px}
.press-title{font-size:.8rem;color:#1A2B5F;font-weight:600;line-height:1.4;margin-bottom:6px}
.press-tags{display:flex;flex-wrap:wrap;gap:4px}
.press-tag{background:#EBF8FF;color:#2B6CB0;border-radius:10px;padding:2px 8px;font-size:.65rem;font-weight:600}

/* ── CP 테이블 ── */
.cp-table{width:100%;border-collapse:collapse;font-size:.79rem}
.cp-table th{background:#EDF2F7;color:#4A5568;font-weight:700;padding:8px 10px;text-align:center;font-size:.72rem;letter-spacing:.3px}
.cp-table td{padding:8px 10px;border-bottom:1px solid #EDF2F7;color:#2D3748;text-align:center}
.cp-table tr:last-child td{border-bottom:none}
.cp-table .cat-label{background:#F7FAFF;font-weight:700;color:#1A2B5F;text-align:left}
.cp-table .name-col{text-align:left;color:#2D3748}
.status-done{display:inline-block;background:#C6F6D5;color:#22543D;border-radius:10px;padding:2px 8px;font-size:.68rem;font-weight:700}
.status-ing{display:inline-block;background:#BEE3F8;color:#2C5282;border-radius:10px;padding:2px 8px;font-size:.68rem;font-weight:700}
.status-plan{display:inline-block;background:#EDF2F7;color:#4A5568;border-radius:10px;padding:2px 8px;font-size:.68rem;font-weight:700}
.pct-high{color:#22543D;font-weight:700}
.pct-mid{color:#2C5282;font-weight:700}
.pct-low{color:#c0392b;font-weight:700}

/* ── 타임라인 ── */
.timeline-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.timeline-section-title{font-size:.75rem;font-weight:700;color:#4A5568;margin-bottom:8px;padding-bottom:4px;border-bottom:2px solid #E2E8F0}
.timeline-item{display:flex;align-items:flex-start;gap:7px;padding:5px 0;border-bottom:1px dashed #EDF2F7}
.timeline-item:last-child{border-bottom:none}
.tl-date{font-size:.68rem;color:#3182CE;font-weight:700;white-space:nowrap;min-width:34px}
.tl-dot{width:6px;height:6px;background:#0D3B8E;border-radius:50%;margin-top:4px;flex-shrink:0}
.tl-text{font-size:.76rem;color:#2D3748;line-height:1.4}

/* ── 인사이트 배너 ── */
.insight-banner{background:linear-gradient(135deg,#1A365D,#2B6CB0);border-radius:12px;padding:18px 22px;margin-bottom:18px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.insight-icon{font-size:1.8rem}
.insight-content{flex:1;min-width:200px}
.insight-title{color:white;font-size:.9rem;font-weight:700;margin-bottom:5px}
.insight-text{color:rgba(255,255,255,.8);font-size:.78rem;line-height:1.55}
.insight-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.insight-chip{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 10px;color:white;font-size:.7rem;font-weight:600}
.insight-chip.warn{background:rgba(255,87,51,.25);border-color:rgba(255,87,51,.5)}
.insight-chip.ok{background:rgba(52,211,153,.2);border-color:rgba(52,211,153,.4)}

/* ── TOP 버튼 ── */
.top-btn{position:fixed;bottom:28px;right:24px;width:42px;height:42px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;color:white;font-size:1.1rem;font-weight:700;box-shadow:0 3px 14px rgba(13,59,142,.4);z-index:9999;text-decoration:none;transition:all .2s}
.top-btn:hover{transform:translateY(-3px);box-shadow:0 6px 18px rgba(13,59,142,.5)}

/* ── 반응형 ── */
@media(max-width:1024px){
    .kpi-grid{grid-template-columns:repeat(2,1fr)}
    .timeline-grid{grid-template-columns:1fr}
    .dash-content{padding:16px 18px 30px}
    .dash-nav{padding:0 18px}
    .dash-subheader{padding:8px 18px}
}
@media(max-width:640px){
    .kpi-grid{grid-template-columns:1fr}
    .dash-nav-right{display:none}
    .kpi-value{font-size:1.6rem}
}
</style>
<a class="top-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="맨 위로">↑</a>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  샘플 데이터 (구글 시트 연동 전 기본값)
# ══════════════════════════════════════════════════════════════
kpi_data = {
    "달성률": {"value": 48, "unit": "%", "sub": "목표 40건 · 실적 19건", "color": "blue", "max": 100},
    "내부신고": {"value": 12, "unit": "건", "sub": "처리완료 11 · 진행중 1", "color": "green", "max": 30},
    "법령검토": {"value": 350, "unit": "건", "sub": "평균 3.5일 · 미처리 2건", "color": "orange", "max": 500},
    "공정거래검토": {"value": 761, "unit": "건", "sub": "가맹사업법 594건(78%)", "color": "red", "max": 1000},
}

news_data = [
    "필수품목 위반사항 OO업체의 영업처분 진행",
    "최근 A회사의 정보유출 사건으로 인해...",
    "노동법 개정으로 가맹점 운영 영향 예상",
    "공정거래위원회 조사 일정 공지",
]

press_data = [
    {
        "date": "2026-05-19",
        "source": "식품의약품안전처",
        "title": "식품의약품안전처, 하절기 불시 위생 특별 단속 및 알레르기 유발물질 라벨 표시 미흡 처분 공고",
        "tags": ["#식품안전", "#알레르기표시", "#소케이스관리", "#소비기한"]
    }
]

cp_table = [
    {"cat": "구축", "name": "대표이사 의지표명", "goal": 4, "actual": 5, "pct": 125, "status": "완료", "activity": "자율준수 선서식, 컨퍼런스"},
    {"cat": "구축", "name": "CP 확산활동", "goal": 4, "actual": 4, "pct": 100, "status": "완료", "activity": "대표이사 CP 영상 제작"},
    {"cat": "교육", "name": "CP 교육", "goal": 20, "actual": 6, "pct": 30, "status": "진행", "activity": "신입·입직IP 교육 예정"},
    {"cat": "교육", "name": "CP 규정", "goal": 2, "actual": None, "pct": None, "status": "계획", "activity": "개정 진행중"},
    {"cat": "운영", "name": "위험성평가", "goal": 4, "actual": 1, "pct": 25, "status": "진행", "activity": "개선방안 도출(04/22)"},
    {"cat": "운영", "name": "자율준수협의회", "goal": 2, "actual": 1, "pct": 50, "status": "완료", "activity": "공정거래실신 서"},
    {"cat": "평가", "name": "효과성평가", "goal": 2, "actual": 2, "pct": 100, "status": "완료", "activity": "개선방안 도출(04/27)"},
    {"cat": "평가", "name": "사업부 현장컨설팅", "goal": 2, "actual": None, "pct": None, "status": "계획", "activity": "진행 협의 중"},
]

timeline_data = {
    "구축/확산": [
        ("01/30", "자율준수 선서식"),
        ("04/20", "CP 영상 배포"),
        ("04/16", "컨퍼런스 참가"),
    ],
    "교육": [
        ("04/16", "임원 교육"),
        ("04/23", "사전업무협의체 교육"),
        ("04/29", "IP 실무자 교육"),
    ],
    "운영/평가": [
        ("04/22", "위험성평가 결과보고"),
        ("04/27", "효과성평가 결과보고"),
        ("04/11", "1분기 CP 서비스 보고"),
    ],
}

# 법령별 데이터
law_data = {
    "가맹사업법": 594, "약관법": 78, "공정거래법": 35, "하도급법": 27
}

# ══════════════════════════════════════════════════════════════
#  네비게이션
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dash-nav">
  <div class="dash-nav-left">
    <div class="dash-nav-logo">📊 CP 컴플라이언스 대시보드</div>
    <div class="dash-nav-badge">Paris Baguette</div>
  </div>
  <div class="dash-nav-right">
    <button class="nav-btn active" onclick="document.getElementById('sec-overview').scrollIntoView({{behavior:'smooth'}})">전체 현황</button>
    <button class="nav-btn" onclick="document.getElementById('sec-news').scrollIntoView({{behavior:'smooth'}})">일일 뉴스</button>
    <button class="nav-btn" onclick="document.getElementById('sec-cp').scrollIntoView({{behavior:'smooth'}})">CP 운영</button>
    <button class="nav-btn" onclick="document.getElementById('sec-chart').scrollIntoView({{behavior:'smooth'}})">차트 분석</button>
    <button class="nav-btn" onclick="document.getElementById('sec-timeline').scrollIntoView({{behavior:'smooth'}})">활동 타임라인</button>
  </div>
</div>
<div class="dash-subheader">
  <div class="dash-subheader-left">
    <span>📅</span>
    <span class="dash-date">{TODAY}</span>
    <span class="dash-update">기준 · 4월 CP 운영현황</span>
  </div>
  <div class="dash-subheader-right">
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="dash-content">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  핵심 인사이트 배너
# ══════════════════════════════════════════════════════════════
st.markdown('<div id="sec-overview"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-banner">
  <div class="insight-icon">💡</div>
  <div class="insight-content">
    <div class="insight-title">경영진 핵심 인사이트 — 4월 기준</div>
    <div class="insight-text">
      전체 CP 활동 달성률 <strong style="color:#FFD700">48%</strong>로 목표 대비 미흡.
      교육 부문(30%)과 운영 부문(25%)이 주요 미달 영역.
      내부신고 12건 중 1건 처리 진행 중이며, 법령 검토 미처리 2건 신속 처리 필요.
    </div>
    <div class="insight-chips">
      <span class="insight-chip warn">⚠ 교육 목표 30% 달성</span>
      <span class="insight-chip warn">⚠ 운영 목표 25% 달성</span>
      <span class="insight-chip ok">✓ 대표이사 의지표명 125%</span>
      <span class="insight-chip ok">✓ 효과성평가 100%</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  KPI 카드
# ══════════════════════════════════════════════════════════════
kpi_html = '<div class="kpi-grid">'
for label, d in kpi_data.items():
    pct = int(d["value"] / d["max"] * 100)
    kpi_html += f"""
    <div class="kpi-card {d['color']}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{d['value']}<span>{d['unit']}</span></div>
      <div class="kpi-sub">{d['sub']}</div>
      <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct}%;background:{'#0D3B8E' if d['color']=='blue' else '#22863a' if d['color']=='green' else '#d45500' if d['color']=='orange' else '#c0392b'}"></div></div>
    </div>"""
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  뉴스 + 보도자료
# ══════════════════════════════════════════════════════════════
st.markdown('<div id="sec-news"></div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    news_items = "".join([
        f'<div class="news-item"><span class="news-num">{i+1}</span><span class="news-text">{n}</span></div>'
        for i, n in enumerate(news_data)
    ])
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title"><span class="icon">📰</span> 일일 NEWS <span class="section-subtitle">법령/가맹사업 관련</span></div>
      {news_items}
    </div>
    """, unsafe_allow_html=True)

with col2:
    press_items = ""
    for p in press_data:
        tags = "".join([f'<span class="press-tag">{t}</span>' for t in p["tags"]])
        press_items += f"""
        <div class="press-card">
          <div class="press-date">{p['date']} · {p['source']}</div>
          <div class="press-title">{p['title']}</div>
          <div class="press-tags">{tags}</div>
        </div>"""
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title"><span class="icon">📋</span> 공정위 / 식약처 보도자료 <span class="section-subtitle">자료 업데이트</span></div>
      {press_items}
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CP 운영현황 테이블
# ══════════════════════════════════════════════════════════════
st.markdown('<div id="sec-cp"></div>', unsafe_allow_html=True)

def pct_badge(pct):
    if pct is None: return "—"
    if pct >= 100: return f'<span class="pct-high">{pct}%</span>'
    if pct >= 50: return f'<span class="pct-mid">{pct}%</span>'
    return f'<span class="pct-low">{pct}%</span>'

def status_badge(s):
    if s == "완료": return f'<span class="status-done">완료</span>'
    if s == "진행": return f'<span class="status-ing">진행</span>'
    return f'<span class="status-plan">계획</span>'

rows = ""
prev_cat = ""
for row in cp_table:
    cat_cell = ""
    if row["cat"] != prev_cat:
        count = sum(1 for r in cp_table if r["cat"] == row["cat"])
        cat_cell = f'<td class="cat-label" rowspan="{count}">{row["cat"]}</td>'
        prev_cat = row["cat"]
    actual = row["actual"] if row["actual"] else "—"
    rows += f"""<tr>
        {cat_cell}
        <td class="name-col">{row['name']}</td>
        <td>{row['goal']}</td>
        <td>{actual}</td>
        <td>{pct_badge(row['pct'])}</td>
        <td>{status_badge(row['status'])}</td>
        <td style="text-align:left;font-size:.75rem;color:#4A5568">{row['activity']}</td>
    </tr>"""

total_goal = sum(r["goal"] for r in cp_table)
total_actual = sum(r["actual"] for r in cp_table if r["actual"])
total_pct = int(total_actual / total_goal * 100)

st.markdown(f"""
<div class="section-card">
  <div class="section-title"><span class="icon">📊</span> CP 운영현황 <span class="section-subtitle">4월 기준</span></div>
  <table class="cp-table">
    <thead>
      <tr>
        <th>구분</th><th>내용</th><th>목표</th><th>실적</th><th>달성률</th><th>상태</th><th>주요 활동</th>
      </tr>
    </thead>
    <tbody>
      {rows}
      <tr style="background:#EDF2F7;font-weight:700">
        <td colspan="2" style="text-align:center;color:#1A2B5F">합계</td>
        <td>{total_goal}</td><td>{total_actual}</td>
        <td>{pct_badge(total_pct)}</td><td></td><td></td>
      </tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  차트 섹션 (Chart.js)
# ══════════════════════════════════════════════════════════════
st.markdown('<div id="sec-chart"></div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="section-card" style="min-height:280px"><div class="section-title"><span class="icon">📥</span> 내부신고 현황</div>', unsafe_allow_html=True)
    components.html("""
    <canvas id="c1" style="width:100%;height:180px"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
    new Chart(document.getElementById('c1'),{
      type:'bar',
      data:{
        labels:['1월','2월','3월','4월'],
        datasets:[{
          label:'신고건수',
          data:[2,3,4,3],
          backgroundColor:'rgba(13,59,142,0.7)',
          borderRadius:6
        },{
          label:'처리완료',
          data:[2,3,4,2],
          backgroundColor:'rgba(52,211,153,0.7)',
          borderRadius:6
        }]
      },
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{labels:{font:{family:'Noto Sans KR',size:10},boxWidth:10}}},
        scales:{
          y:{beginAtZero:true,ticks:{font:{family:'Noto Sans KR',size:10}}},
          x:{ticks:{font:{family:'Noto Sans KR',size:10}}}
        }
      }
    });
    </script>
    """, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card" style="min-height:280px"><div class="section-title"><span class="icon">📖</span> 법령 검토건수</div>', unsafe_allow_html=True)
    components.html("""
    <canvas id="c2" style="width:100%;height:180px"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
    new Chart(document.getElementById('c2'),{
      type:'line',
      data:{
        labels:['1월','2월','3월','4월'],
        datasets:[{
          label:'누적 검토',
          data:[82,175,268,350],
          borderColor:'#0D3B8E',
          backgroundColor:'rgba(13,59,142,0.08)',
          fill:true,tension:.4,pointRadius:5,
          pointBackgroundColor:'#0D3B8E'
        }]
      },
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{labels:{font:{family:'Noto Sans KR',size:10},boxWidth:10}}},
        scales:{
          y:{beginAtZero:true,ticks:{font:{family:'Noto Sans KR',size:10}}},
          x:{ticks:{font:{family:'Noto Sans KR',size:10}}}
        }
      }
    });
    </script>
    """, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="section-card" style="min-height:280px"><div class="section-title"><span class="icon">⚖️</span> 공정거래 법령별 검토</div>', unsafe_allow_html=True)
    law_labels = list(law_data.keys())
    law_values = list(law_data.values())
    components.html(f"""
    <canvas id="c3" style="width:100%;height:180px"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
    new Chart(document.getElementById('c3'),{{
      type:'doughnut',
      data:{{
        labels:{json.dumps(law_labels, ensure_ascii=False)},
        datasets:[{{
          data:{law_values},
          backgroundColor:['#0D3B8E','#1A56C4','#3182CE','#63B3ED'],
          borderWidth:2,borderColor:'#fff'
        }}]
      }},
      options:{{
        responsive:true,maintainAspectRatio:false,
        plugins:{{
          legend:{{position:'right',labels:{{font:{{family:'Noto Sans KR',size:10}},boxWidth:10}}}},
          tooltip:{{callbacks:{{label:function(c){{return c.label+': '+c.raw+'건'}}}}}}
        }}
      }}
    }});
    </script>
    """, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  활동 타임라인
# ══════════════════════════════════════════════════════════════
st.markdown('<div id="sec-timeline"></div>', unsafe_allow_html=True)

tl_cols = ""
for section, items in timeline_data.items():
    items_html = "".join([
        f'<div class="timeline-item"><span class="tl-date">{d}</span><span class="tl-dot"></span><span class="tl-text">{t}</span></div>'
        for d, t in items
    ])
    tl_cols += f'<div><div class="timeline-section-title">{section}</div>{items_html}</div>'

st.markdown(f"""
<div class="section-card">
  <div class="section-title"><span class="icon">🗓️</span> 4월 주요 활동 타임라인</div>
  <div class="timeline-grid">{tl_cols}</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # dash-content 닫기

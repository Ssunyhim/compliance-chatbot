# ============================================================
# dashboard.py  ─  CP 컴플라이언스 대시보드 (Paris Baguette)
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
KST   = ZoneInfo("Asia/Seoul")
NOW   = datetime.datetime.now(KST)
TODAY = NOW.strftime("%Y년 %m월 %d일 (%a)")

# ── 공통 CSS ──────────────────────────────────────────────────
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

/* 탭 */
.stTabs [data-baseweb="tab-list"]{background:#1A365D!important;gap:0!important;padding:0 16px}
.stTabs [data-baseweb="tab"]{color:rgba(255,255,255,.65)!important;font-size:.82rem!important;font-weight:600!important;padding:14px 18px!important;border-radius:0!important}
.stTabs [aria-selected="true"]{color:white!important;border-bottom:3px solid white!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}
.stTabs [data-baseweb="tab-border"]{display:none!important}
.stTabs [data-baseweb="tab-panel"]{padding:0!important}

/* 카드 */
.card{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 6px rgba(0,0,0,.07);border:1px solid #E8EDF5;margin-bottom:16px}
.card-title{font-size:.86rem;font-weight:700;color:#1A2B5F;display:flex;align-items:center;gap:7px;border-bottom:1px solid #EDF2F7;padding-bottom:10px;margin-bottom:14px}
.card-title .sub{font-size:.7rem;color:#A0AEC0;margin-left:auto;font-weight:400}

/* KPI */
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

/* 뉴스 */
.news-row{display:flex;align-items:flex-start;gap:8px;padding:8px 0;border-bottom:1px dashed #EDF2F7}
.news-row:last-child{border-bottom:none}
.news-n{min-width:20px;height:20px;background:#EBF4FF;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.62rem;font-weight:700;color:#0D3B8E;flex-shrink:0;margin-top:1px}
.news-t{font-size:.79rem;color:#2D3748;line-height:1.5}

/* 보도자료 */
.press{background:#F7FAFF;border:1px solid #BEE3F8;border-radius:8px;padding:12px 14px;margin-bottom:8px}
.press-d{font-size:.67rem;color:#3182CE;font-weight:600;margin-bottom:3px}
.press-t{font-size:.79rem;color:#1A2B5F;font-weight:600;line-height:1.4;margin-bottom:6px}
.press-tag{display:inline-block;background:#EBF8FF;color:#2B6CB0;border-radius:10px;padding:2px 7px;font-size:.63rem;font-weight:600;margin:2px 2px 0 0}

/* 인사이트 */
.insight{background:linear-gradient(135deg,#1A365D,#2B6CB0);border-radius:12px;padding:18px 22px;margin-bottom:16px}
.insight-t{color:white;font-size:.9rem;font-weight:700;margin-bottom:6px}
.insight-txt{color:rgba(255,255,255,.82);font-size:.78rem;line-height:1.55;margin-bottom:10px}
.chip{display:inline-block;border-radius:20px;padding:3px 10px;font-size:.69rem;font-weight:600;margin:2px 3px 2px 0}
.chip-warn{background:rgba(255,87,51,.22);border:1px solid rgba(255,87,51,.45);color:#FED7CC}
.chip-ok{background:rgba(52,211,153,.18);border:1px solid rgba(52,211,153,.38);color:#C6F6D5}

/* 타임라인 */
.tl-item{display:flex;align-items:flex-start;gap:7px;padding:5px 0;border-bottom:1px dashed #EDF2F7}
.tl-item:last-child{border-bottom:none}
.tl-date{font-size:.67rem;color:#3182CE;font-weight:700;white-space:nowrap;min-width:34px}
.tl-dot{width:6px;height:6px;background:#0D3B8E;border-radius:50%;margin-top:4px;flex-shrink:0}
.tl-text{font-size:.75rem;color:#2D3748;line-height:1.4}
.tl-sec{font-size:.74rem;font-weight:700;color:#4A5568;border-bottom:2px solid #E2E8F0;padding-bottom:5px;margin-bottom:8px}

/* TOP 버튼 */
.top-btn{position:fixed;bottom:28px;right:24px;width:42px;height:42px;background:linear-gradient(135deg,#0B2461,#1A56C4);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.1rem;font-weight:700;box-shadow:0 3px 14px rgba(13,59,142,.4);z-index:9999;cursor:pointer;text-decoration:none;border:none;transition:all .2s}

/* 반응형 */
@media(max-width:768px){.block-container{padding:0 8px!important}}
</style>
<button class="top-btn" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#061B4A 0%,#0D3B8E 60%,#1A56C4 100%);padding:14px 28px;display:flex;align-items:center;gap:14px">
  <span style="font-family:'Noto Serif KR',serif;color:white;font-size:1.08rem;font-weight:700">📊 CP 컴플라이언스 대시보드</span>
  <span style="background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 11px;color:rgba(255,255,255,.85);font-size:.7rem;font-weight:600">Paris Baguette</span>
  <span style="margin-left:auto;color:rgba(255,255,255,.65);font-size:.75rem">📅 {TODAY} &nbsp;·&nbsp; 4월 CP 운영현황 기준</span>
</div>
""", unsafe_allow_html=True)

# ── 탭 네비게이션 ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 전체 현황", "📰 일일 뉴스", "📊 CP 운영", "🔍 차트 분석", "🗓️ 활동 타임라인"
])

# ══════════════════════════════════════════════════
# TAB 1: 전체 현황
# ══════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)

    # 인사이트 배너
    st.markdown("""
    <div class="insight">
      <div class="insight-t">💡 경영진 핵심 인사이트 — 4월 기준</div>
      <div class="insight-txt">
        전체 CP 활동 달성률 <strong style="color:#FFD700">48%</strong>로 목표 대비 미흡.
        교육 부문(30%)과 운영 부문(25%)이 주요 미달 영역.
        내부신고 12건 중 1건 처리 진행 중이며, 법령 검토 미처리 2건 신속 처리 필요.
      </div>
      <div>
        <span class="chip chip-warn">⚠ 교육 목표 30% 달성</span>
        <span class="chip chip-warn">⚠ 운영 목표 25% 달성</span>
        <span class="chip chip-ok">✓ 대표이사 의지표명 125%</span>
        <span class="chip chip-ok">✓ 효과성평가 100%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI 카드
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "달성률", "48", "%", "목표 40건 · 실적 19건", "b", "#0D3B8E", 48),
        (k2, "내부신고", "12", "건", "처리완료 11 · 진행중 1", "g", "#22863a", 40),
        (k3, "법령검토", "350", "건", "평균 3.5일 · 미처리 2건", "o", "#d45500", 70),
        (k4, "공정거래검토", "761", "건", "가맹사업법 594건(78%)", "r", "#c0392b", 76),
    ]
    for col, lbl, val, unit, sub, cls, color, pct in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi {cls}">
              <div class="kpi-lbl">{lbl}</div>
              <div class="kpi-val">{val}<span>{unit}</span></div>
              <div class="kpi-sub">{sub}</div>
              <div class="kpi-bar"><div class="kpi-fill" style="width:{pct}%;background:{color}"></div></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 2: 일일 뉴스
# ══════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="card">
          <div class="card-title">📰 일일 NEWS <span class="sub">법령/가맹사업 관련</span></div>
          <div class="news-row"><span class="news-n">1</span><span class="news-t">필수품목 위반사항 OO업체의 영업처분 진행</span></div>
          <div class="news-row"><span class="news-n">2</span><span class="news-t">최근 A회사의 정보유출 사건으로 인해...</span></div>
          <div class="news-row"><span class="news-n">3</span><span class="news-t">노동법 개정으로 가맹점 운영 영향 예상</span></div>
          <div class="news-row"><span class="news-n">4</span><span class="news-t">공정거래위원회 조사 일정 공지</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
          <div class="card-title">📋 공정위 / 식약처 보도자료 <span class="sub">자료 업데이트</span></div>
          <div class="press">
            <div class="press-d">2026-05-19 · 식품의약품안전처</div>
            <div class="press-t">식품의약품안전처, 하절기 불시 위생 특별 단속 및 알레르기 유발물질 라벨 표시 미흡 처분 공고</div>
            <span class="press-tag">#식품안전</span>
            <span class="press-tag">#알레르기표시</span>
            <span class="press-tag">#소케이스관리</span>
            <span class="press-tag">#소비기한</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 3: CP 운영현황
# ══════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)
    st.markdown('<div class="card-title" style="font-size:.9rem;font-weight:700;color:#1A2B5F;padding:0 0 10px;border-bottom:1px solid #EDF2F7;margin-bottom:16px">📊 CP 운영현황 <span style="font-size:.72rem;color:#A0AEC0;font-weight:400;margin-left:auto">4월 기준</span></div>', unsafe_allow_html=True)

    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    body{font-family:'Noto Sans KR',sans-serif;margin:0;padding:0}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th{background:#EDF2F7;color:#4A5568;font-weight:700;padding:9px 10px;text-align:center;font-size:11px;letter-spacing:.3px;border:1px solid #E2E8F0}
    td{padding:8px 10px;border:1px solid #E2E8F0;color:#2D3748;text-align:center;vertical-align:middle}
    .cat{background:#F7FAFF;font-weight:700;color:#1A2B5F;text-align:center}
    .nm{text-align:left}
    .act{text-align:left;color:#4A5568;font-size:12px}
    .done{background:#C6F6D5;color:#22543D;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}
    .ing{background:#BEE3F8;color:#2C5282;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}
    .plan{background:#EDF2F7;color:#4A5568;border-radius:10px;padding:2px 8px;font-size:11px;font-weight:700;display:inline-block}
    .hi{color:#22543D;font-weight:700}.md{color:#2C5282;font-weight:700}.lo{color:#c0392b;font-weight:700}
    tfoot td{background:#EDF2F7;font-weight:700;color:#1A2B5F}
    </style>
    <table>
      <thead><tr><th>구분</th><th>내용</th><th>목표</th><th>실적</th><th>달성률</th><th>상태</th><th>주요 활동</th></tr></thead>
      <tbody>
        <tr><td class="cat" rowspan="2">구축</td><td class="nm">대표이사 의지표명</td><td>4</td><td>5</td><td><span class="hi">125%</span></td><td><span class="done">완료</span></td><td class="act">자율준수 선서식, 컨퍼런스</td></tr>
        <tr><td class="nm">CP 확산활동</td><td>4</td><td>4</td><td><span class="hi">100%</span></td><td><span class="done">완료</span></td><td class="act">대표이사 CP 영상 제작</td></tr>
        <tr><td class="cat" rowspan="2">교육</td><td class="nm">CP 교육</td><td>20</td><td>6</td><td><span class="lo">30%</span></td><td><span class="ing">진행</span></td><td class="act">신입·입직IP 교육 예정</td></tr>
        <tr><td class="nm">CP 규정</td><td>2</td><td>—</td><td>—</td><td><span class="plan">계획</span></td><td class="act">개정 진행중</td></tr>
        <tr><td class="cat" rowspan="2">운영</td><td class="nm">위험성평가</td><td>4</td><td>1</td><td><span class="lo">25%</span></td><td><span class="ing">진행</span></td><td class="act">개선방안 도출(04/22)</td></tr>
        <tr><td class="nm">자율준수협의회</td><td>2</td><td>1</td><td><span class="md">50%</span></td><td><span class="done">완료</span></td><td class="act">공정거래실신 서</td></tr>
        <tr><td class="cat" rowspan="2">평가</td><td class="nm">효과성평가</td><td>2</td><td>2</td><td><span class="hi">100%</span></td><td><span class="done">완료</span></td><td class="act">개선방안 도출(04/27)</td></tr>
        <tr><td class="nm">사업부 현장컨설팅</td><td>2</td><td>—</td><td>—</td><td><span class="plan">계획</span></td><td class="act">진행 협의 중</td></tr>
      </tbody>
      <tfoot><tr><td colspan="2">합계</td><td>40</td><td>19</td><td><span class="lo">48%</span></td><td></td><td></td></tr></tfoot>
    </table>
    """, height=320)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 4: 차트 분석
# ══════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="card"><div class="card-title">📥 내부신고 현황</div>', unsafe_allow_html=True)
        components.html("""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch1" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch1'),{
          type:'bar',
          data:{labels:['1월','2월','3월','4월'],
            datasets:[
              {label:'신고건수',data:[2,3,4,3],backgroundColor:'rgba(13,59,142,0.75)',borderRadius:6},
              {label:'처리완료',data:[2,3,4,2],backgroundColor:'rgba(52,211,153,0.75)',borderRadius:6}
            ]},
          options:{responsive:true,maintainAspectRatio:false,
            plugins:{legend:{labels:{font:{size:11},boxWidth:10}}},
            scales:{y:{beginAtZero:true,ticks:{font:{size:11}}},x:{ticks:{font:{size:11}}}}}
        });
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">📖 법령 검토건수</div>', unsafe_allow_html=True)
        components.html("""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch2" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch2'),{
          type:'line',
          data:{labels:['1월','2월','3월','4월'],
            datasets:[{label:'누적 검토',data:[82,175,268,350],
              borderColor:'#0D3B8E',backgroundColor:'rgba(13,59,142,0.08)',
              fill:true,tension:.4,pointRadius:5,pointBackgroundColor:'#0D3B8E'}]},
          options:{responsive:true,maintainAspectRatio:false,
            plugins:{legend:{labels:{font:{size:11},boxWidth:10}}},
            scales:{y:{beginAtZero:true,ticks:{font:{size:11}}},x:{ticks:{font:{size:11}}}}}
        });
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="card"><div class="card-title">⚖️ 공정거래 법령별 검토</div>', unsafe_allow_html=True)
        components.html("""
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <canvas id="ch3" style="width:100%;height:220px"></canvas>
        <script>
        new Chart(document.getElementById('ch3'),{
          type:'doughnut',
          data:{labels:['가맹사업법','약관법','공정거래법','하도급법'],
            datasets:[{data:[594,78,35,27],
              backgroundColor:['#0D3B8E','#1A56C4','#3182CE','#63B3ED'],
              borderWidth:2,borderColor:'#fff'}]},
          options:{responsive:true,maintainAspectRatio:false,
            plugins:{
              legend:{position:'right',labels:{font:{size:11},boxWidth:10}},
              tooltip:{callbacks:{label:function(c){return c.label+': '+c.raw+'건'}}}}}
        });
        </script>
        """, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    # CP 달성률 가로 바 차트
    st.markdown('<div class="card"><div class="card-title">📊 CP 부문별 달성률 비교</div>', unsafe_allow_html=True)
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <canvas id="ch4" style="width:100%;height:200px"></canvas>
    <script>
    new Chart(document.getElementById('ch4'),{
      type:'bar',
      data:{
        labels:['대표이사 의지표명','CP 확산활동','CP 교육','위험성평가','자율준수협의회','효과성평가'],
        datasets:[
          {label:'목표',data:[4,4,20,4,2,2],backgroundColor:'rgba(200,210,230,0.5)',borderRadius:4},
          {label:'실적',data:[5,4,6,1,1,2],backgroundColor:'rgba(13,59,142,0.75)',borderRadius:4}
        ]},
      options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',
        plugins:{legend:{labels:{font:{size:11},boxWidth:10}}},
        scales:{y:{ticks:{font:{size:11}}},x:{beginAtZero:true,ticks:{font:{size:11}}}}}
    });
    </script>
    """, height=220)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 5: 활동 타임라인
# ══════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="padding:20px 24px 30px">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    timelines = {
        "🔨 구축/확산": [("01/30","자율준수 선서식"),("04/20","CP 영상 배포"),("04/16","컨퍼런스 참가")],
        "📚 교육": [("04/16","임원 교육"),("04/23","사전업무협의체 교육"),("04/29","IP 실무자 교육")],
        "📋 운영/평가": [("04/22","위험성평가 결과보고"),("04/27","효과성평가 결과보고"),("04/11","1분기 CP 서비스 보고")],
    }
    for col, (sec, items) in zip([c1,c2,c3], timelines.items()):
        with col:
            rows = "".join([
                f'<div class="tl-item"><span class="tl-date">{d}</span><span class="tl-dot"></span><span class="tl-text">{t}</span></div>'
                for d, t in items
            ])
            st.markdown(f"""
            <div class="card">
              <div class="tl-sec">{sec}</div>
              {rows}
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

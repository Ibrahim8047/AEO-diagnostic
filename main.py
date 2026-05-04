import streamlit as st
import json
import re
import time
import requests
from google import genai as google_genai
from datetime import datetime

st.set_page_config(
    page_title="AEO Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
}

/* ── Color Tokens ── */
:root {
    --bg:        #060A12;
    --card:      #0C1220;
    --card2:     #0A0F1C;
    --border:    #1A2540;
    --border2:   #111D35;
    --violet:    #7C3AED;
    --violet-lt: #A78BFA;
    --cyan:      #06B6D4;
    --cyan-lt:   #67E8F9;
    --emerald:   #10B981;
    --amber:     #F59E0B;
    --rose:      #F43F5E;
    --txt-1:     #F0F2FF;
    --txt-2:     #8892AA;
    --txt-3:     #3D4D6A;
    --txt-4:     #232E46;
}

/* ── App shell ── */
.stApp { background: var(--bg); }
.block-container { padding: 0 2.5rem 3rem; max-width: 1240px; }

/* ── Hide sidebar ── */
section[data-testid="stSidebar"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }

/* ── Top bar ── */
.topbar {
    background: linear-gradient(135deg, #0C1425 0%, #0E1830 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    margin: 2rem 0 0;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.topbar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--violet), var(--cyan), var(--emerald));
}
.topbar-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 600;
    background: linear-gradient(135deg, var(--txt-1) 40%, var(--violet-lt));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 0.3rem;
}
.topbar-query {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: var(--txt-3);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.topbar-query span { color: var(--txt-2); }
.topbar-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--txt-4);
    letter-spacing: 0.08em;
    text-align: right;
    margin-bottom: 0.5rem;
}
.topbar-pill {
    background: linear-gradient(135deg, var(--emerald), #059669);
    color: #fff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    padding: 3px 10px;
    border-radius: 4px;
    letter-spacing: 0.1em;
    font-weight: 700;
    box-shadow: 0 0 12px rgba(16,185,129,0.4);
}

/* ── Source chips ── */
.source-chips {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.8rem 0; margin-bottom: 0.5rem;
    justify-content: space-between;
}
.source-chip {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    padding: 4px 12px; border-radius: 20px;
    border: 1px solid;
}
.source-chip.google { background: rgba(124,58,237,0.12); border-color: rgba(124,58,237,0.35); color: var(--violet-lt); }
.source-chip.gemini { background: rgba(6,182,212,0.12); border-color: rgba(6,182,212,0.35); color: var(--cyan-lt); }
.chip-dot { width:6px; height:6px; border-radius:50%; display:inline-block; }
.chip-dot.google { background: var(--violet); }
.chip-dot.gemini { background: var(--cyan); }
.source-chip-right {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: var(--txt-3);
    margin-left: auto;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--txt-1) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--violet) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--txt-4) !important; }

label[data-testid="stWidgetLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    color: var(--txt-3) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-weight: 500 !important;
    margin-bottom: 0.3rem !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--violet) 0%, #6D28D9 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.75rem 1.8rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6D28D9 0%, var(--cyan) 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── KPI cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.kpi-card {
    background: linear-gradient(160deg, var(--card) 0%, var(--card2) 100%);
    border: 1px solid var(--border2);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--violet), var(--cyan));
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%);
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: var(--txt-1);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-sub {
    font-size: 0.7rem;
    color: var(--txt-4);
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Section heading ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2.2rem 0 1.2rem;
}
.sec-head-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    color: var(--txt-2);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    white-space: nowrap;
}
.sec-head-line { flex: 1; height: 1px; background: var(--border2); }
.sec-head-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--txt-3);
}

/* ── Rank table ── */
.rank-table { width: 100%; border-collapse: collapse; }
.rank-table thead tr {
    border-bottom: 1.5px solid var(--border2);
}
.rank-table thead th {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    padding: 0 0.8rem 0.8rem;
    text-align: left;
    font-weight: 500;
}
.rank-table thead th:first-child { padding-left: 0; }
.rank-table tbody tr {
    border-bottom: 1px solid var(--border2);
    transition: background 0.15s;
}
.rank-table tbody tr:hover { background: rgba(124,58,237,0.04); }
.rank-table tbody td {
    padding: 1rem 0.8rem;
    vertical-align: middle;
}
.rank-table tbody td:first-child { padding-left: 0; }

.rank-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--txt-4);
    width: 30px;
}
.rank-num.top { color: var(--emerald); }
.brand-cell-name {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--txt-1);
    margin-bottom: 2px;
}
.brand-cell-cat {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: var(--txt-3);
    letter-spacing: 0.08em;
}

/* Source tags */
.src-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    padding: 2px 7px;
    border-radius: 3px;
    margin-right: 4px;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.src-badge.google { background: rgba(124,58,237,0.15); color: var(--violet-lt); border: 1px solid rgba(124,58,237,0.25); }
.src-badge.gemini { background: rgba(6,182,212,0.12); color: var(--cyan-lt); border: 1px solid rgba(6,182,212,0.25); }
.src-badge.claude { background: rgba(245,158,11,0.12); color: #FCD34D; border: 1px solid rgba(245,158,11,0.25); }
.src-badge.ai_overview { background: rgba(255,255,255,0.04); color: var(--txt-3); border: 1px solid var(--border2); }

/* Inline bar */
.ibar-wrap { width: 100%; max-width: 120px; background: var(--border2); border-radius: 2px; height: 4px; }
.ibar-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, var(--violet), var(--cyan)); }

.score-cell {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--txt-1);
}
.score-sub { font-size: 0.6rem; color: var(--txt-3); font-weight: 400; }

/* ── Detail panel (Score Breakdown) ── */
.detail-panel {
    background: linear-gradient(160deg, #0E1830 0%, var(--card2) 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 0.5rem;
    position: relative;
    overflow: hidden;
}
.detail-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--violet), var(--cyan));
}
.score-rows-panel {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: 12px;
    padding: 1.2rem 1.6rem 1.4rem;
}
.dp-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--txt-1);
    margin-bottom: 2px;
}
.dp-cat {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1.2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border2);
}
.dp-score-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border2);
}
.dp-score-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.dp-score-right { display: flex; align-items: center; gap: 10px; }
.dp-bar-wrap { width: 80px; background: var(--border2); border-radius: 2px; height: 3px; }
.dp-bar-fill { height: 100%; border-radius: 2px; }
.dp-bar-fill.goog { background: linear-gradient(90deg, var(--violet), var(--violet-lt)); }
.dp-bar-fill.gem  { background: linear-gradient(90deg, var(--cyan), var(--cyan-lt)); }
.dp-bar-fill.claud { background: linear-gradient(90deg, var(--amber), #FCD34D); }
.dp-bar-fill.sent { background: linear-gradient(90deg, var(--emerald), #6EE7B7); }
.dp-bar-fill.vis  { background: linear-gradient(90deg, var(--rose), #FDA4AF); }
.dp-score-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--txt-1);
    width: 28px;
    text-align: right;
}
.dp-overall {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin: 1.2rem 0 1rem;
    padding: 1rem;
    background: rgba(124,58,237,0.08);
    border-radius: 8px;
    border: 1px solid rgba(124,58,237,0.2);
}
.dp-overall-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 600;
    background: linear-gradient(135deg, var(--txt-1), var(--violet-lt));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.dp-overall-denom {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--txt-3);
}
.dp-insight {
    font-size: 0.8rem;
    color: var(--txt-2);
    line-height: 1.7;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border2);
    font-style: italic;
}

/* ── Comparison table ── */
.cmp-panel {
    background: var(--card2);
    border: 1px solid var(--border2);
    border-radius: 14px;
    padding: 1rem 1.4rem 1.2rem;
    margin-top: 0.6rem;
}
.cmp-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 0.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border2);
    display: flex; align-items: center; gap: 6px;
}
.cmp-dot { width:5px; height:5px; border-radius:50%; background: var(--amber); display:inline-block; }
.cmp-row {
    display: grid;
    grid-template-columns: 1fr 40px 40px 40px 40px 48px;
    align-items: center;
    gap: 6px;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--border2);
}
.cmp-row:last-child { border-bottom: none; }
.cmp-row.header {
    padding-bottom: 0.4rem;
}
.cmp-brand { font-family: 'IBM Plex Sans', sans-serif; font-size: 0.72rem; font-weight: 500; color: var(--txt-1); }
.cmp-brand.active { color: var(--violet-lt); }
.cmp-brand.others { color: var(--txt-2); }
.cmp-hdr { font-family: 'IBM Plex Mono', monospace; font-size: 0.52rem; color: var(--txt-3);
           text-transform: uppercase; letter-spacing: 0.1em; text-align: center; }
.cmp-val { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; text-align: center; color: var(--txt-2); }
.cmp-val.hi { color: var(--emerald); font-weight: 500; }
.cmp-val.lo { color: var(--txt-3); }
.cmp-overall { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 600;
               text-align: right; color: var(--txt-1); }
.cmp-overall.active { color: var(--violet-lt); }

/* ── Intelligence cards ── */
.intel-card {
    background: linear-gradient(160deg, var(--card) 0%, var(--card2) 100%);
    border: 1px solid var(--border2);
    border-radius: 14px;
    padding: 1.6rem;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.intel-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    color: var(--txt-3);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.intel-dot { width: 5px; height: 5px; border-radius: 50%; display: inline-block; }
.intel-dot.blue { background: var(--violet); box-shadow: 0 0 8px var(--violet); }
.intel-dot.green { background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }
.intel-body {
    font-size: 0.85rem;
    color: var(--txt-2);
    line-height: 1.75;
}

/* ── SERP list ── */
.serp-row {
    display: flex;
    gap: 1rem;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--border2);
    align-items: flex-start;
}
.serp-pos-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--violet-lt);
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 4px;
    padding: 2px 7px;
    flex-shrink: 0;
    margin-top: 2px;
}
.serp-title { font-size: 0.85rem; font-weight: 500; color: var(--txt-1); margin-bottom: 3px; }
.serp-snip { font-size: 0.75rem; color: var(--txt-3); line-height: 1.5; margin-bottom: 4px; }
.serp-url { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: var(--txt-4); }

/* ── Progress bar (loading) ── */
.stProgress > div > div > div { background: var(--violet) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    color: var(--txt-3) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    background: var(--card) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.85rem !important;
    color: var(--txt-1) !important;
}

/* ── Success / warning ── */
.stSuccess { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 8px !important; }
.stWarning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 8px !important; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid var(--border2); margin: 2rem 0; }

/* ── Run status chips ── */
.run-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--card); border: 1px solid var(--border2);
    border-radius: 6px; padding: 5px 12px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: var(--txt-3);
    margin-bottom: 0.5rem;
}
.chip-dot-ok  { width:5px; height:5px; border-radius:50%; background:var(--emerald); flex-shrink:0; box-shadow: 0 0 6px var(--emerald); }
.chip-dot-run { width:5px; height:5px; border-radius:50%; background:var(--amber); flex-shrink:0; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Top bar ───────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%d %b %Y  %H:%M")
_q = st.session_state.get("query", "")
query_display = f'"{_q}"' if _q else "—"
st.markdown(f"""
<div class="topbar">
  <div>
    <div class="topbar-title">AEO Diagnostic</div>
    <div class="topbar-query">QUERY &nbsp;·&nbsp; <span>{query_display}</span></div>
  </div>
  <div style="text-align:right;">
    <div class="topbar-meta">{now}</div>
    <span class="topbar-pill">LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── API Keys ──────────────────────────────────────────────────────────────────
with st.expander("🔑  API Keys", expanded=False):
    st.markdown("""
    <style>
    .key-note { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#3D4D6A;
                letter-spacing:0.06em; margin-bottom:0.6rem; }
    </style>
    <div class="key-note">Keys are stored only in this session — never saved or shared.</div>
    """, unsafe_allow_html=True)
    ka1, ka2 = st.columns(2)
    with ka1:
        serp_key_input = st.text_input(
            "SerpAPI Key",
            type="password",
            placeholder="762719f3…",
            key="serp_api_key",
            help="Get your key at serpapi.com"
        )
    with ka2:
        gemini_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIzaSy…",
            key="gemini_api_key",
            help="Get your key at aistudio.google.com"
        )

SERP_KEY_DEFAULT   = serp_key_input.strip()
GEMINI_KEY_DEFAULT = gemini_key_input.strip()
GEMINI_JUDGE_KEY   = gemini_key_input.strip()

# ─── Query input ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([5, 1])
with c1:
    query = st.text_input("Search Query", placeholder='e.g. best magnesium supplement for seniors', key="query")
with c2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run = st.button("Run Analysis", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Functions ─────────────────────────────────────────────────────────────────
def fetch_serp(query: str, key: str) -> dict:
    try:
        r = requests.get("https://serpapi.com/search", params={
            "q": query, "api_key": key, "engine": "google", "num": 10, "gl": "us", "hl": "en"
        }, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_ai_overview(query: str, key: str) -> str:
    try:
        r = requests.get("https://serpapi.com/search", params={
            "q": query, "api_key": key, "engine": "google", "num": 5
        }, timeout=15)
        data = r.json()
        ao = data.get("ai_overview", {})
        if ao:
            blocks = ao.get("text_blocks", [])
            text = " ".join(b.get("snippet", "") for b in blocks if b.get("snippet"))
            if text: return text
        ab = data.get("answer_box", {})
        return ab.get("answer", "") or ab.get("snippet", "")
    except Exception:
        return ""

def query_gemini(query: str) -> str:
    try:
        client = google_genai.Client(api_key=GEMINI_KEY_DEFAULT)
        r = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"What are the best options for: {query}? List specific product/brand names with brief reasons. Be comprehensive."
        )
        return r.text
    except Exception as e:
        return f"[Gemini error: {e}]"

def extract_serp_results(data: dict) -> list:
    return [{
        "position": i + 1,
        "title": r.get("title", ""),
        "snippet": r.get("snippet", ""),
        "link": r.get("link", ""),
        "domain": r.get("displayed_link", "")
    } for i, r in enumerate(data.get("organic_results", [])[:10])]

def build_judge_prompt(query, serp_results, gemini_resp, ai_overview):
    serp_text = "\n".join(f"[#{r['position']}] {r['title']} — {r['snippet']}" for r in serp_results[:8])
    ao_block = f"\nGOOGLE AI OVERVIEW:\n{ai_overview}\n" if ai_overview else ""
    return f"""You are a senior AEO analyst. Analyze this data and return JSON only.

QUERY: "{query}"

GOOGLE RESULTS:
{serp_text}
{ao_block}
GEMINI RESPONSE:
{gemini_resp[:600]}

Find TOP 5 brands. Score 0-10 each dimension.

IMPORTANT: Respond with ONLY the JSON below, nothing else, no explanation, no markdown, no ```json fence.

{{"top5":[{{"rank":1,"brand":"Brand Name","category":"category","sources":["google","gemini"],"scores":{{"google_rank":8,"gemini_score":7,"sentiment":9,"visibility":8}},"overall":8.0,"insight":"Why this brand leads for this query."}},{{"rank":2,"brand":"Brand2","category":"category","sources":["google"],"scores":{{"google_rank":7,"gemini_score":5,"sentiment":7,"visibility":7}},"overall":6.5,"insight":"Insight for brand 2."}},{{"rank":3,"brand":"Brand3","category":"category","sources":["gemini"],"scores":{{"google_rank":5,"gemini_score":8,"sentiment":8,"visibility":6}},"overall":6.0,"insight":"Insight for brand 3."}},{{"rank":4,"brand":"Brand4","category":"category","sources":["google"],"scores":{{"google_rank":4,"gemini_score":4,"sentiment":7,"visibility":5}},"overall":5.0,"insight":"Insight for brand 4."}},{{"rank":5,"brand":"Brand5","category":"category","sources":["google"],"scores":{{"google_rank":3,"gemini_score":3,"sentiment":6,"visibility":4}},"overall":4.0,"insight":"Insight for brand 5."}}],"summary":"Expert summary of AEO landscape for this query.","opportunity":"One actionable tactic for a challenger brand."}}

Fill in real brand names from the data above. Return only that JSON, nothing else."""


def parse_json_robust(raw: str) -> dict | None:
    """Multi-strategy JSON extractor — handles markdown fences, extra text, nested braces."""
    if not raw:
        return None

    # Strategy 1: strip markdown fences then direct parse
    cleaned = re.sub(r'```(?:json)?\s*', '', raw).strip().rstrip('`').strip()
    try:
        data = json.loads(cleaned)
        if "top5" in data:
            return data
    except Exception:
        pass

    # Strategy 2: find outermost {...} that contains "top5"
    try:
        # find all { positions
        starts = [i for i, c in enumerate(raw) if c == '{']
        for start in starts:
            # find matching closing brace
            depth = 0
            for i, c in enumerate(raw[start:], start):
                if c == '{': depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = raw[start:i+1]
                        try:
                            data = json.loads(candidate)
                            if "top5" in data:
                                return data
                        except Exception:
                            break
    except Exception:
        pass

    # Strategy 3: regex extract then fix common issues
    try:
        m = re.search(r'\{[\s\S]*"top5"[\s\S]*\}', raw)
        if m:
            candidate = m.group()
            # fix trailing commas
            candidate = re.sub(r',\s*([}\]])', r'\1', candidate)
            return json.loads(candidate)
    except Exception:
        pass

    return None


def query_gemini_judge(prompt: str, retries: int = 2) -> tuple[str, dict | None]:
    """Query Gemini and attempt parse, retry on failure. Returns (raw, parsed)."""
    client = google_genai.Client(api_key=GEMINI_JUDGE_KEY)
    raw = ""
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                time.sleep(5)          # wait between retries to avoid rate limit
            r = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            raw = r.text
            parsed = parse_json_robust(raw)
            if parsed:
                return raw, parsed
            if attempt < retries:
                prompt = prompt + "\n\nPREVIOUS ATTEMPT FAILED JSON PARSING. Return ONLY the JSON object starting with { and ending with }. Absolutely no other text."
        except Exception as e:
            raw = f"[Error attempt {attempt+1}: {e}]"
            if attempt < retries:
                time.sleep(10)         # longer wait on hard errors (quota exceeded etc.)
    return raw, None

def medal(rank): return {1:"🥇",2:"🥈",3:"🥉"}.get(rank, "")
def pct(v): return int(float(v) * 10)

# ─── Main execution ────────────────────────────────────────────────────────────
if not run:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0 3rem;">
      <div style="font-family:'Playfair Display',serif; font-size:2.5rem; background:linear-gradient(135deg,#F0F2FF,#A78BFA); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:0.8rem; font-weight:600;">Enter a query to begin</div>
      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:#3D4D6A; letter-spacing:0.12em; text-transform:uppercase;">Diagnose which brands own the answer layer for any search query</div>
    </div>

    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; max-width:800px; margin:0 auto;">
      <div style="background:linear-gradient(160deg,#0C1220,#0A0F1C);border:1px solid #1A2540;border-radius:12px;padding:1.4rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#7C3AED,#06B6D4);"></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3D4D6A;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">01 · Google SERP</div>
        <div style="font-size:0.82rem;color:#3D4D6A;line-height:1.6;">Real-time organic results via SerpAPI — positions 1 through 10.</div>
      </div>
      <div style="background:linear-gradient(160deg,#0C1220,#0A0F1C);border:1px solid #1A2540;border-radius:12px;padding:1.4rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#06B6D4,#10B981);"></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3D4D6A;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">02 · Gemini AI</div>
        <div style="font-size:0.82rem;color:#3D4D6A;line-height:1.6;">What Google's own AI recommends when users ask this question.</div>
      </div>
      <div style="background:linear-gradient(160deg,#0C1220,#0A0F1C);border:1px solid #1A2540;border-radius:12px;padding:1.4rem;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#10B981,#F59E0B);"></div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#3D4D6A;text-transform:uppercase;letter-spacing:0.15em;margin-bottom:0.5rem;">03 · AI Overview</div>
        <div style="font-size:0.82rem;color:#3D4D6A;line-height:1.6;">Google's featured AI answer box — the highest-value AEO real estate.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not SERP_KEY_DEFAULT or not GEMINI_KEY_DEFAULT:
    st.warning("⚠️ Please enter your SerpAPI and Gemini API keys above before running.")
    st.stop()

if not query.strip():
    st.warning("Please enter a search query.")
    st.stop()

key = SERP_KEY_DEFAULT

# ── Fetch phase ──
col_run1, col_run2, col_run3 = st.columns(3)

with col_run1:
    with st.spinner(""):
        st.markdown('<div class="run-chip"><span class="chip-dot-run"></span>Fetching Google SERP...</div>', unsafe_allow_html=True)
        t0 = time.time()
        serp_data = fetch_serp(query, key)
        time.sleep(2)                          # wait before next SerpAPI call
        ai_overview = fetch_ai_overview(query, key)
        serp_results = extract_serp_results(serp_data)
        serp_time = round(time.time() - t0, 1)
    st.markdown(f'<div class="run-chip"><span class="chip-dot-ok"></span>Google SERP · {len(serp_results)} results · {serp_time}s</div>', unsafe_allow_html=True)

time.sleep(3)                                  # wait before hitting Gemini

with col_run2:
    with st.spinner(""):
        st.markdown('<div class="run-chip"><span class="chip-dot-run"></span>Querying Gemini 1.5...</div>', unsafe_allow_html=True)
        t0 = time.time()
        gemini_resp = query_gemini(query)
        gemini_time = round(time.time() - t0, 1)
    st.markdown(f'<div class="run-chip"><span class="chip-dot-ok"></span>Gemini AI · {gemini_time}s</div>', unsafe_allow_html=True)

time.sleep(3)                                  # wait before judge call

with col_run3:
    with st.spinner(""):
        st.markdown('<div class="run-chip"><span class="chip-dot-run"></span>Running analysis...</div>', unsafe_allow_html=True)
        t0 = time.time()
        prompt = build_judge_prompt(query, serp_results, gemini_resp, ai_overview)
        raw, data = query_gemini_judge(prompt, retries=2)
        ana_time = round(time.time() - t0, 1)
    if data:
        st.markdown(f'<div class="run-chip"><span class="chip-dot-ok"></span>Analysis complete · {ana_time}s</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="run-chip"><span class="chip-dot-run"></span>Parse failed after retries</div>', unsafe_allow_html=True)

if not data:
    st.error("Analysis failed — Gemini returned unparseable output after 3 attempts.")
    with st.expander("Debug — Raw Gemini output"):
        st.code(raw)
    st.stop()

top5        = data.get("top5", [])
summary     = data.get("summary", "")
opportunity = data.get("opportunity", "")

# ── Update topbar query display + source chips ──
total_time = round(serp_time + gemini_time + ana_time, 1)
st.markdown(f"""
<script>
  var el = document.getElementById('query-display');
  if(el) el.innerText = '"{query}"';
</script>
<div class="source-chips">
  <span class="source-chip google"><span class="chip-dot google"></span>Google SERP</span>
  <span class="source-chip gemini"><span class="chip-dot gemini"></span>Gemini 1.5</span>
  <span class="source-chip-right">Analysis · {total_time}s total</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── KPI row ──
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Brands Identified</div><div class="kpi-value">{len(top5)}</div><div class="kpi-sub">across all sources</div></div>', unsafe_allow_html=True)
with kpi2:
    ts = round(top5[0]["overall"], 1) if top5 else "—"
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Top AEO Score</div><div class="kpi-value">{ts}</div><div class="kpi-sub">out of 10.0</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">SERP Positions</div><div class="kpi-value">{len(serp_results)}</div><div class="kpi-sub">analysed</div></div>', unsafe_allow_html=True)
with kpi4:
    ao_val = "Active" if ai_overview else "None"
    ao_sub = "featured answer" if ai_overview else "no AI overview found"
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">AI Overview</div><div class="kpi-value" style="font-size:1.4rem;padding-top:0.3rem;">{ao_val}</div><div class="kpi-sub">{ao_sub}</div></div>', unsafe_allow_html=True)

# ── Rankings ──
st.markdown(f'<div class="sec-head"><span class="sec-head-label">Competitive Rankings</span><span class="sec-head-line"></span><span class="sec-head-num">TOP {len(top5)}</span></div>', unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    # Table header
    st.markdown("""
    <table class="rank-table">
      <thead>
        <tr>
          <th style="width:30px">#</th>
          <th>Brand</th>
          <th>Sources</th>
          <th>Score</th>
          <th>Visibility</th>
        </tr>
      </thead>
      <tbody>
    """, unsafe_allow_html=True)

    for b in top5:
        rank = b["rank"]
        top_cls = "top" if rank <= 3 else ""
        scores = b["scores"]
        vis_pct = pct(scores.get("visibility", 0))
        overall = b["overall"]
        src_html = "".join(
            f'<span class="src-badge {s}">{s.replace("_"," ")}</span>'
            for s in b.get("sources", [])
        )
        medal_html = f'{medal(rank)} ' if medal(rank) else ''

        st.markdown(f"""
        <tr>
          <td><span class="rank-num {top_cls}">{rank}</span></td>
          <td>
            <div class="brand-cell-name">{medal_html}{b['brand']}</div>
            <div class="brand-cell-cat">{b.get('category','')}</div>
          </td>
          <td>{src_html}</td>
          <td>
            <span class="score-cell">{overall}<span class="score-sub">/10</span></span>
          </td>
          <td>
            <div class="ibar-wrap"><div class="ibar-fill" style="width:{vis_pct}%"></div></div>
          </td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</tbody></table>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="sec-head" style="margin-top:0;"><span class="sec-head-label" style="color:#666;">Score Breakdown</span><span class="sec-head-line"></span></div>', unsafe_allow_html=True)
    chosen = st.selectbox("Brand", [b["brand"] for b in top5], label_visibility="collapsed")
    bd = next((b for b in top5 if b["brand"] == chosen), None)

    if bd:
        sc  = bd["scores"]
        src_badges = "".join(
            f'<span class="src-badge {s}">{s.replace("_"," ")}</span>'
            for s in bd.get("sources", [])
        )

        # ── Header card ──
        st.markdown(f"""
        <div class="detail-panel">
          <div class="dp-brand">{medal(bd['rank'])} {bd['brand']}</div>
          <div class="dp-cat">Rank #{bd['rank']} &nbsp;·&nbsp; {bd.get('category','')} &nbsp;·&nbsp; {src_badges}</div>
          <div class="dp-overall">
            <span class="dp-overall-num">{bd['overall']}</span>
            <span class="dp-overall-denom">/ 10 &nbsp;&nbsp; AEO Score</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Score rows ──
        BAR_COLORS = {
            "goog":  "linear-gradient(90deg,#7C3AED,#A78BFA)",
            "gem":   "linear-gradient(90deg,#06B6D4,#67E8F9)",
            "sent":  "linear-gradient(90deg,#10B981,#6EE7B7)",
            "vis":   "linear-gradient(90deg,#F43F5E,#FDA4AF)",
        }
        score_rows = [
            ("GOOGLE SERP",  sc.get("google_rank",  0), "goog"),
            ("GEMINI AI",    sc.get("gemini_score", 0), "gem"),
            ("SENTIMENT",    sc.get("sentiment",    0), "sent"),
            ("VISIBILITY",   sc.get("visibility",   0), "vis"),
        ]

        st.markdown("""
        <style>
        .sb-row { display:flex; align-items:center; justify-content:space-between;
                  padding: 0.55rem 0; border-bottom: 1px solid #111D35; }
        .sb-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                  color:#3D4D6A; text-transform:uppercase; letter-spacing:0.1em; }
        .sb-num { font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                  font-weight:500; color:#F0F2FF; min-width:36px; text-align:right; }
        .sb-bar-bg { flex:1; margin: 0 10px; height:3px; background:#111D35; border-radius:2px; }
        .sb-bar-fill { height:100%; border-radius:2px; }
        .sb-insight { font-size:0.78rem; color:#8892AA; line-height:1.7; margin-top:1rem;
                      padding-top:1rem; border-top:1px solid #111D35; font-style:italic; }
        </style>
        """, unsafe_allow_html=True)

        rows_html = ""
        for lbl, val, cls in score_rows:
            w   = int(float(val) * 10)
            col = BAR_COLORS[cls]
            rows_html += f"""
            <div class="sb-row">
              <span class="sb-lbl">{lbl}</span>
              <div class="sb-bar-bg"><div class="sb-bar-fill" style="width:{w}%;background:{col};"></div></div>
              <span class="sb-num">{int(val)}/10</span>
            </div>"""

        insight = bd.get("insight", "")
        st.markdown(
            f'<div style="background:#0A0F1C;border:1px solid #1A2540;border-radius:12px;'
            f'padding:1rem 1.4rem 1.2rem;">'
            f'{rows_html}'
            f'<div class="sb-insight">{insight}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── All Brands Comparison ──
        SCORE_KEYS = [
            ("google_rank",  "SERP"),
            ("gemini_score", "GEM"),
            ("sentiment",    "SENT"),
            ("visibility",   "VIS"),
        ]

        # Find max per column for highlighting
        col_maxes = {k: max(float(b["scores"].get(k, 0)) for b in top5) for k, _ in SCORE_KEYS}

        header_cols = "".join(f'<div class="cmp-hdr">{lbl}</div>' for _, lbl in SCORE_KEYS)
        cmp_rows_html = f"""
        <div class="cmp-row header">
          <div class="cmp-hdr" style="text-align:left">BRAND</div>
          {header_cols}
          <div class="cmp-hdr" style="text-align:right">SCORE</div>
        </div>"""

        for b in top5:
            is_active = b["brand"] == chosen
            bname_cls = "active" if is_active else "others"
            overall_cls = "active" if is_active else ""
            medal_icon = medal(b["rank"]) + " " if medal(b["rank"]) else f"#{b['rank']} "
            vals_html = ""
            for k, _ in SCORE_KEYS:
                v = float(b["scores"].get(k, 0))
                hi = v >= col_maxes[k] and col_maxes[k] > 0
                lo_cls = "hi" if hi else ("lo" if v < 4 else "")
                vals_html += f'<div class="cmp-val {lo_cls}">{int(v)}</div>'

            cmp_rows_html += f"""
            <div class="cmp-row" style="{'background:rgba(124,58,237,0.06);border-radius:6px;' if is_active else ''}">
              <div class="cmp-brand {bname_cls}">{medal_icon}{b['brand']}</div>
              {vals_html}
              <div class="cmp-overall {overall_cls}">{b['overall']}</div>
            </div>"""

        st.markdown(f"""
        <div class="cmp-panel">
          <div class="cmp-title"><span class="cmp-dot"></span>All Brands Comparison</div>
          {cmp_rows_html}
        </div>""", unsafe_allow_html=True)

# ── Strategic Intelligence ──
st.markdown('<div class="sec-head"><span class="sec-head-label">Strategic Intelligence</span><span class="sec-head-line"></span></div>', unsafe_allow_html=True)

ic1, ic2 = st.columns(2)
with ic1:
    st.markdown(f"""
    <div class="intel-card">
      <div class="intel-eyebrow"><span class="intel-dot blue"></span>Landscape Analysis</div>
      <div class="intel-body">{summary}</div>
    </div>""", unsafe_allow_html=True)
with ic2:
    st.markdown(f"""
    <div class="intel-card">
      <div class="intel-eyebrow"><span class="intel-dot green"></span>Growth Opportunity</div>
      <div class="intel-body">{opportunity}</div>
    </div>""", unsafe_allow_html=True)

# ── Raw data expanders ──
st.markdown("<hr>", unsafe_allow_html=True)

exp1, exp2, exp3 = st.columns(3)
with exp1:
    with st.expander(f"Google SERP · {len(serp_results)} results"):
        for r in serp_results[:8]:
            st.markdown(f"""
            <div class="serp-row">
              <span class="serp-pos-badge">#{r['position']}</span>
              <div>
                <div class="serp-title">{r['title']}</div>
                <div class="serp-snip">{r['snippet']}</div>
                <div class="serp-url">{r['domain']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

with exp2:
    with st.expander("Gemini AI Response"):
        st.markdown(f'<div style="font-size:0.82rem;color:#888;line-height:1.7;white-space:pre-wrap;">{gemini_resp}</div>', unsafe_allow_html=True)

with exp3:
    if ai_overview:
        with st.expander("Google AI Overview"):
            st.markdown(f'<div class="intel-card"><div class="intel-body">{ai_overview}</div></div>', unsafe_allow_html=True)
    else:
        with st.expander("Google AI Overview"):
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#AAA;">No AI Overview found for this query.</div>', unsafe_allow_html=True)

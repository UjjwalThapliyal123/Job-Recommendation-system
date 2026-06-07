import streamlit as st
import requests

# ── Config ────────────────────────────────────────────────────
API = "http://localhost:8000"

st.set_page_config(
    page_title="Jobbr",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Colour palette (duplicated as hex — CSS vars don't reach Streamlit widgets) ──
# --navy      #0A0E1A   --navy-mid  #111827   --navy-card #151C2E
# --navy-line #1E2940   --gold      #C9A84C   --gold-dim  #8A6C28
# --cream     #F0EBE0   --cream-dim #9A9080

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── 1. GLOBAL RESET ─────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
.main,
[data-testid="stMain"] {
    background: #0A0E1A !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: #F0EBE0 !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display:    none !important;
    visibility: hidden !important;
}

.main .block-container {
    padding:   0 48px 80px !important;
    max-width: 1160px !important;
}

/* ── 2. SIDEBAR ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background:   #111827 !important;
    border-right: 1px solid #1E2940 !important;
    min-width:    260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Every text node inside sidebar — catch-all */
[data-testid="stSidebar"] *:not(button):not(input):not(textarea) {
    color:       #9A9080 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* Sidebar select box background + text */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background:   #0A0E1A !important;
    border-color: #1E2940 !important;
    border-radius: 4px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {
    background: #0A0E1A !important;
    color:      #F0EBE0 !important;
}

/* Sidebar slider thumb + track */
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
    background:   #C9A84C !important;
    border-color: #C9A84C !important;
}
[data-testid="stSidebar"] [data-testid="stSliderTrackFill"] {
    background: #C9A84C !important;
}

/* Sidebar widget labels */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {
    color:          #3A4560 !important;
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      9px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    font-weight:    400 !important;
}

/* Sidebar slider value readout */
[data-testid="stSidebar"] .stSlider p,
[data-testid="stSidebar"] [data-testid="stTickBar"] span {
    color:       #9A9080 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size:   11px !important;
}

/* ── 3. MAIN WIDGET LABELS ───────────────────────────────── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stTextInput    > label p,
.stTextArea     > label p,
.stSelectbox    > label p,
.stSlider       > label p,
.stRadio        > label p,
.stNumberInput  > label p {
    color:          #3A4560 !important;
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      9px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    font-weight:    400 !important;
}

/* ── 4. TEXT INPUTS ──────────────────────────────────────── */
.stTextInput input,
.stTextArea  textarea {
    background:  #151C2E !important;
    border:      1px solid #1E2940 !important;
    border-radius: 4px !important;
    color:       #F0EBE0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size:   14px !important;
    font-weight: 300 !important;
    padding:     12px 16px !important;
    box-shadow:  none !important;
    transition:  border-color 0.15s !important;
}
.stTextInput input:focus,
.stTextArea  textarea:focus {
    border-color: #C9A84C !important;
    box-shadow:   0 0 0 1px rgba(201,168,76,0.15) !important;
    outline:      none !important;
}
.stTextInput input::placeholder,
.stTextArea  textarea::placeholder {
    color:       #9A9080 !important;
    opacity:     1 !important;
    font-weight: 300 !important;
}

/* ── 5. SELECT BOX (main area) ───────────────────────────── */
[data-baseweb="select"] > div {
    background:    #151C2E !important;
    border-color:  #1E2940 !important;
    border-radius: 4px !important;
    color:         #F0EBE0 !important;
    font-family:   'IBM Plex Sans', sans-serif !important;
    font-size:     14px !important;
    font-weight:   300 !important;
}
[data-baseweb="select"] span {
    color:       #F0EBE0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size:   14px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #C9A84C !important;
}
[data-baseweb="menu"] {
    background:    #151C2E !important;
    border:        1px solid #1E2940 !important;
    border-radius: 4px !important;
}
[data-baseweb="menu"] li {
    background:  #151C2E !important;
    color:       #9A9080 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size:   13px !important;
    font-weight: 300 !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] li[aria-selected="true"] {
    background: #1E2940 !important;
    color:      #F0EBE0 !important;
}

/* ── 6. RADIO BUTTONS ────────────────────────────────────── */
.stRadio > div {
    display:        flex !important;
    flex-direction: row !important;
    gap:            8px !important;
}
.stRadio label {
    display:       flex !important;
    align-items:   center !important;
    gap:           8px !important;
    padding:       8px 18px !important;
    border:        1px solid #1E2940 !important;
    border-radius: 4px !important;
    background:    #151C2E !important;
    cursor:        pointer !important;
    transition:    border-color 0.15s !important;
}
.stRadio label:hover {
    border-color: #8A6C28 !important;
}
/* Radio label text — explicit override */
.stRadio label p,
.stRadio label span {
    color:          #9A9080 !important;
    font-family:    'IBM Plex Sans', sans-serif !important;
    font-size:      13px !important;
    font-weight:    300 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}
/* Radio circle */
.stRadio [data-baseweb="radio"] div {
    border-color: #1E2940 !important;
    background:   transparent !important;
}
/* Selected radio fills gold */
.stRadio [aria-checked="true"] [data-baseweb="radio"] div {
    background:   #C9A84C !important;
    border-color: #C9A84C !important;
}

/* ── 7. SLIDERS (main area) ──────────────────────────────── */
.stSlider [role="slider"] {
    background:   #C9A84C !important;
    border-color: #C9A84C !important;
}
.stSlider [data-testid="stSliderTrackFill"] {
    background: #C9A84C !important;
}
.stSlider p {
    color:       #9A9080 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size:   11px !important;
}

/* ── 8. BUTTONS ──────────────────────────────────────────── */
.stButton button {
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      10px !important;
    font-weight:    500 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    border-radius:  4px !important;
    padding:        12px 32px !important;
    cursor:         pointer !important;
    transition:     all 0.15s !important;
}
.stButton button[kind="primary"],
.stButton button[data-testid="baseButton-primary"] {
    background:   #C9A84C !important;
    color:        #0A0E1A !important;
    border:       1px solid #C9A84C !important;
    font-weight:  600 !important;
}
.stButton button[kind="primary"]:hover,
.stButton button[data-testid="baseButton-primary"]:hover {
    background:   #D4B468 !important;
    border-color: #D4B468 !important;
}
.stButton button[kind="secondary"],
.stButton button[data-testid="baseButton-secondary"] {
    background:   transparent !important;
    color:        #C9A84C !important;
    border:       1px solid #8A6C28 !important;
}

/* ── 9. TABS ─────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #1E2940 !important;
    gap:           0 !important;
    background:    transparent !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      10px !important;
    font-weight:    400 !important;
    color:          #3A4560 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    padding:        12px 24px !important;
    border:         none !important;
    border-bottom:  1px solid transparent !important;
    background:     transparent !important;
    margin-bottom:  -1px !important;
}
/* Tab label text */
[data-testid="stTabs"] [role="tab"] p,
[data-testid="stTabs"] [role="tab"] span {
    color:          inherit !important;
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      10px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color:        #C9A84C !important;
    border-bottom: 1px solid #C9A84C !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
[data-testid="stTabs"] [role="tab"][aria-selected="true"] span {
    color: #C9A84C !important;
}

/* ── 10. EXPANDER ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background:    #111827 !important;
    border:        1px solid #1E2940 !important;
    border-radius: 4px !important;
    box-shadow:    none !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color:          #3A4560 !important;
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      9px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    font-weight:    400 !important;
}

/* ── 11. ALERTS / WARNINGS ───────────────────────────────── */
[data-testid="stAlert"] {
    background:    #111827 !important;
    border-radius: 4px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color:       #9A9080 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size:   13px !important;
    font-weight: 300 !important;
}

/* ── 12. SPINNER ─────────────────────────────────────────── */
[data-testid="stSpinner"] p {
    color:          #8A6C28 !important;
    font-family:    'IBM Plex Mono', monospace !important;
    font-size:      11px !important;
    letter-spacing: 0.08em !important;
}

/* ── 13. CAPTION ─────────────────────────────────────────── */
.stCaption, .stCaption p {
    color:       #3A4560 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size:   12px !important;
    font-weight: 300 !important;
}

/* ── 14. COLUMN PADDING ──────────────────────────────────── */
[data-testid="column"] { padding: 0 8px !important; }
[data-testid="column"]:first-child { padding-left:  0 !important; }
[data-testid="column"]:last-child  { padding-right: 0 !important; }

/* ── 15. CUSTOM HTML COMPONENTS ──────────────────────────── */

/* Topbar */
.topbar {
    display:         flex;
    align-items:     center;
    justify-content: space-between;
    padding:         24px 0 22px;
    border-bottom:   1px solid #1E2940;
    margin-bottom:   48px;
}
.topbar-logo {
    font-family:    'Playfair Display', serif;
    font-size:      26px;
    font-weight:    600;
    color:          #F0EBE0;
    letter-spacing: -0.5px;
}
.topbar-logo span { color: #C9A84C; }
.topbar-meta {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      11px;
    color:          #9A9080;
    letter-spacing: 0.08em;
}
.topbar-dot {
    display:        inline-block;
    width:          6px;
    height:         6px;
    border-radius:  50%;
    background:     #C9A84C;
    margin-right:   8px;
    vertical-align: middle;
    animation:      blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* Hero */
.hero {
    margin-bottom:  52px;
    padding-bottom: 48px;
    border-bottom:  1px solid #1E2940;
}
.hero-eyebrow {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color:          #C9A84C;
    margin-bottom:  16px;
}
.hero-title {
    font-family:    'Playfair Display', serif;
    font-size:      52px;
    font-weight:    400;
    color:          #F0EBE0;
    letter-spacing: -1.5px;
    line-height:    1.05;
    max-width:      640px;
}
.hero-title em { font-style: italic; color: #C9A84C; }
.hero-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size:   15px;
    color:       #9A9080;
    margin-top:  16px;
    font-weight: 300;
    line-height: 1.7;
    max-width:   460px;
}

/* Sidebar brand block */
.sb-header {
    padding:       32px 24px 26px;
    border-bottom: 1px solid #1E2940;
    margin-bottom: 24px;
}
.sb-wordmark {
    font-family:    'Playfair Display', serif;
    font-size:      22px;
    font-weight:    600;
    color:          #F0EBE0;
    letter-spacing: -0.3px;
}
.sb-wordmark span { color: #C9A84C; }
.sb-tag {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color:          #8A6C28;
    margin-top:     6px;
}
.sb-stat {
    margin-top:  16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size:   11px;
    color:       #3A4560;
}
.sb-stat strong {
    color:       #9A9080;
    font-weight: 400;
}
.sb-label {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color:          #3A4560;
    padding:        0 24px;
    margin-bottom:  8px;
    display:        block;
}
.sb-divider {
    border:     none;
    border-top: 1px solid #1E2940;
    margin:     20px 0;
}

/* Section label */
.section-label {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color:          #3A4560;
    margin-bottom:  10px;
    display:        block;
}

/* Weight warning */
.weight-warn {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    color:          #C4882A;
    letter-spacing: 0.06em;
    margin-top:     8px;
}

/* Results header */
.results-header {
    display:         flex;
    align-items:     baseline;
    justify-content: space-between;
    padding:         20px 0 16px;
    border-bottom:   1px solid #1E2940;
    margin-bottom:   22px;
}
.results-left  { display: flex; align-items: baseline; gap: 12px; }
.results-count {
    font-family:    'Playfair Display', serif;
    font-size:      32px;
    font-weight:    400;
    color:          #F0EBE0;
    letter-spacing: -0.5px;
}
.results-label {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color:          #3A4560;
}
.results-tag {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color:          #8A6C28;
    border:         1px solid #8A6C28;
    border-radius:  2px;
    padding:        2px 8px;
}

/* Job card */
.job-card {
    background:    #151C2E;
    border:        1px solid #1E2940;
    border-radius: 6px;
    padding:       26px 30px;
    margin-bottom: 10px;
    position:      relative;
    overflow:      hidden;
    transition:    border-color 0.2s, box-shadow 0.2s;
}
.job-card::before {
    content:    '';
    position:   absolute;
    left:0; top:0; bottom:0;
    width:      2px;
    background: transparent;
    transition: background 0.2s;
}
.job-card:hover { border-color: #2A3550; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
.job-card:hover::before { background: #C9A84C; }

.card-num {
    position:       absolute;
    top:26px; right:30px;
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    color:          #1E2940;
    letter-spacing: 0.08em;
}
.score-badge {
    display:        inline-flex;
    align-items:    center;
    gap:            6px;
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    font-weight:    500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding:        4px 10px;
    border-radius:  2px;
    margin-bottom:  12px;
}
.score-dot {
    width:         4px;
    height:        4px;
    border-radius: 50%;
    background:    currentColor;
    display:       inline-block;
    flex-shrink:   0;
}
.score-high   { background:#0D2318; color:#4CAF82; border:1px solid #1A4030; }
.score-medium { background:#211408; color:#C4882A; border:1px solid #3A2808; }
.score-low    { background:#210808; color:#C44040; border:1px solid #3A0808; }

.card-title {
    font-family:    'Playfair Display', serif;
    font-size:      21px;
    font-weight:    400;
    color:          #F0EBE0;
    letter-spacing: -0.3px;
    line-height:    1.2;
    margin-bottom:  5px;
}
.card-company {
    font-family:   'IBM Plex Sans', sans-serif;
    font-size:     13px;
    color:         #9A9080;
    font-weight:   300;
    margin-bottom: 18px;
}
.card-company strong { color: #C0BBAF; font-weight: 500; }
.card-company .sep  { color: #2A3550; margin: 0 8px; }

.card-meta {
    display:               grid;
    grid-template-columns: repeat(4, 1fr);
    border:                1px solid #1E2940;
    border-radius:         4px;
    overflow:              hidden;
    margin-bottom:         18px;
}
.card-meta-cell {
    padding:      10px 14px;
    border-right: 1px solid #1E2940;
}
.card-meta-cell:last-child { border-right: none; }
.meta-label {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      8px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color:          #2A3550;
    margin-bottom:  4px;
}
.meta-value {
    font-family:   'IBM Plex Sans', sans-serif;
    font-size:     12px;
    color:         #9A9080;
    font-weight:   400;
    white-space:   nowrap;
    overflow:      hidden;
    text-overflow: ellipsis;
}

.card-skills {
    display:       flex;
    flex-wrap:     wrap;
    gap:           5px;
    margin-bottom: 16px;
}
.skill-tag {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    color:          #4A5570;
    background:     #0A0E1A;
    border:         1px solid #1E2940;
    border-radius:  2px;
    padding:        3px 8px;
    letter-spacing: 0.03em;
    white-space:    nowrap;
}

.card-footer {
    display:         flex;
    align-items:     center;
    justify-content: space-between;
    padding-top:     14px;
    border-top:      1px solid #1E2940;
}
.card-id {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    color:          #2A3550;
    letter-spacing: 0.08em;
}
.card-link {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      9px;
    font-weight:    500;
    color:          #8A6C28;
    text-decoration: none;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border-bottom:  1px solid #8A6C28;
    padding-bottom: 1px;
    transition:     color 0.15s, border-color 0.15s;
}
.card-link:hover { color: #C9A84C; border-bottom-color: #C9A84C; }

/* Source banner */
.source-banner {
    background:   #111827;
    border:       1px solid #1E2940;
    border-left:  2px solid #8A6C28;
    border-radius: 4px;
    padding:      12px 18px;
    margin-bottom: 22px;
    font-family:  'IBM Plex Sans', sans-serif;
    font-size:    12px;
    font-weight:  300;
    color:        #9A9080;
    line-height:  1.6;
}
.source-banner strong { color: #F0EBE0; font-weight: 500; }

/* Empty state */
.empty-state {
    text-align:    center;
    padding:       72px 40px;
    border:        1px solid #1E2940;
    border-radius: 6px;
    background:    #111827;
}
.empty-title {
    font-family: 'Playfair Display', serif;
    font-size:   26px;
    font-weight: 400;
    font-style:  italic;
    color:       #2A3550;
    margin-bottom: 10px;
}
.empty-sub {
    font-family:    'IBM Plex Mono', monospace;
    font-size:      10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color:          #1E2940;
}
</style>
""", unsafe_allow_html=True)


# ── Load filters ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_filters():
    try:
        r = requests.get(f"{API}/filters", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {
        "experience_levels": [],
        "work_types":        [],
        "salary_range":      {"min": 0, "max": 300000},
        "total_jobs":        0,
    }

filters = load_filters()
sal_min = int(filters.get("salary_range", {}).get("min", 0))
sal_max = int(filters.get("salary_range", {}).get("max", 300000))
total   = filters.get("total_jobs", 0)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-header">
        <div class="sb-wordmark">Jobb<span>r</span></div>
        <div class="sb-tag">Intelligent matching</div>
        <div class="sb-stat"><strong>{total:,}</strong> positions indexed</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sb-label">Experience level</span>',
                unsafe_allow_html=True)
    exp_options  = ["Any level"] + filters.get("experience_levels", [])
    exp_selected = st.selectbox(
        "Experience level", exp_options, label_visibility="collapsed"
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    st.markdown('<span class="sb-label">Work arrangement</span>',
                unsafe_allow_html=True)
    wt_options  = ["Any type"] + filters.get("work_types", [])
    wt_selected = st.selectbox(
        "Work type", wt_options, label_visibility="collapsed"
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    st.markdown('<span class="sb-label">Salary range (USD)</span>',
                unsafe_allow_html=True)
    salary = st.slider(
        "Salary",
        min_value=sal_min, max_value=sal_max,
        value=(sal_min, sal_max),
        step=5000, format="$%d",
        label_visibility="collapsed"
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    st.markdown('<span class="sb-label">Results per query</span>',
                unsafe_allow_html=True)
    top_n = st.slider(
        "Results", min_value=5, max_value=50,
        value=10, label_visibility="collapsed"
    )


# ── Shared helpers ────────────────────────────────────────────
def score_class(s):
    if s >= 60: return "score-high"
    if s >= 35: return "score-medium"
    return "score-low"

def apply_filters(jobs):
    if wt_selected != "Any type":
        jobs = [j for j in jobs if j.get("work_type", "") == wt_selected]
    return jobs

def render_jobs(jobs, source_job=None, label=""):
    if not jobs:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-title">No positions found</div>
            <div class="empty-sub">Broaden your criteria or adjust filters</div>
        </div>""", unsafe_allow_html=True)
        return

    if source_job:
        st.markdown(f"""
        <div class="source-banner">
            Positions similar to
            <strong>{source_job.get('title', '')}</strong>
            &mdash; {source_job.get('company_name', '')}
            &middot; {source_job.get('location', '')}
        </div>""", unsafe_allow_html=True)

    tag_html = f'<span class="results-tag">{label}</span>' if label else ""
    st.markdown(f"""
    <div class="results-header">
        <div class="results-left">
            <span class="results-count">{len(jobs)}</span>
            <span class="results-label">positions found</span>
        </div>
        {tag_html}
    </div>""", unsafe_allow_html=True)

    for i, job in enumerate(jobs):
        score   = job.get("score", 0)
        title   = job.get("title", "")            or "Untitled"
        company = job.get("company_name", "")     or "Unknown"
        loc     = job.get("location", "")         or "Not specified"
        exp     = job.get("experience_level", "") or "Not specified"
        wtype   = job.get("work_type", "")        or "Not specified"
        sal     = job.get("salary", "")           or "Not disclosed"
        job_id  = job.get("job_id", "")
        skills  = job.get("skills", "")
        url     = job.get("url", "")

        tags = "".join(
            f'<span class="skill-tag">{s.strip()}</span>'
            for s in skills.split(",")[:12] if s.strip()
        )
        link = (
            f'<a class="card-link" href="{url}" target="_blank">'
            f'View posting &rarr;</a>'
        ) if url else ""

        st.markdown(f"""
        <div class="job-card">
            <span class="card-num">{i+1:02d} / {len(jobs):02d}</span>
            <div class="score-badge {score_class(score)}">
                <span class="score-dot"></span>{score}%&nbsp;match
            </div>
            <div class="card-title">{title}</div>
            <div class="card-company">
                <strong>{company}</strong>
                <span class="sep">/</span>{loc}
            </div>
            <div class="card-meta">
                <div class="card-meta-cell">
                    <div class="meta-label">Experience</div>
                    <div class="meta-value">{exp}</div>
                </div>
                <div class="card-meta-cell">
                    <div class="meta-label">Work type</div>
                    <div class="meta-value">{wtype}</div>
                </div>
                <div class="card-meta-cell">
                    <div class="meta-label">Salary</div>
                    <div class="meta-value">{sal}</div>
                </div>
                <div class="card-meta-cell">
                    <div class="meta-label">Location</div>
                    <div class="meta-value">{loc}</div>
                </div>
            </div>
            <div class="card-skills">{tags}</div>
            <div class="card-footer">
                <span class="card-id">ID &middot; {job_id}</span>
                {link}
            </div>
        </div>""", unsafe_allow_html=True)

def api_error(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        st.error("API offline — run:  uvicorn api:app --reload --port 8000")
    elif isinstance(e, requests.exceptions.HTTPError):
        code = e.response.status_code if e.response else 0
        st.error("No match found." if code == 404 else f"API error {code}.")
    else:
        st.error(f"Unexpected error: {e}")


# ── Topbar + Hero ─────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">Jobb<span>r</span></div>
    <div class="topbar-meta">
        <span class="topbar-dot"></span>
        {total:,} positions &nbsp;&middot;&nbsp; Live
    </div>
</div>
<div class="hero">
    <div class="hero-eyebrow">Intelligent Job Matching</div>
    <div class="hero-title">Find your <em>next</em><br>position</div>
    <div class="hero-sub">
        Match by skills, search in plain language, or discover
        roles similar to ones you already know.
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Skill Match", "Search", "Similar Roles"])


# ── TAB 1 — Skill Match ───────────────────────────────────────
with tab1:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        skills = st.text_area(
            "Your skills",
            placeholder="python, machine learning, sql, data analysis, leadership ...",
            height=108
        )
    with col2:
        location = st.text_input("Location", placeholder="New York, NY")
        max_dist = st.slider("Search radius (km)", 10, 1000, 100, 10)

    with st.expander("Weight configuration"):
        st.caption(
            "Adjust how much each factor contributes to the final score. "
            "Values should sum to 1.0."
        )
        wc1, wc2, wc3, wc4, wc5 = st.columns(5)
        w_skill = wc1.slider("Skills",     0.0, 1.0, 0.40, 0.05, key="w1")
        w_sem   = wc2.slider("Semantic",   0.0, 1.0, 0.25, 0.05, key="w2")
        w_loc   = wc3.slider("Location",   0.0, 1.0, 0.15, 0.05, key="w3")
        w_exp   = wc4.slider("Experience", 0.0, 1.0, 0.10, 0.05, key="w4")
        w_sal   = wc5.slider("Salary",     0.0, 1.0, 0.10, 0.05, key="w5")
        total_w = round(w_skill + w_sem + w_loc + w_exp + w_sal, 2)
        if abs(total_w - 1.0) > 0.01:
            st.markdown(
                f'<div class="weight-warn">Weights sum to {total_w}'
                f' — recommended total is 1.0</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Match positions", type="primary", key="btn1"):
        if not skills.strip():
            st.warning("Enter at least one skill to continue.")
        else:
            with st.spinner("Matching positions..."):
                try:
                    resp = requests.post(f"{API}/recommend", timeout=30, json={
                        "skills":           skills,
                        "location":         location or None,
                        "experience_level": None if exp_selected == "Any level"
                                            else exp_selected,
                        "salary_min":  salary[0] if salary[0] > sal_min else None,
                        "salary_max":  salary[1] if salary[1] < sal_max else None,
                        "max_distance_km":  max_dist,
                        "top_n":            top_n,
                        "weight_skill":     w_skill,
                        "weight_semantic":  w_sem,
                        "weight_location":  w_loc,
                        "weight_exp":       w_exp,
                        "weight_salary":    w_sal,
                    })
                    resp.raise_for_status()
                    render_jobs(
                        apply_filters(resp.json().get("results", [])),
                        label="Skill match"
                    )
                except Exception as e:
                    api_error(e)


# ── TAB 2 — Search ────────────────────────────────────────────
with tab2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    query = st.text_input(
        "Search query",
        placeholder="senior data engineer with Spark experience in healthcare ..."
    )
    sc1, sc2 = st.columns([2, 1], gap="large")
    with sc1:
        search_loc = st.text_input(
            "Near location", placeholder="Chicago, IL", key="sloc"
        )
    with sc2:
        search_dist = st.slider("Radius (km)", 10, 1000, 100, 10, key="sdist")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Search positions", type="primary", key="btn2"):
        if not query.strip():
            st.warning("Enter a search query.")
        else:
            with st.spinner("Searching..."):
                try:
                    resp = requests.post(f"{API}/search", timeout=30, json={
                        "query":           query,
                        "location":        search_loc or None,
                        "max_distance_km": search_dist,
                        "top_n":           top_n,
                    })
                    resp.raise_for_status()
                    render_jobs(
                        apply_filters(resp.json().get("results", [])),
                        label="Semantic search"
                    )
                except Exception as e:
                    api_error(e)


# ── TAB 3 — Similar Roles ─────────────────────────────────────
with tab3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    st.markdown(
        '<span class="section-label">Find similar roles by</span>',
        unsafe_allow_html=True
    )
    mode = st.radio(
        "Find similar roles by",
        ["Job title", "Job ID"],
        horizontal=True,
        label_visibility="collapsed"
    )
    if mode == "Job title":
        sim_input   = st.text_input("Job title", placeholder="Data Engineer", key="simt")
        payload_key = "job_title"
    else:
        sim_input   = st.text_input("Job ID", placeholder="9217162774458", key="simid")
        payload_key = "job_id"

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Find similar positions", type="primary", key="btn3"):
        if not sim_input.strip():
            st.warning("Enter a job title or ID.")
        else:
            with st.spinner("Finding similar positions..."):
                try:
                    resp = requests.post(f"{API}/similar", timeout=30, json={
                        payload_key: sim_input.strip(),
                        "top_n":     top_n,
                    })
                    resp.raise_for_status()
                    data = resp.json()
                    render_jobs(
                        apply_filters(data.get("results", [])),
                        source_job=data.get("source_job"),
                        label="Similar roles"
                    )
                except Exception as e:
                    api_error(e)
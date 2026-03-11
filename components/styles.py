import streamlit as st

ACCENT = "#E50914"
ACCENT_DARK = "#B20710"
BG_DARK = "#0E1117"
BG_CARD = "#1A1C23"
TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#A0A0A0"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"


def inject_css():
    st.markdown(
        """
        <style>
        /* ── Global ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background: #0E1117;
        }

        /* All text white; red on click */
        [data-testid="stAppViewContainer"] *,
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stAppViewContainer"] *:active,
        section[data-testid="stSidebar"] *:active {
            color: #E50914 !important;
        }

        /* ── Sidebar (hamburger when collapsed) ─────────────── */
        section[data-testid="stSidebar"] > div {
            background: linear-gradient(180deg, #0D1117 0%, #161B22 100%);
            border-right: 1px solid #21262D;
            padding-top: 1.5rem;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
            background: transparent;
        }
        /* Sidebar radio buttons → pill style */
        section[data-testid="stSidebar"] [role="radiogroup"] label {
            background: #21262D;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 0.55rem 1rem;
            margin-bottom: 0.35rem;
            transition: all 0.2s;
            cursor: pointer;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            border-color: #E50914;
            background: #1A1E26;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
            border-color: #E50914;
            background: rgba(229,9,20,0.12);
        }

        /* ── Header banner ──────────────────────────────────── */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #FAFAFA;
            text-align: center;
            padding: 1rem 1rem;
            background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #0D1117 100%);
            border-bottom: 3px solid #E50914;
            border-radius: 10px;
            margin-bottom: 1.4rem;
            letter-spacing: 0.3px;
        }

        /* ── KPI cards ──────────────────────────────────────── */
        .kpi-card {
            background: linear-gradient(145deg, #161B22, #1A1F27);
            border: 1px solid #30363D;
            border-radius: 12px;
            padding: 1.1rem 1rem;
            text-align: center;
            transition: all 0.25s ease;
        }
        .kpi-card:hover {
            border-color: #E50914;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229,9,20,0.12);
        }
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #FAFAFA;
            white-space: nowrap;
        }
        .kpi-label {
            font-size: 0.7rem;
            color: #8B949E;
            text-transform: uppercase;
            letter-spacing: 1.4px;
            margin-top: 0.35rem;
        }
        .kpi-icon {
            font-size: 1.3rem;
            margin-bottom: 0.2rem;
        }

        /* ── Tabs ────────────────────────────────────────────── */
        [data-testid="stTabs"] button {
            font-weight: 500 !important;
            letter-spacing: 0.3px;
            padding: 0.5rem 1.2rem !important;
            border-radius: 8px 8px 0 0 !important;
            transition: all 0.2s;
        }
        [data-testid="stTabs"] button:hover {
            background: rgba(229,9,20,0.08) !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom: 3px solid #E50914 !important;
            background: rgba(229,9,20,0.06) !important;
        }

        /* ── Buttons ─────────────────────────────────────────── */
        .stButton > button {
            background: #21262D !important;
            color: #FAFAFA !important;
            border: 1px solid #30363D !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.45rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            border-color: #E50914 !important;
            background: rgba(229,9,20,0.10) !important;
        }
        .stButton > button:active {
            background: rgba(229,9,20,0.18) !important;
        }

        /* ── Section titles ─────────────────────────────────── */
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FAFAFA;
            border-left: 3px solid #E50914;
            padding-left: 0.7rem;
            margin: 1.4rem 0 0.8rem;
        }

        /* ── Dividers ───────────────────────────────────────── */
        hr {
            border: none;
            border-top: 1px solid #21262D;
            margin: 1rem 0;
        }

        /* ── Data frames ────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            border: 1px solid #21262D;
            border-radius: 10px;
            overflow: hidden;
        }

        /* ── Movie browse cards ─────────────────────────────── */
        .movie-card {
            background: #161B22;
            border: 1px solid #30363D;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
            height: 580px;
            display: flex;
            flex-direction: column;
        }
        .movie-card:hover {
            transform: translateY(-4px);
            border-color: #E50914;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        }
        .movie-card img {
            width: 100%;
            height: 310px;
            object-fit: cover;
        }
        .movie-card-body {
            padding: 0.9rem 1rem;
            flex: 1;
            overflow-y: auto;
        }
        .movie-card-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: #FAFAFA;
            margin: 0 0 4px;
        }
        .movie-card-genre {
            font-size: 0.7rem;
            color: #E50914;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .movie-card-overview {
            font-size: 0.78rem;
            color: #8B949E;
            line-height: 1.55;
        }
        .badge {
            display: inline-block;
            background: #21262D;
            border: 1px solid #30363D;
            border-radius: 20px;
            padding: 2px 10px;
            font-size: 0.7rem;
            color: #E50914;
            margin-right: 4px;
            margin-top: 4px;
        }
        .star { color: #E50914; }

        /* ── Footer ─────────────────────────────────────────── */
        .dash-footer {
            text-align: center;
            color: #484F58;
            font-size: 0.78rem;
            padding: 1.2rem 0 0.5rem;
            border-top: 1px solid #21262D;
            margin-top: 0.5rem;
        }

        /* ── Scrollbar ──────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0E1117; }
        ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #484F58; }
        </style>
        """,
        unsafe_allow_html=True,
    )

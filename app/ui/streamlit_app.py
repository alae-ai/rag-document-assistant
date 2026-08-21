import streamlit as st

from app.documents.document_manager import DocumentManager
from app.rag.rag_pipeline import RAGPipeline

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOGO_PATH = BASE_DIR / "assets" / "virtuoso-logo.png"

def apply_custom_style():
    st.markdown(
        """
        <style>

        :root {
            --bg: #f5f7fb;
            --panel: #ffffff;
            --panel-alt: #f8fafc;
            --text: #111827;
            --muted: #4b5563;
            --border: #dfe5ee;

            --primary: #1d4ed8;
            --primary-hover: #1e3a8a;
            --primary-soft: #eaf1ff;

            --success: #166534;
            --warning: #92400e;
        }


        /* =========================
           GLOBAL
           ========================= */

        html, body, .stApp {
            font-size: 18px;
        }

        body {
            font-size: 18px;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 100%;
            padding-left: 3rem;
            padding-right: 3rem;
        }


        /* =========================
           TYPOGRAPHY
           ========================= */

        p, li, label {
            font-size: 18px !important;
            color: var(--text);
        }

        h1 {
            font-size: 32px !important;
        }

        h2 {
            font-size: 26px !important;
        }

        h3 {
            font-size: 21px !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            letter-spacing: -0.02em;
            font-weight: 600 !important;
        }

        [data-testid="stMarkdownContainer"] p {
            font-size: 18px !important;
            line-height: 1.6;
        }


        /* =========================
           SIDEBAR
           ========================= */

        [data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid var(--border);
        }


        /* =========================
           INPUTS
           ========================= */

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stFileUploader > div {
            background: #ffffff;
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            min-height: 42px;
        }

        .stTextInput input,
        .stTextArea textarea {
            font-size: 18px !important;
        }


        /* BLUE FOCUS — no red */

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stNumberInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 1px var(--primary) !important;
            outline: none !important;
        }


        /* =========================
           BUTTONS
           ========================= */

        div.stButton > button {
            background: #ffffff;
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-weight: 600;
            padding: 0.55rem 1rem;
            min-height: 38px;
            box-shadow: none;
            transition: background-color 0.15s ease,
                        border-color 0.15s ease,
                        color 0.15s ease;
        }

        /* Normal hover = blue */

        div.stButton > button:hover {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }

        div.stButton > button:focus,
        div.stButton > button:focus-visible {
            box-shadow: 0 0 0 1px var(--primary) !important;
            outline: none !important;
        }


        /* =========================
           CHECKBOX
           ========================= */

        /* Remove Streamlit's default red accent */

        [data-testid="stCheckbox"] input {
            accent-color: var(--primary) !important;
        }

        [data-testid="stCheckbox"] label {
            color: var(--text) !important;
        }


        /* =========================
           METRICS
           ========================= */

        [data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            box-shadow: none;
        }


        /* =========================
           EXPANDERS
           ========================= */

        .streamlit-expanderHeader {
            background: var(--panel-alt);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            font-weight: 600;
        }

        .streamlit-expanderContent {
            background: #ffffff;
            border: 1px solid var(--border);
            border-top: none;
            border-radius: 0 0 6px 6px;
        }


        /* =========================
           FILE UPLOADER
           ========================= */

        [data-testid="stFileUploaderDropzone"] {
            background: var(--panel-alt);
            border: 1px dashed var(--border);
            border-radius: 6px;
        }


        /* =========================
           ALERTS
           ========================= */

        .stAlert {
            border-radius: 6px;
            border: 1px solid var(--border);
            background: #ffffff;
        }


        /* =========================
           TABS
           ========================= */

        .stTabs [role="tablist"] {
            gap: 0.5rem;
        }

        .stTabs [role="tab"] {
            border: 1px solid var(--border);
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            background: var(--panel-alt);
            color: var(--muted);
            padding: 0.5rem 0.9rem;
        }

        .stTabs [aria-selected="true"] {
            background: #ffffff;
            color: var(--text);
            border-color: var(--border);
        }


        /* =========================
           TABLES
           ========================= */

        .stDataFrame,
        .stTable {
            border: 1px solid var(--border);
            border-radius: 6px;
        }


        /* =========================
           SPACING
           ========================= */

        .element-container {
            margin-bottom: 0.35rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_pipeline():
    return RAGPipeline()


@st.cache_resource
def load_document_manager():
    return DocumentManager()


st.set_page_config(
    page_title="Virtuoso - Votre Assistant documentaire",
    page_icon="🤖",
    layout="wide",
)

apply_custom_style()

if "pipeline" not in st.session_state:
    st.session_state.pipeline = load_pipeline()

if "document_manager" not in st.session_state:
    st.session_state.document_manager = load_document_manager()

from app.ui.pages.assistant import assistant_page
from app.ui.pages.dashboard import dashboard_page
from app.ui.pages.documents import documents_page

col1, col2 = st.columns([1, 4])

with col1:
    st.image(str(LOGO_PATH), width=60)

with col2:
    st.title("Virtuoso")

pg = st.navigation(
    [
        st.Page(dashboard_page, title="Dashboard"),
        st.Page(documents_page, title="Gestion des documents", icon="📁"),
        st.Page(assistant_page, title="Assistant", icon="🤖"),
    ]
)

pg.run()
    
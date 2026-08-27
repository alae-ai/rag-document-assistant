import base64
from pathlib import Path

import streamlit as st

from app.documents.document_manager import DocumentManager
from app.rag.rag_pipeline import RAGPipeline

from app.mcp.google_drive_client import GoogleDriveMCPClient


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
LOGO_PATH = BASE_DIR / "assets" / "virtuoso-logo.png"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Virtuoso - Votre Assistant documentaire",
    page_icon=str(LOGO_PATH),
    layout="wide",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

def apply_custom_style():
    st.markdown(
        """
        <style>

        /* =====================================================
           DESIGN TOKENS
           ===================================================== */

        :root {
            --bg: #f5f7fb;
            --surface: #ffffff;
            --surface-muted: #f8fafc;

            --text: #111827;
            --text-muted: #6b7280;

            --border: #e2e8f0;

            --primary: #1d4ed8;
            --primary-hover: #1e40af;
            --primary-soft: #eff6ff;

            --success: #166534;
            --warning: #92400e;

            --radius-sm: 6px;
            --radius-md: 8px;

            --header-height: 64px;
            --content-max-width: 1400px;
        }


        /* =====================================================
           GLOBAL
           ===================================================== */

        html {
            scroll-behavior: smooth;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        /* Keep content below the fixed header */

        .block-container {
            width: 100%;
            max-width: var(--content-max-width);

            margin: 0 auto;

            padding-top: calc(var(--header-height) + 2rem);
            padding-bottom: 3rem;

            padding-left: clamp(1rem, 3vw, 3rem);
            padding-right: clamp(1rem, 3vw, 3rem);
        }


        /* =====================================================
           TYPOGRAPHY
           ===================================================== */

        body {
            color: var(--text);
        }

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"] {
            font-size: 17px !important;
        }

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            color: var(--text) !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: clamp(2rem, 2vw, 2.5rem) !important;
        }

        h2 {
            font-size: clamp(1.5rem, 1.8vw, 1.9rem) !important;
        }

        h3 {
            font-size: 1.35rem !important;
        }

        p,
        li,
        label,
        .stMarkdown,
        .stTextInput label,
        .stRadio label,
        .stCheckbox label,
        .stSelectbox label,
        .stFileUploader label {
            color: var(--text);
            font-size: 1.03rem !important;
        }

        [data-testid="stMarkdownContainer"] p {
            line-height: 1.7;
            font-size: 1.04rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }


        /* =====================================================
           VIRTUOSO HEADER
           ===================================================== */

        .virtuoso-header {
            position: fixed;

            top: 0;
            left: 0;
            right: 0;

            height: var(--header-height);

            display: flex;
            align-items: center;

            padding: 0 clamp(1rem, 3vw, 3rem);

            background: rgba(255, 255, 255, 0.96);

            border-bottom: 1px solid var(--border);

            z-index: 999999;

            box-sizing: border-box;

            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        .virtuoso-header-inner {
            width: 100%;
            max-width: var(--content-max-width);

            margin: 0 auto;

            display: flex;
            align-items: center;
        }

        .virtuoso-logo {
            width: 40px;
            height: 40px;

            object-fit: contain;

            flex-shrink: 0;
        }

        .virtuoso-name {
            margin-left: 12px;

            font-size: 1.25rem;
            font-weight: 600;

            color: var(--text);

            white-space: nowrap;
        }


        /* =====================================================
           SIDEBAR
           ===================================================== */

        [data-testid="stSidebar"] {
            background: var(--surface-muted);
            border-right: 1px solid var(--border);
        }


        /* =====================================================
           INPUTS
           ===================================================== */

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
            background: var(--surface) !important;
            color: var(--text) !important;

            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus,
        .stNumberInput input:focus {
            border-color: var(--primary) !important;

            box-shadow:
                0 0 0 1px var(--primary) !important;

            outline: none !important;
        }

        .stTextInput input,
        .stTextArea textarea {
            font-size: 1rem !important;
        }


        /* =====================================================
           BUTTONS
           ===================================================== */

        div.stButton > button {
            min-height: 40px;

            padding: 0.5rem 1rem;

            background: var(--surface);
            color: var(--text);

            border: 1px solid var(--border);
            border-radius: var(--radius-sm);

            font-weight: 600;

            transition:
                background-color 0.15s ease,
                border-color 0.15s ease,
                color 0.15s ease;
        }

        div.stButton > button:hover {
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }

        div.stButton > button:focus,
        div.stButton > button:focus-visible {
            outline: none !important;

            box-shadow:
                0 0 0 2px var(--primary-soft) !important;
        }


        /* =====================================================
           CHECKBOX
           ===================================================== */

        [data-testid="stCheckbox"] input {
            accent-color: var(--primary);
        }

        [data-testid="stCheckbox"] label {
            color: var(--text) !important;
        }


        /* =====================================================
           METRICS
           ===================================================== */

        [data-testid="stMetric"] {
            background: var(--surface);

            border: 1px solid var(--border);
            border-radius: var(--radius-md);

            padding: 1rem;

            box-shadow: none;
        }


        /* =====================================================
           EXPANDERS
           ===================================================== */

        .streamlit-expanderHeader {
            background: var(--surface-muted);

            border: 1px solid var(--border);
            border-radius: var(--radius-sm);

            color: var(--text);
            font-weight: 600;
        }

        .streamlit-expanderContent {
            background: var(--surface);

            border: 1px solid var(--border);
            border-top: none;

            border-radius:
                0 0
                var(--radius-sm)
                var(--radius-sm);
        }


        /* =====================================================
           FILE UPLOADER
           ===================================================== */

        [data-testid="stFileUploaderDropzone"] {
            background: var(--surface-muted);

            border: 1px dashed var(--border);
            border-radius: var(--radius-sm);
        }


        /* =====================================================
           ALERTS
           ===================================================== */

        .stAlert {
            background: var(--surface);

            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
        }


        /* =====================================================
           TABS
           ===================================================== */

        .stTabs [role="tablist"] {
            gap: 0.35rem;
        }

        .stTabs [role="tab"] {
            color: var(--text-muted);

            padding: 0.5rem 0.8rem;

            border-radius: var(--radius-sm);
        }

        .stTabs [aria-selected="true"] {
            color: var(--text);

            background: var(--surface);

            border-color: var(--border);
        }


        /* =====================================================
           TABLES
           ===================================================== */

        .stDataFrame,
        .stTable {
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
        }


        /* =====================================================
           RESPONSIVE ADJUSTMENTS
           ===================================================== */

        @media (max-width: 768px) {

            :root {
                --header-height: 56px;
            }

            .virtuoso-logo {
                width: 34px;
                height: 34px;
            }

            .virtuoso-name {
                font-size: 1.1rem;
                margin-left: 9px;
            }

            .block-container {
                padding-top: calc(var(--header-height) + 1.5rem);
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD SERVICES
# ============================================================

@st.cache_resource
def load_pipeline():
    return RAGPipeline()


@st.cache_resource
def load_document_manager():
    return DocumentManager()


# ============================================================
# INITIALIZATION
# ============================================================

apply_custom_style()


if "pipeline" not in st.session_state:
    st.session_state.pipeline = load_pipeline()


if "document_manager" not in st.session_state:
    st.session_state.document_manager = load_document_manager()

# ============================================================
# GOOGLE DRIVE
# ============================================================

@st.cache_resource
def load_google_drive_client():
    return GoogleDriveMCPClient()

google_drive_client = load_google_drive_client()

# ============================================================
# VIRTUOSO HEADER
# ============================================================

with open(LOGO_PATH, "rb") as logo_file:
    logo_base64 = base64.b64encode(logo_file.read()).decode()


st.markdown(
    f"""
    <header class="virtuoso-header">
        <div class="virtuoso-header-inner">
            <img
                src="data:image/png;base64,{logo_base64}"
                class="virtuoso-logo"
                alt="Virtuoso"
            />
            <span class="virtuoso-name">
                Virtuoso
            </span>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GOOGLE DRIVE CONNECTION
# ============================================================

def connect_google_drive():

    client = google_drive_client

    if client.connected:
        return True

    try:

        with st.spinner(
            "Connexion à Google Drive..."
        ):
            client.connect()

        return True

    except Exception as error:

        st.error(
            f"Impossible de se connecter à Google Drive : {error}"
        )

        return False

# ============================================================
# PAGES
# ============================================================

from app.ui.pages.assistant import assistant_page
from app.ui.pages.dashboard import dashboard_page
from app.ui.pages.documents import documents_page


pg = st.navigation(
    [
        st.Page(
            dashboard_page,
            title="Dashboard",
        ),
        st.Page(
            documents_page,
            title="Gestion des documents",
        ),
        st.Page(
            assistant_page,
            title="Assistant",
        ),
    ]
)


pg.run()

# ============================================================
# GOOGLE DRIVE AUTHENTICATION
# ============================================================

if not google_drive_client.connected:

    st.markdown(
        """
        ## Accès à Google Drive

        Une connexion à Google Drive est nécessaire pour
        accéder aux documents de l'organisation.
        """
    )

    if st.button(
        "Se connecter à Google Drive",
        type="primary",
    ):
        if connect_google_drive():
            st.rerun()

    st.stop()
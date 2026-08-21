import streamlit as st

from app.documents.document_manager import DocumentManager
from app.rag.rag_pipeline import RAGPipeline


def apply_custom_style():
    st.markdown(
        """
        <style>
        html, body, .stApp {
        font-size: 18px;
        }
        body {
            font-size: 18px;
        }

        p, li, label {
            font-size: 18px !important;
        }

        .stTextInput input,
        .stTextArea textarea {
            font-size: 18px !important;
        }

        .stButton button {
            font-size: 17px !important;
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
        :root {
            --bg: #f5f7fb;
            --panel: #ffffff;
            --panel-alt: #f8fafc;
            --text: #111827;
            --muted: #4b5563;
            --border: #dfe5ee;
            --primary: #1d4ed8;
            --primary-strong: #1e3a8a;
            --primary-soft: #eaf1ff;
            --success: #166534;
            --warning: #92400e;
            --danger: #991b1b;
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

        [data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid var(--border);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            letter-spacing: -0.02em;
            font-weight: 600 !important;
        }
        
        p, li, div, span, label {
            color: var(--text);
        }

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

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary);
            box-shadow: none;
        }

        div.stButton > button {
            background: var(--primary);
            color: white;
            border: 1px solid var(--primary);
            border-radius: 6px;
            font-weight: 600;
            padding: 0.55rem 1rem;
            min-height: 38px;
            box-shadow: none;
        }

        div.stButton > button:hover {
            background: var(--primary-strong);
            border-color: var(--primary-strong);
        }

        div.stButton > button:focus {
            box-shadow: none;
            outline: none;
        }

        [data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem 1rem;
            box-shadow: none;
        }

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

        [data-testid="stFileUploaderDropzone"] {
            background: var(--panel-alt);
            border: 1px dashed var(--border);
            border-radius: 6px;
        }

        [data-testid="stMarkdownContainer"] p {
            font-size: 18px !important;
            line-height: 1.6;
        }
        .stAlert {
            border-radius: 6px;
            border: 1px solid var(--border);
            background: #ffffff;
        }

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

        .stDataFrame, .stTable {
            border: 1px solid var(--border);
            border-radius: 6px;
        }

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
    page_title="RAG Document Assistant",
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

pg = st.navigation(
    [
        st.Page(dashboard_page, title="Dashboard", icon="📊"),
        st.Page(documents_page, title="Manage documents", icon="📁"),
        st.Page(assistant_page, title="Assistant", icon="🤖"),
    ]
)

pg.run()
    
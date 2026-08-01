import streamlit as st

from app.rag.rag_pipeline import RAGPipeline
from app.documents.document_manager import DocumentManager

from pathlib import Path
import tempfile
# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="🤖",
    layout="wide",
)

# --------------------------------------------------
# Pipeline initialization
# --------------------------------------------------

@st.cache_resource
def load_pipeline():
    return RAGPipeline()


@st.cache_resource
def load_document_manager():
    return DocumentManager()


pipeline = load_pipeline()
document_manager = load_document_manager()

# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("🤖 RAG Document Assistant")

st.write(
    "Ask questions about your company documents."
)

question = st.text_input(
    "Your question:",
    placeholder="e.g. How many remote work days are allowed?"
)

if st.button("Ask"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Searching documents..."):

        answer, chunks = pipeline.ask(question)

    st.subheader("Answer")

    st.markdown(answer)

    with st.expander("Retrieved Sources"):

        if not chunks:
            st.info("No relevant documents found.")

        else:
            st.write(f"Chunks received by UI: {len(chunks)}")
            for i, chunk in enumerate(chunks, start=1):

                payload = chunk.payload

                source = payload.get("source", "Unknown source")
                text = payload.get("text", "")

                st.markdown(f"**{i}. {source}**")

                st.write(text)

                st.divider()

with st.sidebar:



        st.header("📂 Document Management")



        # -------------------------

        # Statistics

        # -------------------------



        st.subheader("Statistics")



        stats = document_manager.get_statistics()



        st.metric(

            "Indexed Documents",

            stats["documents"],

        )



        st.metric(

            "Vectors",

            stats["vectors"],

        )



        st.divider()



        # -------------------------

        # Documents

        # -------------------------

        

        documents = document_manager.list_documents()

        if not documents:
            st.info("No indexed documents.")

        else:

            st.subheader("Indexed Documents")

            for document in documents:

                col1, col2 = st.columns([5, 1])

                with col1:
                    st.write(f"{document}")

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_{document}",
                        help="Remove document",
                    ):

                        st.session_state.document_to_delete = document

                        st.rerun()

        if "document_to_delete" not in st.session_state:
            st.session_state.document_to_delete = None

        if st.session_state.document_to_delete is not None:

            document = st.session_state.document_to_delete

            st.warning(
                f"Delete '{document}'?"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Delete",
                    key="confirm_delete",
                ):

                    document_manager.remove_document(document)

                    st.success(
                        f"{document} removed successfully."
                    )

                    st.session_state.document_to_delete = None

                    st.rerun()

            with col2:

                if st.button(
                    "Cancel",
                    key="cancel_delete",
                ):

                    st.session_state.document_to_delete = None

                    st.rerun()

        st.divider()



        # -------------------------

        # Upload

        # -------------------------

        st.subheader("Upload Document")

        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0


        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "docx", "txt"],
            key=f"uploader_{st.session_state.uploader_key}",
        )


        if uploaded_file is not None:

            st.success(f"Selected: {uploaded_file.name}")

            if st.button("Index Document"):

                destination = Path("data/raw") / uploaded_file.name

                destination.write_bytes(
                    uploaded_file.getbuffer()
                )

                result = document_manager.add_document(
                    str(destination)
                )

                if result:
                    st.success(
                        f"{uploaded_file.name} indexed successfully."
                    )

                    st.session_state.uploader_key += 1
                    st.rerun()

                else:

                    st.warning(
                        f"{uploaded_file.name} already exists."
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "Replace Document",
                            key=f"replace_{uploaded_file.name}",
                        ):

                            document_manager.replace_document(
                                str(destination)
                            )

                            

                            st.success(
                                f"{uploaded_file.name} replaced successfully."
                            )
                            
                            st.session_state.uploader_key += 1

                            st.rerun()

                    with col2:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{uploaded_file.name}",
                        ):

                            st.info("Replacement cancelled.")
                        
                            st.session_state.uploader_key += 1


                            st.rerun()
        st.divider()



        # -------------------------

        # Clear Database

        # -------------------------


        st.subheader("Clear Database")

        if "confirm_clear_database" not in st.session_state:
            st.session_state.confirm_clear_database = False

        if not st.session_state.confirm_clear_database:

            if st.button(
                "Clear Database",
                key="clear_database",
            ):
                st.session_state.confirm_clear_database = True
                st.rerun()

        else:

            st.warning(
                "Are you sure? This will remove all indexed documents."
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Yes",
                    key="confirm_clear",
                ):

                    document_manager.clear_database()

                    st.session_state.confirm_clear_database = False

                    st.success("Database cleared successfully.")

                    st.rerun()

            with col2:

                if st.button(
                    "Cancel",
                    key="cancel_clear",
                ):

                    st.session_state.confirm_clear_database = False

                    st.rerun()
    
from pathlib import Path

import streamlit as st


def documents_page():
    st.title("Document management")

    manager = st.session_state.document_manager

    st.subheader("Statistics")
    try:
        stats = manager.get_statistics()
    except Exception as e:
        st.error(f"Unable to retrieve statistics.\n\n{e}")
        stats = {"documents": 0, "vectors": 0}

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Indexed documents", stats.get("documents", 0))
    with col2:
        st.metric("Vectors", stats.get("vectors", 0))

    st.divider()

    try:
        documents = manager.list_documents()
    except Exception as e:
        st.error(f"Unable to retrieve document list.\n\n{e}")
        documents = []

    if not documents:
        st.info("No indexed documents.")
    else:
        st.subheader("Indexed documents")
        for document in documents:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(document)
            with col2:
                if st.button("Delete", key=f"delete_{document}", help="Remove document"):
                    st.session_state.document_to_delete = document
                    st.rerun()

    if "document_to_delete" not in st.session_state:
        st.session_state.document_to_delete = None

    if st.session_state.document_to_delete is not None:
        document = st.session_state.document_to_delete
        st.warning(f"Delete '{document}'?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete", key="confirm_delete"):
                try:
                    manager.remove_document(document)
                except Exception as e:
                    st.error(f"Unable to remove document.\n\n{e}")
                st.success(f"{document} removed successfully.")
                st.session_state.document_to_delete = None
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_delete"):
                st.session_state.document_to_delete = None
                st.rerun()

    st.divider()
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
            destination.write_bytes(uploaded_file.getbuffer())

            try:
                result = manager.add_document(str(destination))
            except Exception as e:
                if destination.exists():
                    destination.unlink()
                st.error(f"Unable to index document.\n\n{e}")
                return

            if result:
                st.success(f"{uploaded_file.name} indexed successfully.")
                st.session_state.uploader_key += 1
                st.rerun()
            else:
                st.warning(f"{uploaded_file.name} already exists.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Replace Document", key=f"replace_{uploaded_file.name}"):
                        try:
                            manager.replace_document(str(destination))
                        except Exception as e:
                            if destination.exists():
                                destination.unlink()
                            st.error(f"Unable to replace document.\n\n{e}")
                            return
                        st.success(f"{uploaded_file.name} replaced successfully.")
                        st.session_state.uploader_key += 1
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"cancel_{uploaded_file.name}"):
                        st.info("Replacement cancelled.")
                        st.session_state.uploader_key += 1
                        st.rerun()

    st.divider()
    st.subheader("Clear Database")

    if "confirm_clear_database" not in st.session_state:
        st.session_state.confirm_clear_database = False

    if not st.session_state.confirm_clear_database:
        if st.button("Clear Database", key="clear_database"):
            st.session_state.confirm_clear_database = True
            st.rerun()
    else:
        st.warning("Are you sure? This will remove all indexed documents.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", key="confirm_clear"):
                try:
                    manager.clear_database()
                except Exception as e:
                    st.error(f"Unable to clear database.\n\n{e}")
                st.session_state.confirm_clear_database = False
                st.success("Database cleared successfully.")
                st.rerun()
        with col2:
            if st.button("Cancel", key="cancel_clear"):
                st.session_state.confirm_clear_database = False
                st.rerun()

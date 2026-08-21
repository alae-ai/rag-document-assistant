import streamlit as st


def dashboard_page():
    st.title("Dashboard")
    st.write("Overview of indexed content and retrieval volume.")

    manager = st.session_state.document_manager

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
        st.info("No indexed documents yet.")
    else:
        st.subheader("Indexed documents")
        for document in documents:
            st.markdown(f"- {document}")

import streamlit as st


def dashboard_page():
    st.title("Dashboard")
    st.write("Aperçu du contenu indexé et du volume de récupération.")

    manager = st.session_state.document_manager

    try:
        stats = manager.get_statistics()
    except Exception as e:
        st.error(f"Impossible de récupérer les statistiques.\n\n{e}")
        stats = {"documents": 0, "vectors": 0}

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents indexés", stats.get("documents", 0))
    with col2:
        st.metric("Vectors", stats.get("vectors", 0))

    st.divider()

    try:
        documents = manager.list_documents()
    except Exception as e:
        st.error(f"Impossible de récupérer la liste des documents.\n\n{e}")
        documents = []

    if not documents:
        st.info("Aucun document indexé pour le moment.")
    else:
        st.subheader("Documents indexés")
        for document in documents:
            st.markdown(f"- {document}")

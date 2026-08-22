from pathlib import Path

import streamlit as st


def documents_page():
    st.title("Gestion des documents")

    manager = st.session_state.document_manager

    st.subheader("Statistiques")
    try:
        stats = manager.get_statistics()
    except Exception as e:
        st.error(f"Impossible de récupérer les statistiques.\n\n{e}")
        stats = {"documents": 0, "vectors": 0}

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents indexés", stats.get("documents", 0))
    with col2:
        st.metric("Vecteurs", stats.get("vectors", 0))

    st.divider()
    st.subheader("Charger Document")

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.file_uploader(
        "Charger un document (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:
        st.success(f"Document chargé: {uploaded_file.name}")

        if st.button("Indexer le Document"):
            destination = Path("data/raw") / uploaded_file.name
            destination.write_bytes(uploaded_file.getbuffer())

            try:
                result = manager.add_document(str(destination))
            except Exception as e:
                if destination.exists():
                    destination.unlink()
                st.error(f"Impossible de indexer le document.\n\n{e}")
                return

            if result:
                st.success(f"{uploaded_file.name} document indexé avec succès.")
                st.session_state.uploader_key += 1
                st.rerun()
            else:
                st.warning(f"{uploaded_file.name} document déjà indexé. Vous pouvez le remplacer si nécessaire.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remplacer le Document", key=f"replace_{uploaded_file.name}"):
                        try:
                            manager.replace_document(str(destination))
                        except Exception as e:
                            if destination.exists():
                                destination.unlink()
                            st.error(f"Impossible de remplacer le document.\n\n{e}")
                            return
                        st.success(f"{uploaded_file.name} remplacé avec succès.")
                        st.session_state.uploader_key += 1
                        st.rerun()
                with col2:
                    if st.button("Annuler", key=f"cancel_{uploaded_file.name}"):
                        st.info("Replacement annulé.")
                        st.session_state.uploader_key += 1
                        st.rerun()

    st.divider()
    try:
        documents = manager.list_documents()
    except Exception as e:
        st.error(f"Impossible de récupérer la liste des documents.\n\n{e}")
        documents = []

    if not documents:
        st.info("Aucun document indexé.")
    else:
        st.subheader("Documents indexés")
        for document in documents:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(document)
            with col2:
                if st.button("Supprimer", key=f"delete_{document}", help="Remove document"):
                    st.session_state.document_to_delete = document
                    st.rerun()

    if "document_to_delete" not in st.session_state:
        st.session_state.document_to_delete = None

    if st.session_state.document_to_delete is not None:
        document = st.session_state.document_to_delete
        st.warning(f"Êtes-vous sûr de vouloir supprimer '{document}'?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Supprimer", key="confirm_delete"):
                try:
                    manager.remove_document(document)
                except Exception as e:
                    st.error(f"Impossible de supprimer le document.\n\n{e}")
                st.success(f"{document} supprimé avec succès.")
                st.session_state.document_to_delete = None
                st.rerun()
        with col2:
            if st.button("Annuler", key="cancel_delete"):
                st.session_state.document_to_delete = None
                st.rerun()

    st.divider()
    st.subheader("Vider la base de données")

    if "confirm_clear_database" not in st.session_state:
        st.session_state.confirm_clear_database = False

    if not st.session_state.confirm_clear_database:
        if st.button("Vider la base de données", key="clear_database"):
            st.session_state.confirm_clear_database = True
            st.rerun()
    else:
        st.warning("Vous êtes sur le point de supprimer tous les documents indexés. Cette action est irréversible. Confirmez-vous ?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Oui", key="confirm_clear"):
                try:
                    manager.clear_database()
                except Exception as e:
                    st.error(f"Impossible de vider la base de données.\n\n{e}")
                st.session_state.confirm_clear_database = False
                st.success("Base de données vidée avec succès.")
                st.rerun()
        with col2:
            if st.button("Annuler", key="cancel_clear"):
                st.session_state.confirm_clear_database = False
                st.rerun()

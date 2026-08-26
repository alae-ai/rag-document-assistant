import streamlit as st

#from app.ingestion.google_drive_ingestion import GoogleDriveIngestion
from app.mcp.google_drive_service import GoogleDriveService


def documents_page():
    st.title("Gestion des documents")

    manager = st.session_state.document_manager

    # ========================================================
    # GOOGLE DRIVE SERVICE
    # ========================================================

    if "google_drive_service" not in st.session_state:
        st.session_state.google_drive_service = None

    # ========================================================
    # STATISTICS
    # ========================================================

    st.subheader("Statistiques")

    try:
        stats = manager.get_statistics()

    except Exception as e:
        st.error(
            f"Impossible de récupérer les statistiques.\n\n{e}"
        )

        stats = {
            "documents": 0,
            "vectors": 0,
        }

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Documents indexés",
            stats.get("documents", 0),
        )

    with col2:
        st.metric(
            "Vecteurs",
            stats.get("vectors", 0),
        )

    st.divider()

    # ========================================================
    # LOCAL FILE UPLOAD
    # ========================================================

    st.subheader("Charger Document")

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.file_uploader(
        "Charger un document (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:

        st.success(
            f"Document chargé : {uploaded_file.name}"
        )

        if st.button("Indexer le Document"):

            try:
                result = manager.add_document(
                    uploaded_file.getvalue(),
                    uploaded_file.name,
                )

            except Exception as e:
                st.error(
                    f"Impossible d'indexer le document.\n\n{e}"
                )
                return

            if result:

                st.success(
                    f"{uploaded_file.name} "
                    "document indexé avec succès."
                )

                st.session_state.uploader_key += 1
                st.rerun()

            else:

                st.warning(
                    f"{uploaded_file.name} document déjà indexé. "
                    "Vous pouvez le remplacer si nécessaire."
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Remplacer le Document",
                        key=f"replace_{uploaded_file.name}",
                    ):

                        try:

                            manager.replace_document(
                                uploaded_file.getvalue(),
                                uploaded_file.name,
                            )

                        except Exception as e:

                            st.error(
                                "Impossible de remplacer "
                                f"le document.\n\n{e}"
                            )
                            return

                        st.success(
                            f"{uploaded_file.name} "
                            "remplacé avec succès."
                        )

                        st.session_state.uploader_key += 1
                        st.rerun()

                with col2:

                    if st.button(
                        "Annuler",
                        key=f"cancel_{uploaded_file.name}",
                    ):

                        st.session_state.uploader_key += 1
                        st.rerun()

    st.divider()

    # ========================================================
    # GOOGLE DRIVE
    # ========================================================

    st.subheader("Importer depuis Google Drive")

    drive_service = st.session_state.google_drive_service

    # --------------------------------------------------------
    # Not connected
    # --------------------------------------------------------

    if drive_service is None:

        if st.button(
            "Connecter à Google Drive",
            key="connect_google_drive",
        ):

            try:

                service = GoogleDriveService()

                # Synchronous API
                service.connect()

                st.session_state.google_drive_service = service

                st.success(
                    "Google Drive connecté avec succès."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "Impossible de se connecter "
                    f"à Google Drive.\n\n{e}"
                )

    # --------------------------------------------------------
    # Connected
    # --------------------------------------------------------

    else:

        st.success("Google Drive est connecté.")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Actualiser les fichiers",
                key="refresh_drive_files",
            ):
                st.rerun()

        with col2:

            if st.button(
                "Déconnecter Google Drive",
                key="disconnect_google_drive",
            ):

                try:
                    drive_service.close()

                except Exception as e:
                    st.warning(
                        "Erreur lors de la fermeture "
                        f"de la connexion : {e}"
                    )

                st.session_state.google_drive_service = None

                st.rerun()

        # ----------------------------------------------------
        # Retrieve Drive files
        # ----------------------------------------------------

        try:

            files = drive_service.list_files()

        except Exception as e:

            st.error(
                "Impossible de récupérer les fichiers "
                f"Google Drive.\n\n{e}"
            )

            files = []

        # ----------------------------------------------------
        # Filter files
        # ----------------------------------------------------

        file_options = {
            file["name"]: file
            for file in files
            if file.get("mimeType")
            != "application/vnd.google-apps.folder"
        }

        if file_options:

            selected_name = st.selectbox(
                "Sélectionner un fichier",
                list(file_options.keys()),
                key="google_drive_file",
            )

            selected_file = file_options[selected_name]

            if st.button(
                "Importer depuis Google Drive",
                key="import_google_drive_file",
            ):

                try:

                    ingestion = GoogleDriveIngestion(
                        drive_client=drive_service,
                        document_manager=manager,
                    )

                    result = ingestion.ingest_file(
                        file_id=selected_file["id"],
                        filename=selected_file["name"],
                    )

                    if result:

                        st.success(
                            f"{selected_file['name']} "
                            "a été importé et indexé "
                            "avec succès."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            f"{selected_file['name']} "
                            "est déjà indexé."
                        )

                except Exception as e:

                    st.error(
                        "Impossible d'importer "
                        f"le document.\n\n{e}"
                    )

        else:

            st.info(
                "Aucun fichier disponible sur Google Drive."
            )

    st.divider()

    # ========================================================
    # INDEXED DOCUMENTS
    # ========================================================

    try:

        documents = manager.list_documents()

    except Exception as e:

        st.error(
            "Impossible de récupérer la liste "
            f"des documents.\n\n{e}"
        )

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

                if st.button(
                    "Supprimer",
                    key=f"delete_{document}",
                    help="Remove document",
                ):

                    st.session_state.document_to_delete = document
                    st.rerun()

    # ========================================================
    # DELETE DOCUMENT CONFIRMATION
    # ========================================================

    if "document_to_delete" not in st.session_state:
        st.session_state.document_to_delete = None

    if st.session_state.document_to_delete is not None:

        document = st.session_state.document_to_delete

        st.warning(
            f"Êtes-vous sûr de vouloir supprimer "
            f"'{document}' ?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Supprimer",
                key="confirm_delete",
            ):

                try:

                    manager.remove_document(document)

                    st.success(
                        f"{document} supprimé avec succès."
                    )

                    st.session_state.document_to_delete = None

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Impossible de supprimer "
                        f"le document.\n\n{e}"
                    )

        with col2:

            if st.button(
                "Annuler",
                key="cancel_delete",
            ):

                st.session_state.document_to_delete = None
                st.rerun()

    # ========================================================
    # CLEAR DATABASE
    # ========================================================

    st.divider()

    st.subheader("Vider la base de données")

    if "confirm_clear_database" not in st.session_state:
        st.session_state.confirm_clear_database = False

    if not st.session_state.confirm_clear_database:

        if st.button(
            "Vider la base de données",
            key="clear_database",
        ):

            st.session_state.confirm_clear_database = True
            st.rerun()

    else:

        st.warning(
            "Vous êtes sur le point de supprimer tous les "
            "documents indexés. Cette action est irréversible. "
            "Confirmez-vous ?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Oui",
                key="confirm_clear",
            ):

                try:

                    manager.clear_database()

                    st.session_state.confirm_clear_database = False

                    st.success(
                        "Base de données vidée avec succès."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Impossible de vider la base de "
                        f"données.\n\n{e}"
                    )

        with col2:

            if st.button(
                "Annuler",
                key="cancel_clear",
            ):

                st.session_state.confirm_clear_database = False
                st.rerun()
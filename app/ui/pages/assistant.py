import streamlit as st


def assistant_page():
    st.title("Assistant")
    st.write("Bonjour, votre assistant pour explorer les documents de l’organisation.")

    question = st.text_input(
        "Question",
        placeholder="e.g. Combien de jours de travail à distance sont autorisés ?",
    )
    use_intent_classifier = st.checkbox("Classification d'intention", value=False)

    if st.button("Ask"):
        if not question.strip():
            st.warning("Veuillez saisir une question.")
            st.stop()

        pipeline = st.session_state.pipeline

        with st.spinner("Recherche de documents..."):
            try:
                answer, chunks = pipeline.ask(
                    question,
                    use_intent_classifier=use_intent_classifier,
                )
            except Exception as e:
                st.error(f"Impossible de répondre à votre question.\n\n{e}")
                st.stop()

        st.subheader("Réponse")
        st.markdown(answer)

        with st.expander("Sources"):
            if not chunks:
                st.info("Aucun document pertinent trouvé.")
            else:
                for i, chunk in enumerate(chunks, start=1):
                    payload = chunk.payload
                    source = payload.get("source", "Unknown source")
                    text = payload.get("text", "")
                    st.markdown(f"**{i}. {source}**")
                    st.write(text)
                    st.divider()

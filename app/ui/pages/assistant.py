import streamlit as st


def assistant_page():
    st.title("Assistant")
    st.write("Ask questions about the organization’s documents.")

    question = st.text_input(
        "Question",
        placeholder="e.g. How many remote work days are allowed?",
    )
    use_intent_classifier = st.checkbox("Use intent classification", value=True)

    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        pipeline = st.session_state.pipeline

        with st.spinner("Searching documents..."):
            try:
                answer, chunks = pipeline.ask(
                    question,
                    use_intent_classifier=use_intent_classifier,
                )
            except Exception as e:
                st.error(f"Unable to answer your question.\n\n{e}")
                st.stop()

        st.subheader("Answer")
        st.markdown(answer)

        with st.expander("Sources"):
            if not chunks:
                st.info("No relevant documents found.")
            else:
                for i, chunk in enumerate(chunks, start=1):
                    payload = chunk.payload
                    source = payload.get("source", "Unknown source")
                    text = payload.get("text", "")
                    st.markdown(f"**{i}. {source}**")
                    st.write(text)
                    st.divider()

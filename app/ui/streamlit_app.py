import streamlit as st

from app.rag.rag_pipeline import RAGPipeline

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


pipeline = load_pipeline()

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

    st.write(answer)

    with st.expander("Retrieved Sources"):

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

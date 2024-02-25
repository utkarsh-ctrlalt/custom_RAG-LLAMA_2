import streamlit as st
from PIL import Image
from rag_pipeline import generate_response
import config


def process_query(query):
    output = generate_response(query)
    return output

def main():
    st.title("Simple Streamlit App")

    # Input text box for user query
    query = st.text_input("Enter your query:")
    ip = st.radio(
        "Do you want to use RAG? 👉",
        key="RAG",
        options=["yes", "no"],
    )
    result = []
    with st.form("summarize_form", clear_on_submit=True):
        submitted = st.form_submit_button("Submit")
        with st.spinner("Calculating..."):
            if submitted:
                if ip == "yes":
                    response = generate_response(
                        query,  incontext_learning=True
                    )
                    result.append(response)
                else:
                    response = generate_response(
                        query,  incontext_learning=False
                    )
                    result.append(response)

    if len(result):
        st.info(response)


if __name__ == "__main__":
    main()
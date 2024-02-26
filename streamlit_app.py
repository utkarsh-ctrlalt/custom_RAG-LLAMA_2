import streamlit as st
from PIL import Image
from rag_pipeline import generate_response
import config


def process_query(query):
    """
    Process the user query and generate a response via LLM model.

    Args:
    query (str): User query.

    Returns:
    str: Response generated based on the query via LLM model.
    """
    output = generate_response(query)
    return output

def main():
    """
    Main function to run the Streamlit application.
    """

    # Set the title of the Streamlit application
    st.title("Custom RAG Pipeline - Llama 2")

    # Input text box for user query
    query = st.text_input("Enter your query:")

    # Radio button for selecting whether to use RAG or not
    ip = st.radio(
        "Do you want to use RAG? 👉",
        key="RAG",
        options=["yes", "no"],
    )
    result = []

    # Form for submitting the query
    with st.form("summarize_form", clear_on_submit=True):
        submitted = st.form_submit_button("Submit")
        with st.spinner("Calculating..."):
            if submitted:
                if ip == "yes":
                    # Generate response using RAG if selected
                    response = generate_response(
                        query,  rag=True
                    )
                    result.append(response)
                else:
                    # Generate response without using RAG if selected
                    response = generate_response(
                        query,  rag=False
                    )
                    result.append(response)
                    
    # Display the response if generated
    if len(result):
        st.info(response)


if __name__ == "__main__":
    main()
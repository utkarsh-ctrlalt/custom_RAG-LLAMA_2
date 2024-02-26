# custom_RAG-LLAMA_2
A custom RAG pipeline to answer questions from a textbook

In this project I have created a custom RAG pipeline from scratch using Langchain & HuggingFace Libraries and I have used <b>LLAMA_2-7b-chat-hf</b> as a foundational LLM model.
For vector store, I have used Chroma DB and HuggingFaceInstructEmbeddings as a text embedding model.
I have also implmented GUI using streamlit python framework for interacting with this custom RAG pipeline.

# Running this service as a Docker Container
 ## docker run command - 
    sudo docker run -d --runtime=nvidia --gpus all -p 8501:8501 --name {container_name} {image_name}

 ### <b>NOTE:</b> If you have downloaded the Llama 2-7b-chat-hf locally, update the config.py file according to the comments in that script.

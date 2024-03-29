import requests
from bs4 import BeautifulSoup
import os
import torch
from torch import cuda, bfloat16
import transformers
from PIL import Image

from transformers import AutoTokenizer, StoppingCriteria, StoppingCriteriaList
from langchain import HuggingFacePipeline,PromptTemplate, LLMChain
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts.few_shot import FewShotPromptTemplate

import streamlit as st
import config



def stoppingCriterion(model_id, hf_auth_token):
    """
      Defines a stopping criterion for text generation.

      Args:
          model_id (str): The model identifier.
          hf_auth_token (str): The Hugging Face authentication token.

      Returns:
          StoppingCriteriaList: List of stopping criteria for model generation.
    """
    class StopOnTokens(StoppingCriteria):
        def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
            for stop_ids in stop_token_ids:
                if torch.eq(input_ids[0][-len(stop_ids):], stop_ids).all():
                    return True
            return False

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_id,
        token=hf_auth_token,
        
    )


    stop_list = ['\nHuman:', '\n```\n']

    stop_token_ids = [tokenizer(x)['input_ids'] for x in stop_list]
    #print(f"stop token ids list = {stop_token_ids}")
    device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

    stop_token_ids = [torch.LongTensor(x).to(device) for x in stop_token_ids]
    #print(f" tensor of stop tokens id = {stop_token_ids}")
    stopping_criteria = StoppingCriteriaList([StopOnTokens()])
    
    return stopping_criteria

@st.cache_resource
def database(store_dir_path):
  """
    Loads Created Chroma Vector Store.
    Args:
        store_dir_path (str): Path to the directory to persist the vector store.
    Returns:
        Chroma: The Chroma vector store.
  """
 
  hf_embedding = HuggingFaceInstructEmbeddings()
  db = Chroma(persist_directory=store_dir_path, embedding_function=hf_embedding)

  return db

@st.cache_resource
def getModel(model_id, hf_auth_token):
    """
      Retrieves a pre-trained language model (LLAMA 2-7B-chat-hf).

      Args:
          model_id (str): The model identifier.
          hf_auth_token (str): The Hugging Face authentication token.

      Returns:
          HuggingFacePipeline: The pre-trained language model.
    """
   
    model_config = transformers.AutoConfig.from_pretrained(
        model_id,
        token=hf_auth_token,
    )

    # Model Quantization 
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=bfloat16
    )

    quantized_model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='auto',
        token=hf_auth_token
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, token = hf_auth_token)
    stopping_criteria = stoppingCriterion(model_id, hf_auth_token)
    pipeline = transformers.pipeline(
                    model=quantized_model, 
            tokenizer=tokenizer,
            return_full_text=True,  # langchain expects the full text
            task='text-generation',                          #'text-generation'
            # we pass model parameters here too
            stopping_criteria=stopping_criteria,  # without this model rambles during chat
            temperature=0.01,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
            max_new_tokens=1024,  # max number of tokens to generate in the output
            repetition_penalty=1.1,  # without this output begins repeating
            batch_size=24

    )

    llm = HuggingFacePipeline(pipeline=pipeline)
    llm.model_id = model_id
    return llm


def generate_response(txt, rag=True):
    """
    Generates a response based on input text and pre-trained language models.

    Args:
        txt (str): Input text.
        llm (HuggingFacePipeline): Pre-trained language model.
        db (Chroma): Chroma vector store.
        rag (bool, optional): Whether to use Retrieval Augmented Generation (RAG). Defaults to True.

    Returns:
        str: Generated response.
    """

    model_id = config.summerizer_model_id
    hf_auth_token = config.hf_token
    store_dir_path = config.store_dir_path

    llm = getModel(model_id, hf_auth_token)
    # txt = txt.decode('utf-8')

    if rag == True:
        db = database(store_dir_path)
        search = db.similarity_search(txt, n_results=5)

        template = config.prompt_template
        
        prompt = PromptTemplate(input_variables=["context","question"], template= template)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        return llm_chain.run({"question":txt, "context":search})
        
    else:
        template = config.prompt_template_without_rag
        
        prompt = PromptTemplate(input_variables=["question"], template= template)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        return llm_chain.run({"question":txt})

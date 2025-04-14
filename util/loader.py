import os
from langchain_openai import ChatOpenAI
from langchain_community.llms import VLLMOpenAI
import sys
import traceback
import logging
import httpx
import asyncio
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

def init_llm(agentic=False):
    """
    Initializes LLM based on the family (Llama, Granite, etc) 
    and whether or not it is part of an agentic workflow.
    """
    try:
        api_url = os.getenv(f"OPENAI_API_BASE")
        
        api_key = os.getenv(f"OPENAI_API_KEY")
        
        model_name = str(os.getenv(f"OPENAI_API_MODEL"))
        
        vllm_params = {
            "openai_api_key": api_key, 
            "openai_api_base": api_url, 
            "model_name": model_name,
        }
        
        rag_params = { 
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        agentic_params = {
            "temperature": 0, 
            "request_timeout": 300, 
            "http_client": httpx.Client(verify=False),
        }

        connection_params = { 
            "http_client": httpx.Client(verify=False),
        }

        logger.info(f"vLLM model={model_name}=============\n\n\n")
        logger.info(f"vllm_params={vllm_params}\n\nrag_params={rag_params}\n\nagentic_params={agentic_params}\n\n\n")
        
        logger.info(f"Will use vLLM\n================================\n")
        llm = ChatOpenAI(**{**vllm_params, **agentic_params, **connection_params} ) if agentic else ChatOpenAI(**{**vllm_params, **rag_params, **connection_params} )
    
        return llm
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise Exception(f"Could not load LLM: {str(e)}")
from langchain_ollama.llms import OllamaLLM
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os
import logging
from dotenv import load_dotenv

load_dotenv()  
HF_TOKEN = os.environ.get("HF_TOKEN")

logger = logging.getLogger(__name__)

def LoadModel(model_provider):
    """
    Function to load the specified language model based on the provider.
    Supports "OLLAMA" and "HF_API".
    1. Ollama: Loads a local Ollama model.
    2. HF_API: Loads a model from HuggingFace Inference API using the provided token.
    Raises ValueError for unsupported providers.
    """
    if model_provider == "OLLAMA":
        logger.info("Using Ollama model")
        model = OllamaLLM(model='llama3:8b', temperature=0)
        return model
    elif model_provider == "HF_API":
        logger.info("Using HuggingFace Inference API model")
        try:
            llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                huggingfacehub_api_token=HF_TOKEN,
                max_new_tokens=512,
                temperature=0.2,
            )
            model = ChatHuggingFace(llm=llm)
        except Exception as e:
            logger.error(f"Error loading HuggingFace API model: {e}")
            raise e
        return model
    else:
        logger.error(f"Unsupported model provider: {model_provider}")
        raise ValueError(f"Unsupported model provider: {model_provider}")

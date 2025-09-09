from langchain_ollama.llms import OllamaLLM
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os
import logging
from dotenv import load_dotenv

load_dotenv()  
HF_TOKEN = os.environ.get("HF_TOKEN")

logger = logging.getLogger(__name__)

def LoadModel(model_provider):
    if model_provider == "OLLAMA":
        logger.info("Using Ollama model")
        model = OllamaLLM(model='llama3:8b', temperature=0)
        return model
    elif model_provider == "HF_API":
        logger.info("Using HuggingFace Inference API model")
        try:
            llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=HF_TOKEN,
                max_new_tokens=512,
                temperature=0,
            )
            model = ChatHuggingFace(llm=llm)
        except Exception as e:
            logger.error(f"Error loading HuggingFace API model: {e}")
            raise e
        return model
    elif model_provider == "HF_LOCAL":
        logger.info("Using HuggingFace LOCAL model")
        try:
            model_id = "mistralai/Mistral-7B-Instruct-v0.2" 
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",   
                torch_dtype="auto" 
            )
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0
            )
            hf_pipeline = HuggingFacePipeline(pipeline=pipe)
            return hf_pipeline
        except Exception as e:
            logger.error(f"Error loading local HuggingFace model: {e}")
            raise e
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings

# Ollama models initialization
model = OllamaLLM(model='llama3:8b', temperature=0)
embeddings = OllamaEmbeddings(model='nomic-embed-text:latest')

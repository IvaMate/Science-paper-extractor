# Science-paper-extractor

Python script that extracts metadata and summaries from a database of research papers and outputs the combined information into an Excel sheet. The goal of this tool is to provide a preliminary overview of hundreds of research papers, enabling users to find  the most relevant papers for their specific use case.

Note: This tool is not designed for review papers, as review papers are generally important to read in full and do not require summarization or selective reading like other types of research papers.

## Structure
Science-paper-extractor
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # main loop
│   ├── model_loader.py         # model settings
│   ├── pdf_processing.py       # parsing the data
│   ├── prompts.py              # promts for LLM chains
│   └── helper_utils.py         # helper functions
│
├── Data/
│   ├── input/                  
│   └── output/                 
│
├── notebook/
│   └── demo.ipynb              
│
├── requirements.txt            
├── .env.example     
├── .gitignore                 
└── README.md                                    

## Set up
1. Clone repository

    ```
    git clone <repo>
    cd science-paper-extractor
    ```

2. Python requirements:

- Python version: Python 3.10.12

- Install `OCR` dependencies (linux):
    - sudo apt install poppler-utils
    - sudo apt install tesseract-ocr

- Download `ollama` and pull models: https://ollama.com/download if you want to run it localy
    ```
    ollama pull nomic-embed-text  
    ollama pull llama3:8b
    ```

3. Create virtual environment and install `requirements.txt`

    ```
    python -m venv .venv
    source .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

4. Set up .env if using huggingface API
    ```
    HUGGINGFACE_API_KEY=your_token_here
    ```

## Usage

1. Place your research papers into `Data/input`
2. Choose type of model provider in `config.yaml`:
- `OLLAMA` - ollama local models
- `HF_API` - huggingface API models. Needs token to be updated in `.env` file. Note that there is a monthly free credit limitation for some models.
3. Run the script:

    ```
    python -m src.main
    ```
4. The output Excel file will be saved as `Data/output/research_papers_data.csv`.
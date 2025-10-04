import os
import glob
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import logging
from src import prompts, model_loader, pdf_processing
from tqdm import tqdm 
from src.helper_utils import load_config, CONFIG_PATH

config = load_config(CONFIG_PATH)

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# load model and chains
logger.info("Load model and chains")

model = model_loader.LoadModel("OLLAMA")

logger.info("Model loaded.")

map_prompt = ChatPromptTemplate.from_template(prompts.MAP_PROMPT_TEXT)
summarize_chain = map_prompt | model | StrOutputParser()

extraction_prompt = ChatPromptTemplate.from_template(prompts.EXTRACTION_PROMPT_TEXT)
extraction_chain = extraction_prompt | model | JsonOutputParser()

logger.info("Prompts prepared.")

def main():
    PDF_FOLDER = config["PDF_FOLDER"]
    OUTPUT_CSV = config["OUTPUT_CSV"]
    
    # check input folder
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        logger.warning(f"Created folder '{PDF_FOLDER}'. Please add your research papers and run again.")
        exit()

    # find pdfs
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in '{PDF_FOLDER}'. Please add some papers.")
        exit()

    logger.info(f"Found {len(pdf_files)} PDF(s) to process.")

    all_results = []
    for file_path in tqdm(pdf_files, desc="Processing PDFs", unit="PDF"):
        filename = os.path.basename(file_path)
        try:
            result = pdf_processing.process_paper(file_path, summarize_chain, extraction_chain)
            if result:
                all_results.append(result)
                logger.info(f"Successfully processed '{filename}'.")
            else:
                logger.warning(f"No results returned for '{filename}'.")
        except Exception as e:
            logger.error(f"Unhandled error occurred for '{filename}': {e}")

    # save results
    if all_results:
        df = pd.DataFrame(all_results)
        metadata_cols = ['filename', 'title', 'author', 'subject', 'keywords', 'creator', 'creationYear']
        desired_summary_cols_order = [
            'overall_summary', 'methodology', 'algorithms', 'data_pre_processing_methods', 'results',
            'conclusion', 'dataset', 'future_recommendations'
        ]
        final_cols_order = [col for col in metadata_cols if col in df.columns] + \
                           [col for col in desired_summary_cols_order if col in df.columns]

        # add missing columns
        for col in final_cols_order:
            if col not in df.columns:
                df[col] = None

        df = df[final_cols_order]
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Processing complete. Results saved to '{OUTPUT_CSV}'.")
    else:
        logger.warning("No papers were successfully processed.")

    

# main loop
if __name__ == "__main__":
    main()

   
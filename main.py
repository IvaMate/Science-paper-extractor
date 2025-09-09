import logging
import os
import glob
import pandas as pd
from src import helper_utils

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]  # logs to console
)

config = helper_utils.load_config("config.yaml")
PDF_FOLDER = config["PDF_FOLDER"]
OUTPUT_CSV = config["OUTPUT_CSV"]
MODEL_PROVIDER=config["MODEL_PROVIDER"]

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        logger.warning(f"Created folder '{PDF_FOLDER}'. Please add your research papers to this folder and run again.")
        exit()

    # Get all PDF files
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in the '{PDF_FOLDER}' folder. Please add some papers.")
        exit()

    #print(f"Found {len(pdf_files)} PDF(s) to process.")
    logger.info(f"Found {len(pdf_files)} PDF(s) to process.")
    
    all_results = []
    for file_path in pdf_files:
        try:
            result = helper_utils.process_paper(file_path)
            if result:
                all_results.append(result)
        except Exception as e:
            logger.error(f"Unhandled error in {os.path.basename(file_path)}: {e}")

    # Convert results to a pandas DataFrame and save to CSV
    if all_results:
        df = pd.DataFrame(all_results)
        # Reorder columns to put filename, metadata first, then summary data
        metadata_cols = ['filename', 'title', 'author', 'subject', 'keywords', 'creator', 'creationYear']
        # Define the exact order of your desired summary columns (all lowercase)
        desired_summary_cols_order = [
            'overall_summary', 'methodology', 'algorithms', 'type_of_task',
            'type_of_learning', 'data_pre_processing_methods', 'results',
            'conclusion', 'dataset', 'future_recommendations'
        ]

        # Filter and reorder columns
        final_cols_order = [col for col in metadata_cols if col in df.columns] + \
                           [col for col in desired_summary_cols_order if col in df.columns]

        # Ensure all columns exist before selecting them to avoid KeyError
        for col in final_cols_order:
            if col not in df.columns:
                df[col] = None

        df = df[final_cols_order]
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Processing complete. Results saved to '{OUTPUT_CSV}'.")
    else:
        logger.warning("No papers were successfully processed.")
import fitz 
import os
from unstructured.partition.pdf import partition_pdf
import logging
from src.helper_utils import load_config, CONFIG_PATH

config = load_config(CONFIG_PATH)
logger = logging.getLogger(__name__)

def extract_metadata(file_path):
    metadata = {
        'title': '', 'author': '', 'subject': '', 'creator': '', 'creationYear': ''
    }
    try:
        doc = fitz.open(file_path)
        raw_metadata = doc.metadata

        creation_date = raw_metadata.get('creationDate', '')
        year = ''
        if creation_date.startswith('D:') and len(creation_date) >= 6:
            year = creation_date[2:6]

        metadata.update({
            'title': raw_metadata.get('title', ''),
            'author': raw_metadata.get('author', ''),
            'subject': raw_metadata.get('subject', ''),
            'creator': raw_metadata.get('creator', ''),
            'creationYear': year
        })
        doc.close()
    except Exception as e:
        logger.error(f"   - Error extracting metadata from {os.path.basename(file_path)}: {e}")
    return metadata


def process_paper(file_path, summarize_chain, extraction_chain ):
    logger.info(f"-> Processing PDF: {os.path.basename(file_path)}")

    # extract metadata
    logger.info("   - Extracting metadata...")
    metadata = extract_metadata(file_path)
    metadata['filename'] = os.path.basename(file_path)

    # partition PDF
    logger.info("   - Parsing PDF content...")
    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=False,
        strategy=config["PARTITION_PDF_STRATEGY"], 
        chunking_strategy="by_title",
        max_characters=8000,
        combine_text_under_n_chars=1000,
        new_after_n_chars=1800,
    )

    texts = [chunk for chunk in chunks if "CompositeElement" in str(type(chunk))]
    all_chunks = texts
    if not all_chunks:
        logger.error(f"   - PDF text extraction failed or produced no content for '{os.path.basename(file_path)}'. Skipping content summarization.")
        return metadata

    # summarize chunks
    logger.info(f"   - Summarizing {len(all_chunks)} text chunks...")
    chunk_summaries = [summarize_chain.invoke({"element": chunk.text}) for chunk in all_chunks]

    # merge summaries into a single text
    combined_summaries = "\n\n---\n\n".join(chunk_summaries)

    # synthesize and extract from the combined summaries
    logger.info("   - Synthesizing and extracting final data...")
    extracted_summary_data = extraction_chain.invoke({"chunk_summaries": combined_summaries})

    standardized_extracted_summary_data = {k.lower(): v for k, v in extracted_summary_data.items()}
    final_result = {**metadata, **standardized_extracted_summary_data}

    return final_result
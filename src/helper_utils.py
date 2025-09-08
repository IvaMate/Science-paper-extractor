import fitz 
import os
from unstructured.partition.pdf import partition_pdf
from . import chain_utils, model_utils
import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def extract_metadata(file_path):
    """
    Extracts metadata from a single PDF file.
    Returns a dictionary of metadata.
    """
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
        print(f"   - Error extracting metadata from {os.path.basename(file_path)}: {e}")
    return metadata


def process_paper(file_path):
    """
    Processes a single PDF file:
    1. Extracts metadata.
    2. Partitions it into chunks (text and tables).
    3. Summarizes each chunk (Map step).
    4. Synthesizes summaries to extract key info (Reduce step).
    5. Combines metadata and summary results.
    """
    print(f"-> Processing PDF: {os.path.basename(file_path)}")

    # Extract Metadata
    print("   - Extracting metadata...")
    metadata = extract_metadata(file_path)
    metadata['filename'] = os.path.basename(file_path)

    # Partition PDF
    print("   - Parsing PDF content...")
    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=False,
        strategy="ocr_only",
        extract_image_block_types=[],
        chunking_strategy="by_title",
        max_characters=4000,
        combine_text_under_n_chars=1000,
        new_after_n_chars=3800,
    )

    texts = [chunk for chunk in chunks if "CompositeElement" in str(type(chunk))]
    all_chunks = texts
    if not all_chunks:
        print("   - No content chunks found. Skipping content summarization.")
        return metadata

    # Summarize each chunk concurrently
    print(f"   - Summarizing {len(all_chunks)} text chunks...")
    map_prompt = ChatPromptTemplate.from_template(chain_utils.map_prompt_text)
    summarize_chain = {"element": lambda x: x.text} | map_prompt | model_utils.model | StrOutputParser()
    chunk_summaries = summarize_chain.batch(all_chunks, {"max_concurrency": 5})
    # Combine all individual summaries into one document for the next step
    combined_summaries = "\n\n---\n\n".join(chunk_summaries)

    # Synthesize and extract from the combined summaries
    print("   - Synthesizing and extracting final data...")
    extraction_prompt = ChatPromptTemplate.from_template(chain_utils.extraction_prompt_text)
    extraction_chain = extraction_prompt | model_utils.model | JsonOutputParser()    
    extracted_summary_data = extraction_chain.invoke({"chunk_summaries": combined_summaries})

    # Standardize keys to lowercase
    standardized_extracted_summary_data = {k.lower(): v for k, v in extracted_summary_data.items()}

    # Combine metadata and extracted summary data
    final_result = {**metadata, **standardized_extracted_summary_data}

    return final_result
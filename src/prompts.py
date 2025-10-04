# prompt for summarizing tables and text
MAP_PROMPT_TEXT = """
You are an assistant tasked with summarizing tables and text.
Give a concise summary of the table or text chunk.

Respond only with the summary, no additional comment.
Do not start your message by saying "Here is a summary" or anything like that.
Just give the summary as it is.

Table or text chunk: {element}
"""

# prompt for extracting key data from paper summaries
EXTRACTION_PROMPT_TEXT = """
You are an expert analyst specializing in scientific research papers.
You have been provided with a series of summaries from different sections of a single research paper.
Your task is to synthesize this information and extract the following key points.
Respond with a JSON object containing the following keys: 'overall_summary', 'methodology', 'future_recommendations'.

- 'overall_summary': A comprehensive summary of the paper's purpose, key findings, and conclusions.
- 'methodology': A description of the methodology, techniques, and experiments used in the research.
- 'algorithms': Give only names of algorithms tested in the paper.
- 'data_pre_processing_methods': Give description on specific methods when pre-processing data in this research paper.
- 'results': A concise short description on results.
- 'conclusion': What is the main paper's conclusion and its contribution.
- 'dataset': Concise answer 'yes' if the dataset used is publicly available, 'no' if the dataset isn't available or not mentioned.
- 'future_recommendations': Any future work, open questions, or recommendations for further research mentioned in the paper.

If a particular piece of information is not present, return an empty string for that key.

Here are the summaries of the paper's sections:
{chunk_summaries}
"""

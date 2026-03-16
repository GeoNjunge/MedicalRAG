from docling.document_converter import DocumentConverter
from pathlib import Path
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
import re

converter = DocumentConverter()
embeddings = HuggingFaceEmbeddings(model_name='dmis-lab/biobert-base-cased-v1.1')

# Convert to markdown

# Clean the document

# Chunk the document

# embed if needed

def convert_to_markdown(file):
    doc = converter.convert(file).document
    result = doc.export_to_markdown()
    return result

def clean_document(splits):
    no_dashes = re.sub(r'-{2,}', "", splits)
    no_slashes = re.sub(r"\|", "", no_dashes)
    # no_unnecessary_space = re.sub(r" +", "", no_slashes)
    no_endline_annot = re.sub(r"\\n", "", no_slashes)
    return no_endline_annot

def chunk_docs(file):

    chunker = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80
    )

    chunks = chunker.create_documents([file])

    return chunks

def chunk_cleaner(splits):
    for split in splits:
        if "Header 2" in split.metadata and split.metadata.get("Header 2") == 'Comments' or '## Comments' in split.page_content:
            split.page_content = ""

        split.page_content = clean_document(split.page_content)

    return splits

path = Path("samplePmedReport.pdf")
md = convert_to_markdown(path)
splits = chunk_docs(md)
cleaned_splits = chunk_cleaner(splits)

final_text = "\n\n".join([chunk.page_content for chunk in cleaned_splits])

Path("doc.md").write_text(final_text)
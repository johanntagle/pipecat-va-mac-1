#!/usr/bin/env python3
"""
Process PDF files and store them in the RAG database.

Usage:
    python process_pdf_rag_documents.py <company_id> <file1.pdf> [file2.pdf ...]

Example:
    python process_pdf_rag_documents.py 1 docs/menu.pdf docs/faq.pdf
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re

from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client
import openai
import pypdf

load_dotenv(override=True)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

# Chunking parameters (based on PRD recommendations)
CHUNK_SIZE = 500  # tokens (approximate)
CHUNK_OVERLAP = 50  # tokens (approximate)
CHARS_PER_TOKEN = 4  # Rough estimate: 1 token ≈ 4 characters


def get_company_api_key(company_id: int) -> str:
    """Fetch the company's OpenAI API key from the database."""
    try:
        response = supabase.table("companies").select("openai_api_key").eq("id", company_id).execute()

        if not response.data or len(response.data) == 0:
            logger.error(f"Company with id {company_id} not found")
            sys.exit(1)

        return response.data[0]["openai_api_key"]
    except Exception as e:
        logger.error(f"Error fetching company API key: {e}")
        sys.exit(1)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks based on approximate token count.

    Args:
        text: The text to chunk
        chunk_size: Target chunk size in tokens (approximate)
        overlap: Number of overlapping tokens between chunks

    Returns:
        List of text chunks
    """
    # Convert token counts to character counts (rough estimate)
    chunk_chars = chunk_size * CHARS_PER_TOKEN
    overlap_chars = overlap * CHARS_PER_TOKEN

    # Split by paragraphs first to maintain semantic boundaries
    paragraphs = re.split(r'\n\s*\n', text)

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk size, save current chunk
        if len(current_chunk) + len(para) > chunk_chars and current_chunk:
            chunks.append(current_chunk.strip())

            # Start new chunk with overlap from previous chunk
            if len(current_chunk) > overlap_chars:
                current_chunk = current_chunk[-overlap_chars:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate_embedding(text: str, api_key: str) -> List[float]:
    """
    Generate embedding for text using OpenAI's text-embedding-3-small model.

    Args:
        text: The text to embed
        api_key: OpenAI API key

    Returns:
        List of 1536 floats representing the embedding
    """
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content
    """
    try:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        raise


def extract_pdf_metadata(file_path: str, text: str) -> Dict[str, Any]:
    """
    Extract metadata from PDF content.

    Args:
        file_path: Path to the PDF file
        text: Extracted text content

    Returns:
        Dictionary with metadata
    """
    metadata = {
        "file_name": Path(file_path).name,
        "file_path": file_path,
    }

    # Try to extract PDF metadata
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            pdf_info = pdf_reader.metadata

            if pdf_info:
                if pdf_info.title:
                    metadata["title"] = pdf_info.title
                if pdf_info.author:
                    metadata["author"] = pdf_info.author
                if pdf_info.subject:
                    metadata["subject"] = pdf_info.subject

            metadata["page_count"] = len(pdf_reader.pages)
    except Exception as e:
        logger.warning(f"Error extracting PDF metadata: {e}")

    # If no title found in metadata, try to extract from first line
    if "title" not in metadata and text:
        first_line = text.split('\n')[0].strip()
        if first_line:
            metadata["title"] = first_line[:100]  # Limit to 100 chars

    return metadata


def process_pdf_file(company_id: int, file_path: str, api_key: str) -> None:
    """
    Process a single PDF file and store it in the RAG database.

    Args:
        company_id: The company ID
        file_path: Path to the PDF file
        api_key: OpenAI API key for generating embeddings
    """
    logger.info(f"Processing file: {file_path}")

    # Extract text from PDF
    try:
        content = extract_pdf_text(file_path)
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {e}")
        return

    if not content.strip():
        logger.warning(f"File {file_path} has no extractable text, skipping")
        return

    # Extract metadata
    file_metadata = extract_pdf_metadata(file_path, content)
    file_size = os.path.getsize(file_path)

    # Create document record
    try:
        doc_response = supabase.table("documents").insert({
            "company_id": company_id,
            "file_name": Path(file_path).name,
            "storage_path": file_path,  # For now, store local path
            "file_size": file_size,
            "mime_type": "application/pdf"
        }).execute()

        if not doc_response.data:
            logger.error(f"Failed to create document record for {file_path}")
            return

        document_id = doc_response.data[0]["id"]
        logger.info(f"Created document record with ID: {document_id}")
    except Exception as e:
        logger.error(f"Error creating document record: {e}")
        return

    # Chunk the content
    chunks = chunk_text(content)
    logger.info(f"Split document into {len(chunks)} chunks")

    # Process each chunk
    for idx, chunk in enumerate(chunks):
        try:
            # Generate embedding
            logger.debug(f"Generating embedding for chunk {idx + 1}/{len(chunks)}")
            embedding = generate_embedding(chunk, api_key)

            # Prepare chunk metadata
            chunk_metadata = {
                **file_metadata,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "chunk_length": len(chunk)
            }

            # Insert chunk into database
            supabase.table("rag_chunks").insert({
                "document_id": document_id,
                "chunk_text": chunk,
                "chunk_index": idx,
                "embedding": embedding,
                "metadata": chunk_metadata
            }).execute()

            logger.debug(f"Stored chunk {idx + 1}/{len(chunks)}")
        except Exception as e:
            logger.error(f"Error processing chunk {idx}: {e}")
            continue

    logger.info(f"✓ Successfully processed {file_path} ({len(chunks)} chunks)")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process PDF files and store them in the RAG database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_pdf_rag_documents.py 1 docs/menu.pdf
  python process_pdf_rag_documents.py 1 docs/menu.pdf docs/faq.pdf docs/policies.pdf
        """
    )
    parser.add_argument(
        "company_id",
        type=int,
        help="Company ID to associate documents with"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="PDF files to process"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Chunk size in tokens (default: {CHUNK_SIZE})"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Chunk overlap in tokens (default: {CHUNK_OVERLAP})"
    )

    args = parser.parse_args()

    # Validate company exists and get API key
    logger.info(f"Loading configuration for company ID: {args.company_id}")
    api_key = get_company_api_key(args.company_id)
    logger.info("✓ Company configuration loaded")

    # Validate all files exist
    for file_path in args.files:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        if not file_path.endswith('.pdf'):
            logger.warning(f"File {file_path} is not a PDF file (.pdf)")

    # Process each file
    logger.info(f"Processing {len(args.files)} file(s)...")
    for file_path in args.files:
        process_pdf_file(args.company_id, file_path, api_key)

    logger.info("✓ All files processed successfully")


if __name__ == "__main__":
    main()

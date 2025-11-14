# RAG Document Processing

This document explains how to use the `process_rag_documents.py` script to process markdown files and store them in the RAG database for semantic search.

## Overview

The script processes markdown files by:
1. Reading the markdown content
2. Chunking the text into manageable pieces (~500 tokens with 50 token overlap)
3. Generating embeddings using OpenAI's `text-embedding-3-small` model (1536 dimensions)
4. Storing the chunks and embeddings in the `rag_chunks` table
5. Creating document records in the `documents` table

## Prerequisites

1. **Supabase running**: Make sure your local Supabase instance is running
   ```bash
   supabase start
   ```

2. **Company exists**: You need a valid company ID with an OpenAI API key configured
   ```bash
   # Check companies
   supabase db execute "SELECT id, name FROM companies"
   ```

3. **Dependencies installed**: The script requires the `openai` package
   ```bash
   cd server
   uv sync
   ```

## Usage

### Basic Usage

Process a single markdown file:
```bash
uv run process_rag_documents.py <company_id> <file.md>
```

Example:
```bash
uv run process_rag_documents.py 1 test_rag_sample.md
```

### Process Multiple Files

Process multiple markdown files at once:
```bash
uv run process_rag_documents.py <company_id> <file1.md> <file2.md> <file3.md>
```

Example:
```bash
uv run process_rag_documents.py 1 docs/menu.md docs/faq.md docs/policies.md
```

### Custom Chunking Parameters

You can customize the chunk size and overlap:
```bash
uv run process_rag_documents.py 1 menu.md --chunk-size 1000 --chunk-overlap 100
```

Parameters:
- `--chunk-size`: Target chunk size in tokens (default: 500)
- `--chunk-overlap`: Number of overlapping tokens between chunks (default: 50)

## How It Works

### 1. Document Creation

The script creates a record in the `documents` table:
```sql
INSERT INTO documents (company_id, file_name, storage_path, file_size, mime_type)
VALUES (1, 'menu.md', '/path/to/menu.md', 1234, 'text/markdown');
```

### 2. Text Chunking

The text is split into chunks using paragraph boundaries to maintain semantic coherence:
- Default chunk size: ~500 tokens (≈2000 characters)
- Default overlap: ~50 tokens (≈200 characters)
- Chunks respect paragraph boundaries when possible

### 3. Embedding Generation

For each chunk, the script:
1. Calls OpenAI's API with the company's API key
2. Uses the `text-embedding-3-small` model
3. Receives a 1536-dimensional vector

### 4. Storage

Each chunk is stored in the `rag_chunks` table:
```sql
INSERT INTO rag_chunks (document_id, chunk_text, chunk_index, embedding, metadata)
VALUES (1, 'chunk text...', 0, '[0.123, -0.456, ...]', '{"file_name": "menu.md", ...}');
```

## Metadata

Each chunk includes metadata:
- `file_name`: Name of the source file
- `file_path`: Path to the source file
- `title`: First heading from the markdown (if present)
- `chunk_index`: Position of this chunk in the document
- `total_chunks`: Total number of chunks in the document
- `chunk_length`: Character count of this chunk

## Verification

After processing, you can verify the data:

### Check Documents
```bash
supabase db execute "SELECT * FROM documents WHERE company_id = 1"
```

### Check RAG Chunks
```bash
supabase db execute "SELECT id, document_id, chunk_index, LEFT(chunk_text, 50) as preview FROM rag_chunks ORDER BY document_id, chunk_index"
```

### Count Chunks per Document
```bash
supabase db execute "SELECT document_id, COUNT(*) as chunk_count FROM rag_chunks GROUP BY document_id"
```

## Testing the Script

A sample markdown file is provided for testing:

```bash
# Process the test file
uv run process_rag_documents.py 1 test_rag_sample.md

# Verify it was processed
supabase db execute "SELECT COUNT(*) FROM rag_chunks WHERE document_id IN (SELECT id FROM documents WHERE file_name = 'test_rag_sample.md')"
```

## Troubleshooting

### Error: "Company with id X not found"
- Make sure the company exists in the database
- Check: `supabase db execute "SELECT id, name FROM companies"`

### Error: "Error generating embedding"
- Verify the company has a valid OpenAI API key
- Check: `supabase db execute "SELECT id, name, openai_api_key FROM companies WHERE id = 1"`
- Test the API key manually

### Error: "File not found"
- Use absolute paths or paths relative to where you run the script
- Example: `uv run process_rag_documents.py 1 ../docs/menu.md`

### No chunks created
- Check if the file is empty or has very little content
- Review the logs for any errors during processing

## Next Steps

After processing documents, you can:

1. **Search using vector similarity** (see `docs/SQL-HELPERS.md` for examples)
2. **Integrate with the voice agent** to provide context-aware responses
3. **Build a search UI** in the management app (see `docs/REACT-APP-GUIDE.md`)

## Related Documentation

- `docs/REACT-APP-GUIDE.md` - Building the RAG search UI
- `docs/SQL-HELPERS.md` - Vector search queries
- `supabase/migrations/20250114000000_initial_schema.sql` - Database schema


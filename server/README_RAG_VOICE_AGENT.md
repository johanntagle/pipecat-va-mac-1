# RAG-Enabled Voice Agent (03_rag.py)

This document explains how the RAG (Retrieval-Augmented Generation) system is integrated into the voice agent to provide context-aware responses based on company documents.

## Overview

The `03_rag.py` voice agent extends `02_db_backed.py` with RAG capabilities, allowing the agent to:
1. Automatically search the company's knowledge base when users ask questions
2. Augment LLM prompts with relevant document chunks
3. Provide accurate, company-specific answers based on uploaded documents

## How It Works

### 1. RAG Pipeline Integration

The RAG system is integrated into the Pipecat pipeline using a custom `RAGProcessor`:

```
User Speech → STT → Context Aggregator → RAGProcessor → LLM → TTS → Audio Output
```

The `RAGProcessor` intercepts user messages before they reach the LLM and:
- Generates an embedding for the user's question
- Searches the vector database for similar document chunks
- Augments the user message with relevant context

### 2. Vector Similarity Search

When a user asks a question:
1. The question text is converted to a 1536-dimensional embedding using OpenAI's `text-embedding-3-small` model
2. The embedding is compared against all document chunks in the database using cosine similarity
3. The top N most similar chunks (default: 3) above a threshold (default: 0.7) are retrieved
4. These chunks are formatted and prepended to the user's question

### 3. System Prompt Enhancement

The agent's system prompt is automatically enhanced with:
- **RAG Instructions**: Tells the LLM how to use the provided context
- **Voice Output Instructions**: Ensures responses are optimized for speech synthesis

## Configuration

### RAG Settings

Located in `03_rag.py`:

```python
RAG_CONFIG = {
    "match_threshold": 0.7,  # Minimum similarity score (0-1)
    "match_count": 3,        # Number of chunks to retrieve
    "embedding_model": "text-embedding-3-small",
}
```

**Adjusting these values:**
- `match_threshold`: Lower = more results but less relevant (0.5-0.8 recommended)
- `match_count`: More chunks = more context but longer prompts (2-5 recommended)
- `embedding_model`: Must match the model used in `process_rag_documents.py`

## Usage

### 1. Process Documents First

Before running the RAG-enabled agent, you must process documents into the RAG database:

```bash
# Process a markdown file for company ID 1
uv run process_rag_documents.py 1 path/to/document.md
```

See `README_RAG_PROCESSING.md` for details.

### 2. Run the RAG-Enabled Agent

```bash
# Start the agent for company ID 1
uv run 03_rag.py 1

# With custom host/port
uv run 03_rag.py 1 --host 0.0.0.0 --port 8000
```

### 3. Test RAG Functionality

Ask questions related to your uploaded documents:
- "What are your business hours?"
- "Tell me about your services"
- "What's on the menu?"

The agent will automatically search the knowledge base and provide answers based on the documents.

## Example Conversation Flow

**User**: "What are your business hours?"

**Behind the scenes:**
1. User's speech is transcribed: "What are your business hours?"
2. RAGProcessor generates embedding for the question
3. Vector search finds relevant chunks (e.g., from "business_info.md")
4. Context is added to the prompt:
   ```
   Here is relevant information from the company's knowledge base:
   
   [Source 1: business_info.md (relevance: 0.89)]
   We are open Monday-Friday 9am-5pm, Saturday 10am-3pm, closed Sunday.
   
   ---
   
   User question: What are your business hours?
   ```
5. LLM generates response based on the context
6. Response is spoken to the user

## Monitoring RAG Performance

### Log Messages

The agent logs RAG activity:
- `DEBUG`: "Generating embedding for query: ..."
- `INFO`: "Found N relevant chunks for query"
- `INFO`: "Augmented user message with N RAG chunks"
- `DEBUG`: "No relevant chunks found"

### Checking What Was Retrieved

To see what context was provided to the LLM, check the logs for "Augmented user message" entries.

## Troubleshooting

### No RAG Results

**Symptom**: Agent doesn't use document information

**Possible causes:**
1. No documents processed for this company
   - Check: `supabase db execute "SELECT COUNT(*) FROM rag_chunks WHERE document_id IN (SELECT id FROM documents WHERE company_id = 1)"`
2. Similarity threshold too high
   - Try lowering `match_threshold` to 0.5
3. Question doesn't match document content
   - Try rephrasing or check document content

### RAG Search Errors

**Symptom**: Errors in logs about RAG search

**Possible causes:**
1. Missing `search_rag_chunks` function
   - Run migration: `supabase db reset` or apply `20250114000002_add_search_rag_chunks_function.sql`
2. Invalid OpenAI API key
   - Check company configuration in database
3. Embedding model mismatch
   - Ensure same model used in processing and search

### Poor Quality Answers

**Symptom**: Agent provides irrelevant or incorrect information

**Possible causes:**
1. Retrieved chunks not relevant
   - Lower `match_threshold` or increase `match_count`
2. Document chunks too small/large
   - Adjust chunking parameters in `process_rag_documents.py`
3. System prompt needs tuning
   - Modify `RAG_SYSTEM_INSTRUCTIONS` in `03_rag.py`

## Advanced Customization

### Custom RAG Processor

You can modify the `RAGProcessor` class to:
- Filter chunks by metadata (e.g., only recent documents)
- Implement caching to avoid repeated searches
- Add conversation history to improve context

### Custom RAG Instructions Per Company

Each company can have custom RAG system instructions stored in the database:

```sql
-- Set custom RAG instructions for a company
UPDATE companies
SET rag_system_instructions = 'Your custom instructions here...'
WHERE id = 1;
```

If `rag_system_instructions` is NULL, the default instructions from `RAG_SYSTEM_INSTRUCTIONS` constant will be used.

### Dynamic RAG Configuration

To adjust RAG settings per company, add columns to the `companies` table:
```sql
ALTER TABLE companies ADD COLUMN rag_threshold FLOAT DEFAULT 0.7;
ALTER TABLE companies ADD COLUMN rag_chunk_count INT DEFAULT 3;
```

Then update `load_company_config()` to load these values.

## Related Documentation

- `README_RAG_PROCESSING.md` - How to process documents
- `docs/REACT-APP-GUIDE.md` - Building a document management UI
- `docs/SQL-HELPERS.md` - Database queries for RAG data
- `supabase/migrations/20250114000002_add_search_rag_chunks_function.sql` - Vector search function

## Performance Considerations

- **Embedding Generation**: Each user message requires an OpenAI API call (~100ms)
- **Vector Search**: Fast with HNSW index, typically <50ms
- **Context Size**: More chunks = larger prompts = higher LLM costs
- **Caching**: Consider caching embeddings for common questions

## Next Steps

1. Process your company documents using `process_rag_documents.py`
2. Test the RAG agent with questions about your documents
3. Adjust `RAG_CONFIG` based on performance
4. Monitor logs to ensure RAG is working as expected
5. Build a document management UI (see `REACT-APP-GUIDE.md`)


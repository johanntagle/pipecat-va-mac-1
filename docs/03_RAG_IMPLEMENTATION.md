# 03_rag.py Implementation Summary

This document summarizes the RAG (Retrieval-Augmented Generation) implementation in `03_rag.py`.

## Changes Made

### 1. New File: `server/03_rag.py`

Cloned from `02_db_backed.py` and enhanced with RAG capabilities.

#### Key Additions:

**Imports:**
- `openai` - For generating embeddings
- `List` from typing - For type hints
- `Frame`, `TextFrame`, `LLMMessagesFrame` from pipecat.frames.frames
- `FrameDirection`, `FrameProcessor` from pipecat.processors.frame_processor

**Constants:**
```python
VOICE_OUTPUT_INSTRUCTIONS = """
Do not format your answer in any markdown or include "asterisk" or "star" or any symbols...
When giving phone numbers, give the numbers to be read e.g. ZERO NINE ONE SEVEN, etc.
When giving time, give the time to be read e.g. TEN THIRTY, etc.
"""

RAG_SYSTEM_INSTRUCTIONS = """
You have access to a knowledge base of company documents.
When answering questions, relevant information from these documents will be provided to you as context...
"""

RAG_CONFIG = {
    "match_threshold": 0.7,  # Minimum similarity score (0-1)
    "match_count": 3,        # Number of chunks to retrieve
    "embedding_model": "text-embedding-3-small",
}
```

**New Classes:**
- `RAGProcessor(FrameProcessor)` - Intercepts user messages and augments them with RAG context

**New Functions:**
- `generate_embedding(text, api_key)` - Generates OpenAI embeddings
- `search_rag_chunks(query, company_id, api_key)` - Searches vector database for relevant chunks
- `format_rag_context(chunks)` - Formats retrieved chunks for LLM context

**Modified Functions:**
- `run_bot()` - Now accepts `company_id` parameter and includes RAG processor in pipeline
- `load_company_config()` - Stores `company_id` in global config

**Pipeline Changes:**
```python
pipeline = Pipeline([
    transport.input(),
    stt,
    rtvi,
    context_aggregator.user(),
    rag_processor,  # NEW: Adds RAG context before LLM
    llm,
    text_filter,
    tts,
    transport.output(),
    context_aggregator.assistant(),
])
```

### 2. New Migration: `supabase/migrations/20250114000002_add_search_rag_chunks_function.sql`

Creates the `search_rag_chunks` PostgreSQL function for vector similarity search:
- Uses cosine distance operator `<=>` for similarity
- Filters by company_id
- Returns chunks above similarity threshold
- Orders by relevance

### 3. New Migration: `supabase/migrations/20250114000003_add_rag_system_instructions_to_companies.sql`

Adds `rag_system_instructions` column to the `companies` table:
- Allows each company to have custom RAG instructions
- If NULL, the default `RAG_SYSTEM_INSTRUCTIONS` constant is used
- Provides flexibility for different company needs

### 4. New Documentation: `server/README_RAG_VOICE_AGENT.md`

Comprehensive guide covering:
- How RAG integration works
- Configuration options
- Usage instructions
- Example conversation flow
- Troubleshooting guide
- Performance considerations

### 5. Updated Documentation: `docs/COMPANY-CONFIG-INTEGRATION.md`

- Added reference to `03_rag.py`
- Updated server startup examples to include both `02_db_backed.py` and `03_rag.py`

## How RAG Works in the Voice Agent

### Flow Diagram:
```
User speaks → STT → User message
                        ↓
                   RAGProcessor
                        ↓
              Generate embedding
                        ↓
              Search vector DB
                        ↓
              Format context
                        ↓
         Augment user message
                        ↓
                      LLM
                        ↓
                   TTS → Audio
```

### Example:

**User says:** "What are your business hours?"

**RAGProcessor:**
1. Generates embedding for "What are your business hours?"
2. Searches `rag_chunks` table for similar embeddings
3. Finds relevant chunks (e.g., from business_info.md)
4. Formats context:
   ```
   Here is relevant information from the company's knowledge base:
   
   [Source 1: business_info.md (relevance: 0.89)]
   We are open Monday-Friday 9am-5pm, Saturday 10am-3pm, closed Sunday.
   
   ---
   
   User question: What are your business hours?
   ```
5. Sends augmented message to LLM

**LLM responds:** "We're open Monday through Friday from 9 AM to 5 PM, Saturday from 10 AM to 3 PM, and we're closed on Sundays."

## Custom RAG Instructions Per Company

Each company can have custom RAG system instructions:

```sql
-- Set custom RAG instructions for company 1
UPDATE companies
SET rag_system_instructions = 'You have access to our product catalog. When answering questions about products, always mention the product code and price from the provided context.'
WHERE id = 1;

-- Use default instructions (set to NULL)
UPDATE companies
SET rag_system_instructions = NULL
WHERE id = 2;
```

The system will:
- Use the company's custom `rag_system_instructions` if set
- Fall back to the default `RAG_SYSTEM_INSTRUCTIONS` constant if NULL
- Log which instructions are being used at startup

## Testing Instructions

### 1. Apply the Migrations

```bash
# Reset database to apply new migrations
supabase db reset

# Or apply specific migrations
supabase migration up
```

### 2. Process Documents

```bash
cd server
uv run process_rag_documents.py 1 path/to/document.md
```

### 3. Start RAG-Enabled Agent

```bash
cd server
uv run 03_rag.py 1
```

### 4. Test RAG Functionality

Connect to the agent and ask questions related to your uploaded documents. Check logs for:
- "Generating embedding for query: ..."
- "Found N relevant chunks for query"
- "Augmented user message with N RAG chunks"

## Configuration Tuning

Adjust `RAG_CONFIG` in `03_rag.py`:

- **Lower threshold (0.5-0.6)**: More results, potentially less relevant
- **Higher threshold (0.8-0.9)**: Fewer results, more relevant
- **More chunks (4-5)**: More context, longer prompts, higher costs
- **Fewer chunks (1-2)**: Less context, shorter prompts, lower costs

## Related Files

- `server/03_rag.py` - Main RAG-enabled voice agent
- `server/process_rag_documents.py` - Document processing script
- `server/README_RAG_VOICE_AGENT.md` - Detailed RAG documentation
- `server/README_RAG_PROCESSING.md` - Document processing guide
- `supabase/migrations/20250114000002_add_search_rag_chunks_function.sql` - Vector search function
- `docs/COMPANY-CONFIG-INTEGRATION.md` - Company configuration guide


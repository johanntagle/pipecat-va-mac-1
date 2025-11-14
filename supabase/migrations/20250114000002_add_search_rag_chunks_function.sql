-- Create RPC function for vector similarity search on RAG chunks
CREATE OR REPLACE FUNCTION search_rag_chunks(
  query_embedding vector(1536),
  company_id bigint,
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  document_id bigint,
  chunk_text text,
  similarity float,
  metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    rc.id,
    rc.document_id,
    rc.chunk_text,
    1 - (rc.embedding <=> query_embedding) as similarity,
    rc.metadata
  FROM rag_chunks rc
  JOIN documents d ON rc.document_id = d.id
  WHERE d.company_id = search_rag_chunks.company_id
    AND 1 - (rc.embedding <=> query_embedding) > match_threshold
  ORDER BY rc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Add comment to document the function
COMMENT ON FUNCTION search_rag_chunks IS 'Search for similar RAG chunks using vector cosine similarity. Returns chunks with similarity score above threshold, ordered by relevance.';


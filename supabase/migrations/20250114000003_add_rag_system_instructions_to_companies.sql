-- Add rag_system_instructions column to companies table
-- This allows each company to have custom RAG instructions for their voice agent

ALTER TABLE companies 
ADD COLUMN rag_system_instructions TEXT;

-- Add comment to document the column
COMMENT ON COLUMN companies.rag_system_instructions IS 'Custom instructions for how the LLM should use RAG context. If NULL, a default instruction set will be used.';


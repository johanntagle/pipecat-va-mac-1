-- Add llm_model column to companies table
ALTER TABLE companies 
ADD COLUMN llm_model TEXT NOT NULL DEFAULT 'gpt-4o-mini';

-- Add comment to document the column
COMMENT ON COLUMN companies.llm_model IS 'The LLM model to use for this company (e.g., gpt-4o-mini, gpt-4o, gpt-3.5-turbo)';


# Migration: Add LLM Model to Companies

## Overview
Added `llm_model` column to the `companies` table to allow each company to specify which OpenAI model they want to use for their voice agent.

## Migration Details

**File:** `supabase/migrations/20250114000001_add_llm_model_to_companies.sql`

**Changes:**
- Added `llm_model` column to `companies` table
- Type: `TEXT NOT NULL`
- Default value: `'gpt-4o-mini'`
- Includes column comment for documentation

## SQL
```sql
ALTER TABLE companies 
ADD COLUMN llm_model TEXT NOT NULL DEFAULT 'gpt-4o-mini';

COMMENT ON COLUMN companies.llm_model IS 'The LLM model to use for this company (e.g., gpt-4o-mini, gpt-4o, gpt-3.5-turbo)';
```

## Updated Schema

### Companies Table
| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | bigint | auto | Primary key |
| name | text | - | Company name |
| openai_api_key | text | - | OpenAI API key |
| system_prompt | text | - | System prompt for the agent |
| **llm_model** | **text** | **'gpt-4o-mini'** | **LLM model to use** |
| created_at | timestamptz | now() | Creation timestamp |
| updated_at | timestamptz | now() | Last update timestamp |

## Supported Models

Common OpenAI models that can be used:
- `gpt-4o` - Latest GPT-4 Optimized
- `gpt-4o-mini` - Faster, cost-effective GPT-4 (default)
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - GPT-3.5 Turbo

## Updated Seed Data

The seed data now includes different models for each company:
- **Acme Corporation**: `gpt-4o-mini`
- **TechStart Inc**: `gpt-4o`
- **Global Services Ltd**: `gpt-3.5-turbo`

## Impact on Application

### Backend Changes Needed
When making API calls to OpenAI, use the company's `llm_model` field:

```python
# Example Python code
company = get_company(company_id)
response = openai.ChatCompletion.create(
    model=company.llm_model,  # Use company's model
    messages=[
        {"role": "system", "content": company.system_prompt},
        {"role": "user", "content": user_message}
    ]
)
```

### Frontend Changes Needed

#### Company Form
Add a dropdown/select field for LLM model:

```typescript
// Example React component
<select name="llm_model" defaultValue="gpt-4o-mini">
  <option value="gpt-4o">GPT-4 Optimized</option>
  <option value="gpt-4o-mini">GPT-4 Optimized Mini (Recommended)</option>
  <option value="gpt-4-turbo">GPT-4 Turbo</option>
  <option value="gpt-4">GPT-4</option>
  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
</select>
```

#### TypeScript Types
Update the Company type:

```typescript
interface Company {
  id: number;
  name: string;
  openai_api_key: string;
  system_prompt: string;
  llm_model: string;  // NEW
  created_at: string;
  updated_at: string;
}
```

## Migration Status

- ✅ Migration file created
- ✅ Migration applied to local database
- ✅ Seed data updated
- ✅ Documentation updated (PRD, SETUP)
- ⏳ Frontend implementation pending
- ⏳ Backend integration pending

## Testing

### Verify Migration
```sql
-- Check column exists
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'companies' AND column_name = 'llm_model';

-- Check default value works
INSERT INTO companies (name, openai_api_key, system_prompt)
VALUES ('Test Co', 'sk-test', 'Test prompt')
RETURNING llm_model;
-- Should return: 'gpt-4o-mini'
```

### Test Different Models
```sql
-- Insert companies with different models
INSERT INTO companies (name, openai_api_key, system_prompt, llm_model)
VALUES 
  ('Fast Co', 'sk-test', 'Fast responses', 'gpt-3.5-turbo'),
  ('Premium Co', 'sk-test', 'Best quality', 'gpt-4o');

-- Verify
SELECT name, llm_model FROM companies;
```

## Rollback

If needed, rollback with:
```sql
ALTER TABLE companies DROP COLUMN llm_model;
```

## Next Steps

1. ✅ Migration applied
2. ✅ Seed data updated
3. ✅ Documentation updated
4. 🔲 Update TypeScript types: `npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts`
5. 🔲 Add LLM model dropdown to company form in UI
6. 🔲 Update backend to use company's `llm_model` when making OpenAI API calls
7. 🔲 Add validation for supported model names
8. 🔲 Consider adding model pricing/limits information in UI

## Notes

- The default model (`gpt-4o-mini`) is a good balance of performance and cost
- Companies can be updated to use different models at any time
- The model selection affects both cost and response quality
- Consider adding model descriptions in the UI to help users choose

---

**Migration Date:** 2025-01-14  
**Applied:** Yes  
**Status:** Complete


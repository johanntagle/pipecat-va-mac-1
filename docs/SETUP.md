# Setup Guide: Call Management & RAG System

## Prerequisites

- Node.js 18+ and npm/pnpm
- Supabase CLI installed (`npm install -g supabase`)
- Supabase account (for production) or local Supabase (for development)

## Local Development Setup

### 1. Start Supabase Locally

```bash
# From the project root
cd /Users/johanntagle/LEARN/macos-local-voice-agents

# Start Supabase (this will run migrations automatically)
supabase start
```

This will:
- Start PostgreSQL database on port 54322
- Start Supabase Studio on http://localhost:54323
- Run the migration in `supabase/migrations/20250114000000_initial_schema.sql`
- Run the seed data in `supabase/seed.sql`

### 2. Verify Database Setup

Open Supabase Studio at http://localhost:54323 and check:

- **Tables**: You should see 6 tables:
  - `companies`
  - `calls`
  - `call_details`
  - `appointments`
  - `documents`
  - `rag_chunks`

- **Storage**: You should see a bucket named `company-documents`

- **Sample Data**: Run this query in the SQL Editor:
  ```sql
  SELECT 
    c.name as company,
    COUNT(DISTINCT ca.id) as total_calls,
    COUNT(DISTINCT a.id) as total_appointments
  FROM companies c
  LEFT JOIN calls ca ON c.id = ca.company_id
  LEFT JOIN appointments a ON c.id = a.company_id
  GROUP BY c.id, c.name;
  ```

### 3. Get Your Supabase Credentials

After running `supabase start`, you'll see output like:

```
API URL: http://127.0.0.1:54321
DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
Studio URL: http://127.0.0.1:54323
anon key: eyJhbGc...
service_role key: eyJhbGc...
```

Save these for your React app configuration.

### 4. Create React App Environment File

Create `mgmt-ui/.env.local`:

```env
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_ANON_KEY=<your-anon-key-from-supabase-start>
```

**Note:** The management UI is in `/mgmt-ui`, separate from the voice agent client in `/client`.

## Production Setup (Supabase Cloud)

### 1. Create a New Supabase Project

Go to https://supabase.com/dashboard and create a new project.

### 2. Link Your Local Project

```bash
# Login to Supabase
supabase login

# Link to your remote project
supabase link --project-ref <your-project-ref>
```

### 3. Push Migration to Production

```bash
# Push the migration
supabase db push

# Or use the Supabase dashboard SQL Editor to run the migration manually
```

### 4. Enable PGvector Extension

In your Supabase project dashboard:
1. Go to Database → Extensions
2. Search for "vector"
3. Enable the `vector` extension

### 5. Create Storage Bucket

In your Supabase project dashboard:
1. Go to Storage
2. Create a new bucket named `company-documents`
3. Set it to **Private** (not public)

### 6. Update Production Environment Variables

Update your production `.env`:

```env
VITE_SUPABASE_URL=https://<your-project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-production-anon-key>
```

## Database Schema Overview

### Tables

1. **companies** - Company configurations
   - Stores OpenAI API keys, system prompts, and LLM model selection
   - Fields: id, name, openai_api_key, system_prompt, llm_model, created_at, updated_at
   - Parent table for calls, appointments, documents

2. **calls** - Call sessions
   - Tracks start/end time and summary
   - Links to company

3. **call_details** - Conversation logs
   - Turn-by-turn conversation
   - Speaker: 'agent' or 'caller'
   - Millisecond-precision timestamps

4. **appointments** - Scheduled appointments
   - Links to company and call
   - Stores caller information

5. **documents** - Knowledge base files
   - Links to Supabase Storage
   - Metadata: filename, size, mime type

6. **rag_chunks** - Vector embeddings
   - 1536-dimension vectors (OpenAI)
   - HNSW index for fast similarity search
   - Metadata for context

### Key Features

- **Row Level Security (RLS)**: Enabled on all tables (currently permissive for development)
- **Indexes**: Optimized for common queries
- **Triggers**: Auto-update `updated_at` timestamps
- **Cascade Deletes**: Deleting a company removes all related data
- **Vector Search**: HNSW index for fast similarity search

## Testing the Setup

### 1. Test Database Connection

```sql
-- In Supabase Studio SQL Editor
SELECT * FROM companies;
```

You should see 3 sample companies.

### 2. Test Relationships

```sql
-- Get calls with company names
SELECT 
  c.id,
  c.start_time,
  c.end_time,
  co.name as company_name,
  c.call_summary
FROM calls c
JOIN companies co ON c.company_id = co.id
ORDER BY c.start_time DESC;
```

### 3. Test Vector Extension

```sql
-- Verify vector extension is working
SELECT vector_dims('[1,2,3]'::vector);
-- Should return: 3
```

## Common Issues

### Issue: Migration fails with "extension vector does not exist"

**Solution**: Enable the vector extension manually:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: Storage bucket not found

**Solution**: Create the bucket manually in Supabase Studio:
- Go to Storage → New Bucket
- Name: `company-documents`
- Public: No

### Issue: RLS policies blocking queries

**Solution**: For development, the migration creates permissive policies. In production, update policies based on your auth requirements.

## Next Steps

1. ✅ Database setup complete
2. 📖 Read the [PRD](./PRD-call-management-app.md) for feature details
3. 🚀 Start building the React app (see Phase 1 in PRD)
4. 🧪 Test with sample data from seed.sql

## Useful Commands

```bash
# Reset database (WARNING: deletes all data)
supabase db reset

# Create a new migration
supabase migration new <migration_name>

# Check migration status
supabase migration list

# Stop Supabase
supabase stop

# View logs
supabase logs
```

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PGvector Documentation](https://github.com/pgvector/pgvector)
- [React + Supabase Guide](https://supabase.com/docs/guides/getting-started/quickstarts/reactjs)


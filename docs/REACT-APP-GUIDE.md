# React App Development Guide

## Project Structure

**Note:** This management UI is in the `/mgmt-ui` directory, separate from the voice agent client in `/client`.

```
mgmt-ui/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── layout/         # Layout components (Header, Sidebar, etc.)
│   │   ├── companies/      # Company-related components
│   │   ├── calls/          # Call-related components
│   │   ├── appointments/   # Appointment components
│   │   ├── documents/      # Document management components
│   │   └── rag/            # RAG search components
│   ├── pages/              # Page components (routes)
│   │   ├── Home.tsx
│   │   ├── Companies.tsx
│   │   ├── CompanyDetail.tsx
│   │   ├── Calls.tsx
│   │   ├── CallDetail.tsx
│   │   ├── Appointments.tsx
│   │   ├── Documents.tsx
│   │   └── RAGSearch.tsx
│   ├── lib/                # Utilities and configurations
│   │   ├── supabase.ts     # Supabase client setup
│   │   └── types.ts        # TypeScript types
│   ├── hooks/              # Custom React hooks
│   │   ├── useCompanies.ts
│   │   ├── useCalls.ts
│   │   └── useDocuments.ts
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── .env.local              # Environment variables
└── package.json
```

## Initial Setup

### 1. Create Vite + React + TypeScript Project

```bash
# From project root
mkdir mgmt-ui
cd mgmt-ui
npm create vite@latest . -- --template react-ts
npm install
```

### 2. Install Dependencies

```bash
# Supabase client
npm install @supabase/supabase-js

# Routing
npm install react-router-dom

# UI Framework (choose one)
npm install tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Or use a component library
npm install @headlessui/react @heroicons/react

# Data fetching
npm install @tanstack/react-query

# Form handling
npm install react-hook-form zod @hookform/resolvers

# Date handling
npm install date-fns

# File upload
npm install react-dropzone
```

### 3. Configure Supabase Client

Create `mgmt-ui/src/lib/supabase.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'
import { Database } from './types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)
```

### 4. Generate TypeScript Types

```bash
# From project root
npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts
```

## Core Patterns

### 1. Data Fetching with React Query

```typescript
// hooks/useCompanies.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'

export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('companies')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) throw error
      return data
    }
  })
}

export function useCreateCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (company: NewCompany) => {
      const { data, error } = await supabase
        .from('companies')
        .insert([company])
        .select()
        .single()
      
      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    }
  })
}
```

### 2. Fetching Related Data

```typescript
// Get call with company info and conversation
export function useCallDetail(callId: number) {
  return useQuery({
    queryKey: ['calls', callId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('calls')
        .select(`
          *,
          company:companies(*),
          call_details(*),
          appointments(*)
        `)
        .eq('id', callId)
        .single()
      
      if (error) throw error
      return data
    }
  })
}
```

### 3. File Upload to Supabase Storage

```typescript
export async function uploadDocument(
  companyId: number,
  file: File
): Promise<string> {
  const fileName = `${Date.now()}_${file.name}`
  const filePath = `${companyId}/${fileName}`
  
  const { error: uploadError } = await supabase.storage
    .from('company-documents')
    .upload(filePath, file)
  
  if (uploadError) throw uploadError
  
  // Create document record
  const { data, error } = await supabase
    .from('documents')
    .insert([{
      company_id: companyId,
      file_name: file.name,
      storage_path: filePath,
      file_size: file.size,
      mime_type: file.type
    }])
    .select()
    .single()
  
  if (error) throw error
  return data.id
}
```

### 4. Vector Search (RAG)

```typescript
export async function searchDocuments(
  companyId: number,
  query: string,
  limit: number = 5
) {
  // First, generate embedding for the query (call OpenAI API)
  const embedding = await generateEmbedding(query)
  
  // Then search using vector similarity
  const { data, error } = await supabase.rpc('search_rag_chunks', {
    query_embedding: embedding,
    company_id: companyId,
    match_threshold: 0.7,
    match_count: limit
  })
  
  if (error) throw error
  return data
}
```

You'll need to create this RPC function in Supabase:

```sql
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
```

## Component Examples

### Company List Component

```typescript
// components/companies/CompanyList.tsx
import { useCompanies } from '@/hooks/useCompanies'

export function CompanyList() {
  const { data: companies, isLoading, error } = useCompanies()
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div className="space-y-4">
      {companies?.map(company => (
        <div key={company.id} className="border p-4 rounded">
          <h3 className="font-bold">{company.name}</h3>
          <p className="text-sm text-gray-600">
            Created: {new Date(company.created_at).toLocaleDateString()}
          </p>
        </div>
      ))}
    </div>
  )
}
```

### Conversation View Component

```typescript
// components/calls/ConversationView.tsx
interface ConversationViewProps {
  callDetails: CallDetail[]
}

export function ConversationView({ callDetails }: ConversationViewProps) {
  return (
    <div className="space-y-4">
      {callDetails.map(detail => (
        <div
          key={detail.id}
          className={`flex ${
            detail.speaker === 'agent' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-md p-3 rounded-lg ${
              detail.speaker === 'agent'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200'
            }`}
          >
            <div className="text-xs opacity-75 mb-1">
              {detail.speaker.toUpperCase()} •{' '}
              {new Date(detail.timestamp).toLocaleTimeString()}
            </div>
            <div>{detail.message}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
```

## Best Practices

1. **Type Safety**: Always use generated TypeScript types from Supabase
2. **Error Handling**: Use try-catch and display user-friendly error messages
3. **Loading States**: Show skeletons or spinners during data fetching
4. **Optimistic Updates**: Update UI immediately, rollback on error
5. **Pagination**: Implement pagination for large datasets
6. **Debouncing**: Debounce search inputs to reduce API calls
7. **Caching**: Use React Query's caching effectively

## Testing Strategy

1. **Unit Tests**: Test hooks and utility functions
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test critical user flows (Playwright/Cypress)

## Performance Optimization

1. **Code Splitting**: Use React.lazy() for route-based splitting
2. **Memoization**: Use useMemo/useCallback appropriately
3. **Virtual Lists**: For large lists (react-window)
4. **Image Optimization**: Lazy load images
5. **Bundle Analysis**: Use vite-bundle-visualizer

## Deployment

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

Deploy to:
- Vercel (recommended for Vite)
- Netlify
- Cloudflare Pages
- Your own server

## Next Steps

1. Set up the basic layout and routing
2. Implement Companies CRUD
3. Add Calls management
4. Build conversation view
5. Implement document upload
6. Add RAG search functionality


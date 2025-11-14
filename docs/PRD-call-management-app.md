# Product Requirements Document: Call Management & RAG System

## 1. Overview

### 1.1 Product Name
**Call Management & RAG System** - A multi-tenant application for managing voice agent calls, appointments, and document-based knowledge retrieval.

### 1.2 Purpose
Enable companies to manage their AI voice agent infrastructure including:
- Custom OpenAI configurations per company
- Call logging and conversation tracking
- Appointment scheduling from calls
- Document management with RAG (Retrieval Augmented Generation) capabilities

### 1.3 Target Users
- Company administrators managing voice agent configurations
- Operations teams monitoring calls and appointments
- Support teams reviewing conversation logs

## 2. Technical Stack

### 2.1 Frontend
- **Framework**: React 18+ with Vite
- **Language**: TypeScript
- **UI Library**: TBD (Tailwind CSS + Headless UI recommended)
- **State Management**: React Query for server state, Context API for local state
- **Routing**: React Router v6
- **Location**: `/mgmt-ui` directory (separate from voice agent client in `/client`)

### 2.2 Backend
- **Database**: Supabase (PostgreSQL 17)
- **Storage**: Supabase Storage
- **Vector Search**: PGvector extension
- **Real-time**: Supabase Realtime (optional for live call updates)

### 2.3 Authentication
- **Phase 1**: No authentication (development)
- **Phase 2**: Supabase Auth (future enhancement)

## 3. Database Schema

### 3.1 Tables Overview

#### Companies
- Stores company information and their OpenAI configurations
- Each company has their own API key, system prompt, and LLM model
- Fields: id, name, openai_api_key, system_prompt, llm_model, created_at, updated_at
- One-to-many with: calls, appointments, documents

#### Calls
- Tracks voice agent call sessions
- Links to company
- Stores start/end time and summary
- One-to-many with: call_details, appointments

#### Call Details
- Conversation logs (turn-by-turn)
- Speaker: 'agent' or 'caller'
- Timestamp with millisecond precision
- Message text

#### Appointments
- Scheduled appointments created during calls
- Links to both company and call
- Stores caller information and appointment details

#### Documents
- Company knowledge base files
- Links to Supabase Storage
- Metadata: filename, size, mime type

#### RAG Chunks
- Vector embeddings of document chunks
- 1536-dimension vectors (OpenAI embeddings)
- Metadata for context (page numbers, sections)
- HNSW index for fast similarity search

### 3.2 Key Relationships
```
companies (1) ──→ (many) calls
companies (1) ──→ (many) appointments
companies (1) ──→ (many) documents
calls (1) ──→ (many) call_details
calls (1) ──→ (many) appointments
documents (1) ──→ (many) rag_chunks
```

## 4. Core Features

### 4.1 Company Management
**Priority**: P0 (Must Have)

#### Features:
- List all companies
- Create new company with:
  - Company name
  - OpenAI API key
  - LLM model (dropdown: gpt-4o, gpt-4o-mini, gpt-3.5-turbo, etc.)
  - System prompt (textarea)
- Edit company details
- Delete company (with cascade warning)
- View company details page showing:
  - Recent calls
  - Total appointments
  - Document count

#### UI Components:
- Companies list page (table view)
- Company form (create/edit modal or page)
- Company detail page (dashboard view)

### 4.2 Call Management
**Priority**: P0 (Must Have)

#### Features:
- List calls (filterable by company, date range)
- View call details:
  - Company name
  - Start/end time, duration
  - Call summary
  - Full conversation transcript (call_details)
- Create call manually (for testing)
- Delete call

#### UI Components:
- Calls list page (table with filters)
- Call detail page with:
  - Call metadata card
  - Conversation timeline (chat-like UI)
  - Related appointments section

### 4.3 Call Details (Conversation Logs)
**Priority**: P0 (Must Have)

#### Features:
- Display conversation in chronological order
- Visual distinction between agent/caller
- Timestamp display
- Search within conversation
- Export conversation as text/JSON

#### UI Components:
- Chat-style conversation view
- Speaker badges (Agent/Caller)
- Timestamp formatting
- Search bar

### 4.4 Appointment Management
**Priority**: P1 (Should Have)

#### Features:
- List appointments (filterable by company, date, call)
- View appointment details
- Create appointment manually
- Edit appointment details
- Delete appointment
- Link to originating call

#### UI Components:
- Appointments list page (table/calendar view)
- Appointment form (modal)
- Appointment detail card

### 4.5 Document Management
**Priority**: P1 (Should Have)

#### Features:
- List documents by company
- Upload documents (PDF, TXT, DOCX)
- Download documents
- Delete documents (with cascade warning for RAG chunks)
- View document metadata
- Process document for RAG (trigger chunking & embedding)

#### UI Components:
- Documents list page (table with file icons)
- File upload component (drag & drop)
- Document detail card
- Processing status indicator

#### Technical Notes:
- Store files in Supabase Storage bucket: `company-documents`
- Path structure: `{company_id}/{document_id}/{filename}`
- Max file size: 50MB (configurable)

### 4.6 RAG (Vector Search)
**Priority**: P2 (Nice to Have)

#### Features:
- Search across company documents using natural language
- Display relevant chunks with similarity scores
- Show source document and metadata
- Highlight matching sections
- Test RAG search interface

#### UI Components:
- RAG search page (search bar + results)
- Chunk result card (text + metadata + score)
- Source document link

#### Technical Notes:
- Use OpenAI `text-embedding-3-small` (1536 dimensions)
- Chunk size: ~500 tokens with 50 token overlap
- Similarity threshold: 0.7 (cosine similarity)
- Return top 5 chunks by default

## 5. User Interface Design

### 5.1 Layout Structure
```
┌─────────────────────────────────────────┐
│ Header (Logo, Navigation)               │
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │  Main Content Area           │
│          │                              │
│ - Home   │  (Dynamic based on route)    │
│ - Comp.  │                              │
│ - Calls  │                              │
│ - Appts  │                              │
│ - Docs   │                              │
│ - RAG    │                              │
│          │                              │
└──────────┴──────────────────────────────┘
```

### 5.2 Navigation Structure
- **Home/Dashboard**: Overview stats, recent activity
- **Companies**: List, create, edit companies
- **Calls**: List, view call details
- **Appointments**: List, manage appointments
- **Documents**: Upload, manage documents
- **RAG Search**: Test vector search

### 5.3 Key UI Patterns
- **Tables**: Sortable, filterable, paginated
- **Forms**: Validation, error handling, loading states
- **Modals**: For create/edit operations
- **Toast notifications**: Success/error feedback
- **Loading states**: Skeletons for data fetching
- **Empty states**: Helpful messages when no data

## 6. Data Flow Examples

### 6.1 Creating a Call with Details
```
1. User creates call → POST /calls
2. Call created with company_id, start_time
3. User adds conversation turns → POST /call_details (multiple)
4. User ends call → PATCH /calls/{id} (set end_time, summary)
5. System creates appointments → POST /appointments (if any)
```

### 6.2 Document Upload & RAG Processing
```
1. User uploads file → Supabase Storage
2. Create document record → POST /documents
3. Trigger processing:
   a. Extract text from file
   b. Split into chunks (~500 tokens)
   c. Generate embeddings (OpenAI API)
   d. Store chunks → POST /rag_chunks (batch)
4. Document ready for RAG search
```

### 6.3 RAG Search Flow
```
1. User enters query → "How do I reset my password?"
2. Generate query embedding → OpenAI API
3. Vector similarity search → SELECT with <=> operator
4. Return top 5 chunks with metadata
5. Display results with source documents
```

## 7. API Endpoints (Supabase Client)

### 7.1 Companies
- `GET /companies` - List all companies
- `GET /companies/:id` - Get company details
- `POST /companies` - Create company
- `PATCH /companies/:id` - Update company
- `DELETE /companies/:id` - Delete company

### 7.2 Calls
- `GET /calls?company_id=X` - List calls (filtered)
- `GET /calls/:id` - Get call with details
- `POST /calls` - Create call
- `PATCH /calls/:id` - Update call
- `DELETE /calls/:id` - Delete call

### 7.3 Call Details
- `GET /call_details?call_id=X` - Get conversation
- `POST /call_details` - Add conversation turn
- `DELETE /call_details/:id` - Delete turn

### 7.4 Appointments
- `GET /appointments?company_id=X` - List appointments
- `POST /appointments` - Create appointment
- `PATCH /appointments/:id` - Update appointment
- `DELETE /appointments/:id` - Delete appointment

### 7.5 Documents
- `GET /documents?company_id=X` - List documents
- `POST /documents` - Create document record
- `DELETE /documents/:id` - Delete document
- Storage: `supabase.storage.from('company-documents')`

### 7.6 RAG
- `POST /rpc/search_documents` - Vector similarity search
- `GET /rag_chunks?document_id=X` - Get chunks for document

## 8. Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up React + Vite + TypeScript project
- [ ] Configure Supabase client
- [ ] Run migration (create tables)
- [ ] Set up routing and basic layout
- [ ] Create Companies CRUD

### Phase 2: Core Features (Week 2)
- [ ] Calls management
- [ ] Call details (conversation view)
- [ ] Appointments management
- [ ] Basic filtering and search

### Phase 3: Documents & Storage (Week 3)
- [ ] Document upload to Supabase Storage
- [ ] Document list and management
- [ ] File download functionality

### Phase 4: RAG Implementation (Week 4)
- [ ] Document processing (chunking)
- [ ] Embedding generation (OpenAI)
- [ ] Vector search implementation
- [ ] RAG search UI

### Phase 5: Polish (Week 5)
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Loading states
- [ ] Empty states
- [ ] Responsive design
- [ ] Testing

## 9. Non-Functional Requirements

### 9.1 Performance
- Page load time: < 2 seconds
- API response time: < 500ms (excluding embeddings)
- Vector search: < 1 second for top 5 results

### 9.2 Scalability
- Support 100+ companies
- Handle 1000+ calls per company
- Store 100+ documents per company
- 10,000+ RAG chunks per company

### 9.3 Security
- **Phase 1**: No authentication (development only)
- **Phase 2**: Row Level Security based on user roles
- API keys stored encrypted
- HTTPS only in production

### 9.4 Browser Support
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## 10. Future Enhancements

### 10.1 Authentication & Multi-tenancy
- Supabase Auth integration
- User roles (admin, viewer)
- Company-based access control

### 10.2 Real-time Features
- Live call status updates
- Real-time conversation streaming
- Notification system

### 10.3 Analytics
- Call volume dashboard
- Appointment conversion rates
- Popular search queries
- Document usage statistics

### 10.4 Advanced RAG
- Multi-document search
- Hybrid search (keyword + vector)
- Re-ranking algorithms
- Citation generation

### 10.5 Integrations
- Calendar integration (Google Calendar, Outlook)
- CRM integration (Salesforce, HubSpot)
- Webhook support for external systems
- Export to CSV/Excel

## 11. Success Metrics

- **Usability**: Users can create a company and upload documents in < 5 minutes
- **Performance**: RAG search returns results in < 1 second
- **Reliability**: 99.9% uptime for core features
- **Adoption**: All test companies successfully onboarded

## 12. Open Questions

1. Should we support multiple OpenAI API keys per company (for different models)?
2. Do we need call recording storage (audio files)?
3. Should appointments have calendar integration from day 1?
4. What document formats should we support initially? (PDF, TXT, DOCX, MD?)
5. Should we implement automatic call summarization using LLM?

## 13. Appendix

### 13.1 Sample Data Structure

#### Company
```json
{
  "id": 1,
  "name": "Acme Corp",
  "openai_api_key": "sk-...",
  "system_prompt": "You are a helpful assistant for Acme Corp...",
  "llm_model": "gpt-4o-mini",
  "created_at": "2025-01-14T10:00:00Z",
  "updated_at": "2025-01-14T10:00:00Z"
}
```

#### Call
```json
{
  "id": 1,
  "company_id": 1,
  "start_time": "2025-01-14T14:30:00Z",
  "end_time": "2025-01-14T14:35:00Z",
  "call_summary": "Customer inquired about product pricing and scheduled a demo."
}
```

#### Call Detail
```json
{
  "id": 1,
  "call_id": 1,
  "speaker": "caller",
  "timestamp": "2025-01-14T14:30:15.234Z",
  "message": "Hi, I'd like to know more about your pricing."
}
```

#### RAG Chunk
```json
{
  "id": 1,
  "document_id": 1,
  "chunk_text": "Our pricing starts at $99/month for the basic plan...",
  "chunk_index": 0,
  "embedding": [0.123, -0.456, ...], // 1536 dimensions
  "metadata": {
    "page": 1,
    "section": "Pricing"
  }
}
```

### 13.2 Environment Variables
```env
# mgmt-ui/.env.local
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
VITE_OPENAI_API_KEY=sk-... (for RAG processing)
```

### 13.3 Project Structure
```
/
├── client/              # Voice agent interface (existing)
├── mgmt-ui/            # Management UI (this app)
│   ├── src/
│   ├── .env.local
│   └── package.json
├── server/             # Voice agent server (existing)
├── supabase/           # Database migrations and config
└── docs/               # Documentation
```

---

**Document Version**: 1.1
**Last Updated**: 2025-01-14
**Author**: Development Team
**Status**: Draft



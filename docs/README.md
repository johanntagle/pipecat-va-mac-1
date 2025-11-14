# Call Management & RAG System - Documentation

Welcome to the Call Management & RAG System documentation. This system enables multi-tenant management of AI voice agent calls, appointments, and document-based knowledge retrieval.

## 📁 Documentation Structure

### 1. [QUICKSTART.md](./QUICKSTART.md) - **Start Here!**
Step-by-step checklist to get up and running in 45 minutes.
- Database setup
- React app initialization
- Connection testing
- Troubleshooting

### 2. [PRD-call-management-app.md](./PRD-call-management-app.md) - **Product Requirements**
Complete product specification including:
- Feature requirements
- Database schema
- UI/UX design
- API endpoints
- Development phases
- Success metrics

### 3. [SETUP.md](./SETUP.md) - **Detailed Setup Guide**
Comprehensive setup instructions for:
- Local development with Supabase
- Production deployment
- Database migrations
- Storage configuration
- Common issues and solutions

### 4. [REACT-APP-GUIDE.md](./REACT-APP-GUIDE.md) - **Development Guide**
React development patterns and examples:
- Project structure
- Data fetching patterns
- Component examples
- Best practices
- Performance optimization

## 🗄️ Database Schema

### Tables
1. **companies** - Company configurations with OpenAI API keys
2. **calls** - Call sessions with start/end times
3. **call_details** - Turn-by-turn conversation logs
4. **appointments** - Scheduled appointments from calls
5. **documents** - Knowledge base files in Supabase Storage
6. **rag_chunks** - Vector embeddings for semantic search

### Key Features
- ✅ Row Level Security (RLS) enabled
- ✅ Automatic timestamps with triggers
- ✅ Cascade deletes for data integrity
- ✅ Vector similarity search (HNSW index)
- ✅ Optimized indexes for common queries

## 🚀 Quick Start

```bash
# 1. Start Supabase
supabase start

# 2. Create React app (in mgmt-ui directory)
mkdir mgmt-ui
cd mgmt-ui
npm create vite@latest . -- --template react-ts
npm install

# 3. Install dependencies
npm install @supabase/supabase-js react-router-dom @tanstack/react-query

# 4. Configure environment
echo "VITE_SUPABASE_URL=http://127.0.0.1:54321" > .env.local
echo "VITE_SUPABASE_ANON_KEY=<your-key>" >> .env.local

# 5. Generate types (from project root)
cd ..
npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts

# 6. Start dev server
cd mgmt-ui
npm run dev
```

## 📊 Database Migration

The migration file is located at:
```
supabase/migrations/20250114000000_initial_schema.sql
```

It includes:
- All table definitions
- Indexes for performance
- RLS policies
- Storage bucket creation
- Triggers for auto-updates

## 🌱 Seed Data

Sample data is provided in:
```
supabase/seed.sql
```

Includes:
- 3 sample companies
- 5 sample calls
- Conversation logs
- 3 sample appointments

## 🏗️ Project Structure

```
/
├── client/              # Voice agent interface (existing - Next.js)
├── mgmt-ui/            # Management UI (this app - React + Vite)
│   ├── src/
│   ├── .env.local
│   └── package.json
├── server/             # Voice agent server (existing - Python)
├── supabase/           # Database migrations and config
│   ├── migrations/
│   ├── seed.sql
│   └── config.toml
└── docs/               # Documentation
```

**Important:** The management UI is in `/mgmt-ui`, separate from the voice agent client in `/client`.

## 🏗️ Tech Stack

### Frontend
- **React 18+** with TypeScript
- **Vite** for build tooling
- **React Router** for navigation
- **React Query** for data fetching
- **Tailwind CSS** for styling
- **Location:** `/mgmt-ui` directory

### Backend
- **Supabase** (PostgreSQL 17)
- **PGvector** for embeddings
- **Supabase Storage** for files
- **OpenAI API** for embeddings

## 📋 Development Phases

### Phase 1: Foundation (Week 1)
- [x] Database schema and migration
- [ ] React app setup
- [ ] Basic layout and routing
- [ ] Companies CRUD

### Phase 2: Core Features (Week 2)
- [ ] Calls management
- [ ] Conversation view
- [ ] Appointments management

### Phase 3: Documents (Week 3)
- [ ] File upload/download
- [ ] Document management UI

### Phase 4: RAG (Week 4)
- [ ] Document processing
- [ ] Embedding generation
- [ ] Vector search UI

### Phase 5: Polish (Week 5)
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Testing
- [ ] Documentation

## 🎯 Key Features

### Company Management
- Multi-tenant architecture
- Custom OpenAI API keys per company
- Custom system prompts
- Company dashboard with stats

### Call Management
- Call session tracking
- Start/end time logging
- Call summaries
- Full conversation transcripts

### Conversation Logs
- Turn-by-turn tracking
- Speaker identification (agent/caller)
- Millisecond-precision timestamps
- Chat-style UI

### Appointments
- Link to originating call
- Caller information
- Appointment details
- Calendar view (future)

### Document Management
- File upload to Supabase Storage
- Support for PDF, TXT, DOCX
- Document metadata tracking
- Download functionality

### RAG (Retrieval Augmented Generation)
- Document chunking
- Vector embeddings (OpenAI)
- Semantic search
- Similarity scoring
- Source attribution

## 🔒 Security Notes

**Current State (Development):**
- No authentication required
- Permissive RLS policies
- All operations allowed

**Future (Production):**
- Supabase Auth integration
- User roles (admin, viewer)
- Company-based access control
- Encrypted API key storage

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [React Query Documentation](https://tanstack.com/query/latest)
- [PGvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

## 🤝 Contributing

1. Read the PRD to understand requirements
2. Follow the React App Guide for patterns
3. Test locally with `supabase start`
4. Write tests for new features
5. Update documentation

## 📞 Support

For issues or questions:
1. Check [SETUP.md](./SETUP.md) troubleshooting section
2. Review [QUICKSTART.md](./QUICKSTART.md) for common issues
3. Check Supabase logs: `supabase logs`

---

**Last Updated:** 2025-01-14  
**Version:** 1.0  
**Status:** Ready for Development


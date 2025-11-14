# Quick Start Checklist

Follow these steps to get the Call Management & RAG System up and running.

## ✅ Phase 1: Database Setup (15 minutes)

### Step 1: Start Supabase
```bash
cd /Users/johanntagle/LEARN/macos-local-voice-agents
supabase start
```

**Expected Output:**
- API URL: http://127.0.0.1:54321
- Studio URL: http://127.0.0.1:54323
- anon key: eyJhbGc...

### Step 2: Verify Database
1. Open http://127.0.0.1:54323 (Supabase Studio)
2. Go to **Table Editor**
3. Verify these tables exist:
   - ✅ companies
   - ✅ calls
   - ✅ call_details
   - ✅ appointments
   - ✅ documents
   - ✅ rag_chunks

### Step 3: Check Sample Data
1. In Supabase Studio, go to **SQL Editor**
2. Run: `SELECT * FROM companies;`
3. You should see 3 companies (Acme, TechStart, Global Services)

### Step 4: Verify Storage
1. Go to **Storage** in Supabase Studio
2. Verify bucket exists: `company-documents`

---

## ✅ Phase 2: React App Setup (30 minutes)

### Step 1: Create React App
```bash
# From project root
mkdir mgmt-ui
cd mgmt-ui
npm create vite@latest . -- --template react-ts
npm install
```

### Step 2: Install Dependencies
```bash
npm install @supabase/supabase-js react-router-dom @tanstack/react-query
npm install tailwindcss postcss autoprefixer
npm install react-hook-form zod @hookform/resolvers
npm install date-fns react-dropzone
npx tailwindcss init -p
```

### Step 3: Configure Environment
Create `mgmt-ui/.env.local`:
```env
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_ANON_KEY=<paste-your-anon-key-here>
```

### Step 4: Generate TypeScript Types
```bash
# From project root
npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts
```

### Step 5: Create Supabase Client
Create `mgmt-ui/src/lib/supabase.ts`:
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Step 6: Test Connection
Create `mgmt-ui/src/App.tsx`:
```typescript
import { useEffect, useState } from 'react'
import { supabase } from './lib/supabase'

function App() {
  const [companies, setCompanies] = useState([])

  useEffect(() => {
    async function fetchCompanies() {
      const { data } = await supabase.from('companies').select('*')
      setCompanies(data || [])
    }
    fetchCompanies()
  }, [])

  return (
    <div>
      <h1>Companies</h1>
      <ul>
        {companies.map((c: any) => (
          <li key={c.id}>{c.name}</li>
        ))}
      </ul>
    </div>
  )
}

export default App
```

### Step 7: Run Dev Server
```bash
npm run dev
```

Open http://localhost:5173 - you should see the 3 companies listed!

---

## ✅ Phase 3: Build Core Features (Week 1-2)

### Week 1: Foundation
- [ ] Set up routing (React Router)
- [ ] Create layout (Header, Sidebar, Main)
- [ ] Build Companies page (list view)
- [ ] Build Company form (create/edit)
- [ ] Build Company detail page

### Week 2: Calls & Appointments
- [ ] Build Calls page (list with filters)
- [ ] Build Call detail page
- [ ] Build Conversation view component
- [ ] Build Appointments page
- [ ] Build Appointment form

---

## ✅ Phase 4: Advanced Features (Week 3-4)

### Week 3: Documents
- [ ] Build Documents page
- [ ] Implement file upload (drag & drop)
- [ ] Implement file download
- [ ] Add document processing status

### Week 4: RAG
- [ ] Create RPC function for vector search
- [ ] Build RAG search page
- [ ] Implement embedding generation
- [ ] Display search results with scores

---

## 🧪 Testing Your Setup

### Test 1: Database Connection
```sql
-- In Supabase Studio SQL Editor
SELECT 
  c.name,
  COUNT(ca.id) as call_count
FROM companies c
LEFT JOIN calls ca ON c.id = ca.company_id
GROUP BY c.id, c.name;
```

### Test 2: React Query
```typescript
// In your React app
const { data } = useQuery({
  queryKey: ['companies'],
  queryFn: async () => {
    const { data } = await supabase.from('companies').select('*')
    return data
  }
})
```

### Test 3: File Upload
```typescript
const { data, error } = await supabase.storage
  .from('company-documents')
  .upload('test/test.txt', new Blob(['Hello World']))
```

---

## 📚 Documentation Reference

- **[PRD](./PRD-call-management-app.md)** - Full product requirements
- **[SETUP](./SETUP.md)** - Detailed setup instructions
- **[REACT-APP-GUIDE](./REACT-APP-GUIDE.md)** - React development guide

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Supabase"
**Solution:** Make sure `supabase start` is running

### Issue: "Table does not exist"
**Solution:** Run `supabase db reset` to reapply migrations

### Issue: "CORS error"
**Solution:** Check that VITE_SUPABASE_URL matches your Supabase API URL

### Issue: "Types not found"
**Solution:** Run `npx supabase gen types typescript --local > src/lib/types.ts`

---

## 🎯 Success Criteria

You're ready to start building when:
- ✅ Supabase is running locally
- ✅ All 6 tables exist with sample data
- ✅ Storage bucket is created
- ✅ React app connects to Supabase
- ✅ You can fetch and display companies

---

## 🚀 Next Steps

1. Read the [PRD](./PRD-call-management-app.md) to understand all features
2. Follow the [React App Guide](./REACT-APP-GUIDE.md) for implementation patterns
3. Start with Phase 1: Companies CRUD
4. Iterate and test frequently

Good luck! 🎉


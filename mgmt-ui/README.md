# Call Management & RAG System - Management UI

This is the management interface for the Call Management & RAG System. It provides a web-based UI for managing companies, calls, appointments, documents, and RAG search.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Supabase running locally (see [../docs/SETUP.md](../docs/SETUP.md))

### Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   Create `.env.local`:
   ```env
   VITE_SUPABASE_URL=http://127.0.0.1:54321
   VITE_SUPABASE_ANON_KEY=<your-anon-key>
   ```

3. **Generate TypeScript types:**
   ```bash
   # From project root
   npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts
   ```

4. **Start dev server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to http://localhost:5173

## 📁 Project Structure

```
mgmt-ui/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components (routes)
│   ├── lib/            # Utilities and configurations
│   ├── hooks/          # Custom React hooks
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── .env.local          # Environment variables (not committed)
└── package.json
```

## 🛠️ Tech Stack

- **React 18+** with TypeScript
- **Vite** for build tooling
- **React Router** for navigation
- **React Query** for data fetching
- **Tailwind CSS** for styling
- **Supabase** for backend

## 📚 Documentation

- [Quick Start Guide](../docs/QUICKSTART.md)
- [Product Requirements](../docs/PRD-call-management-app.md)
- [React Development Guide](../docs/REACT-APP-GUIDE.md)
- [Setup Instructions](../docs/SETUP.md)

## 🔧 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🎯 Features

### Phase 1 (Current)
- [ ] Companies CRUD
- [ ] Calls management
- [ ] Conversation view
- [ ] Appointments management

### Phase 2 (Planned)
- [ ] Document upload/management
- [ ] RAG search interface
- [ ] Analytics dashboard

## 🐛 Troubleshooting

### Cannot connect to Supabase
Make sure Supabase is running:
```bash
cd ..
supabase start
```

### Types not found
Regenerate types:
```bash
cd ..
npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts
```

### Port already in use
Change the port in `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 5174  // Change to any available port
  }
})
```

## 📝 Notes

- This app is separate from the voice agent client in `/client`
- Uses Supabase for all backend operations
- No authentication in Phase 1 (development only)
- See [PRD](../docs/PRD-call-management-app.md) for complete feature list

## 🤝 Contributing

1. Read the [PRD](../docs/PRD-call-management-app.md)
2. Follow the [React App Guide](../docs/REACT-APP-GUIDE.md)
3. Test locally before committing
4. Update documentation as needed


# Quick Start Guide

## Prerequisites
- Supabase running locally (from parent directory)
- Node.js 18+ installed

## Setup (3 Steps)

### 1. Install Dependencies
```bash
npm install
```

### 2. Verify Supabase
```bash
cd ..
npx supabase status
cd mgmt-ui
```

### 3. Start Dev Server
```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

## What You'll See

- **Home** - Welcome page with feature overview
- **Companies** - List of all companies
- **Calls** - Call history with "View Details" button
- **Appointments** - Scheduled appointments
- **Documents** - Uploaded files
- **RAG Chunks** - Text embeddings

## Testing Call Details

1. Go to **Calls** page
2. Click **"View Details"** on any call
3. See the conversation in chat format:
   - Agent messages (blue, left)
   - Caller messages (gray, right)
   - Timestamps for each message

## Troubleshooting

**"Failed to fetch"**
- Make sure Supabase is running: `npx supabase status`

**Port in use**
- Vite will automatically use the next available port

**Dependencies fail**
- Try: `npm install --legacy-peer-deps`

## Configuration Files

All configuration is already set up:
- ✅ Tailwind CSS configured
- ✅ PostCSS configured  
- ✅ TypeScript configured
- ✅ Vite configured
- ✅ Environment variables set

No additional setup needed!

## Next Steps

See `TESTING-CHECKLIST.md` for comprehensive testing instructions.


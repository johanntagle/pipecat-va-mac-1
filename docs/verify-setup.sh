#!/bin/bash

# Verification script for Call Management & RAG System setup
# Run this after setting up the database and before building the React app

set -e

echo "🔍 Verifying Call Management & RAG System Setup..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project root
if [ ! -f "supabase/config.toml" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root${NC}"
    exit 1
fi

echo "✅ Running from project root"
echo ""

# Check if Supabase CLI is installed
echo "Checking Supabase CLI..."
if ! command -v supabase &> /dev/null; then
    echo -e "${RED}❌ Supabase CLI not found${NC}"
    echo "Install with: npm install -g supabase"
    exit 1
fi
echo -e "${GREEN}✅ Supabase CLI installed${NC}"
echo ""

# Check if Supabase is running
echo "Checking if Supabase is running..."
if ! curl -s http://127.0.0.1:54321/rest/v1/ > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Supabase is not running${NC}"
    echo "Start with: supabase start"
    exit 1
fi
echo -e "${GREEN}✅ Supabase is running${NC}"
echo ""

# Check if migration file exists
echo "Checking migration file..."
if [ ! -f "supabase/migrations/20250114000000_initial_schema.sql" ]; then
    echo -e "${RED}❌ Migration file not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Migration file exists${NC}"
echo ""

# Check if seed file exists
echo "Checking seed file..."
if [ ! -f "supabase/seed.sql" ]; then
    echo -e "${RED}❌ Seed file not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Seed file exists${NC}"
echo ""

# Check if tables exist
echo "Checking database tables..."
TABLES=("companies" "calls" "call_details" "appointments" "documents" "rag_chunks")
for table in "${TABLES[@]}"; do
    if ! supabase db execute "SELECT 1 FROM $table LIMIT 1" > /dev/null 2>&1; then
        echo -e "${RED}❌ Table '$table' not found${NC}"
        echo "Run: supabase db reset"
        exit 1
    fi
    echo -e "${GREEN}✅ Table '$table' exists${NC}"
done
echo ""

# Check if sample data exists
echo "Checking sample data..."
COMPANY_COUNT=$(supabase db execute "SELECT COUNT(*) FROM companies" --format csv | tail -n 1)
if [ "$COMPANY_COUNT" -lt 1 ]; then
    echo -e "${YELLOW}⚠️  No sample data found${NC}"
    echo "Run: supabase db reset"
else
    echo -e "${GREEN}✅ Found $COMPANY_COUNT companies${NC}"
fi
echo ""

# Check if storage bucket exists
echo "Checking storage bucket..."
if ! supabase db execute "SELECT 1 FROM storage.buckets WHERE id = 'company-documents'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Storage bucket 'company-documents' not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Storage bucket 'company-documents' exists${NC}"
echo ""

# Check if vector extension is enabled
echo "Checking vector extension..."
if ! supabase db execute "SELECT 1 FROM pg_extension WHERE extname = 'vector'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Vector extension not enabled${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Vector extension enabled${NC}"
echo ""

# Check if mgmt-ui directory exists
echo "Checking mgmt-ui directory..."
if [ ! -d "mgmt-ui" ]; then
    echo -e "${YELLOW}⚠️  mgmt-ui directory not found${NC}"
    echo "Create with: mkdir mgmt-ui && cd mgmt-ui && npm create vite@latest . -- --template react-ts"
else
    echo -e "${GREEN}✅ mgmt-ui directory exists${NC}"
    
    # Check if package.json exists
    if [ -f "mgmt-ui/package.json" ]; then
        echo -e "${GREEN}✅ mgmt-ui/package.json exists${NC}"
    else
        echo -e "${YELLOW}⚠️  mgmt-ui/package.json not found${NC}"
        echo "Initialize with: cd mgmt-ui && npm create vite@latest . -- --template react-ts"
    fi
    
    # Check if .env.local exists
    if [ -f "mgmt-ui/.env.local" ]; then
        echo -e "${GREEN}✅ mgmt-ui/.env.local exists${NC}"
    else
        echo -e "${YELLOW}⚠️  mgmt-ui/.env.local not found${NC}"
        echo "Create with environment variables (see docs/QUICKSTART.md)"
    fi
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Setup verification complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. If mgmt-ui is not set up, follow docs/QUICKSTART.md"
echo "2. Generate TypeScript types:"
echo "   npx supabase gen types typescript --local > mgmt-ui/src/lib/types.ts"
echo "3. Start the dev server:"
echo "   cd mgmt-ui && npm run dev"
echo ""
echo "Documentation:"
echo "- Quick Start: docs/QUICKSTART.md"
echo "- PRD: docs/PRD-call-management-app.md"
echo "- Setup Guide: docs/SETUP.md"
echo ""


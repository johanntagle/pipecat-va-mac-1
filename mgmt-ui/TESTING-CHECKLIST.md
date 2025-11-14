# Testing Checklist for Management UI

## Pre-Testing Setup

- [ ] Supabase is running (`npx supabase status` from parent directory)
- [ ] Dependencies are installed (`npm install` completed successfully)
- [ ] Development server starts without errors (`npm run dev`)
- [ ] Browser opens to `http://localhost:5173`

## Page Navigation Tests

### Home Page
- [ ] Home page loads successfully
- [ ] All 5 feature cards are displayed
- [ ] Sidebar navigation is visible
- [ ] Header shows "Call Management System"

### Companies Page
- [ ] Navigate to Companies from sidebar
- [ ] Page loads without errors
- [ ] If data exists: Table displays with all columns (ID, Name, LLM Model, Has API Key, Created At)
- [ ] If no data: Empty state message appears
- [ ] API Key status shows green "Yes" badge or gray "No" badge
- [ ] Dates are formatted correctly (e.g., "Jan 15, 2024 14:30")

### Calls Page
- [ ] Navigate to Calls from sidebar
- [ ] Page loads without errors
- [ ] If data exists: Table displays with all columns (ID, Company, Start Time, End Time, Duration, Summary, Actions)
- [ ] If no data: Empty state message appears
- [ ] Company names are displayed (not just IDs)
- [ ] Duration shows in seconds (e.g., "45s")
- [ ] "In progress" shows for calls without end_time
- [ ] "View Details" button appears for each call
- [ ] Clicking "View Details" opens a modal
- [ ] Modal displays call conversation in chat format
- [ ] Agent messages appear on the left with blue background
- [ ] Caller messages appear on the right with gray background
- [ ] Each message shows speaker name and timestamp
- [ ] Modal can be closed with "Close" button
- [ ] Modal can be closed by clicking outside
- [ ] If no conversation details exist, empty state shows in modal

### Appointments Page
- [ ] Navigate to Appointments from sidebar
- [ ] Page loads without errors
- [ ] If data exists: Table displays with all columns (ID, Company, Caller Name, Phone, Appointment Time, Status)
- [ ] If no data: Empty state message appears
- [ ] Status badges are color-coded (green for confirmed, yellow for pending)
- [ ] Phone numbers display correctly or show "N/A"

### Documents Page
- [ ] Navigate to Documents from sidebar
- [ ] Page loads without errors
- [ ] If data exists: Table displays with all columns (ID, Company, File Name, File Size, MIME Type, Created At)
- [ ] If no data: Empty state message appears
- [ ] File sizes are formatted (KB or MB)
- [ ] Long file names are truncated properly

### RAG Chunks Page
- [ ] Navigate to RAG Chunks from sidebar
- [ ] Page loads without errors
- [ ] If data exists: Table displays with all columns (ID, Document, Company, Chunk Index, Chunk Text, Has Embedding, Created At)
- [ ] If no data: Empty state message appears
- [ ] Chunk text is truncated to 2 lines
- [ ] Embedding status shows green "Yes" or gray "No" badge
- [ ] Nested data (document name, company name) displays correctly

## Loading States

- [ ] Loading spinner appears when fetching data
- [ ] Loading spinner is centered and animated
- [ ] Page doesn't flash or jump when data loads

## Error Handling

To test error states, you can:
1. Stop Supabase: `npx supabase stop`
2. Refresh the page
3. Verify error message appears

- [ ] Error message displays when Supabase is not running
- [ ] Error message is user-friendly (not raw error text)
- [ ] Error message has red background and icon

## Responsive Design

Test at different screen sizes:

- [ ] Desktop (1920px): Sidebar and content side-by-side
- [ ] Tablet (768px): Layout adjusts appropriately
- [ ] Mobile (375px): Tables scroll horizontally if needed
- [ ] Navigation remains accessible on all sizes

## Data Integrity

If you have test data in your database:

- [ ] All foreign key relationships display correctly (company names in calls, appointments, etc.)
- [ ] Dates are in correct timezone
- [ ] Null values show as "N/A" instead of blank
- [ ] Numbers are formatted correctly

## Browser Console

- [ ] No errors in browser console
- [ ] No warnings about missing keys in lists
- [ ] React Query devtools show successful queries (if enabled)

## Performance

- [ ] Initial page load is fast (< 2 seconds)
- [ ] Navigation between pages is instant (data is cached)
- [ ] Tables with many rows scroll smoothly
- [ ] No memory leaks when navigating between pages

## Additional Checks

- [ ] URL changes when navigating (e.g., `/companies`, `/calls`)
- [ ] Browser back/forward buttons work correctly
- [ ] Refreshing a page loads the correct content
- [ ] Invalid URLs redirect to home page

## Common Issues and Solutions

### Issue: "Failed to fetch"
**Solution**: Ensure Supabase is running with `npx supabase status`

### Issue: Empty tables when data exists
**Solution**: Check browser console for CORS or authentication errors

### Issue: TypeScript errors in IDE
**Solution**: Run `npm install` to ensure all types are installed

### Issue: Styles not loading
**Solution**: Verify Tailwind CSS is configured correctly in `index.css`

### Issue: Page not found (404)
**Solution**: Check that React Router is configured in `App.tsx`

## Test Data Creation

If you need to create test data, you can use the Supabase Studio:

1. Open `http://127.0.0.1:54323` (Supabase Studio)
2. Navigate to Table Editor
3. Insert sample data into each table
4. Refresh the management UI to see the data

## Success Criteria

The application is working correctly if:
- ✅ All pages load without errors
- ✅ Data from all 6 tables is displayed correctly
- ✅ Loading and error states work as expected
- ✅ Navigation is smooth and responsive
- ✅ No console errors or warnings
- ✅ UI is responsive on different screen sizes


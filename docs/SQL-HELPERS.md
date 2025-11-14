# SQL Helper Queries

Useful SQL queries for development, testing, and debugging.

## 📊 Data Overview Queries

### Get Company Statistics
```sql
SELECT 
  c.id,
  c.name,
  COUNT(DISTINCT ca.id) as total_calls,
  COUNT(DISTINCT a.id) as total_appointments,
  COUNT(DISTINCT d.id) as total_documents,
  COUNT(DISTINCT rc.id) as total_rag_chunks
FROM companies c
LEFT JOIN calls ca ON c.id = ca.company_id
LEFT JOIN appointments a ON c.id = a.company_id
LEFT JOIN documents d ON c.id = d.company_id
LEFT JOIN rag_chunks rc ON d.id = rc.document_id
GROUP BY c.id, c.name
ORDER BY c.name;
```

### Get Recent Calls with Details
```sql
SELECT 
  ca.id,
  co.name as company_name,
  ca.start_time,
  ca.end_time,
  EXTRACT(EPOCH FROM (ca.end_time - ca.start_time)) as duration_seconds,
  ca.call_summary,
  COUNT(cd.id) as message_count
FROM calls ca
JOIN companies co ON ca.company_id = co.id
LEFT JOIN call_details cd ON ca.id = cd.call_id
GROUP BY ca.id, co.name, ca.start_time, ca.end_time, ca.call_summary
ORDER BY ca.start_time DESC
LIMIT 10;
```

### Get Conversation for a Call
```sql
-- Replace {call_id} with actual call ID
SELECT 
  cd.speaker,
  cd.timestamp,
  cd.message,
  EXTRACT(EPOCH FROM (cd.timestamp - LAG(cd.timestamp) OVER (ORDER BY cd.timestamp))) as seconds_since_last
FROM call_details cd
WHERE cd.call_id = {call_id}
ORDER BY cd.timestamp;
```

## 🔍 Search and Filter Queries

### Find Calls by Date Range
```sql
SELECT 
  ca.id,
  co.name as company,
  ca.start_time,
  ca.call_summary
FROM calls ca
JOIN companies co ON ca.company_id = co.id
WHERE ca.start_time BETWEEN '2025-01-01' AND '2025-01-31'
ORDER BY ca.start_time DESC;
```

### Search Conversations by Keyword
```sql
-- Find calls containing specific keywords in conversation
SELECT DISTINCT
  ca.id,
  co.name as company,
  ca.start_time,
  ca.call_summary
FROM calls ca
JOIN companies co ON ca.company_id = co.id
JOIN call_details cd ON ca.id = cd.call_id
WHERE cd.message ILIKE '%pricing%'  -- Change keyword here
ORDER BY ca.start_time DESC;
```

### Find Appointments by Date
```sql
SELECT 
  a.id,
  co.name as company,
  a.caller_name,
  a.caller_contact_number,
  a.appointment_details,
  ca.start_time as call_time
FROM appointments a
JOIN companies co ON a.company_id = co.id
LEFT JOIN calls ca ON a.call_id = ca.id
WHERE a.created_at >= CURRENT_DATE
ORDER BY a.created_at DESC;
```

## 🧪 Testing Queries

### Insert Test Company
```sql
INSERT INTO companies (name, openai_api_key, system_prompt)
VALUES (
  'Test Company',
  'sk-test-key-replace-me',
  'You are a helpful assistant for Test Company.'
)
RETURNING *;
```

### Insert Test Call
```sql
-- Replace {company_id} with actual company ID
INSERT INTO calls (company_id, start_time, end_time, call_summary)
VALUES (
  {company_id},
  NOW() - INTERVAL '10 minutes',
  NOW() - INTERVAL '5 minutes',
  'Test call for development purposes.'
)
RETURNING *;
```

### Insert Test Conversation
```sql
-- Replace {call_id} with actual call ID
INSERT INTO call_details (call_id, speaker, timestamp, message)
VALUES 
  ({call_id}, 'caller', NOW() - INTERVAL '5 minutes', 'Hello, I need help.'),
  ({call_id}, 'agent', NOW() - INTERVAL '4 minutes 55 seconds', 'Hi! How can I assist you today?'),
  ({call_id}, 'caller', NOW() - INTERVAL '4 minutes 50 seconds', 'I have a question about pricing.'),
  ({call_id}, 'agent', NOW() - INTERVAL '4 minutes 45 seconds', 'I''d be happy to help with pricing information.');
```

## 🧹 Cleanup Queries

### Delete Test Data
```sql
-- Delete a specific company and all related data (cascade)
DELETE FROM companies WHERE name = 'Test Company';

-- Delete old calls (older than 30 days)
DELETE FROM calls WHERE start_time < NOW() - INTERVAL '30 days';

-- Delete orphaned appointments (no associated call)
DELETE FROM appointments WHERE call_id IS NULL;
```

### Reset All Data (DANGEROUS!)
```sql
-- WARNING: This deletes ALL data
TRUNCATE companies, calls, call_details, appointments, documents, rag_chunks RESTART IDENTITY CASCADE;
```

## 📈 Analytics Queries

### Call Volume by Company
```sql
SELECT 
  co.name,
  COUNT(ca.id) as total_calls,
  AVG(EXTRACT(EPOCH FROM (ca.end_time - ca.start_time))) as avg_duration_seconds,
  COUNT(CASE WHEN ca.end_time IS NULL THEN 1 END) as ongoing_calls
FROM companies co
LEFT JOIN calls ca ON co.id = ca.company_id
GROUP BY co.id, co.name
ORDER BY total_calls DESC;
```

### Appointments Conversion Rate
```sql
SELECT 
  co.name,
  COUNT(DISTINCT ca.id) as total_calls,
  COUNT(DISTINCT a.id) as total_appointments,
  ROUND(COUNT(DISTINCT a.id)::numeric / NULLIF(COUNT(DISTINCT ca.id), 0) * 100, 2) as conversion_rate
FROM companies co
LEFT JOIN calls ca ON co.id = ca.company_id
LEFT JOIN appointments a ON ca.id = a.call_id
GROUP BY co.id, co.name
ORDER BY conversion_rate DESC;
```

### Most Active Hours
```sql
SELECT 
  EXTRACT(HOUR FROM start_time) as hour,
  COUNT(*) as call_count
FROM calls
GROUP BY hour
ORDER BY hour;
```

## 🔧 Maintenance Queries

### Check Table Sizes
```sql
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Index Usage
```sql
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan as index_scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Vacuum and Analyze
```sql
-- Optimize database performance
VACUUM ANALYZE companies;
VACUUM ANALYZE calls;
VACUUM ANALYZE call_details;
VACUUM ANALYZE appointments;
VACUUM ANALYZE documents;
VACUUM ANALYZE rag_chunks;
```

## 🎯 Vector Search Queries

### Test Vector Similarity (Manual)
```sql
-- Create a test embedding (normally from OpenAI)
-- This is just for testing the vector functionality
SELECT 
  id,
  chunk_text,
  1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM rag_chunks
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### Check Vector Index
```sql
SELECT 
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'rag_chunks'
  AND indexname LIKE '%embedding%';
```

## 🔐 Security Queries

### Check RLS Policies
```sql
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Check Storage Policies
```sql
SELECT 
  name,
  definition
FROM storage.policies
ORDER BY name;
```

---

## 💡 Tips

1. **Use EXPLAIN ANALYZE** to check query performance:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM calls WHERE company_id = 1;
   ```

2. **Use transactions** for multiple related inserts:
   ```sql
   BEGIN;
   INSERT INTO calls (...) VALUES (...) RETURNING id;
   INSERT INTO call_details (...) VALUES (...);
   COMMIT;
   ```

3. **Use CTEs** for complex queries:
   ```sql
   WITH recent_calls AS (
     SELECT * FROM calls WHERE start_time > NOW() - INTERVAL '7 days'
   )
   SELECT * FROM recent_calls WHERE company_id = 1;
   ```

4. **Always test destructive queries** on a copy first!


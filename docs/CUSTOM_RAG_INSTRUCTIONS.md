# Custom RAG Instructions Per Company

This guide explains how to set custom RAG system instructions for each company in the voice agent system.

## Overview

Each company can have custom instructions that tell the LLM how to use RAG (Retrieval-Augmented Generation) context. This allows you to tailor the agent's behavior based on:
- The type of documents in the knowledge base
- The company's preferred response style
- Specific requirements for how information should be presented

## Database Schema

The `companies` table includes a `rag_system_instructions` column:

```sql
-- Column definition
rag_system_instructions TEXT NULL
```

- **Type**: TEXT (can be long, multi-paragraph instructions)
- **Nullable**: Yes (NULL means use default instructions)
- **Default**: NULL

## Setting Custom Instructions

### Via SQL

```sql
-- Set custom instructions for a company
UPDATE companies 
SET rag_system_instructions = 'Your custom instructions here...'
WHERE id = 1;

-- Example: Product catalog company
UPDATE companies 
SET rag_system_instructions = 'You have access to our product catalog. When answering questions about products:
- Always mention the product code and price from the provided context
- If multiple products match, list all of them
- If a product is out of stock (mentioned in context), inform the customer
- Suggest related products when appropriate'
WHERE id = 1;

-- Example: Restaurant company
UPDATE companies 
SET rag_system_instructions = 'You have access to our menu and business information. When answering questions:
- For menu items, include the price and any dietary information from the context
- For business hours, be specific about days and times
- For reservations, use the information from the context about our booking policy
- Maintain a friendly, welcoming tone that matches our restaurant atmosphere'
WHERE id = 2;

-- Example: Technical support company
UPDATE companies 
SET rag_system_instructions = 'You have access to our technical documentation and troubleshooting guides. When helping customers:
- Provide step-by-step instructions from the documentation
- Reference specific article numbers or section titles when available
- If the context contains multiple solutions, start with the most common fix
- Always ask if the solution worked before moving to the next step'
WHERE id = 3;
```

### Via Supabase Studio

1. Open Supabase Studio (http://127.0.0.1:54323)
2. Go to **Table Editor** → **companies**
3. Click on the company row you want to edit
4. Find the `rag_system_instructions` column
5. Enter your custom instructions
6. Click **Save**

## Using Default Instructions

To use the default RAG instructions (defined in `RAG_SYSTEM_INSTRUCTIONS` constant):

```sql
-- Set to NULL to use default
UPDATE companies 
SET rag_system_instructions = NULL
WHERE id = 1;
```

## Default Instructions

If `rag_system_instructions` is NULL, the system uses these default instructions:

```
You have access to a knowledge base of company documents.
When answering questions, relevant information from these documents will be provided to you as context.
Use this context to provide accurate, specific answers based on the company's information.
If the context doesn't contain relevant information for a question, rely on your general knowledge but mention that you're not finding specific company information about that topic.
```

## How It Works

1. **At Startup**: When `03_rag.py` starts, it loads the company configuration including `rag_system_instructions`
2. **Fallback Logic**: 
   - If `rag_system_instructions` is set → use custom instructions
   - If `rag_system_instructions` is NULL → use default `RAG_SYSTEM_INSTRUCTIONS`
3. **Logging**: The system logs which instructions are being used:
   ```
   - Using custom RAG instructions from database
   ```
   or
   ```
   - Using default RAG instructions
   ```
4. **Runtime**: The instructions are combined with the system prompt and voice instructions before being sent to the LLM

## Best Practices

### 1. Be Specific About Context Usage

❌ Bad:
```
Use the documents to answer questions.
```

✅ Good:
```
You have access to our product catalog. When answering questions about products, always include:
- Product name and code
- Current price
- Availability status
```

### 2. Define Response Format

❌ Bad:
```
Answer questions about our services.
```

✅ Good:
```
When describing our services:
- Start with a brief overview
- List key features from the context
- Mention pricing if available in the context
- End with a call-to-action (e.g., "Would you like to book this service?")
```

### 3. Handle Missing Information

❌ Bad:
```
Answer all questions from the documents.
```

✅ Good:
```
If the context contains relevant information, use it to provide a detailed answer.
If the context doesn't contain the information, say: "I don't have specific information about that in our knowledge base, but I can help you with general information or connect you with someone who can assist."
```

### 4. Match Company Tone

For a formal business:
```
Maintain a professional, courteous tone. Use formal language and avoid colloquialisms.
```

For a casual brand:
```
Keep responses friendly and conversational. It's okay to use casual language that matches our brand personality.
```

## Testing Custom Instructions

After setting custom instructions:

1. **Restart the agent**:
   ```bash
   # Stop the current agent (Ctrl+C)
   # Start again
   uv run 03_rag.py 1
   ```

2. **Check the logs** for confirmation:
   ```
   ✓ Loaded configuration for: Your Company
     - LLM Model: gpt-4o-mini
     - System Prompt: You are...
     - Using custom RAG instructions from database
     - RAG enabled with threshold: 0.7
   ```

3. **Test with questions** that should trigger RAG:
   - Ask about topics in your documents
   - Verify the agent follows your custom instructions
   - Check if the response format matches your requirements

## Examples by Industry

### E-commerce
```sql
UPDATE companies SET rag_system_instructions = 
'You have access to our product catalog and policies. When helping customers:
- For product questions: Include name, price, and key features from context
- For availability: Check context for stock status
- For shipping: Reference our shipping policy from context
- For returns: Use our return policy from context
- Always be helpful and aim to complete the sale'
WHERE id = 1;
```

### Healthcare
```sql
UPDATE companies SET rag_system_instructions = 
'You have access to our medical information and appointment system. Important:
- For medical questions: Only provide information directly from our approved documents
- Never diagnose or provide medical advice beyond what is in the context
- For appointments: Use the scheduling information from context
- Always recommend speaking with a healthcare provider for specific medical concerns
- Maintain patient privacy and confidentiality'
WHERE id = 2;
```

### Real Estate
```sql
UPDATE companies SET rag_system_instructions = 
'You have access to our property listings and company information. When assisting:
- For property inquiries: Include address, price, bedrooms, bathrooms from context
- For viewings: Reference our viewing policy from context
- For neighborhoods: Use location information from context
- Always ask qualifying questions to better match properties to client needs
- Maintain enthusiasm about properties while being factual'
WHERE id = 3;
```

## Troubleshooting

### Instructions Not Being Used

**Symptom**: Agent doesn't follow custom instructions

**Solutions**:
1. Verify the column is set:
   ```sql
   SELECT id, name, rag_system_instructions FROM companies WHERE id = 1;
   ```
2. Restart the agent (configuration is loaded at startup)
3. Check logs for "Using custom RAG instructions from database"

### Instructions Too Long

**Symptom**: Responses are slow or incomplete

**Solution**: Keep instructions concise (under 500 words). Focus on key behaviors.

### Conflicting Instructions

**Symptom**: Agent behavior is inconsistent

**Solution**: Ensure custom RAG instructions don't conflict with the main `system_prompt`. They should complement each other.

## Related Documentation

- `server/README_RAG_VOICE_AGENT.md` - Complete RAG system guide
- `docs/03_RAG_IMPLEMENTATION.md` - Technical implementation details
- `docs/COMPANY-CONFIG-INTEGRATION.md` - Company configuration guide


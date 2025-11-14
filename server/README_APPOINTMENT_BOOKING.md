# Appointment Booking Voice Agent (04_add_tooling_appointment.py)

This document explains how the appointment booking functionality is integrated into the voice agent using OpenAI function calling.

## Overview

The `04_add_tooling_appointment.py` voice agent extends `03_rag.py` with function calling capabilities, allowing the agent to:
1. Collect appointment information through natural conversation
2. Automatically book appointments into the database
3. Provide confirmation numbers to users
4. Handle booking errors gracefully

## How It Works

### 1. Function Calling Pipeline

The appointment booking system is integrated into the Pipecat pipeline:

```
User: "I'd like to book an appointment"
  ↓
STT → Context Aggregator → RAG Processor → LLM
  ↓
LLM decides to call book_appointment function
  ↓
book_appointment() → Supabase appointments table
  ↓
LLM receives confirmation → TTS → "Your appointment is booked, confirmation #42"
```

### 2. Information Collection

The agent collects three required pieces of information:
1. **Caller's full name**: "John Smith"
2. **Contact number**: "555-1234"
3. **Appointment details**: "Consultation next Tuesday at 2 PM"

The LLM is instructed to collect all information naturally before calling the function.

### 3. Database Integration

When the function is called:
1. Validates all parameters are provided
2. Inserts record into `appointments` table with `company_id` from config
3. Returns success/failure to LLM
4. LLM confirms booking with user

## Configuration

### Appointment Instructions

Located in `04_add_tooling_appointment.py`:

```python
APPOINTMENT_INSTRUCTIONS = """
You have the ability to book appointments for users. When a user wants to schedule an appointment, book something, or set up a meeting:

1. Collect the following information naturally in conversation:
   - Caller's full name
   - Caller's contact number (phone number)
   - Appointment details (what they want to book, preferred date/time, purpose, etc.)

2. Once you have all the required information, use the book_appointment function to create the appointment.

3. After successfully booking, confirm the appointment details with the user.

4. If any required information is missing, politely ask for it before booking.
"""
```

**Customizing**: Edit this constant to change how the agent collects information.

## Usage

### 1. Start the Server

```bash
# Start the agent for company ID 1
uv run 04_add_tooling_appointment.py 1

# With custom host/port
uv run 04_add_tooling_appointment.py 1 --host 0.0.0.0 --port 8000
```

### 2. Test Appointment Booking

**Example conversation**:

```
User: "I need to schedule an appointment"
Agent: "I'd be happy to help you schedule an appointment. May I have your full name?"
User: "Sarah Johnson"
Agent: "Thank you, Sarah. What's the best contact number for you?"
User: "555-9876"
Agent: "Great! What would you like to schedule?"
User: "I need a product demo on Friday at 3 PM"
Agent: "Perfect! I've booked your product demo for Friday at 3 PM. Your confirmation number is 15."
```

### 3. Verify in Database

```sql
SELECT * FROM appointments WHERE company_id = 1 ORDER BY created_at DESC LIMIT 5;
```

Expected result:
```
id | company_id | caller_name    | caller_contact_number | appointment_details
15 | 1          | Sarah Johnson  | 555-9876              | I need a product demo on Friday at 3 PM
```

## Code Structure

### Key Components

1. **APPOINTMENT_INSTRUCTIONS** (lines 78-92)
   - System prompt instructions for the LLM
   - Tells agent when and how to book appointments

2. **book_appointment()** (lines 240-295)
   - Async function that creates database records
   - First parameter: `FunctionCallParams` (required by Pipecat)
   - Remaining parameters: collected from user conversation
   - Uses `params.result_callback()` to return results to LLM

3. **Function Schema Definition** (lines 339-367)
   ```python
   tools = [
       {
           "type": "function",
           "function": {
               "name": "book_appointment",
               "description": "Book an appointment for a caller...",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "caller_name": {...},
                       "caller_contact_number": {...},
                       "appointment_details": {...}
                   },
                   "required": ["caller_name", "caller_contact_number", "appointment_details"]
               }
           }
       }
   ]
   ```
   - Defines function schema in OpenAI format
   - Tells OpenAI what functions are available and their parameters

4. **Function Registration** (line 329 + context creation)
   ```python
   # Step 1: Register the handler
   llm.register_function("book_appointment", book_appointment)

   # Step 2: Add schema to context
   context = OpenAILLMContext(
       [{"role": "user", "content": full_system_prompt}],
       tools=tools  # Add the function schema
   )
   ```
   - **Step 1**: Registers Python function handler with Pipecat
   - **Step 2**: Adds function schema to context so OpenAI knows about it
   - **Both steps required**: Handler alone won't work

5. **System Prompt Integration** (lines 333-338)
   ```python
   full_system_prompt = (
       system_prompt + "\n\n" + 
       rag_system_instructions + "\n\n" + 
       APPOINTMENT_INSTRUCTIONS + "\n\n" + 
       VOICE_OUTPUT_INSTRUCTIONS
   )
   ```

## Features Inherited from Previous Versions

This version includes all features from `03_rag.py`:

- ✅ **RAG (Retrieval-Augmented Generation)**: Searches company documents
- ✅ **Text Filtering**: Removes markdown and unwanted characters
- ✅ **Sentence Aggregation**: Buffers text into complete sentences
- ✅ **Company Configuration**: Loads settings from database
- ✅ **Custom RAG Instructions**: Per-company RAG behavior

**New in this version**:
- ✅ **Function Calling**: LLM can invoke Python functions
- ✅ **Appointment Booking**: Creates database records automatically
- ✅ **Database Writes**: Inserts into appointments table

## Troubleshooting

### Function Not Called

**Check**:
1. LLM model supports function calling (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
2. Function handler is registered: `llm.register_function("book_appointment", book_appointment)`
3. Function schema is added to context: `OpenAILLMContext(..., tools=tools)`
4. Instructions are clear enough for LLM to understand

**Common mistake**: Only registering the handler without adding the schema to the context. Both are required!

**Logs to look for**:
```
INFO: Booking appointment for Sarah Johnson (555-9876)
INFO: ✓ Appointment booked successfully with ID: 15
```

**If function is not being called**:
- Check that `tools` array is defined with the function schema
- Verify `tools=tools` is passed to `OpenAILLMContext()`
- Look for OpenAI API errors in logs

### Database Insertion Fails

**Check**:
1. Supabase connection is working
2. `company_id` is valid in database
3. All required fields are provided

**Debug**:
```bash
# Check error logs
tail -f error.log | grep "appointment"
```

### Missing Information

If agent tries to book without collecting all info, make instructions more explicit:

```python
APPOINTMENT_INSTRUCTIONS = """
CRITICAL: You MUST collect ALL three pieces of information before calling book_appointment:
1. Full name (first and last)
2. Complete phone number
3. Appointment details (date, time, purpose)

Do NOT call the function until you have ALL THREE.
"""
```

## Next Steps

1. **Test various scenarios**: Try different ways users might request appointments
2. **Monitor database**: Check appointments table regularly
3. **Customize instructions**: Adjust based on your use case
4. **Add validation**: Implement phone number/email validation
5. **Extend functionality**: Add cancel/reschedule functions

## Related Documentation

- [Appointment Booking Guide](../docs/04_APPOINTMENT_BOOKING.md) - Comprehensive guide
- [Pipecat Function Calling](https://docs.pipecat.ai/guides/learn/function-calling) - Official docs
- [Database Schema](../docs/SETUP.md#database-schema-overview) - Table structure
- [SQL Helpers](../docs/SQL-HELPERS.md) - Useful queries


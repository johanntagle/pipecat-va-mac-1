# Appointment Booking with Function Calling

## Overview

The `04_add_tooling_appointment.py` server adds **function calling** capabilities to enable the voice agent to book appointments directly into the database when users request to schedule something.

This implementation uses OpenAI's function calling feature through Pipecat to allow the LLM to invoke a Python function that creates appointment records in the Supabase `appointments` table.

## Key Features

- **Natural conversation flow**: Agent collects appointment information through dialogue
- **Automatic database insertion**: Appointments are saved to Supabase automatically
- **Confirmation numbers**: Users receive appointment IDs for reference
- **Error handling**: Graceful handling of booking failures
- **No client-side changes needed**: Works with existing voice client

## Architecture

### Components

1. **APPOINTMENT_INSTRUCTIONS constant**: System prompt instructions for the LLM
2. **book_appointment() function**: Python function that creates database records
3. **Function registration**: Registered with OpenAI LLM service via `llm.register_function()`
4. **Database integration**: Uses Supabase client to insert appointments

### How It Works

```
User: "I'd like to book an appointment"
  ↓
Agent: Collects name, phone, details through conversation
  ↓
LLM: Decides to call book_appointment function
  ↓
book_appointment(): Inserts record into appointments table
  ↓
Agent: Confirms booking with appointment ID
```

## Implementation Details

### 1. Appointment Instructions (Lines 78-92)

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

**Purpose**: Instructs the LLM on when and how to use the appointment booking function.

### 2. Book Appointment Function (Lines 240-295)

```python
async def book_appointment(
    params: FunctionCallParams,
    caller_name: str,
    caller_contact_number: str,
    appointment_details: str
):
    """
    Book an appointment for a caller.
    
    Args:
        params: Function call parameters from Pipecat
        caller_name: The full name of the caller
        caller_contact_number: The caller's phone number
        appointment_details: Details about the appointment (date, time, purpose, etc.)
    """
```

**Key Points**:
- First parameter must be `FunctionCallParams` (required by Pipecat)
- Remaining parameters match the function schema that OpenAI sees
- Uses `params.result_callback()` to return results to the LLM
- Inserts into `appointments` table with `company_id` from global config
- Sets `call_id` to `None` (not tracked in this version)

### 3. Function Schema Definition (Lines 339-367)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a caller. Use this when the user wants to schedule an appointment, make a booking, or reserve a time slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_name": {
                        "type": "string",
                        "description": "The full name of the person booking the appointment (first and last name)"
                    },
                    "caller_contact_number": {
                        "type": "string",
                        "description": "The caller's phone number or contact number"
                    },
                    "appointment_details": {
                        "type": "string",
                        "description": "Complete details about the appointment including date, time, purpose, and any other relevant information"
                    }
                },
                "required": ["caller_name", "caller_contact_number", "appointment_details"]
            }
        }
    }
]
```

**Purpose**: Defines the function schema in OpenAI format. This schema is sent to OpenAI so the LLM knows:
- When to call the function (based on description)
- What parameters to provide
- Which parameters are required

### 4. Function Registration (Line 329)

```python
# Step 1: Register the handler
llm.register_function("book_appointment", book_appointment)

# Step 2: Add schema to context
context = OpenAILLMContext(
    [{"role": "user", "content": full_system_prompt}],
    tools=tools  # Add the function schema
)
```

**Purpose**: Two-step registration process:
1. **Register handler**: Tells Pipecat which Python function to call when OpenAI invokes `book_appointment`
2. **Add schema to context**: Tells OpenAI what functions are available and how to call them

**Important**: Both steps are required. The handler alone won't work because OpenAI won't know the function exists.

### 5. System Prompt Integration (Lines 333-338)

```python
full_system_prompt = (
    system_prompt + "\n\n" + 
    rag_system_instructions + "\n\n" + 
    APPOINTMENT_INSTRUCTIONS + "\n\n" + 
    VOICE_OUTPUT_INSTRUCTIONS
)
```

**Purpose**: Combines all instruction sets into a single system prompt.

## Database Schema

The function inserts into the `appointments` table:

```sql
CREATE TABLE appointments (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  call_id BIGINT REFERENCES calls(id) ON DELETE SET NULL,
  caller_name TEXT NOT NULL,
  caller_contact_number TEXT NOT NULL,
  appointment_details TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Fields populated by function**:
- `company_id`: From `COMPANY_CONFIG["company_id"]`
- `call_id`: Set to `None` (not tracked in this version)
- `caller_name`: From function parameter
- `caller_contact_number`: From function parameter
- `appointment_details`: From function parameter
- `created_at`, `updated_at`: Auto-populated by database

## Testing Instructions

### 1. Start the Server

```bash
cd server
uv run 04_add_tooling_appointment.py 1
```

### 2. Test Appointment Booking

**Example conversation**:

```
User: "I'd like to book an appointment"
Agent: "I'd be happy to help you book an appointment. May I have your full name?"
User: "John Smith"
Agent: "Thank you, John. What's the best contact number for you?"
User: "555-1234"
Agent: "Great! What would you like to schedule?"
User: "I need a consultation next Tuesday at 2 PM"
Agent: "Perfect! I've booked your consultation for next Tuesday at 2 PM. 
       Your confirmation number is 42."
```

### 3. Verify in Database

```sql
SELECT * FROM appointments ORDER BY created_at DESC LIMIT 5;
```

You should see the newly created appointment with:
- Caller name: "John Smith"
- Contact number: "555-1234"
- Details: "I need a consultation next Tuesday at 2 PM"

## Troubleshooting

### Function Not Being Called

**Symptom**: Agent doesn't book appointments even when user requests it

**Possible causes**:
1. **LLM model doesn't support function calling**: Ensure you're using `gpt-4o`, `gpt-4o-mini`, or `gpt-3.5-turbo`
2. **Function not registered**: Check logs for function registration confirmation
3. **Instructions unclear**: The LLM might not understand when to call the function

**Solution**:
```bash
# Check logs for:
# "Registered function: book_appointment"
# "Function call: book_appointment"
```

### Database Insertion Fails

**Symptom**: Function is called but appointment not saved

**Check**:
1. Supabase connection is working
2. `company_id` is valid
3. All required fields are provided

**Debug**:
```python
# Check logs for:
logger.info(f"Booking appointment for {caller_name} ({caller_contact_number})")
logger.error(f"Error booking appointment: {e}")
```

### Missing Information

**Symptom**: Agent tries to book without collecting all information

**Solution**: Update `APPOINTMENT_INSTRUCTIONS` to be more explicit:
```python
APPOINTMENT_INSTRUCTIONS = """
IMPORTANT: You MUST collect ALL of the following before calling book_appointment:
1. Caller's FULL name (first and last)
2. Caller's phone number (complete, with area code)
3. Appointment details including:
   - Preferred date
   - Preferred time
   - Purpose/reason for appointment

Do NOT call book_appointment until you have ALL three pieces of information.
"""
```

## Advanced Customization

### Adding More Fields

To collect additional information (e.g., email, appointment type):

1. **Update function signature**:
```python
async def book_appointment(
    params: FunctionCallParams,
    caller_name: str,
    caller_contact_number: str,
    caller_email: str,  # New field
    appointment_type: str,  # New field
    appointment_details: str
):
```

2. **Update database insertion**:
```python
response = supabase.table("appointments").insert({
    "company_id": company_id,
    "call_id": None,
    "caller_name": caller_name,
    "caller_contact_number": caller_contact_number,
    "caller_email": caller_email,  # New field
    "appointment_type": appointment_type,  # New field
    "appointment_details": appointment_details,
}).execute()
```

3. **Update instructions**:
```python
APPOINTMENT_INSTRUCTIONS = """
...
- Caller's email address
- Type of appointment (consultation, follow-up, etc.)
...
"""
```

### Validating Input

Add validation before database insertion:

```python
async def book_appointment(
    params: FunctionCallParams,
    caller_name: str,
    caller_contact_number: str,
    appointment_details: str
):
    try:
        # Validate phone number format
        import re
        if not re.match(r'^\d{3}-\d{4}$|^\d{10}$', caller_contact_number):
            await params.result_callback({
                "success": False,
                "error": "Invalid phone number format. Please provide a 10-digit number."
            })
            return

        # Validate name is not empty
        if not caller_name or len(caller_name.strip()) < 2:
            await params.result_callback({
                "success": False,
                "error": "Please provide a valid name."
            })
            return

        # Continue with insertion...
```

### Sending Confirmation Emails

Integrate with email service after booking:

```python
async def book_appointment(...):
    # ... existing code ...

    if response.data and len(response.data) > 0:
        appointment_id = response.data[0]["id"]

        # Send confirmation email
        await send_confirmation_email(
            to=caller_email,
            appointment_id=appointment_id,
            details=appointment_details
        )

        await params.result_callback({
            "success": True,
            "appointment_id": appointment_id,
            "message": f"Appointment booked! Confirmation email sent to {caller_email}"
        })
```

## Differences from Previous Versions

| Feature | 03_rag.py | 04_add_tooling_appointment.py |
|---------|-----------|-------------------------------|
| RAG | ✅ Yes | ✅ Yes |
| Text Filtering | ✅ Yes | ✅ Yes |
| Sentence Aggregation | ✅ Yes | ✅ Yes |
| Function Calling | ❌ No | ✅ Yes (appointment booking) |
| Database Writes | ❌ No | ✅ Yes (appointments table) |

## Next Steps

1. **Test thoroughly**: Try various appointment booking scenarios
2. **Monitor logs**: Watch for function calls and database insertions
3. **Verify data**: Check appointments table regularly
4. **Customize**: Adjust instructions and validation as needed
5. **Extend**: Add more functions (cancel appointment, reschedule, etc.)

## Related Documentation

- [Pipecat Function Calling Guide](https://docs.pipecat.ai/guides/learn/function-calling)
- [Database Schema](./SETUP.md#database-schema-overview)
- [SQL Helpers](./SQL-HELPERS.md)
- [Company Configuration](./COMPANY-CONFIG-INTEGRATION.md)




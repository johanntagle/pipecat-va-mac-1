# Company Configuration Integration

This document describes how the voice agent server (`02_db_backed.py`) integrates with the Supabase database to fetch company-specific configurations.

## Overview

The voice agent accepts a `company_id` as a command-line argument at startup and loads the following configuration from the `companies` table:
- OpenAI API key
- System prompt
- LLM model

This allows running separate voice agent instances for different companies, each with their own configuration.

## Changes Made

### 1. Server Changes (`server/02_db_backed.py`)

#### Added Dependencies
- `supabase` Python client library
- `HTTPException` from FastAPI for error handling

#### Global Company Configuration
```python
# Global company configuration (loaded at startup)
COMPANY_CONFIG = {
    "openai_api_key": "",
    "system_prompt": "",
    "llm_model": "",
    "company_name": "",
}
```

#### Supabase Client Initialization
```python
supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)
```

#### Load Company Configuration Function
Loads configuration from database at startup:
```python
def load_company_config(company_id: int):
    """Load company configuration from database at startup."""
    try:
        logger.info(f"Loading company configuration for ID: {company_id}")
        response = supabase.table("companies").select("*").eq("id", company_id).execute()

        if not response.data or len(response.data) == 0:
            logger.error(f"Company with id {company_id} not found")
            sys.exit(1)

        company = response.data[0]
        COMPANY_CONFIG["openai_api_key"] = company["openai_api_key"]
        COMPANY_CONFIG["system_prompt"] = company["system_prompt"]
        COMPANY_CONFIG["llm_model"] = company["llm_model"]
        COMPANY_CONFIG["company_name"] = company["name"]

        logger.info(f"✓ Loaded configuration for: {company['name']}")

    except Exception as e:
        logger.error(f"Error loading company configuration: {e}")
        sys.exit(1)
```

#### Modified `run_bot` Function
The function now accepts company-specific configuration:
```python
async def run_bot(webrtc_connection, openai_api_key: str, system_prompt: str, llm_model: str):
    # Uses the provided parameters instead of environment variables
    llm = OpenAILLMService(
        api_key=openai_api_key,
        model=llm_model,
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    )

    context = OpenAILLMContext([{
        "role": "user",
        "content": system_prompt,
    }])
```

#### Modified `/api/offer` Endpoint
The endpoint now uses the global configuration loaded at startup:
```python
@app.post("/api/offer")
async def offer(request: dict, background_tasks: BackgroundTasks):
    pc_id = request.get("pc_id")

    # Use the global company configuration loaded at startup
    openai_api_key = COMPANY_CONFIG["openai_api_key"]
    system_prompt = COMPANY_CONFIG["system_prompt"]
    llm_model = COMPANY_CONFIG["llm_model"]

    # ... WebRTC connection setup ...

    # Pass to run_bot
    background_tasks.add_task(run_bot, pipecat_connection, openai_api_key, system_prompt, llm_model)
```

#### Command-Line Argument Parser
Added `company_id` as a required positional argument:
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Bot Runner")
    parser.add_argument(
        "company_id", type=int, help="Company ID to load configuration from database"
    )
    parser.add_argument(
        "--host", default="localhost", help="Host for HTTP server (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=7860, help="Port for HTTP server (default: 7860)"
    )
    args = parser.parse_args()

    # Load company configuration before starting server
    load_company_config(args.company_id)

    uvicorn.run(app, host=args.host, port=args.port)
```

### 2. Client Changes

No changes to the client - it remains unchanged and connects to `/api/offer` as before.

### 3. Environment Configuration (`server/env.example`)

Added Supabase configuration:
```env
# Supabase Configuration
SUPABASE_URL="http://127.0.0.1:54321"
SUPABASE_ANON_KEY=""
```

### 4. Dependencies (`server/pyproject.toml`)

Added `supabase` to the dependencies list.

## Usage

### 1. Set Up Environment Variables

Create `server/.env` with:
```env
SUPABASE_URL="http://127.0.0.1:54321"
SUPABASE_ANON_KEY="your-anon-key-here"
LLM_BASE_URL="https://api.openai.com/v1"
```

### 2. Install Dependencies

```bash
cd server
uv sync
# or
pip install supabase
```

### 3. Start the Server with Company ID

Start the server with a specific company ID as an argument:

```bash
cd server

# Start with company ID 1 (Acme Corporation)
uv run python 02_db_backed.py 1

# Or with company ID 2 (TechStart Inc)
uv run python 02_db_backed.py 2

# Or with company ID 3 (Global Services Ltd)
uv run python 02_db_backed.py 3
```

You should see output like:
```
Loading company configuration for ID: 1
✓ Loaded configuration for: Acme Corporation
  - LLM Model: gpt-4o-mini
  - System Prompt: You are a helpful AI assistant for Acme Corporation...
```

### 4. Access the Client

Open the client in your browser:
```
http://localhost:3000/
```

The client will connect to the server which is configured for the company ID you specified at startup.

## Database Schema

The `companies` table must have these fields:
- `id` (BIGINT) - Primary key
- `openai_api_key` (TEXT) - OpenAI API key for this company
- `system_prompt` (TEXT) - System prompt for the voice agent
- `llm_model` (TEXT) - LLM model to use (e.g., "gpt-4o-mini", "gpt-4o")

## Testing

### 1. Verify the Configuration is Working

1. **Check Server Logs**: Look for the startup log message showing which company config was loaded
2. **Test the Voice Agent**: The agent should use the system prompt from the database
3. **Test Different Companies**: Stop the server and restart with a different company ID to test different configurations

### 2. Test Error Handling

**Invalid Company ID:**
```bash
uv run python 02_db_backed.py 999
```
Should exit with error: "Company with id 999 not found"

**Missing Company ID:**
```bash
uv run python 02_db_backed.py
```
Should show usage error: "the following arguments are required: company_id"

## Error Handling

The server exits with error code 1 if:
- Company ID is not found in the database
- Database connection fails
- Error loading company configuration


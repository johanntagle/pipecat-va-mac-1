import argparse
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List

# Add local pipecat to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipecat", "src"))

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from loguru import logger
from supabase import create_client, Client
import openai

from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v2 import LocalSmartTurnAnalyzerV2
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.llm_service import FunctionCallParams

from pipecat.services.whisper.stt import WhisperSTTServiceMLX, MLXModel
from pipecat.transports.base_transport import TransportParams
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.transports.network.small_webrtc import SmallWebRTCTransport
from pipecat.transports.network.webrtc_connection import IceServer, SmallWebRTCConnection
from pipecat.processors.aggregators.llm_response import LLMUserAggregatorParams
from pipecat.frames.frames import Frame, TextFrame, LLMMessagesFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from tts_mlx_isolated import TTSMLXIsolated
from text_filter import LLMTextFilter
from sentence_aggregator import SentenceAggregator

load_dotenv(override=True)

app = FastAPI()

pcs_map: Dict[str, SmallWebRTCConnection] = {}

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)

# Global preloaded models (initialized at startup)
PRELOADED_MODELS = {
    "smart_turn": None,  # Will hold preloaded LocalSmartTurnAnalyzerV2
    "vad": None,  # Will hold preloaded SileroVADAnalyzer
}

# Global company configuration (loaded at startup)
COMPANY_CONFIG = {
    "openai_api_key": "",
    "system_prompt": "",
    "llm_model": "",
    "company_name": "",
    "company_id": 0,
    "rag_system_instructions": "",
}

# Additional system prompt instructions for voice output formatting
VOICE_OUTPUT_INSTRUCTIONS = """
Do not format your answer in any markdown or include "asterisk" or "star" or any symbols that should not be read or spoken.
When giving phone numbers, give the numbers to be read e.g. ZERO NINE ONE SEVEN, etc.
When giving time, give the time to be read e.g. TEN THIRTY, etc.
"""

# Default RAG system instructions (used if company doesn't have custom instructions)
RAG_SYSTEM_INSTRUCTIONS = """
You have access to a knowledge base of company documents.
When answering questions, relevant information from these documents will be provided to you as context.
Use this context to provide accurate, specific answers based on the company's information.
If the context doesn't contain relevant information for a question, rely on your general knowledge but mention that you're not finding specific company information about that topic.
"""

# Appointment booking instructions
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

# RAG configuration
RAG_CONFIG = {
    "match_threshold": 0.7,  # Minimum similarity score (0-1)
    "match_count": 3,  # Number of chunks to retrieve
    "embedding_model": "text-embedding-3-small",  # OpenAI embedding model
}

ice_servers = [
    IceServer(
        urls="stun:stun.l.google.com:19302",
    )
]


class RAGProcessor(FrameProcessor):
    """
    Processor that intercepts LLM messages and augments them with RAG context.
    """

    def __init__(self, company_id: int, api_key: str):
        super().__init__()
        self._company_id = company_id
        self._api_key = api_key

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # Intercept LLM messages going to the LLM
        if isinstance(frame, LLMMessagesFrame):
            messages = frame.messages

            # Get the last user message
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            if user_messages:
                last_user_message = user_messages[-1]
                user_text = last_user_message.get("content", "")

                # Search for relevant RAG chunks
                logger.debug(f"Searching RAG for: {user_text[:100]}...")
                chunks = await search_rag_chunks(user_text, self._company_id, self._api_key)

                # If we found relevant chunks, augment the message
                if chunks:
                    rag_context = format_rag_context(chunks)
                    augmented_content = f"{rag_context}\nUser question: {user_text}"

                    # Update the last user message with RAG context
                    last_user_message["content"] = augmented_content
                    logger.info(f"Augmented user message with {len(chunks)} RAG chunks")

        await self.push_frame(frame, direction)


def generate_embedding(text: str, api_key: str) -> List[float]:
    """
    Generate embedding for text using OpenAI's embedding model.

    Args:
        text: The text to embed
        api_key: OpenAI API key

    Returns:
        List of floats representing the embedding
    """
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model=RAG_CONFIG["embedding_model"],
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def search_rag_chunks(query: str, company_id: int, api_key: str) -> List[Dict]:
    """
    Search for relevant RAG chunks using vector similarity.

    Args:
        query: The search query
        company_id: The company ID to filter by
        api_key: OpenAI API key for generating embeddings

    Returns:
        List of relevant chunks with their text and metadata
    """
    try:
        # Generate embedding for the query
        logger.debug(f"Generating embedding for query: {query[:100]}...")
        query_embedding = generate_embedding(query, api_key)

        # Search for similar chunks using vector similarity
        # Using cosine distance operator <=> for similarity search
        response = supabase.rpc(
            "search_rag_chunks",
            {
                "query_embedding": query_embedding,
                "company_id": company_id,
                "match_threshold": RAG_CONFIG["match_threshold"],
                "match_count": RAG_CONFIG["match_count"],
            }
        ).execute()

        if response.data:
            logger.info(f"Found {len(response.data)} relevant chunks for query")
            return response.data
        else:
            logger.debug("No relevant chunks found")
            return []

    except Exception as e:
        logger.error(f"Error searching RAG chunks: {e}")
        # Return empty list on error to allow conversation to continue
        return []


def format_rag_context(chunks: List[Dict]) -> str:
    """
    Format RAG chunks into a context string for the LLM.

    Args:
        chunks: List of chunk dictionaries with text and metadata

    Returns:
        Formatted context string
    """
    if not chunks:
        return ""

    context_parts = ["Here is relevant information from the company's knowledge base:\n"]

    for i, chunk in enumerate(chunks, 1):
        chunk_text = chunk.get("chunk_text", "")
        metadata = chunk.get("metadata", {})
        file_name = metadata.get("file_name", "Unknown")
        similarity = chunk.get("similarity", 0)

        context_parts.append(f"\n[Source {i}: {file_name} (relevance: {similarity:.2f})]")
        context_parts.append(chunk_text)

    context_parts.append("\n---\n")
    return "\n".join(context_parts)


async def book_appointment(
    function_name: str,
    tool_call_id: str,
    arguments: dict,
    llm: Any,
    context: Any,
    result_callback: Any
):
    """
    Book an appointment for a caller.

    This function is called by the LLM when a user wants to schedule an appointment.
    It creates a record in the appointments table.

    Args:
        function_name: Name of the function being called
        tool_call_id: Unique ID for this function call
        arguments: Dictionary containing caller_name, caller_contact_number, appointment_details
        llm: The LLM service instance
        context: The conversation context
        result_callback: Callback to return results to the LLM
    """
    try:
        # Extract arguments from the dict
        caller_name = arguments.get("caller_name", "")
        caller_contact_number = arguments.get("caller_contact_number", "")
        appointment_details = arguments.get("appointment_details", "")

        company_id = COMPANY_CONFIG["company_id"]

        logger.info(f"Booking appointment for {caller_name} ({caller_contact_number})")
        logger.debug(f"Appointment details: {appointment_details}")

        # Insert appointment into database
        response = supabase.table("appointments").insert({
            "company_id": company_id,
            "call_id": None,  # We don't track call_id in this version
            "caller_name": caller_name,
            "caller_contact_number": caller_contact_number,
            "appointment_details": appointment_details,
        }).execute()

        if response.data and len(response.data) > 0:
            appointment_id = response.data[0]["id"]
            logger.info(f"✓ Appointment booked successfully with ID: {appointment_id}")

            # Return success message to LLM
            await result_callback({
                "success": True,
                "appointment_id": appointment_id,
                "message": f"Appointment successfully booked for {caller_name}. Confirmation number: {appointment_id}"
            })
        else:
            logger.error("Failed to book appointment: No data returned from database")
            await result_callback({
                "success": False,
                "error": "Failed to create appointment record"
            })

    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        await result_callback({
            "success": False,
            "error": f"Failed to book appointment: {str(e)}"
        })


async def run_bot(webrtc_connection, openai_api_key: str, system_prompt: str, llm_model: str, company_id: int, rag_system_instructions: str):
    # Use preloaded models for instant startup
    logger.info("Using preloaded VAD and Smart Turn models for fast startup")

    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=PRELOADED_MODELS["vad"],
            turn_analyzer=PRELOADED_MODELS["smart_turn"],
        ),
    )

    stt = WhisperSTTServiceMLX(model=MLXModel.LARGE_V3_TURBO_Q4)
    tts = TTSMLXIsolated(
        model="mlx-community/Kokoro-82M-bf16",
        voice="af_heart",
        sample_rate=24000,
        aggregate_sentences=False  # We use custom SentenceAggregator instead
    )

    llm = OpenAILLMService(
        api_key=openai_api_key,
        model=llm_model,
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    )

    # Register the appointment booking function handler
    llm.register_function("book_appointment", book_appointment)

    # Combine system prompt with RAG, appointment, and voice instructions
    # Use company-specific RAG instructions if provided, otherwise use default
    full_system_prompt = (
        system_prompt + "\n\n" +
        rag_system_instructions + "\n\n" +
        APPOINTMENT_INSTRUCTIONS + "\n\n" +
        VOICE_OUTPUT_INSTRUCTIONS
    )

    # Define the function schema for OpenAI
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

    context = OpenAILLMContext(
        [
            {
                "role": "user",
                "content": full_system_prompt,
            }
        ],
        tools=tools  # Add the function schema to the context
    )
    context_aggregator = llm.create_context_aggregator(
        context,
        # Whisper local service isn't streaming, so it delivers the full text all at
        # once, after the UserStoppedSpeaking frame. Set aggregation_timeout to a
        # a de minimus value since we don't expect any transcript aggregation to be
        # necessary.
        user_params=LLMUserAggregatorParams(aggregation_timeout=0.05),
    )

    #
    # RTVI events for Pipecat client UI
    #
    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Text filter to clean LLM output before TTS
    text_filter = LLMTextFilter()

    # Sentence aggregator to buffer text into sentences and flush on completion
    sentence_aggregator = SentenceAggregator()

    # RAG processor to augment user messages with relevant context
    rag_processor = RAGProcessor(company_id=company_id, api_key=openai_api_key)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            rtvi,
            context_aggregator.user(),
            rag_processor,  # Add RAG context before LLM
            llm,
            text_filter,  # Clean text before sentence aggregation
            sentence_aggregator,  # Aggregate into sentences, flush on LLMFullResponseEndFrame
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        await rtvi.set_bot_ready()
        # Kick off the conversation
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        print(f"Participant joined: {participant}")
        await transport.capture_participant_transcription(participant["id"])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        print(f"Participant left: {participant}")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)


@app.post("/api/offer")
async def offer(request: dict, background_tasks: BackgroundTasks):
    pc_id = request.get("pc_id")

    # Use the global company configuration loaded at startup
    openai_api_key = COMPANY_CONFIG["openai_api_key"]
    system_prompt = COMPANY_CONFIG["system_prompt"]
    llm_model = COMPANY_CONFIG["llm_model"]
    company_id = COMPANY_CONFIG["company_id"]
    rag_system_instructions = COMPANY_CONFIG["rag_system_instructions"]

    if pc_id and pc_id in pcs_map:
        pipecat_connection = pcs_map[pc_id]
        logger.info(f"Reusing existing connection for pc_id: {pc_id}")
        await pipecat_connection.renegotiate(
            sdp=request["sdp"],
            type=request["type"],
            restart_pc=request.get("restart_pc", False),
        )
    else:
        pipecat_connection = SmallWebRTCConnection(ice_servers)
        await pipecat_connection.initialize(sdp=request["sdp"], type=request["type"])

        @pipecat_connection.event_handler("closed")
        async def handle_disconnected(webrtc_connection: SmallWebRTCConnection):
            logger.info(f"Discarding peer connection for pc_id: {webrtc_connection.pc_id}")
            pcs_map.pop(webrtc_connection.pc_id, None)

        # Run bot with company-specific configuration including RAG
        background_tasks.add_task(run_bot, pipecat_connection, openai_api_key, system_prompt, llm_model, company_id, rag_system_instructions)

    answer = pipecat_connection.get_answer()
    # Updating the peer connection inside the map
    pcs_map[answer["pc_id"]] = pipecat_connection

    return answer


def preload_models():
    """Preload heavy models at startup to avoid delays during first connection."""
    import time

    logger.info("=" * 60)
    logger.info("PRELOADING MODELS FOR FAST STARTUP")
    logger.info("=" * 60)

    # Preload VAD model
    logger.info("1/2 Loading Silero VAD model...")
    start = time.time()
    PRELOADED_MODELS["vad"] = SileroVADAnalyzer(params=VADParams(stop_secs=0.2))
    elapsed = time.time() - start
    logger.info(f"  ✓ VAD loaded in {elapsed:.2f}s")

    # Preload Smart Turn model (this is the slow one - 20+ seconds)
    logger.info("2/2 Loading Local Smart Turn v2 model (this may take 20-30 seconds)...")
    start = time.time()
    PRELOADED_MODELS["smart_turn"] = LocalSmartTurnAnalyzerV2(
        smart_turn_model_path="",  # Download from HuggingFace
        params=SmartTurnParams(),
    )
    elapsed = time.time() - start
    logger.info(f"  ✓ Smart Turn loaded in {elapsed:.2f}s")

    logger.info("=" * 60)
    logger.info("✓ ALL MODELS PRELOADED - Ready for instant connections!")
    logger.info("=" * 60)


def load_company_config(company_id: int):
    """Load company configuration from database at startup."""
    try:
        logger.info(f"Loading company configuration for ID: {company_id}")
        response = supabase.table("companies").select("*").eq("id", company_id).execute()

        if not response.data or len(response.data) == 0:
            logger.error(f"Company with id {company_id} not found")
            sys.exit(1)

        company = response.data[0]
        COMPANY_CONFIG["company_id"] = company_id
        COMPANY_CONFIG["openai_api_key"] = company["openai_api_key"]
        COMPANY_CONFIG["system_prompt"] = company["system_prompt"]
        COMPANY_CONFIG["llm_model"] = company["llm_model"]
        COMPANY_CONFIG["company_name"] = company["name"]

        # Load RAG system instructions (use default if not set)
        rag_instructions = company.get("rag_system_instructions")
        if rag_instructions:
            COMPANY_CONFIG["rag_system_instructions"] = rag_instructions
            logger.info(f"  - Using custom RAG instructions from database")
        else:
            COMPANY_CONFIG["rag_system_instructions"] = RAG_SYSTEM_INSTRUCTIONS
            logger.info(f"  - Using default RAG instructions")

        logger.info(f"✓ Loaded configuration for: {company['name']}")
        logger.info(f"  - LLM Model: {company['llm_model']}")
        logger.info(f"  - System Prompt: {company['system_prompt'][:100]}...")
        logger.info(f"  - RAG enabled with threshold: {RAG_CONFIG['match_threshold']}")

    except Exception as e:
        logger.error(f"Error loading company configuration: {e}")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # Run app
    coros = [pc.disconnect() for pc in pcs_map.values()]
    await asyncio.gather(*coros)
    pcs_map.clear()


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

    # Preload heavy models before starting server
    # This takes ~20-30 seconds but only happens once at startup
    # After this, all connections will be instant!
    preload_models()

    uvicorn.run(app, host=args.host, port=args.port)

import argparse
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict

# Add local pipecat to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipecat", "src"))

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from loguru import logger

from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v2 import LocalSmartTurnAnalyzerV2
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.openai.llm import OpenAILLMService

from pipecat.services.whisper.stt import WhisperSTTServiceMLX, MLXModel
from pipecat.transports.base_transport import TransportParams
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.transports.network.small_webrtc import SmallWebRTCTransport
from pipecat.transports.network.webrtc_connection import IceServer, SmallWebRTCConnection
from pipecat.processors.aggregators.llm_response import LLMUserAggregatorParams

from tts_mlx_isolated import TTSMLXIsolated

load_dotenv(override=True)

app = FastAPI()

pcs_map: Dict[str, SmallWebRTCConnection] = {}

ice_servers = [
    IceServer(
        urls="stun:stun.l.google.com:19302",
    )
]


SYSTEM_INSTRUCTION = """
You are the concierge for Tomatito Sexy Tapas Bar—a vibrant, funky Spanish-inspired venue that brings the energy of 80’s tapas bars into a modern, upbeat setting. Your dual role is to delight guests with engaging details about our diverse menu and to efficiently handle table bookings and reservations. Always remember that all prices are VAT inclusive and subject to a 7.5% service charge.
Be Engaging & Informative:  
  Use a warm, friendly, and upbeat tone that reflects the sexy, modern, and fun ambiance of Tomatito.  
  Provide clear, succinct answers for both menu details and reservation processes while also being ready to expand upon any menu category if further details are requested.
  Do not format your answer in any markdown or include "asterisk" or "star" symbols. When giving phone numbers, give the numbers to be read e.g. ZERO NINE ONE SEVEN, etc
Pretend to be human and introduce yourself as Lenny then wait for the user to say something.

1. Menu Inquiries & Highlights

When answering questions about our menu, include these detailed highlights:

- Drinks, Beers & Cocktails:  
  • Offerings range from refreshing soft drinks and juices to creative cocktails like “Gazing into the Sunset” and classic mixes.  
  • Highlight our “Make your own Gin & Tonic” option with customizable choices of gins, fruits, spices, and herbs.

- Ala Carte Selections:  
  • Feature our signature platters such as the Tabla de Quesos (Cheese Platter), Tabla de Embutidos (Cold Cuts Platter), and the Tabla Mixta de Embutidos y Quesos (Mixed Platter) for a taste of Spanish charcuterie and cheeses.

- Tapas & Pintxos:  
  • Spotlight our famous “Sexy Bites” which include items like Bombas de Jamon (ham bombs with Manchego cheese cream and paprika), Tuna TNT (tuna tataki with a spicy twist), Mini Pork Buns, and Chorizo and Manchego Air Baguette.  
  • Emphasize that many items offer the option to add extra pieces for an even bigger flavor explosion.

- Chef’s Recommendations:  
  • Mention standouts such as Patatas Bravas (crispy potatoes with chili oil and aioli), Gambas al Ajillo (garlicky shrimps with white wine), Sexy Chicken Fingers (served with honey mustard sauce), and Carpaccio de Solomillo (beef carpaccio with truffle sour cream and jalapeño).

- Paellas:  
  • Our paella selection includes a variety of choices—from Paella Iberica (with Iberian pork and ham) and Paella Negra (featuring baby squid and a rich aioli sauce) to seafood favorites like Paella El Chiringuito and even a special Paella Cochinillo (suckling pig) for a grand dining experience.

- Pescados y Carnes (Fish and Meat):  
  • Highlights include Sexy Fish & Chips (Spanish cod with kimchi and caper sauce), A5 Wagyu Sirloin (served on a hot stone plate), Beef Salpicao, and other hearty meat dishes such as Callos con Garbanzos and Flamenquin.

- Good for Sharing:  
  • Ideal for groups, options like Pollo Asado (roasted chicken), Solomillo a la Parrilla (grilled tenderloin with potatoes), Cochinillo Segoviano (roasted suckling pig), and Chuleton (USDA Prime Ribeye) are designed to be shared and enjoyed together.

- Dulce Tentación (Desserts):  
  • End your meal on a sweet note with treats such as Volcan de Chocolate (chocolate coulant with vanilla ice cream), Tarta de Queso Vasco (Spanish cheesecake with blueberry stew), Churros Dos Salsas, Bollycao, Flan de Yema, and assorted ice cream selections.

Feel free to mention that these highlights represent the core of our menu as featured in the menu pages 8–18. Encourage guests to ask for further details or recommendations based on their taste preferences.

2. Reservations & Bookings

- Branch Details & Hours:  
  Provide location-specific reservation details when asked:
  - BGC:  
    - Address: Ground Floor, BGC Corporate Center, 30th Street corner 11th Avenue, Taguig City  
    - Contact: 0286622523, 0917 524 5058  
    - Emails: ask@bistro.com.ph; tomatitobgc@bistro.com.ph  
    - Hours: Monday–Thursday & Sunday: 11:00 AM–10:00 PM; Friday–Saturday: 11:00 AM–12:00 AM
  - Pasig:  
    - Address: Ground Floor, Estancia at Capital Commons, Camino Verde Road, Pasig City  
    - Contact: 0286622523, 0917 524 5058  
    - Emails: ask@bistro.com.ph; tomatitoestancia@bistro.com.ph  
    - Hours: Monday–Thursday & Sunday: 11:00 AM–11:00 PM; Friday–Saturday: 11:00 AM–12:00 AM
  - Quezon City:  
    - Address: Robinson's Place Opus, Bridgetowne Estate, E. Rodriguez Jr. Ave, Brgy. Ugong, Quezon City  
    - Contact: 0286622523, 0917 524 5058  
    - Emails: ask@bistro.com.ph; tomatitoopus@bistro.com.ph  
    - Hours: Monday–Sunday: 11:00 AM–10:00 PM

- Booking Process:  
  • Ask for the name, customer’s desired branch, date, time, and party size. Lastly, ask for the customer's contact number.
  • Confirm the reservation details by repeating them back, ensuring all information is accurate.  
  • Inform the customer that we accept dine-in, takeout, and delivery, and guide them to book their table or order accordingly.

By following these guidelines and incorporating the detailed menu highlights (from pages 8–18), you will create a seamless and engaging experience for every guest—whether they’re exploring our eclectic food and drink offerings or looking to reserve a table at one of our prime locations.

"""


async def run_bot(webrtc_connection):
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV2(
                smart_turn_model_path="",  # Download from HuggingFace
                params=SmartTurnParams(),
            ),
        ),
    )

    stt = WhisperSTTServiceMLX(model=MLXModel.LARGE_V3_TURBO_Q4)

    tts = TTSMLXIsolated(model="mlx-community/Kokoro-82M-bf16", voice="af_heart", sample_rate=24000)
    # tts = TTSMLXIsolated(model="Marvis-AI/marvis-tts-250m-v0.1", voice=None)

    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    )

    context = OpenAILLMContext(
        [
            {
                "role": "user",
                "content": SYSTEM_INSTRUCTION,
            }
        ],
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

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            rtvi,
            context_aggregator.user(),
            llm,
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

        # Run example function with SmallWebRTC transport arguments.
        background_tasks.add_task(run_bot, pipecat_connection)

    answer = pipecat_connection.get_answer()
    # Updating the peer connection inside the map
    pcs_map[answer["pc_id"]] = pipecat_connection

    return answer


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # Run app
    coros = [pc.disconnect() for pc in pcs_map.values()]
    await asyncio.gather(*coros)
    pcs_map.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Bot Runner")
    parser.add_argument(
        "--host", default="localhost", help="Host for HTTP server (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=7860, help="Port for HTTP server (default: 7860)"
    )
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)

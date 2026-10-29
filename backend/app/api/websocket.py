from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
from app.services.gemini_live import gemini_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Full-duplex WebSocket gateway connecting the Next.js frontend
    to the Google Gemini Multimodal Live API.
    """
    await websocket.accept()
    logger.info("Client connected to Leo Voice Agent WebSocket gateway.")

    try:
        # Establish live connection with Gemini
        async with await gemini_service.get_live_session() as gemini_session:
            logger.info("Connected to Google Gemini Live API successfully.")

            async def client_to_gemini():
                """Task to receive audio chunks from the frontend and send to Gemini."""
                try:
                    while True:
                        data = await websocket.receive()
                        if "bytes" in data:
                            audio_bytes = data["bytes"]
                            # Send raw PCM audio chunks to Gemini
                            await gemini_session.send(
                                input={"media_chunks": [{"data": audio_bytes, "mime_type": "audio/pcm"}]},
                                end_of_turn=False
                            )
                        elif "text" in data:
                            text_msg = data["text"]
                            await gemini_session.send(input=text_msg, end_of_turn=True)
                except WebSocketDisconnect:
                    pass
                except Exception as e:
                    logger.error(f"Error in client_to_gemini stream: {e}")

            async def gemini_to_client():
                """Task to receive audio responses from Gemini and stream them back to the frontend."""
                try:
                    async for response in gemini_session.receive():
                        server_content = response.server_content
                        if server_content and server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                # If Gemini sends back audio data, stream it to client
                                if part.inline_data:
                                    await websocket.send_bytes(part.inline_data.data)
                                # If Gemini sends back text transcripts, send them as JSON/text
                                if part.text:
                                    await websocket.send_text(part.text)
                except Exception as e:
                    logger.error(f"Error in gemini_to_client stream: {e}")

            # Run both streaming directions concurrently
            await asyncio.gather(
                client_to_gemini(),
                gemini_to_client()
            )

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket gateway.")
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
    finally:
        logger.info("Leo Voice Agent WebSocket connection closed.")
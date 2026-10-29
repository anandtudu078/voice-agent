import os
from google import genai
from google.genai import types
from app.core.config import settings

class GeminiVoiceService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    async def get_live_session(self):
        """
        Prepares the config for Gemini's Multimodal Live API websocket session.
        """
        if not self.client:
            raise ValueError("Gemini API Client is not initialized. Please check your API key.")

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                )
            ),
            system_instruction=types.Content(
                parts=[
                    types.Part.from_text(
                        text="You are Leo, an elite, highly concise, and practical AI software engineer collaborator. "
                             "You talk to the developer via voice in real-time, helping them write clean code, architect monorepos, "
                             "and debug issues. Keep your spoken responses punchy, sharp, and natural."
                    )
                ]
            ),
        )
        return self.client.aio.live.connect(
            model="gemini-3.8-live",  # <--- Updated to the correct Live API model
            config=config
        )

gemini_service = GeminiVoiceService()
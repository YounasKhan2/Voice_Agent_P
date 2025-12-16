import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env next to backend folder root if present
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))


class Settings(BaseModel):
    livekit_url: str = os.getenv("LIVEKIT_URL", "")
    livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", "")
    livekit_api_secret: str = os.getenv("LIVEKIT_API_SECRET", "")

    deepgram_api_key: str | None = os.getenv("DEEPGRAM_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    grok_api_key: str | None = os.getenv("GROK_API_KEY")
    cartesia_api_key: str | None = os.getenv("CARTESIA_API_KEY")

    system_prompt: str = os.getenv("SYSTEM_PROMPT", "You are a friendly travel assistant.")

    # CORS / server
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    # Dynamic audio/LLM provider selection
    stt_provider: str = os.getenv("STT_PROVIDER", "openai")  # openai|deepgram
    tts_provider: str = os.getenv("TTS_PROVIDER", "openai")  # openai|cartesia
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai (default) - extensible
    tts_voice: str = os.getenv("TTS_VOICE", "alloy")  # voice name for TTS engine if supported

    # Persistence service
    django_base_url: str | None = os.getenv("DJANGO_BASE_URL")
    ingest_token: str | None = os.getenv("INGEST_TOKEN")

    # VAD (Voice Activity Detection) settings
    vad_min_speech_duration: float = float(os.getenv("VAD_MIN_SPEECH_DURATION", "0.1"))
    vad_min_silence_duration: float = float(os.getenv("VAD_MIN_SILENCE_DURATION", "0.3"))
    vad_padding_duration: float = float(os.getenv("VAD_PADDING_DURATION", "0.1"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()

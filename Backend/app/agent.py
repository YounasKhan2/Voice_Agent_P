from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass
import uuid
from typing import Optional, Dict, Callable, Awaitable, Any

from livekit import rtc, api
from livekit.agents import Agent, AgentSession
from livekit.agents.voice.room_io import RoomOutputOptions
from livekit.plugins import silero, openai, deepgram, cartesia

from .config import get_settings
from .utils.persistence import schedule_ingest

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)


@dataclass
class SessionHandle:
    session: AgentSession
    task: asyncio.Task[None]
    room: rtc.Room
    http_session: any = None


class SimpleVoiceAgent(Agent):
    def __init__(self, instructions: str) -> None:
        super().__init__(instructions=instructions)

    async def on_enter(self):
        # greet once at session start using the system instructions directly
        # avoids hard-coded prompt and keeps initialization consistent
        self.session.generate_reply(instructions=self.instructions)


class AgentManager:
    """Manages LiveKit voice agent sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionHandle] = {}
        self._broadcast_cb: Callable[[str, dict], Awaitable[None] | None] | None = None

    def set_transcript_broadcaster(
        self, cb: Callable[[str, dict], Awaitable[None] | None]
    ) -> None:
        self._broadcast_cb = cb

    async def start_session(
        self,
        room_name: str,
        instructions: str,
        user_id: Optional[str] = None,
        user_preferences: Optional[Dict] = None
    ) -> str:
        """
        Start a voice agent session.
        
        Args:
            room_name: LiveKit room name
            instructions: System prompt/instructions for the agent
            user_id: Optional authenticated user ID (None for anonymous sessions)
            user_preferences: Optional user preferences dict containing:
                - preferred_voice: TTS voice identifier
                - preferred_language: Language code
                - system_prompt_override: Custom system prompt
                
        Returns:
            session_id: Unique session identifier
        """
        settings = get_settings()

        # Build pipeline: STT -> LLM -> TTS with VAD turn detection, with provider selection via env
        if settings.stt_provider.lower() == "deepgram" and settings.deepgram_api_key:
            stt_engine = deepgram.STT(api_key=settings.deepgram_api_key)
        else:
            stt_engine = openai.STT(api_key=settings.openai_api_key)

        # Determine TTS voice (user preference takes precedence)
        tts_voice = settings.tts_voice
        if user_preferences and user_preferences.get('preferred_voice'):
            tts_voice = user_preferences['preferred_voice']
            logger.info(f"Using user preferred voice: {tts_voice}")

        if settings.tts_provider.lower() == "cartesia" and settings.cartesia_api_key:
            tts_engine = cartesia.TTS(api_key=settings.cartesia_api_key, voice=tts_voice or None)
        else:
            tts_engine = openai.TTS(api_key=settings.openai_api_key, voice=tts_voice or None)

        llm_engine = openai.LLM(api_key=settings.openai_api_key, model="gpt-4o-mini")

        session = AgentSession(
            vad=silero.VAD.load(
                min_speech_duration=settings.vad_min_speech_duration,
                min_silence_duration=settings.vad_min_silence_duration,
                padding_duration=settings.vad_padding_duration,
            ),
            stt=stt_engine,
            llm=llm_engine,
            tts=tts_engine,
            # prevent overlapping speech using built-in turn detection
            resume_false_interruption=True,
            false_interruption_timeout=1.0,
        )

        agent = SimpleVoiceAgent(instructions=instructions)

        # Start a background task that joins the room and runs the session
        room = rtc.Room()
        # assign a UUID session id (required by Django persistence schema)
        session_id = str(uuid.uuid4())

        # metadata sent to Django persistence service
        session_meta = {
            "id": session_id,
            "room": room_name,
            "system_prompt": instructions,
            "user_id": user_id  # Will be None for anonymous sessions
        }
        
        # Log session type
        if user_id:
            logger.info(f"Starting authenticated session {session_id} for user {user_id}")
        else:
            logger.info(f"Starting anonymous session {session_id}")

        def _emit(payload: dict) -> None:
            if self._broadcast_cb is None:
                return
            try:
                res = self._broadcast_cb(session_id, payload)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass
            # persistence (fire-and-forget)
            schedule_ingest(session_meta, [payload])

        # user transcript (interim + final)
        @session.on("user_input_transcribed")
        def _on_user_input(ev: Any) -> None:
            try:
                text = getattr(ev, "transcript", "")
                if text:
                    final = bool(getattr(ev, "is_final", False))
                    # include is_final flag expected by Django API
                    _emit({"role": "user", "text": text, "is_final": final})
            except Exception:
                pass

        # assistant message added to chat history
        @session.on("conversation_item_added")
        def _on_item_added(ev: Any) -> None:
            try:
                item = getattr(ev, "item", None)
                if item is None:
                    return
                role = getattr(item, "role", None)
                text = getattr(item, "text_content", None)
                if role == "assistant" and text:
                    _emit({"role": "agent", "text": text, "is_final": True})
            except Exception:
                pass

        # agent speech synthesis events
        @session.on("agent_speech_started")
        def _on_agent_speech_started(ev: Any) -> None:
            try:
                _emit({"role": "agent", "event": "speech_started", "is_final": True})
            except Exception:
                pass

        @session.on("agent_speech_ended")
        def _on_agent_speech_ended(ev: Any) -> None:
            try:
                _emit({"role": "agent", "event": "speech_ended", "is_final": True})
            except Exception:
                pass

        # user speech detection events
        @session.on("user_speech_started")
        def _on_user_speech_started(ev: Any) -> None:
            try:
                _emit({"role": "user", "event": "speech_started", "is_final": True})
            except Exception:
                pass

        @session.on("user_speech_ended")
        def _on_user_speech_ended(ev: Any) -> None:
            try:
                _emit({"role": "user", "event": "speech_ended", "is_final": True})
            except Exception:
                pass

        async def _run_session() -> None:
            # connect this server-side agent participant to the room
            if not settings.livekit_url or not settings.livekit_api_key or not settings.livekit_api_secret:
                raise RuntimeError("LiveKit credentials not configured")

            token = (
                api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
                .with_identity(f"voice-agent-{id(session)}")
                .with_kind("agent")
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                        can_publish_data=True,
                        can_update_own_metadata=True,
                    )
                )
                .to_jwt()
            )

            await room.connect(settings.livekit_url, token)

            # Run until disconnect or task cancelled
            try:
                await session.start(
                    agent=agent,
                    room=room,
                    room_output_options=RoomOutputOptions(
                        audio_enabled=True,
                        transcription_enabled=True,
                    ),
                )

                done = asyncio.Event()

                @room.on("disconnected")
                def _on_disc() -> None:
                    if not done.is_set():
                        done.set()

                await done.wait()
            except asyncio.CancelledError:
                # expected when stopping the session
                pass
            finally:
                try:
                    await session.aclose()
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass
                try:
                    await room.disconnect()
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

        job = asyncio.create_task(_run_session(), name=f"agent_session_{room_name}")
        self._sessions[session_id] = SessionHandle(session=session, task=job, room=room)
        return session_id

    async def stop_session(self, session_id: str) -> bool:
        handle = self._sessions.pop(session_id, None)
        if not handle:
            return False
        try:
            await handle.session.aclose()
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        if not handle.task.done():
            handle.task.cancel()
            try:
                await handle.task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        try:
            await handle.room.disconnect()
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        return True


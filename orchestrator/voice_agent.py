"""
E-Labz Voice Agent — ElevenLabs Integration (Skeleton)
Audio content generation and voice branding for the swarm.

This module is ready to activate once the ELEVENLABS_API_KEY is set.

Capabilities (when active):
- Voice clone setup for brand consistency
- Convert tweets/threads into audio snippets
- Generate voice-over for video content
- Audio newsletters / podcast clips
- Voice replies for high-value engagement

Install: pip install elevenlabs
"""

import os
from pathlib import Path
from typing import Optional, Dict

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("voice_agent")

# ============================================================
# CONFIGURATION
# ============================================================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
VOICE_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "audio"


class VoiceAgent:
    """
    ElevenLabs-powered voice content agent.
    
    Converts text content into natural-sounding audio
    for social media, newsletters, and brand building.
    
    Requires ELEVENLABS_API_KEY in config/.env
    """
    
    def __init__(self):
        self.client = None
        self.voice_id = None
        self._init_client()
    
    def _init_client(self):
        """Initialize ElevenLabs client."""
        if not ELEVENLABS_API_KEY:
            logger.info("No ELEVENLABS_API_KEY — voice agent in standby mode")
            return
        
        try:
            from elevenlabs import ElevenLabs
            self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            VOICE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("🎙️ ElevenLabs voice agent initialized")
        except ImportError:
            logger.info("elevenlabs package not installed — pip install elevenlabs")
        except Exception as e:
            logger.warning(f"ElevenLabs init failed: {e}")
    
    @property
    def is_active(self) -> bool:
        """Check if voice agent is ready."""
        return self.client is not None
    
    def text_to_audio(self, text: str, filename: str = "output.mp3",
                       voice: str = "Adam") -> Optional[str]:
        """
        Convert text to audio file.
        
        Args:
            text: The text to convert
            filename: Output filename
            voice: ElevenLabs voice name or ID
            
        Returns:
            Path to the generated audio file, or None if offline.
        """
        if not self.is_active:
            logger.info("Voice agent not active — set ELEVENLABS_API_KEY")
            return None
        
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            output_path = VOICE_OUTPUT_DIR / filename
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            
            logger.info(f"🎙️ Audio generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.warning(f"Audio generation failed: {e}")
            return None
    
    def tweet_to_audio(self, tweet_text: str) -> Optional[str]:
        """Convert a tweet into an audio clip for social media."""
        import hashlib
        filename = f"tweet_{hashlib.md5(tweet_text.encode()).hexdigest()[:8]}.mp3"
        return self.text_to_audio(tweet_text, filename)
    
    def thread_to_audio(self, thread_tweets: list) -> Optional[str]:
        """Convert a thread into a single audio file."""
        combined = "\n\n".join(thread_tweets)
        import hashlib
        filename = f"thread_{hashlib.md5(combined.encode()).hexdigest()[:8]}.mp3"
        return self.text_to_audio(combined, filename)
    
    def list_voices(self) -> list:
        """List available ElevenLabs voices."""
        if not self.is_active:
            return []
        
        try:
            response = self.client.voices.get_all()
            return [{"name": v.name, "id": v.voice_id} for v in response.voices]
        except Exception as e:
            logger.warning(f"Failed to list voices: {e}")
            return []


# ============================================================
# SINGLETON
# ============================================================

_voice_agent = None

def get_voice_agent() -> VoiceAgent:
    """Get the singleton voice agent."""
    global _voice_agent
    if _voice_agent is None:
        _voice_agent = VoiceAgent()
    return _voice_agent


if __name__ == "__main__":
    agent = get_voice_agent()
    print(f"Voice agent active: {agent.is_active}")
    
    if agent.is_active:
        voices = agent.list_voices()
        print(f"Available voices: {len(voices)}")
        
        path = agent.tweet_to_audio("AI agents are going to change everything about how we work.")
        print(f"Audio: {path}")
    else:
        print("Set ELEVENLABS_API_KEY in config/.env to activate")
    
    print("✅ Voice agent module ready")

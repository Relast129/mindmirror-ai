"""
Speech Processing Module
Handles speech-to-text and text-to-speech with fallbacks.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import requests
import os
from gtts import gTTS
import io

from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class SpeechProcessor:
    """Handles speech processing tasks."""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
        self.transcription_models = ModelRegistry.get_models("transcription")
        self.tts_models = ModelRegistry.get_models("tts")
    
    async def transcribe(self, audio_file: Any) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Returns:
            {
                "text": "...",
                "model_used": "...",
                "fallback": bool
            }
        """
        # Try Whisper models
        for model_config in self.transcription_models:
            try:
                result = await self._call_transcription_model(audio_file, model_config)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Transcription model {model_config['id']} failed: {str(e)}")
                continue
        
        # Fallback to local speech_recognition (requires setup)
        logger.warning("All transcription models failed, using fallback")
        return self._transcription_fallback()
    
    async def _call_transcription_model(self, audio_file: Any, model_config: Dict) -> Optional[Dict]:
        """Call Whisper API for transcription."""
        api_url = f"https://api-inference.huggingface.co/models/{model_config['id']}"
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        # Read audio file bytes
        if hasattr(audio_file, 'read'):
            audio_bytes = audio_file.read()
        else:
            audio_bytes = audio_file
        
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(api_url, headers=headers, data=audio_bytes, timeout=model_config.get("timeout", 15))
                ),
                timeout=model_config.get("timeout", 15) + 2
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("text", "")
                
                if text:
                    return {
                        "text": text,
                        "model_used": model_config["id"],
                        "fallback": False
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling {model_config['id']}: {str(e)}")
            return None
    
    def _transcription_fallback(self) -> Dict[str, Any]:
        """Fallback for transcription."""
        return {
            "text": "[Audio transcription requires model setup. Please speak clearly and try again, or use text input.]",
            "model_used": "none",
            "fallback": True,
            "note": "Install speech_recognition library and configure for local transcription"
        }
    
    async def text_to_speech(self, text: str) -> Dict[str, Any]:
        """
        Convert text to speech.
        
        Returns:
            {
                "audio": bytes,
                "model_used": "...",
                "fallback": bool
            }
        """
        # Try HF TTS models first
        for model_config in self.tts_models:
            try:
                result = await self._call_tts_model(text, model_config)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"TTS model {model_config['id']} failed: {str(e)}")
                continue
        
        # Fallback to gTTS
        logger.info("Using gTTS fallback for text-to-speech")
        return self._gtts_fallback(text)
    
    async def _call_tts_model(self, text: str, model_config: Dict) -> Optional[Dict]:
        """Call HF TTS model."""
        api_url = f"https://api-inference.huggingface.co/models/{model_config['id']}"
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        payload = {"inputs": text[:500]}  # Limit length
        
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(api_url, headers=headers, json=payload, timeout=model_config.get("timeout", 20))
                ),
                timeout=model_config.get("timeout", 20) + 2
            )
            
            if response.status_code == 200:
                audio_bytes = response.content
                return {
                    "audio": audio_bytes,
                    "model_used": model_config["id"],
                    "fallback": False
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling {model_config['id']}: {str(e)}")
            return None
    
    def _gtts_fallback(self, text: str) -> Dict[str, Any]:
        """Use gTTS for text-to-speech."""
        try:
            tts = gTTS(text=text[:500], lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return {
                "audio": audio_buffer.read(),
                "model_used": "gtts",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            return {
                "audio": None,
                "model_used": "none",
                "fallback": True,
                "error": str(e)
            }

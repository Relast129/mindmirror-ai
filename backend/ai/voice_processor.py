"""
Voice Processing Module for MindMirror AI
Handles speech-to-text and text-to-speech operations
"""

import logging
from typing import Dict, Optional
import httpx
import base64
from gtts import gTTS
import tempfile
import os
from config import settings

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Processes voice recordings and generates speech"""
    
    def __init__(self):
        """Initialize voice processor"""
        self.whisper_api_url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict:
        """
        Transcribe audio file to text using Whisper
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary containing transcription and metadata
        """
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.whisper_api_url,
                    headers=self.headers,
                    data=audio_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    transcription = result.get('text', '')
                    
                    return {
                        "transcription": transcription,
                        "success": True,
                        "language": result.get('language', 'en'),
                        "confidence": 0.9  # Whisper doesn't provide confidence scores
                    }
                
                else:
                    logger.error(f"Transcription API error: {response.status_code}")
                    return self._get_fallback_transcription()
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return self._get_fallback_transcription()
    
    async def transcribe_audio_bytes(self, audio_bytes: bytes) -> Dict:
        """
        Transcribe audio from bytes
        
        Args:
            audio_bytes: Audio data as bytes
            
        Returns:
            Dictionary containing transcription and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.whisper_api_url,
                    headers=self.headers,
                    data=audio_bytes
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    transcription = result.get('text', '')
                    
                    return {
                        "transcription": transcription,
                        "success": True,
                        "language": result.get('language', 'en'),
                        "confidence": 0.9
                    }
                
                else:
                    logger.error(f"Transcription API error: {response.status_code}")
                    return self._get_fallback_transcription()
                    
        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {str(e)}")
            return self._get_fallback_transcription()
    
    def _get_fallback_transcription(self) -> Dict:
        """Provide fallback when transcription fails"""
        return {
            "transcription": "[Unable to transcribe audio. Please try again or use text input.]",
            "success": False,
            "language": "unknown",
            "confidence": 0.0
        }
    
    def generate_speech(self, text: str, language: str = 'en') -> Dict:
        """
        Generate speech from text using gTTS
        
        Args:
            text: Text to convert to speech
            language: Language code (default: 'en')
            
        Returns:
            Dictionary containing audio data and metadata
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_path = tmp_file.name
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_path)
            
            # Read generated audio
            with open(tmp_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up temporary file
            os.remove(tmp_path)
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "audio_base64": audio_base64,
                "audio_bytes": audio_bytes,
                "success": True,
                "language": language,
                "format": "mp3"
            }
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return {
                "audio_base64": None,
                "audio_bytes": None,
                "success": False,
                "error": str(e)
            }
    
    async def process_voice_input(self, audio_file_path: str) -> Dict:
        """
        Complete voice processing pipeline: transcribe and analyze
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary containing transcription and analysis
        """
        # Transcribe audio
        transcription_result = await self.transcribe_audio(audio_file_path)
        
        if not transcription_result['success']:
            return {
                "success": False,
                "error": "Transcription failed",
                "transcription": transcription_result['transcription']
            }
        
        return {
            "success": True,
            "transcription": transcription_result['transcription'],
            "language": transcription_result['language'],
            "confidence": transcription_result['confidence']
        }
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_path: Optional output path for audio
            
        Returns:
            Path to extracted audio file
        """
        try:
            from pydub import AudioSegment
            import moviepy.editor as mp
            
            # Create output path if not provided
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.mp3')
            
            # Extract audio using moviepy
            video = mp.VideoFileClip(video_path)
            video.audio.write_audiofile(output_path, logger=None)
            video.close()
            
            logger.info(f"Extracted audio to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio from video: {str(e)}")
            raise
    
    async def process_video_audio(self, video_path: str) -> Dict:
        """
        Process video file: extract audio and transcribe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing transcription and metadata
        """
        try:
            # Extract audio
            audio_path = self.extract_audio_from_video(video_path)
            
            # Transcribe audio
            result = await self.transcribe_audio(audio_path)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing video audio: {str(e)}")
            return self._get_fallback_transcription()

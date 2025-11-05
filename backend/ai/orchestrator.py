"""
AI Orchestrator - Coordinates all AI model calls with fallbacks and caching
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .model_registry import ModelRegistry
from .emotion import EmotionAnalyzer
from .reflection import ReflectionGenerator
from .art import ArtGenerator
from .speech import SpeechProcessor

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Orchestrates AI pipeline with robust error handling and caching."""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.reflection_generator = ReflectionGenerator()
        self.art_generator = ArtGenerator()
        self.speech_processor = SpeechProcessor()
        
        # Simple in-memory cache (TTL: 5 minutes)
        self._cache = {}
        self._cache_ttl = 300  # seconds
    
    def _get_cache_key(self, content: str, operation: str) -> str:
        """Generate cache key for content."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{operation}:{content_hash}"
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached result if not expired."""
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                logger.info(f"Cache hit for {key}")
                return cached_data
            else:
                del self._cache[key]
        return None
    
    def _set_cached(self, key: str, data: Any):
        """Store result in cache."""
        self._cache[key] = (data, time.time())
        
        # Simple cache cleanup: remove old entries if cache grows too large
        if len(self._cache) > 100:
            current_time = time.time()
            self._cache = {
                k: v for k, v in self._cache.items()
                if current_time - v[1] < self._cache_ttl
            }
    
    async def process_input(
        self,
        content: str,
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Process user input through complete AI pipeline.
        
        Args:
            content: Text content to process
            input_type: Type of input (text, voice, image, etc.)
            
        Returns:
            Dictionary with all AI results and metadata
        """
        start_time = time.time()
        results = {
            "emotions": [],
            "emotion_scores": {},
            "reflection": "",
            "poem": "",
            "advice": "",
            "art_image": None,
            "voice_audio": None,
            "model_versions": {},
            "processing_time": 0,
            "fallback_used": False
        }
        
        try:
            # Step 1: Emotion Analysis
            logger.info("Running emotion analysis...")
            cache_key = self._get_cache_key(content, "emotion")
            emotion_result = self._get_cached(cache_key)
            
            if not emotion_result:
                emotion_result = await self.emotion_analyzer.analyze(content)
                self._set_cached(cache_key, emotion_result)
            
            results["emotions"] = emotion_result.get("emotions", ["neutral"])
            results["emotion_scores"] = emotion_result.get("scores", {})
            results["model_versions"]["emotion"] = emotion_result.get("model_used", "template")
            results["fallback_used"] = results["fallback_used"] or emotion_result.get("fallback", False)
            
            # Step 2: Generate Reflection & Poetry
            logger.info("Generating reflection and poetry...")
            primary_emotion = results["emotions"][0] if results["emotions"] else "neutral"
            
            cache_key = self._get_cache_key(f"{content}:{primary_emotion}", "reflection")
            reflection_result = self._get_cached(cache_key)
            
            if not reflection_result:
                reflection_result = await self.reflection_generator.generate(
                    content=content,
                    emotion=primary_emotion,
                    emotion_scores=results["emotion_scores"]
                )
                self._set_cached(cache_key, reflection_result)
            
            results["reflection"] = reflection_result.get("reflection", "")
            results["poem"] = reflection_result.get("poem", "")
            results["advice"] = reflection_result.get("advice", "")
            results["model_versions"]["reflection"] = reflection_result.get("model_used", "template")
            results["fallback_used"] = results["fallback_used"] or reflection_result.get("fallback", False)
            
            # Step 3: Generate Art
            logger.info("Generating mood-based art...")
            art_result = await self.art_generator.generate(
                emotion=primary_emotion,
                content_summary=content[:200]  # Use first 200 chars for prompt
            )
            
            results["art_image"] = art_result.get("image")
            results["model_versions"]["art"] = art_result.get("model_used", "procedural")
            results["fallback_used"] = results["fallback_used"] or art_result.get("fallback", False)
            
            # Step 4: Optional TTS (skip for now to save time, can be generated on-demand)
            # results["voice_audio"] = await self.speech_processor.text_to_speech(
            #     results["reflection"][:500]  # Limit length
            # )
            
            # Calculate processing time
            results["processing_time"] = time.time() - start_time
            
            logger.info(f"Pipeline completed in {results['processing_time']:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            # Return partial results with error info
            results["error"] = str(e)
            results["processing_time"] = time.time() - start_time
            results["fallback_used"] = True
            return results
    
    async def transcribe_audio(self, audio_file: Any) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Audio file data
            
        Returns:
            {"text": "...", "model_used": "...", "fallback": bool}
        """
        try:
            result = await self.speech_processor.transcribe(audio_file)
            return result
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "text": "[Transcription failed - please try again]",
                "model_used": "none",
                "fallback": True,
                "error": str(e)
            }
    
    async def process_video(self, video_file: Any) -> Dict[str, Any]:
        """
        Process video: extract audio for transcription and frames for analysis.
        
        Args:
            video_file: Video file data
            
        Returns:
            {"transcription": "...", "frames_analyzed": int, ...}
        """
        try:
            # This is a simplified version
            # Full implementation would use ffmpeg to extract audio and frames
            logger.info("Processing video (simplified)")
            
            return {
                "transcription": "[Video processing - audio transcription would go here]",
                "frames_analyzed": 0,
                "model_used": "none",
                "fallback": True,
                "note": "Full video processing requires ffmpeg setup"
            }
        except Exception as e:
            logger.error(f"Video processing error: {str(e)}")
            return {
                "transcription": "[Video processing failed]",
                "error": str(e),
                "fallback": True
            }

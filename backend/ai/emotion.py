"""
Emotion Analysis Module
Detects emotions from text with fallback strategies.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import requests
import os

from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """Analyzes emotions from text using HF models with fallbacks."""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")  # Optional
        self.models = ModelRegistry.get_models("emotion")
        self.fallback_config = ModelRegistry.get_fallback_config("emotion")
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze emotions in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            {
                "emotions": ["joy", "gratitude"],
                "scores": {"joy": 0.85, "gratitude": 0.72},
                "model_used": "model-id",
                "fallback": False
            }
        """
        # Try each model in priority order
        for model_config in self.models:
            try:
                result = await self._call_model(text, model_config)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Model {model_config['id']} failed: {str(e)}")
                continue
        
        # All models failed - use template fallback
        logger.warning("All emotion models failed, using template fallback")
        return self._template_fallback(text)
    
    async def _call_model(self, text: str, model_config: Dict) -> Optional[Dict]:
        """Call HuggingFace inference API."""
        api_url = f"https://api-inference.huggingface.co/models/{model_config['id']}"
        
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        payload = {"inputs": text[:512]}  # Limit text length
        
        try:
            # Use asyncio to run requests with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=model_config.get("timeout", 12)
                    )
                ),
                timeout=model_config.get("timeout", 12) + 2
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response (format varies by model)
                if isinstance(data, list) and len(data) > 0:
                    predictions = data[0]
                    
                    # Extract top emotions
                    emotions = []
                    scores = {}
                    
                    for pred in predictions[:3]:  # Top 3 emotions
                        label = pred.get("label", "").lower()
                        score = pred.get("score", 0)
                        
                        # Normalize label
                        label = self._normalize_emotion_label(label)
                        emotions.append(label)
                        scores[label] = score
                    
                    return {
                        "emotions": emotions,
                        "scores": scores,
                        "model_used": model_config["id"],
                        "fallback": False
                    }
            
            elif response.status_code == 503:
                # Model loading - wait and retry once
                logger.info(f"Model {model_config['id']} loading, waiting...")
                await asyncio.sleep(5)
                # Retry once
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: requests.post(api_url, headers=headers, json=payload, timeout=15)
                    ),
                    timeout=17
                )
                if response.status_code == 200:
                    # Parse again
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        predictions = data[0]
                        emotions = []
                        scores = {}
                        for pred in predictions[:3]:
                            label = self._normalize_emotion_label(pred.get("label", "").lower())
                            score = pred.get("score", 0)
                            emotions.append(label)
                            scores[label] = score
                        return {
                            "emotions": emotions,
                            "scores": scores,
                            "model_used": model_config["id"],
                            "fallback": False
                        }
            
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout calling {model_config['id']}")
            return None
        except Exception as e:
            logger.error(f"Error calling {model_config['id']}: {str(e)}")
            return None
    
    def _normalize_emotion_label(self, label: str) -> str:
        """Normalize emotion labels to standard set."""
        # Map various labels to standard emotions
        emotion_map = {
            "happy": "joy",
            "happiness": "joy",
            "excited": "joy",
            "sad": "sadness",
            "sadness": "sadness",
            "depressed": "sadness",
            "angry": "anger",
            "anger": "anger",
            "mad": "anger",
            "scared": "fear",
            "fear": "fear",
            "anxious": "fear",
            "anxiety": "fear",
            "worried": "fear",
            "love": "love",
            "affection": "love",
            "caring": "love",
            "surprised": "surprise",
            "surprise": "surprise",
            "amazed": "surprise",
            "neutral": "neutral",
            "calm": "neutral"
        }
        
        return emotion_map.get(label.lower(), label.lower())
    
    def _template_fallback(self, text: str) -> Dict[str, Any]:
        """Template-based emotion detection using keywords."""
        text_lower = text.lower()
        
        # Simple keyword matching
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "glad"],
            "sadness": ["sad", "depressed", "down", "unhappy", "miserable", "crying", "tears"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated"],
            "fear": ["scared", "afraid", "anxious", "worried", "nervous", "fear", "panic"],
            "love": ["love", "adore", "cherish", "care", "affection"],
            "surprise": ["surprised", "shocked", "amazed", "unexpected", "wow"],
            "gratitude": ["thank", "grateful", "appreciate", "thankful"],
            "neutral": []
        }
        
        scores = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                scores[emotion] = min(count * 0.3, 0.9)  # Cap at 0.9
        
        # Default to neutral if no matches
        if not scores:
            scores["neutral"] = 0.7
        
        # Sort by score
        sorted_emotions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        emotions = [e[0] for e in sorted_emotions[:3]]
        
        return {
            "emotions": emotions,
            "scores": dict(sorted_emotions),
            "model_used": "template",
            "fallback": True
        }

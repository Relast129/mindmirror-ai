"""
Emotion Detection Module for MindMirror AI
Analyzes text and detects emotional states using Hugging Face models
"""

import logging
from typing import Dict, List
import httpx
from config import settings

logger = logging.getLogger(__name__)

class EmotionDetector:
    """Detects emotions from text using AI models"""
    
    def __init__(self):
        """Initialize emotion detector"""
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.EMOTION_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
    
    async def detect_emotion(self, text: str) -> Dict:
        """
        Detect emotions from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing emotion analysis results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": text}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Process results
                    if isinstance(results, list) and len(results) > 0:
                        emotions = results[0]
                        
                        # Sort by score
                        emotions_sorted = sorted(emotions, key=lambda x: x['score'], reverse=True)
                        
                        primary_emotion = emotions_sorted[0]
                        
                        return {
                            "primary_emotion": primary_emotion['label'],
                            "confidence": primary_emotion['score'],
                            "all_emotions": emotions_sorted,
                            "emotion_summary": self._generate_summary(emotions_sorted)
                        }
                    
                    return {
                        "primary_emotion": "neutral",
                        "confidence": 0.5,
                        "all_emotions": [],
                        "emotion_summary": "Unable to detect specific emotions"
                    }
                
                else:
                    logger.error(f"Emotion detection API error: {response.status_code}")
                    return self._get_fallback_emotion(text)
                    
        except Exception as e:
            logger.error(f"Error detecting emotion: {str(e)}")
            return self._get_fallback_emotion(text)
    
    def _generate_summary(self, emotions: List[Dict]) -> str:
        """
        Generate human-readable emotion summary
        
        Args:
            emotions: List of emotion dictionaries
            
        Returns:
            Summary string
        """
        if not emotions:
            return "Neutral emotional state"
        
        primary = emotions[0]
        emotion_name = primary['label']
        confidence = primary['score']
        
        # Emotion descriptions
        descriptions = {
            "joy": "You're feeling joyful and positive! 😊",
            "sadness": "You're experiencing sadness. It's okay to feel this way. 💙",
            "anger": "You're feeling angry or frustrated. Take a deep breath. 😤",
            "fear": "You're feeling anxious or fearful. You're not alone. 💜",
            "love": "You're feeling love and warmth! ❤️",
            "surprise": "You're feeling surprised or amazed! 😮",
            "neutral": "You're in a calm, neutral state. 😌"
        }
        
        base_description = descriptions.get(emotion_name.lower(), f"You're feeling {emotion_name}")
        
        if confidence > 0.8:
            intensity = "strongly"
        elif confidence > 0.6:
            intensity = "moderately"
        else:
            intensity = "slightly"
        
        # Check for mixed emotions
        if len(emotions) > 1 and emotions[1]['score'] > 0.3:
            secondary = emotions[1]['label']
            return f"{base_description} You're {intensity} experiencing {emotion_name}, with hints of {secondary}."
        
        return f"{base_description} You're {intensity} experiencing {emotion_name}."
    
    def _get_fallback_emotion(self, text: str) -> Dict:
        """
        Provide fallback emotion detection using simple keyword matching
        
        Args:
            text: Input text
            
        Returns:
            Fallback emotion dictionary
        """
        text_lower = text.lower()
        
        # Simple keyword-based detection
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love"],
            "sadness": ["sad", "depressed", "down", "unhappy", "miserable", "lonely"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated"],
            "fear": ["scared", "afraid", "anxious", "worried", "nervous", "fearful"],
            "love": ["love", "adore", "cherish", "care", "affection"],
        }
        
        detected_emotions = []
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                detected_emotions.append({"label": emotion, "score": min(score * 0.2, 0.9)})
        
        if detected_emotions:
            detected_emotions.sort(key=lambda x: x['score'], reverse=True)
            primary = detected_emotions[0]
            return {
                "primary_emotion": primary['label'],
                "confidence": primary['score'],
                "all_emotions": detected_emotions,
                "emotion_summary": self._generate_summary(detected_emotions)
            }
        
        return {
            "primary_emotion": "neutral",
            "confidence": 0.5,
            "all_emotions": [{"label": "neutral", "score": 0.5}],
            "emotion_summary": "You're in a calm, neutral state. 😌"
        }
    
    def get_emotion_color(self, emotion: str) -> str:
        """
        Get color associated with emotion for visualization
        
        Args:
            emotion: Emotion name
            
        Returns:
            Hex color code
        """
        colors = {
            "joy": "#FFD700",      # Gold
            "sadness": "#4169E1",  # Royal Blue
            "anger": "#DC143C",    # Crimson
            "fear": "#9370DB",     # Medium Purple
            "love": "#FF69B4",     # Hot Pink
            "surprise": "#FF8C00", # Dark Orange
            "neutral": "#808080"   # Gray
        }
        
        return colors.get(emotion.lower(), "#808080")
    
    def get_emotion_emoji(self, emotion: str) -> str:
        """
        Get emoji associated with emotion
        
        Args:
            emotion: Emotion name
            
        Returns:
            Emoji string
        """
        emojis = {
            "joy": "😊",
            "sadness": "😢",
            "anger": "😤",
            "fear": "😰",
            "love": "❤️",
            "surprise": "😮",
            "neutral": "😌"
        }
        
        return emojis.get(emotion.lower(), "😌")

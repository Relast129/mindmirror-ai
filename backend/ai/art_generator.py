"""
AI Art Generator for MindMirror AI
Creates mood-based abstract art using Stable Diffusion
"""

import logging
from typing import Dict, Optional
import httpx
import base64
from config import settings

logger = logging.getLogger(__name__)

class ArtGenerator:
    """Generates mood-based abstract art using AI"""
    
    def __init__(self):
        """Initialize art generator"""
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.ART_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
    
    async def generate_mood_art(
        self,
        emotion: str,
        user_input: str = "",
        style: str = "abstract"
    ) -> Dict:
        """
        Generate abstract art based on emotional state
        
        Args:
            emotion: Primary emotion
            user_input: User's original text for context
            style: Art style (abstract, watercolor, digital, etc.)
            
        Returns:
            Dictionary containing image data and metadata
        """
        try:
            # Create art prompt based on emotion
            prompt = self._create_art_prompt(emotion, user_input, style)
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "negative_prompt": "text, words, letters, watermark, signature, blurry, low quality",
                            "num_inference_steps": 30,
                            "guidance_scale": 7.5
                        }
                    }
                )
                
                if response.status_code == 200:
                    # Image is returned as bytes
                    image_bytes = response.content
                    
                    # Convert to base64 for easy transmission
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    return {
                        "image_base64": image_base64,
                        "image_bytes": image_bytes,
                        "prompt": prompt,
                        "emotion": emotion,
                        "style": style,
                        "success": True
                    }
                
                else:
                    logger.error(f"Art generation API error: {response.status_code}")
                    return self._get_fallback_art(emotion)
                    
        except Exception as e:
            logger.error(f"Error generating art: {str(e)}")
            return self._get_fallback_art(emotion)
    
    def _create_art_prompt(self, emotion: str, user_input: str, style: str) -> str:
        """
        Create art generation prompt based on emotion
        
        Args:
            emotion: Primary emotion
            user_input: User's text
            style: Art style
            
        Returns:
            Art generation prompt
        """
        # Emotion-specific art descriptions
        emotion_prompts = {
            "joy": "vibrant golden sunburst, flowing ribbons of light, warm yellows and oranges, uplifting energy, radiant glow, celebration of happiness",
            "sadness": "deep blue ocean waves, gentle rain, soft melancholic colors, flowing tears transformed into art, peaceful blues and purples, emotional depth",
            "anger": "intense red and orange flames, dynamic energy, powerful brushstrokes, volcanic eruption of emotion, fierce crimson waves, raw power",
            "fear": "swirling purple mist, mysterious shadows, anxious energy, dark blues and violets, ethereal fog, protective light breaking through",
            "love": "soft pink and red hearts, warm embrace of colors, gentle rose petals, romantic sunset, tender affection, harmonious blend",
            "surprise": "explosive burst of colors, unexpected patterns, dynamic orange and yellow, lightning bolt of emotion, exciting energy, spontaneous creation",
            "neutral": "balanced zen garden, peaceful grays and whites, minimalist harmony, calm waters, serene landscape, meditative space"
        }
        
        base_prompt = emotion_prompts.get(emotion.lower(), "abstract emotional expression, colorful, artistic")
        
        # Add style modifiers
        style_modifiers = {
            "abstract": "abstract art, modern, artistic, high quality, detailed",
            "watercolor": "watercolor painting, soft edges, flowing colors, artistic",
            "digital": "digital art, vibrant, modern, high resolution, detailed",
            "minimalist": "minimalist art, clean lines, simple, elegant, modern",
            "surreal": "surreal art, dreamlike, imaginative, artistic, creative"
        }
        
        style_modifier = style_modifiers.get(style.lower(), style_modifiers["abstract"])
        
        full_prompt = f"{base_prompt}, {style_modifier}, emotional visualization, therapeutic art, no text, no words"
        
        return full_prompt
    
    def _get_fallback_art(self, emotion: str) -> Dict:
        """
        Provide fallback when art generation fails
        
        Args:
            emotion: Emotion for fallback
            
        Returns:
            Fallback art dictionary
        """
        # Return a simple color gradient as fallback
        return {
            "image_base64": None,
            "image_bytes": None,
            "prompt": f"Fallback art for {emotion}",
            "emotion": emotion,
            "style": "gradient",
            "success": False,
            "fallback": True,
            "color": self._get_emotion_color(emotion)
        }
    
    def _get_emotion_color(self, emotion: str) -> str:
        """Get primary color for emotion"""
        colors = {
            "joy": "#FFD700",
            "sadness": "#4169E1",
            "anger": "#DC143C",
            "fear": "#9370DB",
            "love": "#FF69B4",
            "surprise": "#FF8C00",
            "neutral": "#808080"
        }
        return colors.get(emotion.lower(), "#808080")
    
    async def generate_multiple_variations(
        self,
        emotion: str,
        count: int = 3
    ) -> list:
        """
        Generate multiple art variations for the same emotion
        
        Args:
            emotion: Primary emotion
            count: Number of variations to generate
            
        Returns:
            List of art dictionaries
        """
        styles = ["abstract", "watercolor", "digital"]
        results = []
        
        for i in range(min(count, len(styles))):
            art = await self.generate_mood_art(emotion, style=styles[i])
            results.append(art)
        
        return results

"""
Art Generator Module
Generates mood-based abstract art using Stable Diffusion with SVG fallback.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import requests
import os
import io
import base64
from PIL import Image

from .model_registry import ModelRegistry

logger = logging.getLogger(__name__)

class ArtGenerator:
    """Generates mood-based art."""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
        self.models = ModelRegistry.get_models("art")
        self.fallback_config = ModelRegistry.get_fallback_config("art")
    
    async def generate(self, emotion: str, content_summary: str = "") -> Dict[str, Any]:
        """
        Generate mood-based art.
        
        Returns:
            {
                "image": bytes or None,
                "model_used": "...",
                "fallback": bool
            }
        """
        # Try SD models
        for model_config in self.models:
            try:
                result = await self._call_model(emotion, content_summary, model_config)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Art model {model_config['id']} failed: {str(e)}")
                continue
        
        # Fallback to procedural SVG
        logger.warning("All art models failed, using procedural SVG")
        return self._svg_fallback(emotion)
    
    async def _call_model(self, emotion: str, summary: str, model_config: Dict) -> Optional[Dict]:
        """Call Stable Diffusion API."""
        prompt = self._build_art_prompt(emotion, summary)
        
        api_url = f"https://api-inference.huggingface.co/models/{model_config['id']}"
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        payload = {
            "inputs": prompt,
            "parameters": model_config.get("params", {})
        }
        
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(api_url, headers=headers, json=payload, timeout=model_config.get("timeout", 45))
                ),
                timeout=model_config.get("timeout", 45) + 2
            )
            
            if response.status_code == 200:
                # Response is image bytes
                image_bytes = response.content
                return {
                    "image": image_bytes,
                    "model_used": model_config["id"],
                    "fallback": False
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling {model_config['id']}: {str(e)}")
            return None
    
    def _build_art_prompt(self, emotion: str, summary: str) -> str:
        """Build prompt for art generation."""
        emotion_prompts = {
            "joy": "abstract art, vibrant colors, warm yellows and oranges, flowing shapes, uplifting, energetic, positive energy, digital art",
            "sadness": "abstract art, cool blues and purples, gentle waves, melancholic, soft gradients, contemplative, serene, digital art",
            "anger": "abstract art, intense reds and blacks, sharp angles, dynamic movement, powerful, bold strokes, dramatic, digital art",
            "fear": "abstract art, dark purples and grays, swirling patterns, mysterious, ethereal, shadowy, atmospheric, digital art",
            "love": "abstract art, soft pinks and warm reds, heart shapes, gentle curves, romantic, tender, harmonious, digital art",
            "surprise": "abstract art, bright oranges and yellows, explosive patterns, dynamic, energetic, unexpected, vibrant, digital art",
            "neutral": "abstract art, balanced colors, geometric patterns, calm, centered, minimalist, peaceful, digital art"
        }
        
        base_prompt = emotion_prompts.get(emotion, emotion_prompts["neutral"])
        return f"{base_prompt}, high quality, artistic, beautiful"
    
    def _svg_fallback(self, emotion: str) -> Dict[str, Any]:
        """Generate procedural SVG art based on emotion."""
        # Color schemes for emotions
        color_schemes = {
            "joy": {"primary": "#FFD700", "secondary": "#FFA500", "accent": "#FF6347"},
            "sadness": {"primary": "#4169E1", "secondary": "#6495ED", "accent": "#87CEEB"},
            "anger": {"primary": "#DC143C", "secondary": "#8B0000", "accent": "#FF4500"},
            "fear": {"primary": "#9370DB", "secondary": "#8B008B", "accent": "#4B0082"},
            "love": {"primary": "#FF69B4", "secondary": "#FF1493", "accent": "#FFB6C1"},
            "surprise": {"primary": "#FF8C00", "secondary": "#FFA500", "accent": "#FFD700"},
            "neutral": {"primary": "#808080", "secondary": "#A9A9A9", "accent": "#C0C0C0"}
        }
        
        colors = color_schemes.get(emotion, color_schemes["neutral"])
        
        # Generate SVG
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="grad1">
            <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:{colors['secondary']};stop-opacity:0.4" />
        </radialGradient>
        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{colors['secondary']};stop-opacity:0.6" />
            <stop offset="100%" style="stop-color:{colors['accent']};stop-opacity:0.8" />
        </linearGradient>
    </defs>
    
    <rect width="512" height="512" fill="url(#grad1)"/>
    
    <circle cx="256" cy="256" r="150" fill="url(#grad2)" opacity="0.7"/>
    <circle cx="180" cy="180" r="80" fill="{colors['accent']}" opacity="0.5"/>
    <circle cx="350" cy="320" r="100" fill="{colors['primary']}" opacity="0.4"/>
    
    <path d="M 50 256 Q 256 100, 462 256 T 50 256" fill="none" stroke="{colors['secondary']}" stroke-width="3" opacity="0.6"/>
    <path d="M 256 50 Q 400 256, 256 462 T 256 50" fill="none" stroke="{colors['accent']}" stroke-width="2" opacity="0.5"/>
</svg>"""
        
        # Convert SVG to PNG using PIL (simplified - in production use cairosvg)
        # For now, return SVG as bytes
        svg_bytes = svg.encode('utf-8')
        
        return {
            "image": svg_bytes,
            "model_used": "procedural_svg",
            "fallback": True,
            "format": "svg"
        }

"""
Reflection Generator Module - Production Ready
Uses OpenRouter primary with robust fallbacks.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .reflection_generator import generate_reflection as generate_reflection_sync

logger = logging.getLogger(__name__)

class ReflectionGenerator:
    """Generates personalized reflections using production-ready pipeline."""
    
    def __init__(self):
        pass  # All configuration is in reflection_generator.py
    
    async def generate(
        self,
        content: str,
        emotion: str,
        emotion_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate reflection, poem, and advice using OpenRouter + fallbacks.
        
        Returns:
            {
                "reflection": "...",
                "poem": "...",
                "advice": "...",
                "model_used": "...",
                "fallback": bool
            }
        """
        # Build user context from emotion data
        user_context = {
            "recent_mood_tags": [emotion] if emotion else [],
            "emotion_scores": emotion_scores,
            "language": "en",
            "sensitivity": "medium"
        }
        
        # Call the production reflection generator (sync function)
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            generate_reflection_sync,
            content,
            user_context
        )
        
        # Transform to match expected format
        return {
            "reflection": result.get("reflection", ""),
            "poem": result.get("poem_line", ""),
            "advice": self._format_micro_actions(result.get("micro_actions", [])),
            "model_used": result.get("model_used", "unknown"),
            "fallback": result.get("source") != "openrouter",
            "severity": result.get("severity", "calm"),
            "tone": result.get("tone", "gentle"),
            "micro_actions": result.get("micro_actions", []),
            "explainability": result.get("explainability", ""),
            "notes": result.get("notes", "")
        }
    
    def _format_micro_actions(self, actions: list) -> str:
        """Format micro-actions into readable advice text."""
        if not actions:
            return "Take a moment to breathe and be present."
        
        formatted = []
        for action in actions:
            label = action.get("label", "")
            instruction = action.get("instruction", "")
            formatted.append(f"{label}: {instruction}")
        
        return " | ".join(formatted)
        
        # Fallback to templates
        logger.warning("All reflection models failed, using templates")
        return self._template_fallback(content, emotion, emotion_scores)
    
    async def _call_model(self, content: str, emotion: str, model_config: Dict) -> Optional[Dict]:
        """Call LLM for reflection generation."""
        prompt = self._build_prompt(content, emotion)
        
        api_url = f"https://api-inference.huggingface.co/models/{model_config['id']}"
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": model_config.get("max_tokens", 256),
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        try:
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: requests.post(api_url, headers=headers, json=payload, timeout=model_config.get("timeout", 30))
                ),
                timeout=model_config.get("timeout", 30) + 2
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = ""
                
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    generated_text = data.get("generated_text", "")
                
                if generated_text:
                    # Parse the generated text
                    parsed = self._parse_generated_text(generated_text, prompt)
                    parsed["model_used"] = model_config["id"]
                    parsed["fallback"] = False
                    return parsed
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling {model_config['id']}: {str(e)}")
            return None
    
    def _build_prompt(self, content: str, emotion: str) -> str:
        """Build prompt for LLM."""
        prompt = f"""You are an empathetic AI companion helping someone process their emotions.

User's journal entry (emotion: {emotion}):
{content[:500]}

Please provide:
1. A warm, empathetic reflection (2-3 sentences)
2. A short poem (4-6 lines) capturing their emotional state
3. Gentle advice or encouragement (1-2 sentences)

Format your response as:
REFLECTION: [your reflection]
POEM: [your poem]
ADVICE: [your advice]
"""
        return prompt
    
    def _parse_generated_text(self, text: str, prompt: str) -> Dict[str, str]:
        """Parse LLM output into structured format."""
        # Remove the prompt if it's included
        if prompt in text:
            text = text.replace(prompt, "").strip()
        
        reflection = ""
        poem = ""
        advice = ""
        
        # Try to parse structured output
        if "REFLECTION:" in text:
            parts = text.split("REFLECTION:")
            if len(parts) > 1:
                rest = parts[1]
                if "POEM:" in rest:
                    reflection_part, rest = rest.split("POEM:", 1)
                    reflection = reflection_part.strip()
                    if "ADVICE:" in rest:
                        poem_part, advice_part = rest.split("ADVICE:", 1)
                        poem = poem_part.strip()
                        advice = advice_part.strip()
        
        # Fallback: use the whole text as reflection if parsing failed
        if not reflection:
            reflection = text[:300]
        
        return {
            "reflection": reflection or "Thank you for sharing your thoughts with me.",
            "poem": poem or "Your feelings matter,\nEach moment is valid,\nYou are not alone.",
            "advice": advice or "Be gentle with yourself today."
        }
    
    def _template_fallback(self, content: str, emotion: str, scores: Dict) -> Dict[str, Any]:
        """Generate reflection using templates."""
        templates = {
            "joy": {
                "reflection": "I can feel the happiness radiating from your words! It's wonderful to see you experiencing such positive emotions. These moments of joy are precious and worth celebrating.",
                "poem": "Sunshine breaks through clouds,\nYour heart sings with delight,\nJoy blooms within you,\nA beautiful, radiant light.",
                "advice": "Savor this feeling and remember it during challenging times. You deserve this happiness!"
            },
            "sadness": {
                "reflection": "I hear the weight in your words, and I want you to know that your feelings are completely valid. Sadness is a natural part of being human, and it's okay to feel this way.",
                "poem": "Tears fall like gentle rain,\nWashing over tender pain,\nIn darkness, stars still shine,\nHealing comes with time.",
                "advice": "Be patient and compassionate with yourself. It's okay to not be okay sometimes. Reach out to someone you trust if you need support."
            },
            "anger": {
                "reflection": "I can sense your frustration and anger. These feelings are telling you that something matters to you. It's important to acknowledge these emotions rather than suppress them.",
                "poem": "Fire burns within your chest,\nDemanding to be heard,\nYour anger speaks of needs unmet,\nOf boundaries that were blurred.",
                "advice": "Take some deep breaths and give yourself space to process these feelings. Consider what triggered this anger and what you might need to feel better."
            },
            "fear": {
                "reflection": "I understand that you're feeling anxious or afraid. Fear can be overwhelming, but remember that you've faced challenges before and made it through. You're stronger than you know.",
                "poem": "Shadows dance and worries grow,\nBut courage lives within,\nOne breath, one step, one moment,\nIs how healing can begin.",
                "advice": "Ground yourself in the present moment. What you're feeling is temporary. Try some deep breathing or reach out to someone who makes you feel safe."
            },
            "love": {
                "reflection": "The warmth and affection in your words are beautiful. Love—whether for others, for life, or for yourself—is one of the most powerful emotions we can experience.",
                "poem": "Hearts connect across the space,\nLove's gentle, healing grace,\nIn giving and receiving too,\nWe find what makes us true.",
                "advice": "Cherish these connections and don't be afraid to express your feelings. Love shared is love multiplied."
            },
            "neutral": {
                "reflection": "Thank you for taking the time to reflect and share your thoughts. Even in moments of calm or uncertainty, the act of self-reflection is valuable and shows self-awareness.",
                "poem": "In stillness, wisdom grows,\nA quiet, steady flow,\nNot every day must soar or sink,\nSometimes we pause to think.",
                "advice": "Use this calm moment to check in with yourself. What do you need right now? What would make today meaningful for you?"
            }
        }
        
        template = templates.get(emotion, templates["neutral"])
        
        return {
            "reflection": template["reflection"],
            "poem": template["poem"],
            "advice": template["advice"],
            "model_used": "template",
            "fallback": True
        }

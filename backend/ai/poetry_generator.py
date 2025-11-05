"""
Poetry and Reflection Generator for MindMirror AI
Creates personalized poetic reflections and empathetic advice
"""

import logging
from typing import Dict
import httpx
from config import settings

logger = logging.getLogger(__name__)

class PoetryGenerator:
    """Generates personalized poetry and reflections using AI"""
    
    def __init__(self):
        """Initialize poetry generator"""
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.POETRY_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}"}
    
    async def generate_reflection(
        self,
        user_input: str,
        emotion: str,
        context: str = ""
    ) -> Dict:
        """
        Generate personalized reflection and poetry
        
        Args:
            user_input: User's original text
            emotion: Detected emotion
            context: Additional context
            
        Returns:
            Dictionary containing reflection, poetry, and advice
        """
        try:
            # Create prompt for the model
            prompt = self._create_prompt(user_input, emotion, context)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 300,
                            "temperature": 0.8,
                            "top_p": 0.9,
                            "do_sample": True
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get('generated_text', '')
                        
                        # Extract the response after the prompt
                        if '[/INST]' in generated_text:
                            response_text = generated_text.split('[/INST]')[-1].strip()
                        else:
                            response_text = generated_text.replace(prompt, '').strip()
                        
                        return self._parse_reflection(response_text, emotion)
                    
                    return self._get_fallback_reflection(user_input, emotion)
                
                else:
                    logger.error(f"Poetry generation API error: {response.status_code}")
                    return self._get_fallback_reflection(user_input, emotion)
                    
        except Exception as e:
            logger.error(f"Error generating reflection: {str(e)}")
            return self._get_fallback_reflection(user_input, emotion)
    
    def _create_prompt(self, user_input: str, emotion: str, context: str) -> str:
        """
        Create prompt for the AI model
        
        Args:
            user_input: User's text
            emotion: Detected emotion
            context: Additional context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""[INST] You are a compassionate emotional wellness companion for youth and Gen Z. 
A user has shared their feelings with you. They are experiencing {emotion}.

User's message: "{user_input}"

Please provide:
1. A short, empathetic reflection (2-3 sentences)
2. A brief, meaningful poem (4-6 lines) that captures their emotional state
3. One gentle piece of advice or encouragement

Be warm, understanding, and youth-friendly. Use modern, relatable language. [/INST]"""
        
        return prompt
    
    def _parse_reflection(self, generated_text: str, emotion: str) -> Dict:
        """
        Parse generated reflection into structured format
        
        Args:
            generated_text: AI-generated text
            emotion: Detected emotion
            
        Returns:
            Structured reflection dictionary
        """
        lines = generated_text.strip().split('\n')
        
        reflection = ""
        poem = ""
        advice = ""
        
        current_section = "reflection"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section changes
            if any(keyword in line.lower() for keyword in ['poem:', 'poetry:', 'verse:']):
                current_section = "poem"
                continue
            elif any(keyword in line.lower() for keyword in ['advice:', 'encouragement:', 'suggestion:']):
                current_section = "advice"
                continue
            
            # Add to appropriate section
            if current_section == "reflection":
                reflection += line + " "
            elif current_section == "poem":
                poem += line + "\n"
            elif current_section == "advice":
                advice += line + " "
        
        # If parsing failed, use the whole text as reflection
        if not reflection and not poem:
            reflection = generated_text[:200]
            poem = self._generate_simple_poem(emotion)
        
        return {
            "reflection": reflection.strip() or self._get_default_reflection(emotion),
            "poem": poem.strip() or self._generate_simple_poem(emotion),
            "advice": advice.strip() or self._get_default_advice(emotion),
            "emotion": emotion
        }
    
    def _get_fallback_reflection(self, user_input: str, emotion: str) -> Dict:
        """
        Generate fallback reflection when API fails
        
        Args:
            user_input: User's input
            emotion: Detected emotion
            
        Returns:
            Fallback reflection dictionary
        """
        return {
            "reflection": self._get_default_reflection(emotion),
            "poem": self._generate_simple_poem(emotion),
            "advice": self._get_default_advice(emotion),
            "emotion": emotion
        }
    
    def _get_default_reflection(self, emotion: str) -> str:
        """Get default reflection based on emotion"""
        reflections = {
            "joy": "Your happiness radiates through your words! It's beautiful to see you experiencing such positive emotions. These moments of joy are precious—hold onto them.",
            "sadness": "I hear the weight in your words, and I want you to know that it's completely okay to feel sad. Your feelings are valid, and you don't have to face them alone.",
            "anger": "I can sense the frustration you're feeling. Anger is a natural emotion, and acknowledging it is the first step. Take a moment to breathe—you've got this.",
            "fear": "I understand that you're feeling anxious or worried. These feelings can be overwhelming, but remember: you're stronger than you think, and this too shall pass.",
            "love": "The warmth and affection in your words are truly touching. Love is a powerful force, and it's wonderful that you're experiencing it so deeply.",
            "surprise": "Life has thrown you a curveball! Surprises can be exciting or unsettling, but they're also opportunities for growth and new experiences.",
            "neutral": "You seem to be in a calm, reflective state. Sometimes, these quiet moments are exactly what we need to recharge and find clarity."
        }
        
        return reflections.get(emotion.lower(), "Thank you for sharing your feelings with me. Your emotional honesty is a sign of strength.")
    
    def _generate_simple_poem(self, emotion: str) -> str:
        """Generate a simple poem based on emotion"""
        poems = {
            "joy": """Sunshine dances in your heart,
Laughter echoes, a brand new start,
Happiness blooms like flowers in spring,
Your spirit soars on golden wing.""",
            
            "sadness": """Tears fall like gentle rain,
Washing away the silent pain,
In darkness, stars still softly gleam,
Tomorrow brings a brighter dream.""",
            
            "anger": """Fire burns within your chest,
Frustration puts you to the test,
But storms will pass, the sky will clear,
Peace and calm are drawing near.""",
            
            "fear": """Shadows whisper in the night,
Anxiety dims the morning light,
But courage lives within your soul,
You have the strength to reach your goal.""",
            
            "love": """Hearts entwined in tender grace,
Warmth reflected in your face,
Love's sweet melody plays on,
A beautiful, eternal song.""",
            
            "surprise": """Life turns in unexpected ways,
Bringing wonder to your days,
Each surprise, a gift to hold,
New stories waiting to unfold.""",
            
            "neutral": """Stillness settles, calm and deep,
Quiet moments yours to keep,
In this peace, you find your way,
Balanced, centered, come what may."""
        }
        
        return poems.get(emotion.lower(), """Your feelings paint a story true,
Each emotion, a different hue,
In this moment, you are here,
Brave and honest, crystal clear.""")
    
    def _get_default_advice(self, emotion: str) -> str:
        """Get default advice based on emotion"""
        advice = {
            "joy": "Savor this moment! Consider journaling about what brought you this joy, so you can revisit it when you need a boost.",
            "sadness": "Be gentle with yourself. It's okay to not be okay. Reach out to someone you trust, or try a small act of self-care today.",
            "anger": "Channel this energy into something productive. Physical activity, creative expression, or talking it out can help release the tension.",
            "fear": "Ground yourself in the present moment. Try the 5-4-3-2-1 technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste.",
            "love": "Cherish this feeling! Express your love to those who matter. Small gestures of kindness can amplify this beautiful emotion.",
            "surprise": "Embrace the unexpected! Sometimes the best experiences come from moments we didn't plan. Stay open and curious.",
            "neutral": "Use this calm to reflect and recharge. It's a perfect time for meditation, planning, or simply being present."
        }
        
        return advice.get(emotion.lower(), "Take a moment to acknowledge your feelings. Self-awareness is the first step toward emotional wellness.")

"""
Production-Ready Reflection Generator with OpenRouter Primary + Fallbacks
Implements robust error handling, caching, and graceful degradation.
"""

import os
import json
import time
import logging
import hashlib
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Free models on OpenRouter (in order of preference)
FREE_MODELS = [
    "google/gemini-flash-1.5",      # Best free option - fast and good quality
    "meta-llama/llama-3.1-8b-instruct:free",  # Backup free option
    "mistralai/mistral-7b-instruct:free"      # Another free backup
]
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", FREE_MODELS[0])  # Default to Gemini Flash
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
HF_API_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")

# Timeouts and retries
REQUEST_TIMEOUT = 12  # seconds
MAX_RETRIES = 2
INITIAL_BACKOFF = 1  # seconds

# Cache settings
CACHE_TTL = 21600  # 6 hours in seconds
_reflection_cache = {}  # {cache_key: (result, timestamp)}


# ============================================================================
# SAFETY KEYWORDS
# ============================================================================

URGENT_KEYWORDS = [
    "kill myself", "end my life", "suicide", "want to die", "harm myself",
    "cut myself", "hurt myself", "no reason to live", "better off dead"
]

EMERGENCY_RESOURCES = {
    "global": "If you're in crisis, please reach out: International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
    "us": "National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
    "uk": "Samaritans: 116 123",
    "sri_lanka": "Sumithrayo: 011-2692909 or 011-2696666"
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cache_key(input_text: str, user_context: dict) -> str:
    """Generate cache key from input and context."""
    context_str = json.dumps(user_context, sort_keys=True)
    combined = f"{input_text}:{context_str}"
    return hashlib.md5(combined.encode()).hexdigest()


def get_cached_reflection(cache_key: str) -> Optional[Dict]:
    """Retrieve cached reflection if not expired."""
    if cache_key in _reflection_cache:
        result, timestamp = _reflection_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            logger.info(f"Cache hit for reflection: {cache_key[:8]}...")
            return result
        else:
            del _reflection_cache[cache_key]
    return None


def set_cached_reflection(cache_key: str, result: Dict):
    """Store reflection in cache."""
    _reflection_cache[cache_key] = (result, time.time())
    
    # Cleanup old entries if cache grows too large
    if len(_reflection_cache) > 100:
        current_time = time.time()
        _reflection_cache.clear()  # Simple cleanup


def check_urgency(input_text: str) -> bool:
    """Check if input contains urgent/crisis keywords."""
    text_lower = input_text.lower()
    return any(keyword in text_lower for keyword in URGENT_KEYWORDS)


def validate_reflection_json(data: dict) -> bool:
    """Validate reflection JSON has required fields."""
    required_fields = ["reflection", "poem_line", "micro_actions", "severity", "tone"]
    return all(field in data for field in required_fields)


# ============================================================================
# OPENROUTER PRIMARY
# ============================================================================

def call_openrouter_with_model(input_text: str, user_context: dict, model: str) -> Dict[str, Any]:
    """
    Call OpenRouter API with a specific model.
    Returns structured JSON or raises exception.
    """
    # Build prompt
    prompt = build_reflection_prompt(input_text, user_context)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mindmirror.ai",  # Optional: for OpenRouter analytics
        "X-Title": "MindMirror AI"
    }
    
    payload = {
        "model": model,  # Use the model parameter
        "messages": [
            {
                "role": "system",
                "content": "You are an empathetic mental wellness assistant. Respond ONLY with valid JSON matching the exact schema provided."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
        # Note: response_format not supported by all free models
    }
    
    backoff = INITIAL_BACKOFF
    last_error = None
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            logger.info(f"OpenRouter attempt {attempt + 1}/{MAX_RETRIES + 1} with model: {model}")
            
            response = requests.post(
                OPENROUTER_BASE_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract content from OpenRouter response
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse JSON from content
                reflection_data = json.loads(content)
                
                # Validate structure
                if validate_reflection_json(reflection_data):
                    reflection_data["source"] = "openrouter"
                    reflection_data["model_used"] = model
                    logger.info(f"OpenRouter reflection generated successfully with {model}")
                    return reflection_data
                else:
                    raise ValueError("Invalid JSON structure from OpenRouter")
            
            elif response.status_code in (429, 502, 503, 504):
                # Rate limit or server error - retry with backoff
                logger.warning(f"OpenRouter returned {response.status_code}, retrying in {backoff}s")
                time.sleep(backoff)
                backoff *= 2
                last_error = f"HTTP {response.status_code}"
                continue
            
            else:
                response.raise_for_status()
        
        except requests.Timeout:
            logger.warning(f"OpenRouter timeout on attempt {attempt + 1}")
            last_error = "Timeout"
            time.sleep(backoff)
            backoff *= 2
            continue
        
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"OpenRouter JSON parsing error: {str(e)}")
            last_error = f"Parse error: {str(e)}"
            break  # Don't retry on parse errors
        
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            last_error = str(e)
            break
    
    raise RuntimeError(f"OpenRouter model {model} failed after {MAX_RETRIES + 1} attempts: {last_error}")


def call_openrouter(input_text: str, user_context: dict) -> Dict[str, Any]:
    """
    Call OpenRouter API trying multiple free models in order.
    Returns structured JSON or raises exception.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment")
    
    # Try each free model in order
    models_to_try = [OPENROUTER_MODEL] + [m for m in FREE_MODELS if m != OPENROUTER_MODEL]
    
    for model in models_to_try:
        try:
            logger.info(f"Trying OpenRouter with free model: {model}")
            result = call_openrouter_with_model(input_text, user_context, model)
            return result
        except Exception as e:
            logger.warning(f"Free model {model} failed: {str(e)}")
            continue
    
    # All free models failed
    raise RuntimeError(f"All OpenRouter free models failed. Tried: {', '.join(models_to_try)}")


def build_reflection_prompt(input_text: str, user_context: dict) -> str:
    """Build the prompt for OpenRouter."""
    context_info = ""
    if user_context:
        if user_context.get("recent_mood_tags"):
            context_info += f"\nRecent moods: {', '.join(user_context['recent_mood_tags'])}"
        if user_context.get("language"):
            context_info += f"\nPreferred language: {user_context['language']}"
        if user_context.get("sensitivity"):
            context_info += f"\nSensitivity level: {user_context['sensitivity']}"
    
    prompt = f"""You are an empathetic mental wellness assistant. Given the user's text and context, produce a JSON object with these exact fields:

User text: "{input_text}"
{context_info}

Required JSON structure:
{{
  "reflection": "1-3 sentences of empathetic, non-judgmental reflection",
  "poem_line": "One poetic line capturing the emotion",
  "micro_actions": [
    {{"label": "Action name", "duration_seconds": 60, "instruction": "Clear step-by-step instruction"}},
    {{"label": "Action name", "duration_seconds": 180, "instruction": "Clear step-by-step instruction"}}
  ],
  "severity": "calm" or "notice" or "urgent",
  "tone": "gentle" or "encouraging" or "practical" or "creative",
  "explainability": "Brief rationale for why this reflection fits"
}}

Guidelines:
- Keep reflection kind, warm, and validating
- Micro-actions must be realistic, under 5 minutes, no equipment needed
- If text suggests self-harm or crisis, set severity to "urgent" and include safety resources in reflection
- severity: "calm" for mild feelings, "notice" for elevated stress, "urgent" for crisis indicators
- Respond ONLY with valid JSON, no other text

Output JSON:"""
    
    return prompt


# ============================================================================
# FALLBACK 1: HUGGING FACE INFERENCE
# ============================================================================

def call_huggingface_fallback(input_text: str, user_context: dict) -> Dict[str, Any]:
    """
    Fallback to Hugging Face Inference API.
    Uses free community models.
    """
    logger.info("Attempting Hugging Face fallback")
    
    # Try multiple HF models in order
    hf_models = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "HuggingFaceH4/zephyr-7b-beta",
        "tiiuae/falcon-7b-instruct"
    ]
    
    prompt = build_reflection_prompt(input_text, user_context)
    
    headers = {"Content-Type": "application/json"}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
    
    for model in hf_models:
        try:
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 400,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract generated text
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                else:
                    generated_text = result.get("generated_text", "")
                
                # Try to parse JSON from response
                reflection_data = json.loads(generated_text)
                
                if validate_reflection_json(reflection_data):
                    reflection_data["source"] = "huggingface"
                    reflection_data["model_used"] = model
                    logger.info(f"HF reflection generated with {model}")
                    return reflection_data
            
            elif response.status_code == 503:
                # Model loading, try next
                logger.warning(f"HF model {model} loading, trying next")
                continue
        
        except Exception as e:
            logger.warning(f"HF model {model} failed: {str(e)}")
            continue
    
    raise RuntimeError("All Hugging Face models failed")


# ============================================================================
# FALLBACK 2: TEMPLATE-BASED GENERATOR
# ============================================================================

EMOTION_TEMPLATES = {
    "sad": {
        "reflections": [
            "I hear the weight you're carrying. Sadness is a natural response to loss or disappointment, and it's okay to feel this way.",
            "Your feelings are valid. Sometimes sadness is our heart's way of processing what matters to us.",
            "It's brave to acknowledge sadness. This feeling won't last forever, even though it feels heavy right now."
        ],
        "poems": [
            "Even in the darkest night, stars find a way to shine.",
            "Tears water the seeds of tomorrow's strength.",
            "Your heart knows how to heal, one gentle breath at a time."
        ],
        "actions": [
            {"label": "Gentle breathing", "duration_seconds": 120, "instruction": "Sit comfortably. Breathe in for 4 counts, hold for 4, out for 6. Repeat 5 times."},
            {"label": "Comfort ritual", "duration_seconds": 180, "instruction": "Make a warm drink, wrap yourself in a blanket, and sit by a window for 3 minutes."}
        ],
        "tone": "gentle"
    },
    "anxious": {
        "reflections": [
            "Anxiety can feel overwhelming, but you're not alone in this. Your nervous system is trying to protect you.",
            "I see you're feeling anxious. That racing mind and tight chest are real, and there are ways to ease them.",
            "Anxiety is uncomfortable, but it's also temporary. Let's find a way to ground you in this moment."
        ],
        "poems": [
            "Breathe in calm, breathe out worry. You are safe in this moment.",
            "Like waves, anxiety rises and falls. You are the steady shore.",
            "One breath at a time, you find your center again."
        ],
        "actions": [
            {"label": "5-4-3-2-1 grounding", "duration_seconds": 180, "instruction": "Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste."},
            {"label": "Progressive relaxation", "duration_seconds": 240, "instruction": "Tense and release each muscle group: feet, legs, stomach, hands, shoulders, face."}
        ],
        "tone": "practical"
    },
    "angry": {
        "reflections": [
            "Anger is a powerful emotion that tells us something matters. It's okay to feel this way.",
            "I hear your frustration. Anger often masks hurt or unmet needs. You deserve to be heard.",
            "Your anger is valid. Let's find a healthy way to express and release this energy."
        ],
        "poems": [
            "Fire can warm or burn. Choose how you channel this flame.",
            "Anger is energy seeking expression. Let it flow, then let it go.",
            "Beneath the storm, your calm center waits."
        ],
        "actions": [
            {"label": "Physical release", "duration_seconds": 120, "instruction": "Do 20 jumping jacks or punch a pillow. Let your body express the energy."},
            {"label": "Cooling breath", "duration_seconds": 180, "instruction": "Breathe in through nose, out through mouth with a 'ha' sound. Imagine releasing heat."}
        ],
        "tone": "encouraging"
    },
    "overwhelmed": {
        "reflections": [
            "Feeling overwhelmed means you care deeply. It's a sign you're human, not weak.",
            "When everything feels like too much, remember: you only need to take the next small step.",
            "Overwhelm is your system saying 'pause.' Let's break this down into manageable pieces."
        ],
        "poems": [
            "Mountains are climbed one step at a time, not all at once.",
            "In the chaos, find one small thing you can control.",
            "You don't have to carry it all. Set something down."
        ],
        "actions": [
            {"label": "Brain dump", "duration_seconds": 300, "instruction": "Write everything on your mind for 5 minutes. Don't organize, just release."},
            {"label": "One thing", "duration_seconds": 120, "instruction": "Choose the smallest task you can do right now. Do only that. Celebrate it."}
        ],
        "tone": "practical"
    },
    "lonely": {
        "reflections": [
            "Loneliness is painful, and I'm sorry you're feeling this way. Connection is a fundamental human need.",
            "Even in loneliness, you're not truly alone. Your feelings matter, and there are people who care.",
            "Loneliness can feel like an empty room, but small connections can light it up again."
        ],
        "poems": [
            "Even the moon needs the sun. Reach out, even in small ways.",
            "Loneliness is a bridge, not a destination. Cross it gently.",
            "Your presence matters. Someone needs your light, even if you can't see it yet."
        ],
        "actions": [
            {"label": "Reach out", "duration_seconds": 180, "instruction": "Send a text to someone you haven't talked to in a while. Just say hi."},
            {"label": "Self-compassion", "duration_seconds": 120, "instruction": "Place hand on heart. Say: 'I am here for myself. I am worthy of connection.'"}
        ],
        "tone": "gentle"
    },
    "neutral": {
        "reflections": [
            "Thank you for sharing. Sometimes just expressing what's on our mind can bring clarity.",
            "I'm here with you. Whatever you're feeling is valid and worth acknowledging.",
            "Taking time to reflect is a gift you give yourself. Keep going."
        ],
        "poems": [
            "In stillness, we find ourselves.",
            "Every moment of awareness is a step toward growth.",
            "Your journey is uniquely yours. Honor it."
        ],
        "actions": [
            {"label": "Mindful moment", "duration_seconds": 120, "instruction": "Close eyes. Notice your breath. Just be present for 2 minutes."},
            {"label": "Gratitude pause", "duration_seconds": 180, "instruction": "Think of 3 small things you're grateful for today. Really feel them."}
        ],
        "tone": "creative"
    }
}


def detect_emotion_from_text(text: str) -> str:
    """Simple keyword-based emotion detection for fallback."""
    text_lower = text.lower()
    
    # Check for specific emotion keywords
    if any(word in text_lower for word in ["sad", "depressed", "down", "hopeless", "crying"]):
        return "sad"
    elif any(word in text_lower for word in ["anxious", "worried", "nervous", "panic", "scared", "afraid"]):
        return "anxious"
    elif any(word in text_lower for word in ["angry", "mad", "furious", "frustrated", "irritated"]):
        return "angry"
    elif any(word in text_lower for word in ["overwhelmed", "too much", "can't handle", "stressed"]):
        return "overwhelmed"
    elif any(word in text_lower for word in ["lonely", "alone", "isolated", "nobody"]):
        return "lonely"
    else:
        return "neutral"


def generate_template_reflection(input_text: str, user_context: dict) -> Dict[str, Any]:
    """
    Generate reflection using template-based approach.
    High-quality fallback when network models fail.
    """
    logger.info("Using template-based reflection fallback")
    
    # Detect emotion
    emotion = detect_emotion_from_text(input_text)
    template = EMOTION_TEMPLATES.get(emotion, EMOTION_TEMPLATES["neutral"])
    
    # Select random items from templates
    import random
    reflection = random.choice(template["reflections"])
    poem_line = random.choice(template["poems"])
    micro_actions = template["actions"][:2]  # Take first 2 actions
    
    # Determine severity
    if check_urgency(input_text):
        severity = "urgent"
        reflection = f"{reflection} {EMERGENCY_RESOURCES['global']}"
    elif emotion in ["anxious", "overwhelmed", "angry"]:
        severity = "notice"
    else:
        severity = "calm"
    
    return {
        "reflection": reflection,
        "poem_line": poem_line,
        "micro_actions": micro_actions,
        "severity": severity,
        "tone": template["tone"],
        "explainability": f"Detected emotion: {emotion}. Used template-based reflection for reliability.",
        "source": "template",
        "model_used": "template_v1"
    }


# ============================================================================
# FALLBACK 3: MINIMAL SAFE RESPONSE
# ============================================================================

def generate_minimal_fallback(input_text: str, user_context: dict) -> Dict[str, Any]:
    """
    Absolute minimal fallback when everything else fails.
    Always returns something safe and helpful.
    """
    logger.warning("Using minimal fallback - all other methods failed")
    
    is_urgent = check_urgency(input_text)
    
    if is_urgent:
        reflection = f"I hear you, and I'm concerned. Please reach out for immediate support. {EMERGENCY_RESOURCES['global']}"
        severity = "urgent"
    else:
        reflection = "I hear you. That sounds really heavy. Try taking a few deep breaths right now. You're not alone in this."
        severity = "notice"
    
    return {
        "reflection": reflection,
        "poem_line": "One breath at a time, you find your way.",
        "micro_actions": [
            {
                "label": "Deep breathing",
                "duration_seconds": 60,
                "instruction": "Breathe in slowly for 4 counts, hold for 4, out for 6. Repeat 3 times."
            }
        ],
        "severity": severity,
        "tone": "gentle",
        "explainability": "Minimal safe response provided due to system limitations.",
        "source": "minimal_fallback",
        "model_used": "none",
        "notes": "All AI services temporarily unavailable. This is a safe fallback response."
    }


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def generate_reflection(input_text: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate empathetic reflection with robust fallback chain.
    
    Args:
        input_text: User's text or transcript
        user_context: Optional context dict with username, recent_mood_tags, language, etc.
    
    Returns:
        Dict with reflection, poem_line, micro_actions, severity, tone, etc.
    """
    if not input_text or not input_text.strip():
        return generate_minimal_fallback("", user_context or {})
    
    user_context = user_context or {}
    
    # Check cache first
    cache_key = get_cache_key(input_text, user_context)
    cached = get_cached_reflection(cache_key)
    if cached:
        cached["from_cache"] = True
        return cached
    
    # Check for urgent keywords immediately
    if check_urgency(input_text):
        logger.warning("Urgent keywords detected - using safe response")
        result = generate_minimal_fallback(input_text, user_context)
        result["severity"] = "urgent"
        set_cached_reflection(cache_key, result)
        return result
    
    # Try primary: OpenRouter
    try:
        result = call_openrouter(input_text, user_context)
        set_cached_reflection(cache_key, result)
        return result
    except Exception as e:
        logger.warning(f"OpenRouter failed: {str(e)}")
    
    # Try fallback 1: Hugging Face
    try:
        result = call_huggingface_fallback(input_text, user_context)
        result["notes"] = "Using fallback AI service (primary temporarily unavailable)"
        set_cached_reflection(cache_key, result)
        return result
    except Exception as e:
        logger.warning(f"Hugging Face fallback failed: {str(e)}")
    
    # Try fallback 2: Template-based
    try:
        result = generate_template_reflection(input_text, user_context)
        result["notes"] = "Using local reflection (AI services temporarily limited)"
        set_cached_reflection(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Template fallback failed: {str(e)}")
    
    # Fallback 3: Minimal safe response (always succeeds)
    result = generate_minimal_fallback(input_text, user_context)
    set_cached_reflection(cache_key, result)
    return result


# ============================================================================
# TESTING HELPER
# ============================================================================

if __name__ == "__main__":
    # Test the reflection generator
    test_inputs = [
        "I'm feeling really anxious about my exams tomorrow",
        "I feel so alone and nobody understands me",
        "I'm so angry at my friend for betraying my trust"
    ]
    
    for test_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"Input: {test_input}")
        print(f"{'='*60}")
        
        result = generate_reflection(test_input, {"language": "en", "sensitivity": "medium"})
        print(json.dumps(result, indent=2))

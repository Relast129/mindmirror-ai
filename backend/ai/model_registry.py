"""
Model Registry - Prioritized list of free/open-source models
Implements fallback strategy for robustness.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Registry of free AI models with fallback priorities."""
    
    # Emotion detection models (text)
    EMOTION_MODELS = [
        {
            "id": "j-hartmann/emotion-english-distilroberta-base",
            "type": "huggingface",
            "task": "text-classification",
            "timeout": 12,
            "description": "DistilRoBERTa emotion classifier"
        },
        {
            "id": "nateraw/bert-base-uncased-emotion",
            "type": "huggingface",
            "task": "text-classification",
            "timeout": 12,
            "description": "BERT emotion classifier"
        },
        {
            "id": "bhadresh-savani/distilbert-base-uncased-emotion",
            "type": "huggingface",
            "task": "text-classification",
            "timeout": 12,
            "description": "DistilBERT emotion classifier"
        }
    ]
    
    # Speech-to-text models
    TRANSCRIPTION_MODELS = [
        {
            "id": "openai/whisper-tiny",
            "type": "huggingface",
            "task": "automatic-speech-recognition",
            "timeout": 15,
            "description": "Whisper tiny model"
        },
        {
            "id": "openai/whisper-base",
            "type": "huggingface",
            "task": "automatic-speech-recognition",
            "timeout": 20,
            "description": "Whisper base model"
        },
        {
            "id": "facebook/wav2vec2-base-960h",
            "type": "huggingface",
            "task": "automatic-speech-recognition",
            "timeout": 15,
            "description": "Wav2Vec2 model"
        }
    ]
    
    # Text generation models for reflection/poetry
    REFLECTION_MODELS = [
        {
            "id": "HuggingFaceH4/zephyr-7b-beta",
            "type": "huggingface",
            "task": "text-generation",
            "timeout": 30,
            "description": "Zephyr 7B instruction model",
            "max_tokens": 256
        },
        {
            "id": "mistralai/Mistral-7B-Instruct-v0.1",
            "type": "huggingface",
            "task": "text-generation",
            "timeout": 30,
            "description": "Mistral 7B Instruct",
            "max_tokens": 256
        },
        {
            "id": "google/flan-t5-base",
            "type": "huggingface",
            "task": "text2text-generation",
            "timeout": 15,
            "description": "FLAN-T5 base model",
            "max_tokens": 200
        }
    ]
    
    # Image generation models
    ART_MODELS = [
        {
            "id": "stabilityai/stable-diffusion-2-1-base",
            "type": "huggingface",
            "task": "text-to-image",
            "timeout": 45,
            "description": "Stable Diffusion 2.1 base (512x512)",
            "params": {"width": 512, "height": 512}
        },
        {
            "id": "CompVis/stable-diffusion-v1-4",
            "type": "huggingface",
            "task": "text-to-image",
            "timeout": 45,
            "description": "Stable Diffusion 1.4",
            "params": {"width": 512, "height": 512}
        },
        {
            "id": "runwayml/stable-diffusion-v1-5",
            "type": "huggingface",
            "task": "text-to-image",
            "timeout": 45,
            "description": "Stable Diffusion 1.5",
            "params": {"width": 512, "height": 512}
        }
    ]
    
    # Text-to-speech models
    TTS_MODELS = [
        {
            "id": "facebook/fastspeech2-en-ljspeech",
            "type": "huggingface",
            "task": "text-to-speech",
            "timeout": 20,
            "description": "FastSpeech2 TTS"
        },
        {
            "id": "espnet/kan-bayashi_ljspeech_vits",
            "type": "huggingface",
            "task": "text-to-speech",
            "timeout": 20,
            "description": "ESPnet VITS TTS"
        }
    ]
    
    @classmethod
    def get_models(cls, task: str) -> List[Dict[str, Any]]:
        """Get prioritized list of models for a task."""
        task_map = {
            "emotion": cls.EMOTION_MODELS,
            "transcription": cls.TRANSCRIPTION_MODELS,
            "reflection": cls.REFLECTION_MODELS,
            "art": cls.ART_MODELS,
            "tts": cls.TTS_MODELS
        }
        return task_map.get(task, [])
    
    @classmethod
    def get_fallback_config(cls, task: str) -> Dict[str, Any]:
        """Get fallback configuration when all models fail."""
        fallback_configs = {
            "emotion": {
                "type": "template",
                "emotions": ["neutral", "contemplative"],
                "confidence": 0.5,
                "message": "Using template-based emotion detection"
            },
            "transcription": {
                "type": "local",
                "library": "speech_recognition",
                "message": "Using local speech recognition (requires setup)"
            },
            "reflection": {
                "type": "template",
                "message": "Using template-based reflection generation"
            },
            "art": {
                "type": "procedural",
                "format": "svg",
                "message": "Using procedural SVG art generation"
            },
            "tts": {
                "type": "gtts",
                "message": "Using Google Text-to-Speech (gTTS)"
            }
        }
        return fallback_configs.get(task, {})

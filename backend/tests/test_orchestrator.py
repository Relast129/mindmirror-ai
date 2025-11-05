"""
Tests for AI Orchestrator
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from ai.orchestrator import AIOrchestrator

@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return AIOrchestrator()

@pytest.mark.asyncio
async def test_process_input_basic(orchestrator):
    """Test basic input processing."""
    # Mock the analyzer methods
    with patch.object(orchestrator.emotion_analyzer, 'analyze', new_callable=AsyncMock) as mock_emotion, \
         patch.object(orchestrator.reflection_generator, 'generate', new_callable=AsyncMock) as mock_reflection, \
         patch.object(orchestrator.art_generator, 'generate', new_callable=AsyncMock) as mock_art:
        
        # Setup mocks
        mock_emotion.return_value = {
            "emotions": ["joy", "gratitude"],
            "scores": {"joy": 0.85, "gratitude": 0.72},
            "model_used": "test-model",
            "fallback": False
        }
        
        mock_reflection.return_value = {
            "reflection": "Test reflection",
            "poem": "Test poem",
            "advice": "Test advice",
            "model_used": "test-model",
            "fallback": False
        }
        
        mock_art.return_value = {
            "image": b"fake_image_data",
            "model_used": "test-model",
            "fallback": False
        }
        
        # Test
        result = await orchestrator.process_input("I'm feeling happy today!", "text")
        
        # Assertions
        assert result["emotions"] == ["joy", "gratitude"]
        assert result["reflection"] == "Test reflection"
        assert result["poem"] == "Test poem"
        assert result["art_image"] == b"fake_image_data"
        assert result["processing_time"] > 0
        assert not result["fallback_used"]

@pytest.mark.asyncio
async def test_process_input_with_fallback(orchestrator):
    """Test input processing with fallback."""
    with patch.object(orchestrator.emotion_analyzer, 'analyze', new_callable=AsyncMock) as mock_emotion:
        # Simulate fallback
        mock_emotion.return_value = {
            "emotions": ["neutral"],
            "scores": {"neutral": 0.7},
            "model_used": "template",
            "fallback": True
        }
        
        result = await orchestrator.process_input("Test content", "text")
        
        # Should still return valid results
        assert "emotions" in result
        assert result["fallback_used"]

@pytest.mark.asyncio
async def test_caching(orchestrator):
    """Test that caching works."""
    with patch.object(orchestrator.emotion_analyzer, 'analyze', new_callable=AsyncMock) as mock_emotion:
        mock_emotion.return_value = {
            "emotions": ["joy"],
            "scores": {"joy": 0.9},
            "model_used": "test",
            "fallback": False
        }
        
        # First call
        await orchestrator.process_input("Same content", "text")
        
        # Second call with same content
        await orchestrator.process_input("Same content", "text")
        
        # Should only call analyzer once due to caching
        assert mock_emotion.call_count == 1

@pytest.mark.asyncio
async def test_transcribe_audio_fallback(orchestrator):
    """Test audio transcription with fallback."""
    with patch.object(orchestrator.speech_processor, 'transcribe', new_callable=AsyncMock) as mock_transcribe:
        mock_transcribe.side_effect = Exception("Model unavailable")
        
        result = await orchestrator.transcribe_audio(b"fake_audio")
        
        # Should return fallback message
        assert "fallback" in result
        assert result["fallback"] is True

def test_cache_key_generation(orchestrator):
    """Test cache key generation."""
    key1 = orchestrator._get_cache_key("test content", "emotion")
    key2 = orchestrator._get_cache_key("test content", "emotion")
    key3 = orchestrator._get_cache_key("different content", "emotion")
    
    assert key1 == key2
    assert key1 != key3

def test_cache_expiry(orchestrator):
    """Test cache expiry."""
    # Set a very short TTL for testing
    orchestrator._cache_ttl = 0.1
    
    key = "test_key"
    data = {"test": "data"}
    
    orchestrator._set_cached(key, data)
    
    # Should be cached immediately
    assert orchestrator._get_cached(key) == data
    
    # Wait for expiry
    import time
    time.sleep(0.2)
    
    # Should be expired
    assert orchestrator._get_cached(key) is None

"""
Unit Tests for Production Reflection Generator
Tests OpenRouter primary, fallbacks, caching, and safety features.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai.reflection_generator import (
    generate_reflection,
    call_openrouter,
    call_huggingface_fallback,
    generate_template_reflection,
    generate_minimal_fallback,
    check_urgency,
    validate_reflection_json,
    get_cache_key,
    get_cached_reflection,
    set_cached_reflection
)


class TestReflectionGenerator(unittest.TestCase):
    """Test suite for reflection generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_input = "I'm feeling really anxious about my exams tomorrow"
        self.test_context = {
            "language": "en",
            "sensitivity": "medium",
            "recent_mood_tags": ["anxious"]
        }
        
        self.valid_reflection = {
            "reflection": "I hear your anxiety about the exams.",
            "poem_line": "Breathe in calm, breathe out worry.",
            "micro_actions": [
                {"label": "Breathing", "duration_seconds": 60, "instruction": "Deep breaths"}
            ],
            "severity": "notice",
            "tone": "gentle",
            "explainability": "Test reflection"
        }
    
    def test_validate_reflection_json_valid(self):
        """Test JSON validation with valid structure."""
        self.assertTrue(validate_reflection_json(self.valid_reflection))
    
    def test_validate_reflection_json_invalid(self):
        """Test JSON validation with invalid structure."""
        invalid = {"reflection": "test"}  # Missing required fields
        self.assertFalse(validate_reflection_json(invalid))
    
    def test_check_urgency_positive(self):
        """Test urgency detection with crisis keywords."""
        urgent_texts = [
            "I want to kill myself",
            "I'm thinking about ending my life",
            "I want to hurt myself"
        ]
        for text in urgent_texts:
            self.assertTrue(check_urgency(text), f"Failed to detect urgency in: {text}")
    
    def test_check_urgency_negative(self):
        """Test urgency detection with non-crisis text."""
        safe_texts = [
            "I'm feeling sad today",
            "I'm anxious about exams",
            "I'm frustrated with my friend"
        ]
        for text in safe_texts:
            self.assertFalse(check_urgency(text), f"False positive for: {text}")
    
    def test_cache_operations(self):
        """Test caching functionality."""
        cache_key = get_cache_key(self.test_input, self.test_context)
        
        # Initially should be None
        self.assertIsNone(get_cached_reflection(cache_key))
        
        # Set cache
        set_cached_reflection(cache_key, self.valid_reflection)
        
        # Should retrieve from cache
        cached = get_cached_reflection(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["reflection"], self.valid_reflection["reflection"])
    
    @patch('ai.reflection_generator.requests.post')
    def test_openrouter_success(self, mock_post):
        """Test successful OpenRouter API call."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps(self.valid_reflection)
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Set API key for test
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}):
            result = call_openrouter(self.test_input, self.test_context)
            
            self.assertEqual(result["source"], "openrouter")
            self.assertIn("reflection", result)
            self.assertTrue(validate_reflection_json(result))
    
    @patch('ai.reflection_generator.requests.post')
    def test_openrouter_timeout(self, mock_post):
        """Test OpenRouter timeout handling."""
        import requests
        mock_post.side_effect = requests.Timeout("Connection timeout")
        
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}):
            with self.assertRaises(RuntimeError):
                call_openrouter(self.test_input, self.test_context)
    
    @patch('ai.reflection_generator.requests.post')
    def test_openrouter_rate_limit(self, mock_post):
        """Test OpenRouter rate limit handling with retry."""
        # First call: rate limited
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        
        # Second call: success
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps(self.valid_reflection)
                }
            }]
        }
        
        mock_post.side_effect = [mock_response_429, mock_response_200]
        
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key'}):
            result = call_openrouter(self.test_input, self.test_context)
            self.assertEqual(result["source"], "openrouter")
            self.assertEqual(mock_post.call_count, 2)  # Verify retry happened
    
    def test_template_fallback(self):
        """Test template-based fallback generation."""
        result = generate_template_reflection(self.test_input, self.test_context)
        
        self.assertEqual(result["source"], "template")
        self.assertTrue(validate_reflection_json(result))
        self.assertIn("reflection", result)
        self.assertIn("poem_line", result)
        self.assertIsInstance(result["micro_actions"], list)
        self.assertGreater(len(result["micro_actions"]), 0)
    
    def test_minimal_fallback(self):
        """Test minimal safe fallback."""
        result = generate_minimal_fallback(self.test_input, self.test_context)
        
        self.assertEqual(result["source"], "minimal_fallback")
        self.assertTrue(validate_reflection_json(result))
        self.assertIn("reflection", result)
        self.assertIn("notes", result)
    
    def test_minimal_fallback_urgent(self):
        """Test minimal fallback with urgent keywords."""
        urgent_input = "I want to kill myself"
        result = generate_minimal_fallback(urgent_input, {})
        
        self.assertEqual(result["severity"], "urgent")
        self.assertIn("emergency", result["reflection"].lower())
    
    @patch('ai.reflection_generator.call_openrouter')
    @patch('ai.reflection_generator.call_huggingface_fallback')
    def test_fallback_chain(self, mock_hf, mock_or):
        """Test fallback chain when primary fails."""
        # OpenRouter fails
        mock_or.side_effect = Exception("OpenRouter unavailable")
        
        # HF succeeds
        hf_result = self.valid_reflection.copy()
        hf_result["source"] = "huggingface"
        mock_hf.return_value = hf_result
        
        result = generate_reflection(self.test_input, self.test_context)
        
        self.assertEqual(result["source"], "huggingface")
        self.assertIn("notes", result)
        self.assertIn("fallback", result["notes"].lower())
    
    @patch('ai.reflection_generator.call_openrouter')
    @patch('ai.reflection_generator.call_huggingface_fallback')
    @patch('ai.reflection_generator.generate_template_reflection')
    def test_all_fallbacks_to_template(self, mock_template, mock_hf, mock_or):
        """Test that template fallback is used when all network calls fail."""
        # All network calls fail
        mock_or.side_effect = Exception("OpenRouter down")
        mock_hf.side_effect = Exception("HF down")
        
        # Template succeeds
        template_result = self.valid_reflection.copy()
        template_result["source"] = "template"
        mock_template.return_value = template_result
        
        result = generate_reflection(self.test_input, self.test_context)
        
        self.assertEqual(result["source"], "template")
        self.assertIn("notes", result)
    
    def test_urgent_input_immediate_response(self):
        """Test that urgent inputs get immediate safe response."""
        urgent_input = "I'm thinking about killing myself"
        result = generate_reflection(urgent_input, {})
        
        self.assertEqual(result["severity"], "urgent")
        self.assertIn("source", result)
        # Should not call external APIs for urgent cases
    
    def test_empty_input_handling(self):
        """Test handling of empty input."""
        result = generate_reflection("", {})
        
        self.assertIn("reflection", result)
        self.assertEqual(result["source"], "minimal_fallback")
    
    def test_cache_prevents_duplicate_calls(self):
        """Test that cache prevents duplicate API calls."""
        with patch('ai.reflection_generator.call_openrouter') as mock_or:
            mock_or.return_value = self.valid_reflection.copy()
            mock_or.return_value["source"] = "openrouter"
            
            # First call
            result1 = generate_reflection(self.test_input, self.test_context)
            
            # Second call with same input (should use cache)
            result2 = generate_reflection(self.test_input, self.test_context)
            
            # OpenRouter should only be called once
            self.assertEqual(mock_or.call_count, 1)
            self.assertTrue(result2.get("from_cache", False))


class TestReflectionJSONSchema(unittest.TestCase):
    """Test that all generators produce valid JSON schema."""
    
    def test_template_schema(self):
        """Test template generator output schema."""
        result = generate_template_reflection("I'm sad", {})
        self._assert_valid_schema(result)
    
    def test_minimal_schema(self):
        """Test minimal fallback output schema."""
        result = generate_minimal_fallback("I'm anxious", {})
        self._assert_valid_schema(result)
    
    def _assert_valid_schema(self, result):
        """Assert result matches expected schema."""
        required_fields = [
            "reflection", "poem_line", "micro_actions",
            "severity", "tone", "explainability", "source"
        ]
        
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")
        
        # Check types
        self.assertIsInstance(result["reflection"], str)
        self.assertIsInstance(result["poem_line"], str)
        self.assertIsInstance(result["micro_actions"], list)
        self.assertIn(result["severity"], ["calm", "notice", "urgent"])
        self.assertIn(result["tone"], ["gentle", "encouraging", "practical", "creative"])
        
        # Check micro_actions structure
        for action in result["micro_actions"]:
            self.assertIn("label", action)
            self.assertIn("duration_seconds", action)
            self.assertIn("instruction", action)
            self.assertIsInstance(action["duration_seconds"], int)


if __name__ == '__main__':
    unittest.main()

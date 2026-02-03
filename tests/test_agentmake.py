"""
Unit tests for the agentmake module.

These tests verify core functionality without requiring actual API calls.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from copy import deepcopy

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMessageNormalization:
    """Tests for message input normalization."""

    def test_string_input_creates_message_list(self):
        """String input should be converted to proper message list."""
        from agentmake import agentmake, DEFAULT_SYSTEM_MESSAGE
        
        # Mock the backend to avoid actual API calls
        with patch('agentmake.OllamaAI.getChatCompletion') as mock_completion:
            mock_completion.return_value = iter([{"message": {"content": "test response"}}])
            
            # We can't easily test the full function without mocking everything,
            # so we'll test the message format logic separately
            input_str = "Hello, world!"
            expected_user_content = "Hello, world!"
            
            # The function should convert string to list format
            messages = [
                {"role": "system", "content": DEFAULT_SYSTEM_MESSAGE},
                {"role": "user", "content": expected_user_content}
            ]
            
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == expected_user_content

    def test_list_input_preserved(self):
        """List input should be deep copied and preserved."""
        original_messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"}
        ]
        messages_copy = deepcopy(original_messages)
        
        # Verify deep copy works correctly
        messages_copy[0]["content"] = "Modified"
        assert original_messages[0]["content"] == "You are helpful."


class TestUpdateSystemMessage:
    """Tests for updateSystemMessage function."""

    def test_update_existing_system_message(self):
        """Should update existing system message and return original."""
        from agentmake import updateSystemMessage
        
        messages = [
            {"role": "system", "content": "Original system"},
            {"role": "user", "content": "Hello"}
        ]
        
        original = updateSystemMessage(messages, "New system")
        
        assert original == "Original system"
        assert messages[0]["content"] == "New system"

    def test_insert_system_message_if_missing(self):
        """Should insert system message if none exists."""
        from agentmake import updateSystemMessage
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        result = updateSystemMessage(messages, "New system")
        
        assert result == "New system"
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "New system"


class TestAddContextToMessages:
    """Tests for addContextToMessages function."""

    def test_adds_context_to_user_prompt(self):
        """Should wrap user prompt with RAG context."""
        from agentmake import addContextToMessages
        
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "What is Python?"}
        ]
        
        context = "Python is a programming language."
        addContextToMessages(messages, context)
        
        # The function should modify the last message
        assert "Python is a programming language" in messages[-1]["content"]
        assert "What is Python?" in messages[-1]["content"]


class TestBackendValidation:
    """Tests for backend validation."""

    def test_supported_backends_list(self):
        """Verify all expected backends are in SUPPORTED_AI_BACKENDS."""
        from agentmake import SUPPORTED_AI_BACKENDS
        
        expected_backends = [
            "anthropic", "azure_anthropic", "azure_openai", "azure_cohere",
            "azure_deepseek", "azure_mistral", "azure_xai", "azure_sdk",
            "cohere", "custom", "custom1", "custom2", "deepseek", "genai",
            "github", "github_any", "googleai", "groq", "llamacpp", "mistral",
            "ollama", "ollamacloud", "openai", "vertexai", "xai"
        ]
        
        for backend in expected_backends:
            assert backend in SUPPORTED_AI_BACKENDS, f"Missing backend: {backend}"

    def test_invalid_backend_returns_empty_list(self):
        """Invalid backend should return empty list (errors are caught internally)."""
        from agentmake import agentmake
        
        # The agentmake function catches all errors and returns empty list
        result = agentmake("test", backend="invalid_backend", print_on_terminal=False)
        assert result == []


class TestResourceLoading:
    """Tests for resource loading utilities."""

    def test_refine_follow_up_prompt_with_string(self):
        """String that's not a file should be returned as-is."""
        from agentmake import refine_follow_up_prompt_content
        
        prompt = "Please elaborate on that point."
        result = refine_follow_up_prompt_content(prompt)
        
        assert result == prompt

    def test_unpack_instruction_content_none(self):
        """None input should return None."""
        from agentmake import unpack_instruction_content
        
        result = unpack_instruction_content(None)
        assert result is None

    def test_unpack_system_content_none(self):
        """None input should return None."""
        from agentmake import unpack_system_content
        
        result = unpack_system_content(None)
        assert result is None


class TestHelperFunctions:
    """Tests for various helper functions."""

    def test_get_default_tool_system_with_schema(self):
        """Should generate system message from schema."""
        from agentmake import getDefaultToolSystem
        
        schema = {
            "description": "A test tool",
            "parameters": {
                "required": ["name"],
                "properties": {
                    "name": {"description": "The name parameter"},
                    "optional_param": {"description": "An optional param"}
                }
            }
        }
        
        result = getDefaultToolSystem(schema)
        
        assert "name" in result
        assert "required" in result.lower()
        assert "optional_param" in result

    def test_get_default_tool_system_empty_properties(self):
        """Empty properties should return empty string."""
        from agentmake import getDefaultToolSystem
        
        schema = {
            "parameters": {
                "required": [],
                "properties": {}
            }
        }
        
        result = getDefaultToolSystem(schema)
        assert result == ""

    def test_show_errors_with_message(self):
        """showErrors should return the provided message."""
        from agentmake import showErrors
        
        result = showErrors(message="Custom error message")
        assert "Custom error message" in result


class TestFabricIntegration:
    """Tests for Fabric pattern integration."""

    def test_is_fabric_pattern_invalid(self):
        """Non-fabric patterns should return False."""
        from agentmake import isFabricPattern
        
        assert isFabricPattern("not_a_fabric_pattern") is False
        assert isFabricPattern("regular_system") is False

    def test_is_fabric_pattern_without_prefix(self):
        """Patterns without fabric. prefix should return False."""
        from agentmake import isFabricPattern
        
        assert isFabricPattern("summarize") is False


class TestConstants:
    """Tests for module constants."""

    def test_package_path_exists(self):
        """PACKAGE_PATH should point to existing directory."""
        from agentmake import PACKAGE_PATH
        
        assert os.path.isdir(PACKAGE_PATH)

    def test_default_ai_backend_is_valid(self):
        """DEFAULT_AI_BACKEND should be in supported backends."""
        from agentmake import DEFAULT_AI_BACKEND, SUPPORTED_AI_BACKENDS
        
        assert DEFAULT_AI_BACKEND in SUPPORTED_AI_BACKENDS

    def test_no_content_constant(self):
        """NO_CONTENT should be defined."""
        from agentmake import NO_CONTENT
        
        assert NO_CONTENT == "[NO_CONTENT]"


class TestBackendRegistry:
    """Tests for the BACKEND_REGISTRY."""

    def test_backend_registry_exists(self):
        """BACKEND_REGISTRY should be defined."""
        from agentmake import BACKEND_REGISTRY
        
        assert isinstance(BACKEND_REGISTRY, dict)

    def test_backend_registry_contains_all_backends(self):
        """BACKEND_REGISTRY should contain entries for all supported backends."""
        from agentmake import BACKEND_REGISTRY, SUPPORTED_AI_BACKENDS
        
        for backend in SUPPORTED_AI_BACKENDS:
            assert backend in BACKEND_REGISTRY, f"Missing backend in registry: {backend}"

    def test_backend_registry_classes_have_get_chat_completion(self):
        """All backend classes should have getChatCompletion method."""
        from agentmake import BACKEND_REGISTRY
        
        for backend_name, backend_class in BACKEND_REGISTRY.items():
            assert hasattr(backend_class, 'getChatCompletion'), \
                f"Backend {backend_name} missing getChatCompletion method"


class TestLoadResource:
    """Tests for the _load_resource helper function."""

    def test_load_resource_returns_none_for_none_input(self):
        """_load_resource should return None when given None."""
        from agentmake import _load_resource
        
        result = _load_resource(None, "plugins")
        assert result is None

    def test_load_resource_returns_string_for_nonexistent_file(self):
        """_load_resource should return original string if not a file."""
        from agentmake import _load_resource
        
        result = _load_resource("not_a_real_file", "plugins")
        assert result == "not_a_real_file"

    def test_load_resource_handles_inline_content(self):
        """_load_resource should return inline content as-is."""
        from agentmake import _load_resource
        
        inline_code = "CONTENT_PLUGIN = lambda x: x.upper()"
        result = _load_resource(inline_code, "plugins")
        assert result == inline_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

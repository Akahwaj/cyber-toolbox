"""Tests for modules/mythos.py – MythosClient availability."""
import os
from unittest.mock import patch

from modules.mythos import MythosClient, SYSTEM_PROMPT, MYTHOS_MODEL, _SCAN_TOOLS


class TestMythosClientAvailability:
    """Test MythosClient initialization and availability checks."""

    def test_not_available_without_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("modules.mythos.ANTHROPIC_AVAILABLE", True):
                client = MythosClient(api_key="")
                assert client.is_available() is False

    def test_not_available_without_anthropic_package(self):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", False):
            client = MythosClient(api_key="fake-key")
            assert client.is_available() is False

    def test_default_model(self):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", False):
            client = MythosClient()
            assert client.model == MYTHOS_MODEL


class TestMythosClientRequireClient:
    """Test _require_client() messaging."""

    def test_require_client_no_package(self, capsys):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", False):
            client = MythosClient()
            result = client._require_client()
            assert result is False
            captured = capsys.readouterr()
            assert "not installed" in captured.out

    def test_require_client_no_api_key(self, capsys):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", True), \
             patch.dict(os.environ, {}, clear=True):
            client = MythosClient(api_key="")
            result = client._require_client()
            assert result is False
            captured = capsys.readouterr()
            assert "ANTHROPIC_API_KEY" in captured.out


class TestMythosStreamQuery:
    """Test stream_query in offline mode."""

    def test_stream_query_returns_empty_when_unavailable(self, capsys):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", False):
            client = MythosClient()
            result = client.stream_query("test prompt")
            assert result == ""


class TestMythosToolAssistedScan:
    """Test tool_assisted_scan in offline mode."""

    def test_tool_scan_returns_none_when_unavailable(self, capsys):
        with patch("modules.mythos.ANTHROPIC_AVAILABLE", False):
            client = MythosClient()
            result = client.tool_assisted_scan("test target")
            assert result is None


class TestMythosConstants:
    """Verify module-level constants."""

    def test_system_prompt_is_string(self):
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_mentions_cybersecurity(self):
        assert "cybersecurity" in SYSTEM_PROMPT.lower()

    def test_model_is_string(self):
        assert isinstance(MYTHOS_MODEL, str)
        assert len(MYTHOS_MODEL) > 0

    def test_scan_tools_structure(self):
        assert isinstance(_SCAN_TOOLS, list)
        assert len(_SCAN_TOOLS) == 1
        tool = _SCAN_TOOLS[0]
        assert tool["name"] == "report_findings"
        assert "input_schema" in tool
        assert "properties" in tool["input_schema"]
        required = tool["input_schema"]["required"]
        assert "severity" in required
        assert "summary" in required
        assert "findings" in required
        assert "next_steps" in required

"""Tests for modules/ai_agent.py – offline mode, availability, provider info."""
import os
from unittest.mock import patch, MagicMock

from modules.ai_agent import AIAgent, CYBERSECURITY_SYSTEM_PROMPT


class TestAIAgentOfflineResponse:
    """Test the offline fallback responses (no API keys needed)."""

    def setup_method(self):
        """Create an agent with no API keys."""
        with patch.dict(os.environ, {}, clear=True):
            # Also ensure the module-level vars are empty
            with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
                 patch("modules.ai_agent.OPENAI_API_KEY", ""), \
                 patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
                 patch("modules.ai_agent.OPENAI_AVAILABLE", False):
                self.agent = AIAgent()

    def test_nmap_query(self):
        resp = self.agent._offline_response("tell me about nmap")
        assert "nmap" in resp.lower() or "Nmap" in resp

    def test_aircrack_query(self):
        resp = self.agent._offline_response("how to use aircrack-ng")
        assert "aircrack" in resp.lower() or "Aircrack" in resp

    def test_wireless_query(self):
        resp = self.agent._offline_response("wireless security")
        assert "wireless" in resp.lower() or "Aircrack" in resp

    def test_wifi_query(self):
        resp = self.agent._offline_response("wifi security testing")
        assert "wireless" in resp.lower() or "wifi" in resp.lower() or "Aircrack" in resp

    def test_password_query(self):
        resp = self.agent._offline_response("password cracking")
        assert "password" in resp.lower()

    def test_sql_injection_query(self):
        resp = self.agent._offline_response("sql injection")
        assert "SQL" in resp or "sql" in resp.lower()

    def test_injection_query(self):
        resp = self.agent._offline_response("injection attacks")
        assert "injection" in resp.lower() or "SQL" in resp

    def test_apk_query(self):
        resp = self.agent._offline_response("apk analysis")
        assert "apk" in resp.lower() or "APK" in resp or "Android" in resp

    def test_android_query(self):
        resp = self.agent._offline_response("android security")
        assert "Android" in resp or "android" in resp.lower()

    def test_ios_query(self):
        resp = self.agent._offline_response("ios security")
        assert "iOS" in resp or "ios" in resp.lower()

    def test_ipa_query(self):
        resp = self.agent._offline_response("ipa analysis")
        assert "iOS" in resp or "IPA" in resp

    def test_generic_query_returns_api_key_message(self):
        resp = self.agent._offline_response("random unrelated question")
        assert "API" in resp or "api" in resp.lower()


class TestAIAgentAvailability:
    """Test _is_available() and _get_provider_info()."""

    def test_not_available_without_clients(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
            assert agent._is_available() is False

    def test_provider_info_offline(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
            info = agent._get_provider_info()
            assert "Offline" in info or "offline" in info.lower()


class TestAIAgentQuery:
    """Test the query routing logic."""

    def test_query_returns_offline_response_when_no_clients(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
            resp = agent.query("tell me about nmap")
            assert "Nmap" in resp or "nmap" in resp.lower()


class TestAIAgentTeachAndExplain:
    """Test teach_tool and explain_topic in offline mode."""

    def setup_method(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            self.agent = AIAgent()

    def test_teach_tool_returns_string(self):
        result = self.agent.teach_tool("nmap")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_explain_topic_returns_string(self):
        result = self.agent.explain_topic("sql injection")
        assert isinstance(result, str)
        assert len(result) > 0


class TestAIAgentAnalyzeLog:
    """Test analyze_log in offline mode."""

    def test_analyze_log_offline_message(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
            result = agent.analyze_log("some log content")
            assert "API" in result or "ANTHROPIC" in result

    def test_analyze_log_truncates_long_content(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
            long_content = "x" * 10000
            result = agent.analyze_log(long_content)
            # Should not crash; returns offline message
            assert isinstance(result, str)


class TestSystemPrompt:
    """Verify the system prompt is properly defined."""

    def test_system_prompt_is_string(self):
        assert isinstance(CYBERSECURITY_SYSTEM_PROMPT, str)

    def test_system_prompt_not_empty(self):
        assert len(CYBERSECURITY_SYSTEM_PROMPT) > 0

    def test_system_prompt_mentions_cybersecurity(self):
        assert "cybersecurity" in CYBERSECURITY_SYSTEM_PROMPT.lower()

"""Tests for modules/ai_agent.py"""
import pytest
from unittest.mock import MagicMock, patch
from modules.ai_agent import AIAgent, CYBERSECURITY_SYSTEM_PROMPT


class TestAIAgentInit:
    def test_creates_without_api_keys(self):
        with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
        assert agent._claude_client is None
        assert agent._openai_client is None

    def test_is_not_available_without_keys(self):
        with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
        assert agent._is_available() is False

    def test_prefer_default_is_claude(self):
        agent = AIAgent()
        assert agent.prefer == "claude"

    def test_prefer_openai(self):
        agent = AIAgent(prefer="openai")
        assert agent.prefer == "openai"


class TestOfflineResponse:
    @pytest.fixture
    def offline_agent(self):
        with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            return AIAgent()

    def test_nmap_response(self, offline_agent):
        response = offline_agent._offline_response("tell me about nmap")
        assert "nmap" in response.lower()
        assert "network" in response.lower()

    def test_aircrack_response(self, offline_agent):
        response = offline_agent._offline_response("how does aircrack work")
        assert "aircrack" in response.lower()

    def test_wireless_response(self, offline_agent):
        response = offline_agent._offline_response("explain wireless security")
        assert len(response) > 0

    def test_wifi_keyword(self, offline_agent):
        response = offline_agent._offline_response("wifi hacking")
        assert len(response) > 0

    def test_password_response(self, offline_agent):
        response = offline_agent._offline_response("password strength tips")
        assert "password" in response.lower()

    def test_sql_injection_response(self, offline_agent):
        response = offline_agent._offline_response("explain sql injection")
        assert "sql" in response.lower() or "injection" in response.lower()

    def test_injection_keyword(self, offline_agent):
        response = offline_agent._offline_response("injection attack")
        assert len(response) > 0

    def test_apk_response(self, offline_agent):
        response = offline_agent._offline_response("how to analyze an apk file")
        assert "apk" in response.lower() or "android" in response.lower()

    def test_android_keyword(self, offline_agent):
        response = offline_agent._offline_response("android security")
        assert len(response) > 0

    def test_ios_response(self, offline_agent):
        response = offline_agent._offline_response("ios ipa analysis")
        assert "ios" in response.lower() or "ipa" in response.lower()

    def test_unknown_topic_returns_api_key_hint(self, offline_agent):
        response = offline_agent._offline_response("some completely unknown topic xyz")
        assert "API" in response or "api" in response.lower()

    def test_returns_string(self, offline_agent):
        response = offline_agent._offline_response("anything")
        assert isinstance(response, str)
        assert len(response) > 0


class TestQueryOffline:
    @pytest.fixture
    def offline_agent(self):
        with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            return AIAgent()

    def test_query_without_keys_returns_offline_response(self, offline_agent):
        response = offline_agent.query("tell me about nmap")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_analyze_log_without_keys(self, offline_agent):
        response = offline_agent.analyze_log("failed password for root")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_analyze_log_truncates_long_content(self, offline_agent):
        long_content = "A" * 10000
        response = offline_agent.analyze_log(long_content)
        assert isinstance(response, str)


class TestGetProviderInfo:
    def test_offline_mode_message(self):
        with patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            agent = AIAgent()
        info = agent._get_provider_info()
        assert "Offline" in info or "no API" in info.lower()

    def test_provider_info_with_mock_claude(self):
        agent = AIAgent()
        agent._claude_client = MagicMock()
        agent._openai_client = None
        info = agent._get_provider_info()
        assert "Claude" in info

    def test_provider_info_with_mock_openai(self):
        agent = AIAgent()
        agent._claude_client = None
        agent._openai_client = MagicMock()
        info = agent._get_provider_info()
        assert "OpenAI" in info or "GPT" in info

    def test_provider_info_with_both_clients(self):
        agent = AIAgent()
        agent._claude_client = MagicMock()
        agent._openai_client = MagicMock()
        info = agent._get_provider_info()
        assert "Claude" in info
        assert "GPT" in info or "OpenAI" in info


class TestQueryWithMockedClients:
    def _make_agent_with_claude(self):
        agent = AIAgent()
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Claude says: test response")]
        mock_client.messages.create.return_value = mock_response
        agent._claude_client = mock_client
        agent._openai_client = None
        return agent

    def _make_agent_with_openai(self):
        agent = AIAgent()
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "OpenAI says: test response"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        agent._claude_client = None
        agent._openai_client = mock_client
        return agent

    def test_query_uses_claude_when_preferred(self):
        agent = self._make_agent_with_claude()
        response = agent.query("test prompt")
        assert "Claude says" in response

    def test_query_uses_openai_when_no_claude(self):
        agent = self._make_agent_with_openai()
        agent.prefer = "openai"
        response = agent.query("test prompt")
        assert "OpenAI says" in response

    def test_query_falls_back_to_openai_when_prefer_claude_but_no_claude(self):
        agent = self._make_agent_with_openai()
        agent.prefer = "claude"  # prefer claude but no claude client
        response = agent.query("test prompt")
        assert "OpenAI says" in response

    def test_query_use_both_combines_responses(self):
        agent = AIAgent()
        agent._claude_client = MagicMock()
        agent._openai_client = MagicMock()
        mock_claude_resp = MagicMock()
        mock_claude_resp.content = [MagicMock(text="Claude answer")]
        agent._claude_client.messages.create.return_value = mock_claude_resp
        mock_oai_choice = MagicMock()
        mock_oai_choice.message.content = "GPT answer"
        mock_oai_resp = MagicMock()
        mock_oai_resp.choices = [mock_oai_choice]
        agent._openai_client.chat.completions.create.return_value = mock_oai_resp
        response = agent.query("test", use_both=True)
        assert "Claude" in response
        assert "GPT" in response

    def test_claude_api_error_returns_error_message(self):
        agent = AIAgent()
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        agent._claude_client = mock_client
        agent._openai_client = None
        response = agent._query_claude("test prompt")
        assert "failed" in response.lower() or "error" in response.lower()

    def test_openai_api_error_returns_error_message(self):
        agent = AIAgent()
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        agent._claude_client = None
        agent._openai_client = mock_client
        response = agent._query_openai("test prompt")
        assert "failed" in response.lower() or "error" in response.lower()

    def test_teach_tool_calls_query(self):
        agent = self._make_agent_with_claude()
        response = agent.teach_tool("nmap")
        assert isinstance(response, str)

    def test_explain_topic_calls_query(self):
        agent = self._make_agent_with_claude()
        response = agent.explain_topic("SQL injection")
        assert isinstance(response, str)

    def test_analyze_apk_info_calls_query(self):
        agent = self._make_agent_with_claude()
        response = agent.analyze_apk_info("com.example.app", ["INTERNET", "READ_CONTACTS"])
        assert isinstance(response, str)

    def test_analyze_apk_info_no_permissions(self):
        agent = self._make_agent_with_claude()
        response = agent.analyze_apk_info("com.example.app")
        assert isinstance(response, str)

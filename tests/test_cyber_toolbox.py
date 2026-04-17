"""Tests for cyber_toolbox.py – MENU_ACTIONS, CLI args, etc."""
import sys
from unittest.mock import patch, MagicMock

from cyber_toolbox import MENU_ACTIONS, show_menu, get_agent, main


class TestMenuActions:
    """Verify the MENU_ACTIONS structure."""

    def test_menu_actions_is_dict(self):
        assert isinstance(MENU_ACTIONS, dict)

    def test_menu_has_10_items(self):
        assert len(MENU_ACTIONS) == 10

    def test_keys_are_string_digits(self):
        for key in MENU_ACTIONS:
            assert key.isdigit()

    def test_values_are_callable_description_tuples(self):
        for key, (func, desc) in MENU_ACTIONS.items():
            assert callable(func)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_key_1_is_password_tool(self):
        _, desc = MENU_ACTIONS["1"]
        assert "Password" in desc

    def test_key_2_is_hash_tool(self):
        _, desc = MENU_ACTIONS["2"]
        assert "Hash" in desc

    def test_key_3_is_network_tool(self):
        _, desc = MENU_ACTIONS["3"]
        assert "Network" in desc

    def test_key_6_is_log_tool(self):
        _, desc = MENU_ACTIONS["6"]
        assert "Log" in desc

    def test_key_7_is_report_tool(self):
        _, desc = MENU_ACTIONS["7"]
        assert "Report" in desc


class TestShowMenu:
    """Test show_menu() output."""

    def test_shows_all_menu_items(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        for key, (_, desc) in MENU_ACTIONS.items():
            assert desc in captured.out

    def test_shows_toolbox_title(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        assert "Cyber" in captured.out or "Toolbox" in captured.out

    def test_shows_exit_option(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        assert "Exit" in captured.out

    def test_shows_teach_mode(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        assert "Teach Mode" in captured.out

    def test_shows_expert_tools(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        assert "Expert Tools" in captured.out

    def test_shows_scenario_learning(self, capsys):
        show_menu()
        captured = capsys.readouterr()
        assert "Scenario" in captured.out


class TestMainCLIQuickStart:
    """Test --quick-start flag."""

    def test_quick_start_runs(self, capsys):
        with patch.object(sys, "argv", ["cyber_toolbox.py", "--quick-start"]):
            main()
        captured = capsys.readouterr()
        assert "Quick Start" in captured.out
        assert "Python" in captured.out


class TestGetAgent:
    """Test get_agent singleton."""

    def test_get_agent_returns_ai_agent(self):
        with patch("modules.ai_agent.ANTHROPIC_AVAILABLE", False), \
             patch("modules.ai_agent.OPENAI_AVAILABLE", False), \
             patch("modules.ai_agent.ANTHROPIC_API_KEY", ""), \
             patch("modules.ai_agent.OPENAI_API_KEY", ""):
            import cyber_toolbox
            cyber_toolbox.AI_AGENT = None  # Reset singleton
            agent = get_agent()
            from modules.ai_agent import AIAgent
            assert isinstance(agent, AIAgent)
            # Second call returns same instance
            agent2 = get_agent()
            assert agent is agent2
            cyber_toolbox.AI_AGENT = None  # Cleanup

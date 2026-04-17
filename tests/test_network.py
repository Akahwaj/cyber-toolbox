"""Tests for modules/network.py – subnet_info, nmap flag validation, etc."""
import re
import subprocess
from unittest.mock import patch, MagicMock

from modules.network import (
    COMMON_PORTS,
    _ALLOWED_NMAP_FLAGS,
    subnet_info,
    check_tool,
    port_scan,
)


class TestCommonPorts:
    """Verify the COMMON_PORTS list."""

    def test_common_ports_is_list(self):
        assert isinstance(COMMON_PORTS, list)

    def test_common_ports_contains_well_known_ports(self):
        for port in [22, 80, 443]:
            assert port in COMMON_PORTS

    def test_all_ports_are_positive_integers(self):
        for port in COMMON_PORTS:
            assert isinstance(port, int)
            assert port > 0


class TestNmapFlagValidation:
    """Test the _ALLOWED_NMAP_FLAGS regex."""

    def test_valid_simple_flags(self):
        assert _ALLOWED_NMAP_FLAGS.match("-sV")
        assert _ALLOWED_NMAP_FLAGS.match("-sS")
        assert _ALLOWED_NMAP_FLAGS.match("-p-")

    def test_valid_multiple_flags(self):
        assert _ALLOWED_NMAP_FLAGS.match("-sV -p 80,443")
        assert _ALLOWED_NMAP_FLAGS.match("-sS -O -T4")

    def test_valid_with_dots(self):
        assert _ALLOWED_NMAP_FLAGS.match("-sV 192.168.1.1")

    def test_invalid_flags_with_shell_chars(self):
        assert not _ALLOWED_NMAP_FLAGS.match("-sV; rm -rf /")
        assert not _ALLOWED_NMAP_FLAGS.match("-sV | cat /etc/passwd")
        assert not _ALLOWED_NMAP_FLAGS.match("-sV && echo hacked")
        assert not _ALLOWED_NMAP_FLAGS.match("-sV $(whoami)")

    def test_empty_string_rejected(self):
        assert not _ALLOWED_NMAP_FLAGS.match("")


class TestSubnetInfo:
    """Test subnet_info() output (it prints to stdout)."""

    def test_valid_cidr_24(self, capsys):
        subnet_info("192.168.1.0/24")
        captured = capsys.readouterr()
        assert "192.168.1.0" in captured.out
        assert "192.168.1.255" in captured.out
        assert "255.255.255.0" in captured.out
        assert "254" in captured.out  # hosts

    def test_valid_cidr_16(self, capsys):
        subnet_info("10.0.0.0/16")
        captured = capsys.readouterr()
        assert "10.0.0.0" in captured.out
        assert "255.255.0.0" in captured.out

    def test_valid_cidr_32(self, capsys):
        subnet_info("192.168.1.1/32")
        captured = capsys.readouterr()
        assert "192.168.1.1" in captured.out

    def test_invalid_cidr(self, capsys):
        subnet_info("not-a-cidr")
        captured = capsys.readouterr()
        assert "Invalid CIDR" in captured.out

    def test_host_address_non_strict(self, capsys):
        # strict=False allows host bits set
        subnet_info("192.168.1.100/24")
        captured = capsys.readouterr()
        assert "192.168.1.0" in captured.out


class TestCheckTool:
    """Test check_tool() with mocked subprocess."""

    @patch("modules.network.subprocess.run")
    def test_tool_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert check_tool("nmap") is True

    @patch("modules.network.subprocess.run", side_effect=FileNotFoundError)
    def test_tool_not_found(self, mock_run):
        assert check_tool("nonexistent_tool") is False

    @patch("modules.network.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=5))
    def test_tool_timeout(self, mock_run):
        assert check_tool("slow_tool") is False


class TestPortScan:
    """Test port_scan() with mocked connections."""

    @patch("modules.network.socket.create_connection")
    def test_open_port_detected(self, mock_conn):
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = port_scan("localhost", [80])
        assert 80 in result

    @patch("modules.network.socket.create_connection", side_effect=ConnectionRefusedError)
    def test_closed_port_not_reported(self, mock_conn):
        result = port_scan("localhost", [80])
        assert 80 not in result

    @patch("modules.network.socket.create_connection", side_effect=OSError)
    def test_os_error_handled(self, mock_conn):
        result = port_scan("localhost", [80, 443])
        assert result == []

    @patch("modules.network.socket.create_connection", side_effect=TimeoutError)
    def test_timeout_handled(self, mock_conn):
        result = port_scan("localhost", [22])
        assert result == []

    @patch("modules.network.socket.create_connection")
    def test_uses_common_ports_when_none(self, mock_conn):
        mock_conn.side_effect = ConnectionRefusedError
        result = port_scan("localhost")
        assert result == []
        assert mock_conn.call_count == len(COMMON_PORTS)

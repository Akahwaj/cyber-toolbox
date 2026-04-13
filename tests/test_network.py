"""Tests for modules/network.py"""
import socket
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from modules.network import subnet_info, check_tool, run_nmap, port_scan, _ALLOWED_NMAP_FLAGS


class TestSubnetInfo:
    def test_valid_class_c_network(self, capsys):
        subnet_info("192.168.1.0/24")
        captured = capsys.readouterr()
        assert "192.168.1.0" in captured.out
        assert "192.168.1.255" in captured.out
        assert "254" in captured.out

    def test_valid_class_b_network(self, capsys):
        subnet_info("10.0.0.0/16")
        captured = capsys.readouterr()
        assert "10.0.0.0" in captured.out
        assert "65534" in captured.out

    def test_valid_slash_30(self, capsys):
        subnet_info("192.168.1.0/30")
        captured = capsys.readouterr()
        assert "2" in captured.out  # 2 usable hosts

    def test_host_address_with_strict_false(self, capsys):
        # strict=False means 192.168.1.5/24 is treated as 192.168.1.0/24
        subnet_info("192.168.1.5/24")
        captured = capsys.readouterr()
        assert "192.168.1.0" in captured.out

    def test_invalid_cidr_prints_error(self, capsys):
        subnet_info("not.a.valid.cidr")
        captured = capsys.readouterr()
        assert "Invalid CIDR" in captured.out

    def test_invalid_cidr_out_of_range(self, capsys):
        subnet_info("999.999.999.999/24")
        captured = capsys.readouterr()
        assert "Invalid CIDR" in captured.out

    def test_outputs_netmask(self, capsys):
        subnet_info("10.0.0.0/8")
        captured = capsys.readouterr()
        assert "255.0.0.0" in captured.out

    def test_outputs_first_and_last_host(self, capsys):
        subnet_info("192.168.1.0/24")
        captured = capsys.readouterr()
        assert "192.168.1.1" in captured.out
        assert "192.168.1.254" in captured.out


class TestCheckTool:
    def test_returns_false_for_nonexistent_tool(self):
        assert check_tool("__nonexistent_tool_xyz__") is False

    def test_returns_true_when_tool_exists(self):
        # Python itself is always available
        with patch("modules.network.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert check_tool("python3") is True

    def test_returns_false_on_timeout(self):
        with patch("modules.network.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            assert check_tool("sometool") is False


class TestNmapFlagValidation:
    def test_valid_flags_match(self):
        assert _ALLOWED_NMAP_FLAGS.match("-sV")
        assert _ALLOWED_NMAP_FLAGS.match("-sV -p 80,443")
        assert _ALLOWED_NMAP_FLAGS.match("-A -T4 192.168.1.0/24")
        assert _ALLOWED_NMAP_FLAGS.match("-p-")

    def test_invalid_flags_do_not_match(self):
        assert not _ALLOWED_NMAP_FLAGS.match("-sV; rm -rf /")
        assert not _ALLOWED_NMAP_FLAGS.match("-sV && cat /etc/passwd")
        assert not _ALLOWED_NMAP_FLAGS.match("$(whoami)")

    def test_run_nmap_rejects_invalid_flags(self, capsys):
        with patch("modules.network.check_tool", return_value=True):
            run_nmap("127.0.0.1", flags="-sV; rm -rf /")
        captured = capsys.readouterr()
        assert "Invalid nmap flags" in captured.out

    def test_run_nmap_skips_when_not_installed(self, capsys):
        with patch("modules.network.check_tool", return_value=False):
            run_nmap("127.0.0.1")
        captured = capsys.readouterr()
        assert "not installed" in captured.out

    def test_run_nmap_timeout(self, capsys):
        with patch("modules.network.check_tool", return_value=True), \
             patch("modules.network.subprocess.run", side_effect=subprocess.TimeoutExpired("nmap", 120)):
            run_nmap("127.0.0.1", flags="-sV")
        captured = capsys.readouterr()
        assert "timed out" in captured.out


class TestPortScan:
    def test_returns_list(self):
        with patch("modules.network.socket.create_connection", side_effect=OSError):
            result = port_scan("127.0.0.1", ports=[9999])
        assert isinstance(result, list)

    def test_open_port_included(self):
        mock_cm = MagicMock()
        mock_cm.__enter__ = MagicMock(return_value=MagicMock())
        mock_cm.__exit__ = MagicMock(return_value=False)
        with patch("modules.network.socket.create_connection", return_value=mock_cm):
            result = port_scan("127.0.0.1", ports=[80])
        assert 80 in result

    def test_closed_port_excluded(self):
        with patch("modules.network.socket.create_connection",
                   side_effect=ConnectionRefusedError):
            result = port_scan("127.0.0.1", ports=[9])
        assert 9 not in result

    def test_uses_default_ports_when_none_given(self):
        with patch("modules.network.socket.create_connection", side_effect=OSError):
            result = port_scan("127.0.0.1")
        assert result == []

    def test_timeout_on_port_skipped(self):
        with patch("modules.network.socket.create_connection",
                   side_effect=TimeoutError):
            result = port_scan("127.0.0.1", ports=[12345])
        assert result == []

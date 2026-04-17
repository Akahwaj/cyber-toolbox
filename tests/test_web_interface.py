"""Tests for modules/web_interface.py – get_local_ip()."""
from unittest.mock import patch, MagicMock
import socket

from modules.web_interface import get_local_ip


class TestGetLocalIp:
    """Test get_local_ip() function."""

    def test_returns_string(self):
        result = get_local_ip()
        assert isinstance(result, str)

    def test_returns_valid_ip_format(self):
        result = get_local_ip()
        parts = result.split(".")
        assert len(parts) == 4
        for part in parts:
            assert part.isdigit()
            assert 0 <= int(part) <= 255

    @patch("modules.web_interface.socket.socket")
    def test_fallback_on_exception(self, mock_socket_cls):
        """When socket fails, should return 127.0.0.1."""
        mock_socket_cls.side_effect = OSError("network unreachable")
        result = get_local_ip()
        assert result == "127.0.0.1"

    @patch("modules.web_interface.socket.socket")
    def test_returns_ip_from_socket(self, mock_socket_cls):
        """Verify it reads the local IP from the socket connection."""
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("10.0.0.42", 12345)
        mock_socket_cls.return_value = mock_sock
        result = get_local_ip()
        assert result == "10.0.0.42"
        mock_sock.connect.assert_called_once_with(("8.8.8.8", 80))
        mock_sock.close.assert_called_once()

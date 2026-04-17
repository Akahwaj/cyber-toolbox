"""Tests for modules/wireless.py – validation helpers."""
from modules.wireless import _validate_interface, _validate_mac, _IFACE_RE, _MAC_RE


class TestValidateInterface:
    """Test wireless interface name validation."""

    def test_valid_interface_wlan0(self):
        assert _validate_interface("wlan0") is True

    def test_valid_interface_wlan0mon(self):
        assert _validate_interface("wlan0mon") is True

    def test_valid_interface_eth0(self):
        assert _validate_interface("eth0") is True

    def test_valid_interface_with_hyphen(self):
        assert _validate_interface("wlan-0") is True

    def test_valid_interface_with_underscore(self):
        assert _validate_interface("wlan_0") is True

    def test_empty_string_rejected(self):
        assert _validate_interface("") is False

    def test_too_long_name_rejected(self):
        assert _validate_interface("a" * 33) is False

    def test_32_char_name_accepted(self):
        assert _validate_interface("a" * 32) is True

    def test_special_characters_rejected(self):
        assert _validate_interface("wlan0;rm") is False
        assert _validate_interface("wlan0 ") is False
        assert _validate_interface("wlan0|test") is False

    def test_dot_rejected(self):
        assert _validate_interface("wlan0.1") is False


class TestValidateMac:
    """Test MAC address validation."""

    def test_valid_mac_uppercase(self):
        assert _validate_mac("AA:BB:CC:DD:EE:FF") is True

    def test_valid_mac_lowercase(self):
        assert _validate_mac("aa:bb:cc:dd:ee:ff") is True

    def test_valid_mac_mixed_case(self):
        assert _validate_mac("Aa:Bb:Cc:Dd:Ee:Ff") is True

    def test_valid_mac_all_zeros(self):
        assert _validate_mac("00:00:00:00:00:00") is True

    def test_invalid_mac_too_short(self):
        assert _validate_mac("AA:BB:CC:DD:EE") is False

    def test_invalid_mac_too_long(self):
        assert _validate_mac("AA:BB:CC:DD:EE:FF:00") is False

    def test_invalid_mac_wrong_separator(self):
        assert _validate_mac("AA-BB-CC-DD-EE-FF") is False

    def test_invalid_mac_no_separator(self):
        assert _validate_mac("AABBCCDDEEFF") is False

    def test_invalid_mac_with_g(self):
        assert _validate_mac("GG:BB:CC:DD:EE:FF") is False

    def test_empty_string(self):
        assert _validate_mac("") is False

    def test_random_string(self):
        assert _validate_mac("not-a-mac") is False

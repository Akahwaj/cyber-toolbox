"""Tests for modules/wireless.py"""
import pytest
from modules.wireless import _validate_interface, _validate_mac


class TestValidateInterface:
    def test_valid_simple_interface(self):
        assert _validate_interface("wlan0") is True

    def test_valid_monitor_mode_interface(self):
        assert _validate_interface("wlan0mon") is True

    def test_valid_eth_interface(self):
        assert _validate_interface("eth0") is True

    def test_valid_with_hyphen(self):
        assert _validate_interface("wlan-0") is True

    def test_valid_with_underscore(self):
        assert _validate_interface("wlan_0") is True

    def test_valid_max_length(self):
        # 32 characters exactly
        assert _validate_interface("a" * 32) is True

    def test_invalid_too_long(self):
        # 33 characters – exceeds limit
        assert _validate_interface("a" * 33) is False

    def test_invalid_empty_string(self):
        assert _validate_interface("") is False

    def test_invalid_special_characters(self):
        assert _validate_interface("wlan0!") is False
        assert _validate_interface("wlan 0") is False
        assert _validate_interface("wlan0;") is False

    def test_invalid_with_slash(self):
        assert _validate_interface("../../etc/passwd") is False

    def test_invalid_with_dot(self):
        assert _validate_interface("wlan0.1") is False

    def test_numbers_only(self):
        assert _validate_interface("12345") is True

    def test_single_character(self):
        assert _validate_interface("a") is True


class TestValidateMac:
    def test_valid_mac_uppercase(self):
        assert _validate_mac("AA:BB:CC:DD:EE:FF") is True

    def test_valid_mac_lowercase(self):
        assert _validate_mac("aa:bb:cc:dd:ee:ff") is True

    def test_valid_mac_mixed_case(self):
        assert _validate_mac("00:1A:2b:3C:4d:5E") is True

    def test_valid_mac_zeros(self):
        assert _validate_mac("00:00:00:00:00:00") is True

    def test_invalid_mac_too_short(self):
        assert _validate_mac("AA:BB:CC:DD:EE") is False

    def test_invalid_mac_too_long(self):
        assert _validate_mac("AA:BB:CC:DD:EE:FF:00") is False

    def test_invalid_mac_no_colons(self):
        assert _validate_mac("AABBCCDDEEFF") is False

    def test_invalid_mac_dashes(self):
        # Uses dashes instead of colons
        assert _validate_mac("AA-BB-CC-DD-EE-FF") is False

    def test_invalid_mac_wrong_separator(self):
        assert _validate_mac("AA.BB.CC.DD.EE.FF") is False

    def test_invalid_mac_non_hex(self):
        assert _validate_mac("GG:HH:II:JJ:KK:LL") is False

    def test_invalid_mac_empty(self):
        assert _validate_mac("") is False

    def test_invalid_mac_extra_chars(self):
        assert _validate_mac("AA:BB:CC:DD:EE:FF; rm -rf /") is False

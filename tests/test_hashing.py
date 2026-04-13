"""Tests for modules/hashing.py"""
import pytest
from modules.hashing import hash_text


class TestHashText:
    # Known-good hash values for "hello"
    KNOWN = {
        "md5": "5d41402abc4b2a76b9719d911017c592",
        "sha1": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
        "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
        "sha512": (
            "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043"
        ),
    }

    def test_md5_known_value(self):
        assert hash_text("hello", "md5") == self.KNOWN["md5"]

    def test_sha1_known_value(self):
        assert hash_text("hello", "sha1") == self.KNOWN["sha1"]

    def test_sha256_known_value(self):
        assert hash_text("hello", "sha256") == self.KNOWN["sha256"]

    def test_sha512_known_value(self):
        assert hash_text("hello", "sha512") == self.KNOWN["sha512"]

    def test_empty_string_md5(self):
        result = hash_text("", "md5")
        assert result == "d41d8cd98f00b204e9800998ecf8427e"

    def test_empty_string_sha256(self):
        result = hash_text("", "sha256")
        assert result == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_returns_lowercase_hex_string(self):
        result = hash_text("test", "md5")
        assert result == result.lower()
        assert all(c in "0123456789abcdef" for c in result)

    def test_md5_length(self):
        assert len(hash_text("anything", "md5")) == 32

    def test_sha1_length(self):
        assert len(hash_text("anything", "sha1")) == 40

    def test_sha256_length(self):
        assert len(hash_text("anything", "sha256")) == 64

    def test_sha512_length(self):
        assert len(hash_text("anything", "sha512")) == 128

    def test_different_inputs_produce_different_hashes(self):
        assert hash_text("hello", "md5") != hash_text("world", "md5")

    def test_same_input_always_same_hash(self):
        assert hash_text("deterministic", "sha256") == hash_text("deterministic", "sha256")

    def test_unicode_input(self):
        result = hash_text("héllo", "sha256")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError):
            hash_text("hello", "nonexistent_algo")

"""Tests for modules/hashing.py – hash_text() and ALGORITHMS."""
import hashlib

from modules.hashing import hash_text, ALGORITHMS


class TestHashText:
    """Verify hash_text produces correct digests."""

    def test_md5_known_value(self):
        result = hash_text("hello", "md5")
        assert result == hashlib.md5(b"hello").hexdigest()

    def test_sha1_known_value(self):
        result = hash_text("hello", "sha1")
        assert result == hashlib.sha1(b"hello").hexdigest()

    def test_sha256_known_value(self):
        result = hash_text("hello", "sha256")
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert result == expected

    def test_sha512_known_value(self):
        result = hash_text("hello", "sha512")
        assert result == hashlib.sha512(b"hello").hexdigest()

    def test_empty_string(self):
        result = hash_text("", "sha256")
        assert result == hashlib.sha256(b"").hexdigest()

    def test_unicode_string(self):
        result = hash_text("café", "sha256")
        assert result == hashlib.sha256("café".encode()).hexdigest()

    def test_long_string(self):
        text = "a" * 10000
        result = hash_text(text, "sha256")
        assert result == hashlib.sha256(text.encode()).hexdigest()

    def test_special_characters(self):
        text = '!@#$%^&*()_+{}|:"<>?'
        result = hash_text(text, "md5")
        assert result == hashlib.md5(text.encode()).hexdigest()


class TestAlgorithmsMapping:
    """Verify the ALGORITHMS dictionary structure."""

    def test_contains_four_algorithms(self):
        assert len(ALGORITHMS) == 4

    def test_keys_are_string_digits(self):
        for key in ALGORITHMS:
            assert key.isdigit()

    def test_values_are_name_algo_tuples(self):
        for key, (name, algo) in ALGORITHMS.items():
            assert isinstance(name, str)
            assert isinstance(algo, str)
            # Verify the algo is a valid hashlib algorithm
            assert algo in hashlib.algorithms_available

    def test_md5_entry(self):
        assert ALGORITHMS["1"] == ("MD5", "md5")

    def test_sha1_entry(self):
        assert ALGORITHMS["2"] == ("SHA-1", "sha1")

    def test_sha256_entry(self):
        assert ALGORITHMS["3"] == ("SHA-256", "sha256")

    def test_sha512_entry(self):
        assert ALGORITHMS["4"] == ("SHA-512", "sha512")

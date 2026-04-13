"""Tests for modules/password.py"""
import pytest
from modules.password import analyze_password


class TestAnalyzePasswordStrength:
    def test_very_short_password_is_weak(self):
        strength, score, feedback = analyze_password("ab")
        assert strength == "Weak"

    def test_empty_password_is_weak(self):
        strength, score, feedback = analyze_password("")
        assert strength == "Weak"
        assert score == 0

    def test_strong_password_full_score(self):
        password = "Secure@Password123"
        strength, score, feedback = analyze_password(password)
        assert strength == "Strong"
        assert score == 6
        assert feedback == []

    def test_moderate_password(self):
        # Has uppercase, lowercase, digit but no special char, length < 12
        password = "Password1"
        strength, score, feedback = analyze_password(password)
        assert strength == "Moderate"

    def test_weak_all_lowercase_short(self):
        strength, score, feedback = analyze_password("abc")
        assert strength == "Weak"

    def test_score_increments_for_length_ge_12(self):
        # A 12-char password with all criteria should score 6
        password = "Abcdefgh1!xy"
        strength, score, feedback = analyze_password(password)
        assert score == 6

    def test_score_does_not_increment_extra_for_length_between_8_and_11(self):
        # 8-char, all criteria except length>=12 -> score 5
        password = "Abc1!xyz"
        strength, score, feedback = analyze_password(password)
        assert score == 5
        assert strength == "Strong"

    def test_feedback_missing_uppercase(self):
        _, _, feedback = analyze_password("password1!")
        assert "Add uppercase letters." in feedback

    def test_feedback_missing_lowercase(self):
        _, _, feedback = analyze_password("PASSWORD1!")
        assert "Add lowercase letters." in feedback

    def test_feedback_missing_digit(self):
        _, _, feedback = analyze_password("Password!")
        assert "Add numbers." in feedback

    def test_feedback_missing_special_char(self):
        _, _, feedback = analyze_password("Password1")
        assert "Add special characters." in feedback

    def test_feedback_too_short(self):
        _, _, feedback = analyze_password("P1!")
        assert "Use at least 8 characters." in feedback

    def test_no_feedback_for_strong_password(self):
        _, _, feedback = analyze_password("MyStr0ng!Pass")
        assert feedback == []

    def test_all_digits_password(self):
        strength, score, feedback = analyze_password("12345678")
        assert "Add uppercase letters." in feedback
        assert "Add lowercase letters." in feedback
        assert "Add special characters." in feedback

    def test_special_characters_recognized(self):
        for char in "!@#$%^&*(),.?\":{}|<>":
            _, _, feedback = analyze_password(f"Password1{char}")
            assert "Add special characters." not in feedback, f"Special char {char!r} not recognized"

    def test_score_range(self):
        _, score, _ = analyze_password("weak")
        assert 0 <= score <= 6

    def test_strength_categories_exhaustive(self):
        assert analyze_password("ab")[0] == "Weak"          # score <=2
        assert analyze_password("Abcde123")[0] == "Moderate"  # score <=4 (no special, no len>=12)
        assert analyze_password("Abcde123!xyz")[0] == "Strong"  # score 6


class TestAnalyzePasswordReturnType:
    def test_returns_tuple_of_three(self):
        result = analyze_password("TestPass1!")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_strength_is_string(self):
        strength, _, _ = analyze_password("TestPass1!")
        assert isinstance(strength, str)

    def test_score_is_int(self):
        _, score, _ = analyze_password("TestPass1!")
        assert isinstance(score, int)

    def test_feedback_is_list(self):
        _, _, feedback = analyze_password("TestPass1!")
        assert isinstance(feedback, list)

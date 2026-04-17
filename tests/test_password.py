"""Tests for modules/password.py – analyze_password()."""
from modules.password import analyze_password


class TestAnalyzePasswordStrength:
    """Verify strength classification for different password types."""

    def test_empty_password_is_weak(self):
        strength, score, feedback = analyze_password("")
        assert strength == "Weak"
        assert score == 0

    def test_short_lowercase_only(self):
        strength, score, feedback = analyze_password("abc")
        assert strength == "Weak"
        assert "Use at least 8 characters." in feedback

    def test_8_char_lowercase_only(self):
        strength, score, feedback = analyze_password("abcdefgh")
        # length>=8 (+1), has lowercase (+1) = 2
        assert score == 2
        assert strength == "Weak"

    def test_moderate_password(self):
        strength, score, feedback = analyze_password("Abcdefgh1")
        # length>=8 (+1), upper (+1), lower (+1), digit (+1) = 4
        assert score == 4
        assert strength == "Moderate"

    def test_strong_password(self):
        strength, score, feedback = analyze_password("Abcdefgh12!@")
        # length>=8 (+1), length>=12 (+1), upper (+1), lower (+1), digit (+1), special (+1) = 6
        assert score == 6
        assert strength == "Strong"
        assert feedback == []

    def test_12_plus_chars_bonus(self):
        strength, score, _ = analyze_password("aaaaaaaaaaaa")
        # length>=8 (+1), length>=12 (+1), lowercase (+1) = 3
        assert score == 3
        assert strength == "Moderate"

    def test_only_digits(self):
        strength, score, feedback = analyze_password("12345678")
        # length>=8 (+1), digit (+1) = 2
        assert score == 2
        assert "Add uppercase letters." in feedback
        assert "Add lowercase letters." in feedback
        assert "Add special characters." in feedback

    def test_only_special_characters(self):
        strength, score, feedback = analyze_password("!@#$%^&*")
        # length>=8 (+1), special (+1) = 2
        assert score == 2

    def test_only_uppercase(self):
        strength, score, feedback = analyze_password("ABCDEFGH")
        assert score == 2
        assert "Add lowercase letters." in feedback

    def test_missing_special_characters_feedback(self):
        _, _, feedback = analyze_password("Abcdefgh1")
        assert "Add special characters." in feedback

    def test_missing_numbers_feedback(self):
        _, _, feedback = analyze_password("Abcdefgh!")
        assert "Add numbers." in feedback


class TestAnalyzePasswordEdgeCases:
    """Edge cases for password analysis."""

    def test_single_character(self):
        strength, score, _ = analyze_password("a")
        assert strength == "Weak"
        assert score <= 2

    def test_unicode_characters(self):
        # Unicode chars shouldn't crash; they count as length but not letter/digit/special
        strength, score, _ = analyze_password("🔐🔐🔐🔐🔐🔐🔐🔐")
        assert strength in ("Weak", "Moderate", "Strong")

    def test_spaces_in_password(self):
        # Spaces count toward length but not special chars (not in the regex)
        strength, score, _ = analyze_password("A b c d e f g h")
        assert score >= 2  # length>=8, uppercase, lowercase

    def test_very_long_password(self):
        strength, score, _ = analyze_password("Aa1!" * 100)
        assert strength == "Strong"
        assert score == 6

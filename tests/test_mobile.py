"""Tests for modules/mobile.py – regex validation and APK analysis."""
import os
import zipfile
from unittest.mock import patch, MagicMock

from modules.mobile import _PKG_RE, analyze_apk_static


class TestPackageNameRegex:
    """Test the Android package name regex."""

    def test_valid_simple_package(self):
        assert _PKG_RE.match("com.example.app")

    def test_valid_deep_package(self):
        assert _PKG_RE.match("com.example.myapp.feature")

    def test_valid_with_numbers(self):
        assert _PKG_RE.match("com.example2.app3")

    def test_valid_with_underscores(self):
        assert _PKG_RE.match("com.my_app.test_feature")

    def test_invalid_single_segment(self):
        assert not _PKG_RE.match("myapp")

    def test_invalid_starts_with_number(self):
        assert not _PKG_RE.match("1com.example.app")

    def test_invalid_segment_starts_with_number(self):
        assert not _PKG_RE.match("com.1example.app")

    def test_invalid_empty_string(self):
        assert not _PKG_RE.match("")

    def test_invalid_with_hyphen(self):
        assert not _PKG_RE.match("com.my-app.test")

    def test_invalid_trailing_dot(self):
        # Regex should not match if there's a trailing dot (no final segment)
        assert not _PKG_RE.match("com.example.")

    def test_invalid_double_dot(self):
        assert not _PKG_RE.match("com..example.app")


class TestAnalyzeApkStatic:
    """Test analyze_apk_static() with real ZIP files."""

    def test_file_not_found(self, capsys):
        analyze_apk_static("/nonexistent/path/to/app.apk")
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_valid_apk_zip(self, tmp_path, capsys):
        """Create a minimal APK-like ZIP and analyze it."""
        apk_path = str(tmp_path / "test.apk")
        with zipfile.ZipFile(apk_path, 'w') as zf:
            zf.writestr("AndroidManifest.xml", "<manifest/>")
            zf.writestr("classes.dex", "fake dex")
            zf.writestr("lib/arm64-v8a/libnative.so", "fake lib")
            zf.writestr("res/values/strings.xml", "<resources/>")
            zf.writestr("assets/config.json", '{"key": "value"}')
            zf.writestr("assets/cert.pem", "fake cert")

        with patch("modules.mobile.check_tool", return_value=False):
            analyze_apk_static(apk_path)

        captured = capsys.readouterr()
        assert "AndroidManifest.xml found" in captured.out
        assert "Native libraries: 1" in captured.out
        assert "libnative.so" in captured.out
        assert "Interesting files" in captured.out

    def test_bad_zip_file(self, tmp_path, capsys):
        """Test with a file that is not a valid ZIP."""
        bad_file = tmp_path / "bad.apk"
        bad_file.write_text("this is not a zip file")
        with patch("modules.mobile.check_tool", return_value=False):
            analyze_apk_static(str(bad_file))
        captured = capsys.readouterr()
        assert "Error reading APK" in captured.out

    def test_apk_without_manifest(self, tmp_path, capsys):
        """APK without AndroidManifest.xml."""
        apk_path = str(tmp_path / "no_manifest.apk")
        with zipfile.ZipFile(apk_path, 'w') as zf:
            zf.writestr("classes.dex", "fake dex")

        with patch("modules.mobile.check_tool", return_value=False):
            analyze_apk_static(apk_path)

        captured = capsys.readouterr()
        assert "AndroidManifest.xml found" not in captured.out

    def test_apk_no_native_libs(self, tmp_path, capsys):
        """APK without native libraries."""
        apk_path = str(tmp_path / "no_native.apk")
        with zipfile.ZipFile(apk_path, 'w') as zf:
            zf.writestr("AndroidManifest.xml", "<manifest/>")
            zf.writestr("classes.dex", "fake dex")

        with patch("modules.mobile.check_tool", return_value=False):
            analyze_apk_static(apk_path)

        captured = capsys.readouterr()
        assert "Native libraries" not in captured.out

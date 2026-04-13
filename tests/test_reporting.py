"""Tests for modules/reporting.py"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch
from modules.reporting import generate_report, _generate_markdown, _generate_html, _generate_json


@pytest.fixture(autouse=True)
def run_in_tmp_dir(tmp_path, monkeypatch):
    """Run each test in a fresh temp directory so generated reports don't litter the repo."""
    monkeypatch.chdir(tmp_path)


class TestGenerateReport:
    def test_markdown_format_returns_filename(self):
        filename = generate_report("Test Report", {}, output_format="markdown")
        assert filename is not None
        assert filename.endswith(".md")

    def test_html_format_returns_filename(self):
        filename = generate_report("Test Report", {}, output_format="html")
        assert filename is not None
        assert filename.endswith(".html")

    def test_json_format_returns_filename(self):
        filename = generate_report("Test Report", {}, output_format="json")
        assert filename is not None
        assert filename.endswith(".json")

    def test_unknown_format_returns_none(self, capsys):
        result = generate_report("Test Report", {}, output_format="xml")
        assert result is None
        captured = capsys.readouterr()
        assert "Unknown format" in captured.out

    def test_created_file_exists(self):
        filename = generate_report("Test", {}, output_format="markdown")
        assert os.path.isfile(filename)


class TestMarkdownReport:
    def test_contains_title(self):
        filename = generate_report("My Security Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "My Security Report" in content

    def test_contains_timestamp(self):
        filename = generate_report("Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "Generated:" in content

    def test_contains_tool_name(self):
        filename = generate_report("Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "Mythos Lab Cyber Toolbox" in content

    def test_empty_findings_message(self):
        filename = generate_report("Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "No findings recorded." in content

    def test_findings_appear_in_report(self):
        findings = {"Critical": ["RCE vulnerability found", "SQL injection in login"]}
        filename = generate_report("Report", findings, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "Critical" in content
        assert "RCE vulnerability found" in content

    def test_list_and_scalar_findings(self):
        findings = {"High": ["Issue A", "Issue B"], "Low": "Single scalar finding"}
        filename = generate_report("Report", findings, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "Issue A" in content
        assert "Single scalar finding" in content

    def test_ai_insights_section_when_provided(self):
        filename = generate_report("Report", {}, ai_insights="Great findings here.", output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "AI-Powered Insights" in content
        assert "Great findings here." in content

    def test_no_ai_section_when_not_provided(self):
        filename = generate_report("Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "AI-Powered Insights" not in content

    def test_disclaimer_present(self):
        filename = generate_report("Report", {}, output_format="markdown")
        with open(filename) as f:
            content = f.read()
        assert "Disclaimer" in content


class TestHtmlReport:
    def test_is_valid_html(self):
        filename = generate_report("Report", {}, output_format="html")
        with open(filename) as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content

    def test_contains_title(self):
        filename = generate_report("HTML Security Report", {}, output_format="html")
        with open(filename) as f:
            content = f.read()
        assert "HTML Security Report" in content

    def test_findings_in_html(self):
        findings = {"Medium": ["Misconfigured header"]}
        filename = generate_report("Report", findings, output_format="html")
        with open(filename) as f:
            content = f.read()
        assert "Misconfigured header" in content

    def test_empty_findings_html(self):
        filename = generate_report("Report", {}, output_format="html")
        with open(filename) as f:
            content = f.read()
        assert "No findings recorded." in content

    def test_ai_insights_in_html(self):
        filename = generate_report("Report", {}, ai_insights="AI said: fix it.", output_format="html")
        with open(filename) as f:
            content = f.read()
        assert "AI-Powered Insights" in content
        assert "AI said: fix it." in content


class TestJsonReport:
    def _load(self, filename):
        with open(filename) as f:
            return json.load(f)

    def test_valid_json_output(self):
        filename = generate_report("JSON Report", {}, output_format="json")
        data = self._load(filename)
        assert isinstance(data, dict)

    def test_json_contains_title(self):
        findings = {"High": ["CVE-2024-9999"]}
        filename = generate_report("Test Title", findings, output_format="json")
        data = self._load(filename)
        assert data["title"] == "Test Title"

    def test_json_contains_findings(self):
        findings = {"Critical": ["SQL injection"]}
        filename = generate_report("Report", findings, output_format="json")
        data = self._load(filename)
        assert "Critical" in data["findings"]
        assert "SQL injection" in data["findings"]["Critical"]

    def test_json_ai_insights_field(self):
        filename = generate_report("R", {}, ai_insights="Insightful.", output_format="json")
        data = self._load(filename)
        assert data["ai_insights"] == "Insightful."

    def test_json_null_ai_insights_when_not_provided(self):
        filename = generate_report("R", {}, output_format="json")
        data = self._load(filename)
        assert data["ai_insights"] is None

    def test_json_tool_field(self):
        filename = generate_report("R", {}, output_format="json")
        data = self._load(filename)
        assert data["tool"] == "Mythos Lab Cyber Toolbox"

    def test_json_empty_findings(self):
        filename = generate_report("R", {}, output_format="json")
        data = self._load(filename)
        assert data["findings"] == {}

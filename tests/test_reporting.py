"""Tests for modules/reporting.py – generate_report() in all formats."""
import json
import os

from modules.reporting import generate_report


class TestGenerateMarkdownReport:
    """Test Markdown report generation."""

    def test_basic_markdown_report(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"Critical": ["SQL Injection in /login"], "High": ["XSS in search"]}
        filename = generate_report("Test Report", findings, output_format="markdown")
        assert filename is not None
        assert filename.endswith(".md")
        content = (tmp_path / filename).read_text()
        assert "# Test Report" in content
        assert "SQL Injection in /login" in content
        assert "XSS in search" in content

    def test_markdown_with_ai_insights(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"High": ["Open port 22"]}
        filename = generate_report("AI Report", findings,
                                   ai_insights="Critical SSH exposure detected.",
                                   output_format="markdown")
        content = (tmp_path / filename).read_text()
        assert "AI-Powered Insights" in content
        assert "Critical SSH exposure detected." in content

    def test_markdown_empty_findings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Empty Report", {}, output_format="markdown")
        content = (tmp_path / filename).read_text()
        assert "No findings recorded." in content

    def test_markdown_contains_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Time Test", {}, output_format="markdown")
        content = (tmp_path / filename).read_text()
        assert "**Generated:**" in content

    def test_markdown_contains_disclaimer(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Disclaimer Test", {}, output_format="markdown")
        content = (tmp_path / filename).read_text()
        assert "Disclaimer" in content
        assert "authorized security testing" in content

    def test_markdown_non_list_findings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"Info": "Single string finding"}
        filename = generate_report("String Finding", findings, output_format="markdown")
        content = (tmp_path / filename).read_text()
        assert "Single string finding" in content


class TestGenerateHtmlReport:
    """Test HTML report generation."""

    def test_basic_html_report(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"Critical": ["SQL Injection"]}
        filename = generate_report("HTML Report", findings, output_format="html")
        assert filename is not None
        assert filename.endswith(".html")
        content = (tmp_path / filename).read_text()
        assert "<html" in content
        assert "HTML Report" in content
        assert "SQL Injection" in content

    def test_html_with_ai_insights(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"High": ["XSS"]}
        filename = generate_report("AI HTML", findings,
                                   ai_insights="XSS is critical",
                                   output_format="html")
        content = (tmp_path / filename).read_text()
        assert "AI-Powered Insights" in content
        assert "XSS is critical" in content

    def test_html_empty_findings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Empty HTML", {}, output_format="html")
        content = (tmp_path / filename).read_text()
        assert "No findings recorded." in content

    def test_html_has_proper_structure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Structure Test", {}, output_format="html")
        content = (tmp_path / filename).read_text()
        assert "<!DOCTYPE html>" in content
        assert "</html>" in content
        assert '<meta charset="UTF-8">' in content


class TestGenerateJsonReport:
    """Test JSON report generation."""

    def test_basic_json_report(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"Critical": ["SQL Injection"]}
        filename = generate_report("JSON Report", findings, output_format="json")
        assert filename is not None
        assert filename.endswith(".json")
        data = json.loads((tmp_path / filename).read_text())
        assert data["title"] == "JSON Report"
        assert data["findings"]["Critical"] == ["SQL Injection"]

    def test_json_with_ai_insights(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        findings = {"High": ["XSS"]}
        filename = generate_report("AI JSON", findings,
                                   ai_insights="AI analysis",
                                   output_format="json")
        data = json.loads((tmp_path / filename).read_text())
        assert data["ai_insights"] == "AI analysis"

    def test_json_empty_findings(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Empty JSON", {}, output_format="json")
        data = json.loads((tmp_path / filename).read_text())
        assert data["findings"] == {}

    def test_json_has_required_fields(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Fields Test", {}, output_format="json")
        data = json.loads((tmp_path / filename).read_text())
        assert "title" in data
        assert "generated" in data
        assert "tool" in data
        assert "findings" in data
        assert "ai_insights" in data

    def test_json_tool_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        filename = generate_report("Tool Test", {}, output_format="json")
        data = json.loads((tmp_path / filename).read_text())
        assert data["tool"] == "Mythos Lab Cyber Toolbox"


class TestGenerateReportUnknownFormat:
    """Test unknown format handling."""

    def test_unknown_format_returns_none(self, capsys):
        result = generate_report("Test", {}, output_format="pdf")
        assert result is None
        captured = capsys.readouterr()
        assert "Unknown format" in captured.out

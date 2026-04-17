"""Shared fixtures for cyber-toolbox tests."""
import os
import sys
import tempfile

import pytest

# Ensure the project root is on sys.path so `modules` can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture
def tmp_dir(tmp_path):
    """Return a temporary directory path (pathlib.Path)."""
    return tmp_path


@pytest.fixture
def sample_log_file(tmp_path):
    """Create a sample log file with various security-relevant entries."""
    content = (
        '192.168.1.10 - - [01/Jan/2024:10:00:00] "GET / HTTP/1.1" 200 1234\n'
        '10.0.0.5 - - [01/Jan/2024:10:01:00] "POST /login HTTP/1.1" 401 0 - failed password\n'
        '10.0.0.5 - - [01/Jan/2024:10:01:05] "POST /login HTTP/1.1" 401 0 - failed password\n'
        '10.0.0.5 - - [01/Jan/2024:10:01:10] "POST /login HTTP/1.1" 401 0 - failed password\n'
        '172.16.0.1 - - [01/Jan/2024:10:02:00] "GET /search?q=union select * from users HTTP/1.1" 200\n'
        '192.168.1.20 - - [01/Jan/2024:10:03:00] "GET /page?x=<script>alert(1)</script> HTTP/1.1" 200\n'
        '10.0.0.99 - - [01/Jan/2024:10:04:00] "GET /../../etc/passwd HTTP/1.1" 403\n'
        '192.168.1.30 - - [01/Jan/2024:10:05:00] "GET / HTTP/1.1" 200 - nmap scan detected\n'
        '10.0.0.50 - - [01/Jan/2024:10:06:00] "POST /cmd HTTP/1.1" 200 - cmd.exe /c whoami\n'
    )
    log_file = tmp_path / "test.log"
    log_file.write_text(content)
    return str(log_file)


@pytest.fixture
def empty_log_file(tmp_path):
    """Create an empty log file."""
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    return str(log_file)


@pytest.fixture
def clean_log_file(tmp_path):
    """Create a log file with no security issues."""
    content = (
        '192.168.1.1 - - [01/Jan/2024:10:00:00] "GET / HTTP/1.1" 200 1234\n'
        '192.168.1.1 - - [01/Jan/2024:10:00:01] "GET /about HTTP/1.1" 200 567\n'
        '192.168.1.1 - - [01/Jan/2024:10:00:02] "GET /contact HTTP/1.1" 200 890\n'
    )
    log_file = tmp_path / "clean.log"
    log_file.write_text(content)
    return str(log_file)

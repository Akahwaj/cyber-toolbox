"""Log analysis module for security event detection."""
import re
import os
from collections import Counter, defaultdict

PATTERNS = {
    "brute_force": re.compile(
        r"(failed password|authentication failure|invalid user|failed login|"
        r"bad password|too many authentication failures)", re.IGNORECASE
    ),
    "sql_injection": re.compile(
        r"(union\s+select|drop\s+table|insert\s+into|or\s+1=1|"
        r"'--|\";--|xp_cmdshell|information_schema)", re.IGNORECASE
    ),
    "xss": re.compile(
        r"(<script|javascript:|onerror=|onload=|alert\(|document\.cookie)", re.IGNORECASE
    ),
    "path_traversal": re.compile(
        r"(\.\./|\.\.\\|%2e%2e|%252e%252e)", re.IGNORECASE
    ),
    "suspicious_ip": re.compile(
        r"\b(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b"
    ),
    "port_scan": re.compile(
        r"(nmap|masscan|zmap|port\s+scan|syn\s+flood)", re.IGNORECASE
    ),
    "malware_indicator": re.compile(
        r"(cmd\.exe|powershell|wget\s+http|curl\s+http|base64|"
        r"eval\(|exec\(|/bin/sh|/bin/bash)", re.IGNORECASE
    ),
}

def analyze_file(file_path, ai_agent=None):
    """Analyze a log file for security issues."""
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\n📋 Log Analysis: {file_path}")
    print("-" * 40)

    findings = defaultdict(list)
    ip_counter = Counter()
    total_lines = 0

    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    with open(file_path, 'r', errors='replace') as f:
        for lineno, line in enumerate(f, 1):
            total_lines += 1
            for threat_type, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings[threat_type].append((lineno, line.strip()))
            ips = ip_pattern.findall(line)
            for ip in ips:
                ip_counter[ip] += 1

    print(f"Total lines analyzed: {total_lines}")
    print(f"\n🚨 Security Findings:")

    if not any(findings.values()):
        print("  No obvious security threats detected.")
    else:
        for threat_type, matches in findings.items():
            if matches:
                print(f"\n  [{threat_type.upper().replace('_', ' ')}] - {len(matches)} occurrence(s)")
                for lineno, line in matches[:3]:
                    print(f"    Line {lineno}: {line[:120]}")
                if len(matches) > 3:
                    print(f"    ... and {len(matches) - 3} more")

    print(f"\n📊 Top IP Addresses:")
    for ip, count in ip_counter.most_common(10):
        print(f"  {ip}: {count} occurrence(s)")

    # AI analysis if available
    if ai_agent:
        print("\n🤖 AI Analysis:")
        with open(file_path, 'r', errors='replace') as f:
            content = f.read()
        print(ai_agent.analyze_log(content))

    return findings

def run(ai_agent=None):
    print("\n📋 Log Analysis Tool")
    print("--------------------")
    path = input("Log file path: ").strip()
    if not path:
        print("No path entered.")
        return
    use_ai = False
    if ai_agent:
        use_ai_input = input("Use AI for enhanced analysis? (yes/no) [no]: ").strip().lower()
        use_ai = use_ai_input in ("yes", "y")
    analyze_file(path, ai_agent=ai_agent if use_ai else None)

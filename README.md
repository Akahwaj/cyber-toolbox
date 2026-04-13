# Cyber Toolbox

Python-based cybersecurity learning toolkit for defensive security, offensive tools, lab practice, and automation — with an integrated **AI Security Agent** that teaches, guides, and answers questions dynamically during assessments.

## Features
- Password strength checker
- Hash generator (MD5, SHA-1, SHA-256, SHA-512)
- AI Security Agent:
  - Interactive tool teaching (Nmap, Aircrack-ng, Metasploit, Hydra, John the Ripper, SQLMap, Wireshark, Snort, Fail2Ban, Suricata, and more)
  - Dynamic Q&A for security topics
  - Guided walkthroughs for common pentesting scenarios
  - Real-time log / output file analysis

## Purpose
This project is built for cybersecurity learning and authorized lab use only.

## Disclaimer
Use this toolkit only on systems you own or are explicitly authorized to test.

## Run (Interactive Menu)
```bash
python cyber_toolbox.py
```

## AI Agent — Command-Line Interface

All AI agent features are also available directly from the command line:

### Teach a Security Tool
```bash
python cyber_toolbox.py --teach-tool nmap
python cyber_toolbox.py --teach-tool aircrack-ng
python cyber_toolbox.py --teach-tool metasploit
python cyber_toolbox.py --teach-tool wireshark
```

### Ask a Security Question
```bash
python cyber_toolbox.py --qa "How do I crack WPA passwords?"
python cyber_toolbox.py --qa "What does a CVSS score of 7.5 mean?"
python cyber_toolbox.py --qa "How do I perform privilege escalation on Linux?"
python cyber_toolbox.py --qa "What is SQL injection?"
```

### Run a Guided Walkthrough
```bash
python cyber_toolbox.py --walkthrough "linux privilege escalation"
python cyber_toolbox.py --walkthrough "web application owasp top 10"
python cyber_toolbox.py --walkthrough "network penetration test"
python cyber_toolbox.py --walkthrough "wpa wifi"
python cyber_toolbox.py --walkthrough "hackthebox linux"
python cyber_toolbox.py --walkthrough "tryhackme"
```

### Analyse a Log or Tool Output File
```bash
python cyber_toolbox.py --contextual-explain --input logs/access.log
python cyber_toolbox.py --contextual-explain --input /var/log/auth.log
```
The agent scans the file for suspicious patterns (authentication failures, SQL injection attempts, XSS, path traversal, command injection, etc.) and provides actionable explanations for each finding.

## Tools Included

### Password Strength Checker
Evaluates password strength and provides suggestions for improvement.

### Hash Generator
Generates MD5, SHA-1, SHA-256, and SHA-512 hashes for text input.

### AI Security Agent
An embedded knowledge-base driven agent covering:

**Offensive tools:** Nmap, Aircrack-ng (full suite), Metasploit, Hydra, John the Ripper, SQLMap, Burp Suite

**Defensive tools:** Wireshark/tshark, Snort, Suricata, Fail2Ban

**Walkthroughs:** Linux privilege escalation, OWASP Top 10 web testing, network penetration test, WPA/WPA2 Wi-Fi auditing, HackTheBox Linux boxes, TryHackMe rooms

**Q&A topics:** CVSS scoring, WPA cracking, Nmap output interpretation, privilege escalation, SQL injection, XSS, port scanning, Metasploit workflow, Wireshark filters

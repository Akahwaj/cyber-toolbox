# 🧰 Mythos Lab Cyber Toolbox

Python-based cybersecurity learning toolkit for defensive security, lab practice,
and automation — now with an integrated **AI Security Assistant**.

## Features
- Password strength checker
- Hash generator (MD5 / SHA1 / SHA256 / SHA512)
- Teach Mode – guided explanations for each tool
- Expert Mode – direct access to built-in tools with AI-powered guidance for external security tools
- **AI Security Assistant** – vulnerability explanations, tool walkthroughs,
  threat analysis, tool recommendations, and an NLP chat interface
Advanced AI-powered cybersecurity platform for security professionals and learners.
Integrates **Claude (Anthropic)** and **OpenAI GPT** with a comprehensive suite of security tools.

## Features

| Module | Description |
|---|---|
| 🔐 Password Checker | Strength analysis with detailed feedback |
| #️⃣ Hash Generator | MD5, SHA-1, SHA-256, SHA-512 |
| 🌐 Network Tools | Port scanner, Nmap integration, subnet helper |
| 📡 Wireless Tools | Aircrack-ng suite, monitor mode, packet capture |
| 📱 Mobile Tools | Android APK analysis, ADB, Frida integration |
| 📋 Log Analysis | Detect brute-force, SQLi, XSS, path traversal |
| 📄 Report Generator | Markdown, HTML, JSON security reports |
| 🤖 AI Assistant | Claude + OpenAI chat, teach mode, topic explainer |
| 🔮 Mythos Integration | Anthropic Claude SDK — streaming, tool-use, multi-turn chat |
| 🌐 Web Interface | Mobile-accessible browser UI (Flask) |

## Quick Start

## Run (interactive menu)
```bash
# Clone and install dependencies
pip install anthropic>=0.40.0 openai flask

# Set AI API keys (optional but recommended for Mythos and AI features)
export ANTHROPIC_API_KEY=your-claude-key
export OPENAI_API_KEY=your-openai-key

# Run environment check
python cyber_toolbox.py --quick-start

# Start interactive menu
python cyber_toolbox.py
```

## AI Features (command-line)

### Explain a vulnerability
```bash
python cyber_toolbox.py --ai-explain --vulnerability "SQL Injection"
python cyber_toolbox.py --ai-explain --vulnerability "CVE-2021-44228" --context "Log4Shell RCE"
```

### Explain a tool's output
```bash
python cyber_toolbox.py --ai-explain --tool nmap --output "Open ports: 22, 80, 443"
python cyber_toolbox.py --ai-explain --tool aircrack-ng
```

### Step-by-step walkthrough
```bash
python cyber_toolbox.py --ai-walkthrough "wireless assessment"
python cyber_toolbox.py --ai-walkthrough "Explain how to harden an Apache server."
python cyber_toolbox.py --ai-walkthrough "malware investigation"
```

### Recommend tools for a goal
```bash
python cyber_toolbox.py --recommend-tools --goal "wireless penetration testing"
python cyber_toolbox.py --recommend-tools --goal "network recon"
```

### Threat / log analysis
```bash
python cyber_toolbox.py --detect-threats --input-file /var/log/auth.log
```

### NLP chat interface
```bash
python cyber_toolbox.py --nlp-interface
```

## OpenAI Integration (optional)
To enable live GPT-powered responses, install the optional `openai` Python package
and set the `OPENAI_API_KEY` environment variable.
Without the package or API key, the toolbox uses its built-in knowledge base and
works fully offline.

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
python cyber_toolbox.py --ai-explain --vulnerability "buffer overflow"
```

> **Privacy note:** When `OPENAI_API_KEY` is set, queries are sent to the OpenAI API.
> For sensitive data (e.g. log files), use the `--no-openai` flag to force offline analysis:
> ```bash
> python cyber_toolbox.py --detect-threats --input-file /var/log/auth.log --no-openai
> ```

## Tools Covered by the AI Assistant
All tools listed below have built-in offline explanations. When `OPENAI_API_KEY` is set,
any tool or vulnerability can be queried even if not listed here.

| Category | Tools (built-in offline guidance) |
|---|---|
| Network | Nmap, Wireshark, Snort, Suricata |
| Wireless | airmon-ng, airodump-ng, aireplay-ng, aircrack-ng |
| Exploitation | Metasploit, SQLMap |
| Credentials | Hydra, John the Ripper, Hashcat |
| Defensive | OpenVAS, Lynis, OSSEC, iptables/ufw (via tool recommendations) |
| Forensics | Volatility, Autopsy, ClamAV, Ghidra (via tool recommendations) |
## CLI Usage

```bash
python cyber_toolbox.py                          # Interactive menu
python cyber_toolbox.py --chat                   # AI chat mode
python cyber_toolbox.py --teach nmap             # Learn about nmap
python cyber_toolbox.py --explain "SQL injection" # Explain a topic
python cyber_toolbox.py --analyze-logs auth.log  # Analyze log file
python cyber_toolbox.py --enable-server          # Start web interface
python cyber_toolbox.py --report                 # Generate report
python cyber_toolbox.py --scenario               # Guided scenarios
```

## Mythos Integration (Anthropic Claude SDK)

The **Mythos Integration** module (`modules/mythos.py`) provides a dedicated interface to
Anthropic's Python SDK with cybersecurity-focused helpers:

### Installation

```bash
pip install anthropic>=0.40.0
export ANTHROPIC_API_KEY=your-api-key
```

### Features

| Feature | Description |
|---|---|
| **Streaming responses** | Live token-by-token output via `stream_query()` |
| **Tool-use / structured output** | Structured JSON findings via `tool_assisted_scan()` |
| **Multi-turn chat** | Persistent conversation history via `multi_turn_chat()` |

### Quick Example

```python
from modules.mythos import MythosClient

client = MythosClient()

# Streaming question
client.stream_query("What is a SYN flood attack and how do I defend against it?")

# Structured security scan with tool-use
result = client.tool_assisted_scan(
    "Apache 2.4.49 web server with directory listing enabled on Ubuntu 20.04"
)
if result:
    print(result["severity"], result["summary"])
    for finding in result["findings"]:
        print(f"  [{finding['title']}] {finding['recommendation']}")

# Interactive multi-turn session
client.multi_turn_chat()
```

### Via the Interactive Menu

```bash
python cyber_toolbox.py     # Choose option 10 → Mythos Integration
```

## AI Integration

The AI agent works with or without API keys:

- **With Claude / Mythos**: Set `ANTHROPIC_API_KEY` + `pip install anthropic>=0.40.0`
- **With OpenAI**: Set `OPENAI_API_KEY` + `pip install openai`
- **Offline**: Built-in responses for common security topics

## Web Interface

Start the mobile-accessible web server:

```bash
python cyber_toolbox.py --enable-server
# Access at http://<your-ip>:5000
```

Features: password checker, hash generator, AI chat, tool tutorials.

## External Tools (Optional)

```bash
sudo apt install nmap aircrack-ng wireless-tools adb apktool
pip install frida-tools
```

## Purpose

Built for cybersecurity learning and **authorized** security testing only.
See `USAGE_GUIDE.txt` for full documentation.

## Disclaimer

Use this toolkit only on systems you own or are explicitly authorized to test.
Always comply with applicable laws and regulations.

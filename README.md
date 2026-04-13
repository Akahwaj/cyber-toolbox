# 🧰 Mythos Lab Cyber Toolbox

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

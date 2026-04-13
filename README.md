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
| 🌐 Web Interface | Mobile-accessible browser UI (Flask) |

## Quick Start

```bash
# Clone and install optional dependencies
pip install anthropic openai flask

# Set AI API keys (optional)
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

## AI Integration

The AI agent works with or without API keys:

- **With Claude**: Set `ANTHROPIC_API_KEY` + `pip install anthropic`
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

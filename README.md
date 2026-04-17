# Cyber Toolbox

Python-based cybersecurity learning toolkit for defensive security, lab practice,
and automation — now with an integrated **AI Security Assistant**.

## Features
- Password strength checker
- Hash generator (MD5 / SHA1 / SHA256 / SHA512)
- Teach Mode – guided explanations for each tool
- Expert Mode – direct access to built-in tools with AI-powered guidance for external security tools
- **AI Security Assistant** – vulnerability explanations, tool walkthroughs,
  threat analysis, tool recommendations, and an NLP chat interface

## Purpose
This project is built for cybersecurity learning and authorized lab use only.

## Disclaimer
Use this toolkit only on systems you own or are explicitly authorized to test.

## Run (interactive menu)
```bash
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

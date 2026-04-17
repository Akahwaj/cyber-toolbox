"""
ai_explainer.py – AI-powered guidance for the Cyber Toolbox.

Uses the OpenAI API when the ``openai`` package is installed and the
``OPENAI_API_KEY`` environment variable is set.  Falls back to a built-in
knowledge base so the rest of the toolkit keeps working without any
external dependencies.
"""

import os
import textwrap

# ---------------------------------------------------------------------------
# Optional OpenAI dependency
# ---------------------------------------------------------------------------
try:
    import openai as _openai  # type: ignore
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

# ---------------------------------------------------------------------------
# Built-in knowledge base (used when OpenAI is unavailable / not configured)
# ---------------------------------------------------------------------------

_VULNERABILITY_KB = {
    "sql injection": {
        "description": (
            "SQL Injection allows an attacker to interfere with an application's "
            "database queries by injecting malicious SQL code through user input."
        ),
        "impact": "Unauthorized data access, data modification, or full database compromise.",
        "fixes": [
            "Use parameterized queries / prepared statements.",
            "Apply input validation and allowlisting.",
            "Use a Web Application Firewall (WAF).",
            "Follow the principle of least privilege for DB accounts.",
        ],
    },
    "xss": {
        "description": (
            "Cross-Site Scripting (XSS) lets attackers inject client-side scripts "
            "into web pages viewed by other users."
        ),
        "impact": "Session hijacking, credential theft, malware distribution.",
        "fixes": [
            "Encode/escape all user-supplied output.",
            "Use a Content-Security-Policy (CSP) header.",
            "Validate and sanitise all input.",
            "Prefer modern frameworks that auto-escape by default.",
        ],
    },
    "buffer overflow": {
        "description": (
            "A buffer overflow occurs when a program writes more data to a buffer "
            "than it can hold, corrupting adjacent memory."
        ),
        "impact": "Arbitrary code execution, privilege escalation, system crash.",
        "fixes": [
            "Use memory-safe languages where possible.",
            "Enable stack canaries and ASLR.",
            "Perform bounds-checking on all inputs.",
            "Keep software patched and up to date.",
        ],
    },
    "weak password": {
        "description": (
            "Weak or default passwords make it trivial for attackers to gain "
            "unauthorised access via brute-force or dictionary attacks."
        ),
        "impact": "Account takeover, lateral movement, data breach.",
        "fixes": [
            "Enforce a strong password policy (length, complexity).",
            "Require multi-factor authentication (MFA).",
            "Use a password manager.",
            "Audit accounts for default or blank credentials.",
        ],
    },
    "open port": {
        "description": (
            "Unnecessary open ports expose services to potential attackers who "
            "can probe them for vulnerabilities."
        ),
        "impact": "Service exploitation, unauthorised access, information disclosure.",
        "fixes": [
            "Close or firewall all ports that are not required.",
            "Use the principle of least exposure.",
            "Regularly audit open ports with Nmap.",
            "Segment the network to limit blast radius.",
        ],
    },
    "default credentials": {
        "description": (
            "Devices or services still using vendor-supplied default usernames and "
            "passwords are trivially compromised."
        ),
        "impact": "Full device compromise, pivot point into internal network.",
        "fixes": [
            "Change all default credentials immediately after deployment.",
            "Maintain an inventory of all network-connected devices.",
            "Use a credential management solution.",
        ],
    },
    "outdated software": {
        "description": (
            "Running unpatched or end-of-life software leaves known CVEs "
            "exploitable in your environment."
        ),
        "impact": "Exploitation of published CVEs, malware infection, data loss.",
        "fixes": [
            "Establish a regular patching cadence.",
            "Subscribe to vendor security advisories.",
            "Use a vulnerability scanner to track exposure.",
            "Decommission EOL software and replace with supported alternatives.",
        ],
    },
}

_TOOL_KB = {
    "nmap": {
        "description": "Nmap is an open-source network scanner used for host discovery and port/service enumeration.",
        "reading_tips": [
            "Open ports (state: open) are potential attack surfaces.",
            "Filtered ports may indicate a firewall or IDS.",
            "Service version info (-sV) helps identify vulnerable software versions.",
            "Script scan results (-sC / --script) highlight configuration weaknesses.",
        ],
        "next_steps": [
            "Research each open port/service for known CVEs.",
            "Close or firewall unnecessary ports.",
            "Upgrade outdated services flagged by version detection.",
        ],
    },
    "aircrack-ng": {
        "description": "Aircrack-ng is a suite of tools for auditing Wi-Fi network security.",
        "reading_tips": [
            "Captured handshakes indicate the passphrase can be tested offline.",
            "BSSID and ESSID help identify specific target networks.",
            "High packet injection rates confirm a suitable wireless interface.",
            "IV count (WEP) — the higher it is, the more data available to crack.",
        ],
        "next_steps": [
            "Use strong WPA2/WPA3 with a long, random passphrase.",
            "Disable WPS; it is vulnerable to brute-force (Reaver).",
            "Monitor for rogue access points with airodump-ng.",
            "Enable 802.11w (Management Frame Protection) where supported.",
        ],
    },
    "wireshark": {
        "description": "Wireshark is a network protocol analyser for capturing and inspecting packets.",
        "reading_tips": [
            "Unencrypted protocols (HTTP, FTP, Telnet) expose credentials in plain text.",
            "ARP spoofing shows duplicate IP-to-MAC mappings.",
            "Large numbers of SYN packets without ACK may indicate a SYN flood.",
            "DNS lookups for unusual or random domains may signal malware C2 traffic.",
        ],
        "next_steps": [
            "Replace clear-text protocols with encrypted alternatives (HTTPS, SFTP, SSH).",
            "Enable Dynamic ARP Inspection (DAI) on managed switches.",
            "Investigate hosts generating anomalous traffic volumes.",
        ],
    },
    "metasploit": {
        "description": "Metasploit is a penetration-testing framework for developing and executing exploits.",
        "reading_tips": [
            "A successful 'meterpreter' session means remote code execution was achieved.",
            "Post-exploitation modules can reveal further credentials and pivot paths.",
            "Check module rank (Excellent, Great, Good) for reliability estimates.",
        ],
        "next_steps": [
            "Document all successfully exploited vectors in your assessment report.",
            "Patch the vulnerabilities leveraged by each exploit.",
            "Re-test after remediation to confirm fixes are effective.",
        ],
    },
    "hydra": {
        "description": "Hydra is a fast and flexible online password-cracking tool.",
        "reading_tips": [
            "Successful login lines show the service, username, and password found.",
            "High error rates may mean rate-limiting or lockout policies are active.",
        ],
        "next_steps": [
            "Immediately change any compromised credentials.",
            "Implement account lockout and rate-limiting on all authentication endpoints.",
            "Enable MFA to mitigate credential-based attacks.",
        ],
    },
    "john": {
        "description": "John the Ripper is an offline password cracking and auditing tool.",
        "reading_tips": [
            "Cracked hashes are displayed in format  'password  (username)'.",
            "Hashes that resist cracking may still be weak; try more wordlists.",
        ],
        "next_steps": [
            "Force password resets for all cracked accounts.",
            "Increase the minimum password length and complexity requirements.",
            "Use bcrypt, scrypt, or Argon2 for password storage instead of MD5/SHA1.",
        ],
    },
    "sqlmap": {
        "description": "SQLMap automates the detection and exploitation of SQL injection flaws.",
        "reading_tips": [
            "'Parameter X appears to be injectable' confirms a vulnerable input.",
            "Database type and version reveal available attack techniques.",
            "Extracted data shows what information is accessible to an attacker.",
        ],
        "next_steps": [
            "Replace dynamic SQL with parameterised queries immediately.",
            "Apply a WAF rule to block common SQLi payloads.",
            "Audit all user-supplied inputs for injection points.",
        ],
    },
    "snort": {
        "description": "Snort is an open-source Network Intrusion Detection/Prevention System (NIDS/NIPS).",
        "reading_tips": [
            "Alert priority (1=high, 3=low) helps triage findings.",
            "Repeated alerts from the same source IP suggest a targeted attack.",
            "Rule SID numbers map to a public database of threat signatures.",
        ],
        "next_steps": [
            "Block source IPs generating high-priority alerts at the firewall.",
            "Tune rules to reduce false positives for your environment.",
            "Keep the rule set updated to cover the latest threat signatures.",
        ],
    },
    "airmon-ng": {
        "description": "airmon-ng enables or disables monitor mode on a wireless interface.",
        "reading_tips": [
            "Conflicting processes listed should be killed before capturing.",
            "Interface name change (e.g. wlan0 → wlan0mon) confirms monitor mode.",
        ],
        "next_steps": [
            "Proceed with airodump-ng to capture frames for analysis.",
            "Restore managed mode after testing with 'airmon-ng stop <iface>'.",
        ],
    },
    "airodump-ng": {
        "description": "airodump-ng captures raw 802.11 frames and displays nearby networks.",
        "reading_tips": [
            "PWR (signal strength) — higher absolute value means closer proximity.",
            "#Data column shows frames captured; useful for WEP IV collection.",
            "ENC column identifies encryption type (OPN, WEP, WPA, WPA2).",
        ],
        "next_steps": [
            "Target a specific BSSID with '--bssid' and '-c <channel>' flags.",
            "Capture a WPA handshake by waiting for or triggering a client reconnect.",
            "Save captures with '-w <prefix>' for offline analysis.",
        ],
    },
    "aireplay-ng": {
        "description": "aireplay-ng injects and replays 802.11 packets for wireless testing.",
        "reading_tips": [
            "Attack mode 0 (deauthentication) forces clients to reconnect, capturing handshakes.",
            "ACKs received confirm that packets are reaching the access point.",
        ],
        "next_steps": [
            "Combine with airodump-ng to capture the resulting WPA handshake.",
            "Use only in authorised lab environments — deauth attacks are detectable.",
        ],
    },
    "suricata": {
        "description": "Suricata is a high-performance open-source Network IDS/IPS/NSM engine.",
        "reading_tips": [
            "Alert severity levels (1=critical, 4=informational) guide triage priority.",
            "EVE JSON logs provide rich, structured event data for SIEM ingestion.",
            "Flow records help identify unusual connection volumes or long-lived sessions.",
            "Protocol anomalies detected (e.g. HTTP on non-standard ports) may indicate tunnelling.",
        ],
        "next_steps": [
            "Block source IPs generating critical alerts at the perimeter firewall.",
            "Feed EVE JSON into an ELK or SIEM stack for correlation.",
            "Keep rule sets (ET Open, ET Pro) regularly updated.",
            "Tune noisy rules to reduce false positives.",
        ],
    },
    "hashcat": {
        "description": "Hashcat is a GPU-accelerated offline password hash cracking tool.",
        "reading_tips": [
            "STATUS=Cracked means the plaintext password has been recovered.",
            "Hash mode (-m) must match the algorithm used (e.g. 0=MD5, 1000=NTLM, 1800=sha512crypt).",
            "Speed (H/s) depends heavily on GPU power and hash algorithm complexity.",
            "Potfile stores already-cracked hashes so sessions can resume without re-cracking.",
        ],
        "next_steps": [
            "Force password resets for all recovered accounts immediately.",
            "Switch to strong adaptive hashing (bcrypt, Argon2) to resist future attacks.",
            "Enforce minimum password length of 12+ characters and MFA.",
        ],
    },
    "openvas": {
        "description": "OpenVAS (Greenbone Vulnerability Manager) is an open-source comprehensive vulnerability scanner.",
        "reading_tips": [
            "Severity scores (CVSS) rank findings from Critical (9-10) down to Log.",
            "Quality of Detection (QoD) values show how confident OpenVAS is in each result.",
            "False positives are common — verify high-severity findings manually.",
        ],
        "next_steps": [
            "Prioritise Critical and High findings for immediate remediation.",
            "Apply vendor patches; re-scan after remediation to confirm fixes.",
            "Schedule regular authenticated scans for continuous coverage.",
        ],
    },
    "lynis": {
        "description": "Lynis is an open-source security auditing tool for Unix-based systems.",
        "reading_tips": [
            "Hardening Index score (0-100) gives a quick system security baseline.",
            "Warnings (!) require immediate attention; Suggestions are best-practice improvements.",
            "Plugin and test categories (Authentication, Networking, etc.) group related findings.",
        ],
        "next_steps": [
            "Address all Warnings before moving to Suggestions.",
            "Apply OS hardening guides (CIS Benchmarks) to improve the Hardening Index.",
            "Integrate Lynis into your CI/CD pipeline to catch regressions.",
        ],
    },
    "ossec": {
        "description": "OSSEC is an open-source Host-based Intrusion Detection System (HIDS).",
        "reading_tips": [
            "Alert level (1-15) indicates severity; levels 7+ typically require review.",
            "Rule IDs map to the OSSEC ruleset documentation for details.",
            "Repeated alerts from the same agent may indicate active compromise or misconfiguration.",
        ],
        "next_steps": [
            "Investigate agents generating repeated high-level alerts.",
            "Configure active-response rules to automatically block malicious IPs.",
            "Tune custom rules to reduce noise from legitimate administrative activity.",
        ],
    },
    "hash generator": {
        "description": (
            "A hash generator produces a fixed-length digest from input data using algorithms "
            "such as MD5, SHA1, SHA256, or SHA512. Hashes are one-way functions used for "
            "data integrity checks and (with strong algorithms) password storage."
        ),
        "reading_tips": [
            "MD5 and SHA1 are cryptographically broken — do NOT use them for security purposes.",
            "SHA256 and SHA512 are safe for data integrity checks.",
            "Identical inputs always produce identical hashes (deterministic).",
            "Even a 1-bit change in input produces a completely different hash (avalanche effect).",
        ],
        "next_steps": [
            "Use SHA256 or SHA512 for file integrity verification.",
            "Use bcrypt, scrypt, or Argon2 (not SHA256/SHA512) for password storage.",
            "Compare hashes before and after file transfer to detect tampering.",
        ],
    },
}

_WALKTHROUGH_KB = {
    "harden apache": textwrap.dedent("""\
        Apache Server Hardening – Step-by-Step
        =======================================
        1. Keep Apache and the OS fully patched.
        2. Disable unused modules:  a2dismod autoindex status userdir
        3. Hide server version:  ServerTokens Prod  /  ServerSignature Off
        4. Restrict access by IP or require authentication on sensitive paths.
        5. Enable HTTPS (Let's Encrypt / Certbot) and redirect HTTP → HTTPS.
        6. Set security headers: X-Frame-Options, X-Content-Type-Options,
           Content-Security-Policy, Strict-Transport-Security.
        7. Disable directory listing: Options -Indexes
        8. Run Apache as a dedicated low-privilege user (www-data).
        9. Configure mod_security (WAF) with the OWASP Core Rule Set.
       10. Regularly audit logs in /var/log/apache2/ for anomalies.
    """),
    "network scan": textwrap.dedent("""\
        Network Scan Walkthrough (Nmap)
        ================================
        1. Discovery ping sweep:   nmap -sn 192.168.1.0/24
        2. Full port scan on live hosts:  nmap -p- -T4 <target>
        3. Service & version detection:   nmap -sV -sC <target>
        4. OS fingerprinting:  nmap -O <target>
        5. Vulnerability scripts:  nmap --script vuln <target>
        6. Save results for reporting:  nmap -oX report.xml <target>
        7. Review each open port:
           - Identify the service and version.
           - Search CVE databases for known vulnerabilities.
           - Determine whether the service is necessary.
        8. Remediate: patch, firewall, or decommission exposed services.
    """),
    "wireless assessment": textwrap.dedent("""\
        Wireless Security Assessment – Step-by-Step
        =============================================
        1. Enable monitor mode:   airmon-ng start wlan0
        2. Survey the area:       airodump-ng wlan0mon
        3. Target a network:      airodump-ng --bssid <BSSID> -c <CH> -w capture wlan0mon
        4. Force a handshake (WPA): aireplay-ng -0 5 -a <BSSID> wlan0mon
        5. Crack the handshake:   aircrack-ng -w wordlist.txt capture*.cap
        6. Document findings and strength of passphrases discovered.
        7. Recommendations:
           - Use WPA3 or WPA2 with a 20+ character random passphrase.
           - Disable WPS.
           - Enable 802.11w (Management Frame Protection).
           - Segment Wi-Fi guests on a separate VLAN.
        8. Stop monitor mode:     airmon-ng stop wlan0mon
    """),
    "password audit": textwrap.dedent("""\
        Password Audit Walkthrough
        ==========================
        1. Export credential hashes (with authorisation): e.g. /etc/shadow on Linux.
        2. Identify hash types with:  hash-identifier  or  hashid
        3. Run John the Ripper:
              john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
        4. Run Hashcat for GPU acceleration:
              hashcat -m <mode> hashes.txt rockyou.txt
        5. Attempt online brute-force against live services with Hydra:
              hydra -L users.txt -P passwords.txt ssh://<target>
        6. Document all cracked credentials.
        7. Remediation:
           - Force password resets for compromised accounts.
           - Enforce a minimum length of 12+ characters.
           - Block previously breached passwords (HaveIBeenPwned list).
           - Enable MFA on all accounts.
    """),
    "malware investigation": textwrap.dedent("""\
        Malware Investigation – Step-by-Step
        =====================================
        1. Isolate the affected system from the network immediately.
        2. Take a memory dump for forensic analysis:
              LiME (Linux) / WinPmem (Windows)
        3. Capture volatile data: running processes, open connections, startup items.
              ps aux / netstat -anp / ss -tulnp
        4. Scan with an AV/anti-malware engine:
              clamscan -r / --log=scan.log (Linux)
        5. Examine suspicious files:
              sha256sum <file>  — compare against VirusTotal.
              strings <file>   — look for hardcoded IPs, URLs, commands.
              file <file>      — verify true file type.
        6. Check for persistence mechanisms:
              Crontabs, systemd units, registry run keys, startup folders.
        7. Analyse network traffic for C2 callbacks with Wireshark or tcpdump.
        8. Remediation:
           - Remove or quarantine the malicious file(s).
           - Patch the initial infection vector.
           - Re-image the system if full compromise is confirmed.
           - Change all credentials that may have been exposed.
        9. Document everything for the incident report.
    """),
    "vulnerability scan": textwrap.dedent("""\
        Vulnerability Scan Walkthrough
        ===============================
        1. Define scope and get written authorisation.
        2. Run an authenticated scan where possible for full coverage.
        3. Tools to use:
           - Nmap + NSE scripts for network-level vulnerabilities.
           - OpenVAS / Nessus for comprehensive host scanning.
           - Nikto for web server misconfigurations.
        4. Review findings by severity (Critical → High → Medium → Low).
        5. For each finding:
           a. Verify the vulnerability is genuine (eliminate false positives).
           b. Identify the root cause.
           c. Apply the vendor patch or recommended mitigation.
        6. Re-scan after remediation to confirm the fix.
        7. Document findings, evidence, and remediation steps in a formal report.
    """),
}

# ---------------------------------------------------------------------------
# AIExplainer class
# ---------------------------------------------------------------------------

class AIExplainer:
    """
    AI-powered explainer for cybersecurity assessments.

    When OpenAI is available and ``OPENAI_API_KEY`` is set the class delegates
    queries to the GPT model.  Otherwise it answers from the built-in
    knowledge base so users can work offline.

    Pass ``offline=True`` to force the built-in knowledge base even when
    ``OPENAI_API_KEY`` is set (e.g. when analysing sensitive log files).
    """

    MODEL = "gpt-4o-mini"

    def __init__(self, *, offline: bool = False):
        self._openai_client = None
        self._use_openai = False
        if offline:
            return
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if _OPENAI_AVAILABLE and api_key:
            try:
                if hasattr(_openai, "OpenAI"):
                    # openai >= 1.0.0 — instantiate the client
                    self._openai_client = _openai.OpenAI(api_key=api_key)
                else:
                    # openai < 1.0.0 — module-level api_key assignment
                    _openai.api_key = api_key
                    self._openai_client = _openai
                self._use_openai = True
            except Exception:
                self._use_openai = False

    def is_online_mode(self) -> bool:
        """Return True if OpenAI is configured and will be used for responses."""
        return self._use_openai

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain_vulnerability(self, vuln_name: str, context: str = "") -> str:
        """Explain a vulnerability and suggest fixes."""
        if self._use_openai:
            prompt = (
                f"You are a cybersecurity expert. Explain the vulnerability "
                f"'{vuln_name}' in plain English. Cover: what it is, why it "
                f"is dangerous, and at least four concrete remediation steps. "
                + (f"Additional context: {context}" if context else "")
            )
            result = self._query_openai(prompt)
            if result is not None:
                return result

        key = vuln_name.lower().strip()
        for kb_key, info in _VULNERABILITY_KB.items():
            if kb_key in key or key in kb_key:
                lines = [
                    f"\n🔍 Vulnerability: {vuln_name}",
                    f"\nDescription:\n  {info['description']}",
                    f"\nImpact:\n  {info['impact']}",
                    "\nRemediation Steps:",
                ]
                for i, fix in enumerate(info["fixes"], 1):
                    lines.append(f"  {i}. {fix}")
                return "\n".join(lines)

        return (
            f"\n⚠️  No built-in entry found for '{vuln_name}'.\n"
            "Tip: Set OPENAI_API_KEY for live AI explanations, or search the\n"
            "NVD database at https://nvd.nist.gov/vuln/search for CVE details."
        )

    def explain_tool_output(self, tool_name: str, output: str = "") -> str:
        """Explain the output of a security tool."""
        if self._use_openai:
            prompt = (
                f"You are a cybersecurity expert. The user has run '{tool_name}'. "
                f"Explain the following tool output in plain English, highlight "
                f"security concerns, and suggest next steps:\n\n{output}"
            )
            result = self._query_openai(prompt)
            if result is not None:
                return result

        key = tool_name.lower().strip()
        for kb_key, info in _TOOL_KB.items():
            if kb_key in key or key in kb_key:
                lines = [
                    f"\n🛠️  Tool: {tool_name}",
                    f"\nAbout:\n  {info['description']}",
                    "\nHow to read the results:",
                ]
                for tip in info["reading_tips"]:
                    lines.append(f"  • {tip}")
                lines.append("\nRecommended next steps:")
                for step in info["next_steps"]:
                    lines.append(f"  • {step}")
                return "\n".join(lines)

        return (
            f"\n⚠️  No built-in guidance found for tool '{tool_name}'.\n"
            "Tip: Set OPENAI_API_KEY for live AI explanations."
        )

    def walkthrough(self, topic: str) -> str:
        """Return a step-by-step walkthrough for a security topic."""
        if self._use_openai:
            prompt = (
                "You are a senior penetration tester. Provide a detailed, "
                f"numbered step-by-step walkthrough for: {topic}"
            )
            result = self._query_openai(prompt)
            if result is not None:
                return result

        key = topic.lower().strip()
        # Full-key substring match: the entire KB key (e.g. "harden apache") must
        # appear within the user topic.  This avoids partial-word false matches such
        # as "harden nginx" incorrectly matching the "harden apache" entry.
        for kb_key, content in _WALKTHROUGH_KB.items():
            if kb_key in key:
                return "\n" + content

        return (
            f"\n⚠️  No built-in walkthrough found for '{topic}'.\n"
            "Tip: Set OPENAI_API_KEY for live AI walkthroughs.\n"
            "Available built-in topics: "
            + ", ".join(_WALKTHROUGH_KB.keys())
        )

    def analyze_threat(self, log_input: str) -> str:
        """Analyse a log snippet or threat description and report findings."""
        if self._use_openai:
            prompt = (
                "You are a SOC analyst. Analyse the following log data or "
                "threat description, identify indicators of compromise, "
                "classify the threat level (Critical/High/Medium/Low), "
                "and suggest immediate response actions:\n\n"
                + log_input
            )
            result = self._query_openai(prompt)
            if result is not None:
                return result

        # Simple pattern-based heuristics
        findings = []
        lower = log_input.lower()

        patterns = {
            "sql injection attempt": ["' or '", "1=1", "union select", "drop table", "xp_cmdshell"],
            "brute-force / credential stuffing": ["failed password", "authentication failure",
                                                  "invalid login", "too many failed"],
            "port scan activity": ["nmap", "syn scan", "port scan", "stealth scan"],
            "malware / C2 traffic": ["cmd.exe", "powershell -enc", "base64", "wget http", "curl http"],
            "privilege escalation attempt": ["sudo su", "chmod 777", "passwd root", "/etc/shadow"],
        }

        for threat, indicators in patterns.items():
            if any(ind in lower for ind in indicators):
                findings.append(threat)

        if not findings:
            return (
                "\n✅ No obvious threat indicators found in the provided input.\n"
                "Consider a deeper forensic review or enable OpenAI for advanced analysis."
            )

        lines = ["\n🚨 Threat Analysis Results", "=" * 40]
        lines.append(f"Indicators detected: {len(findings)}")
        for f in findings:
            lines.append(f"  ⚠️  {f.title()}")
        lines.append("\nRecommended actions:")
        lines.append("  1. Isolate affected systems from the network.")
        lines.append("  2. Preserve logs and memory for forensic analysis.")
        lines.append("  3. Escalate to the incident response team.")
        lines.append("  4. Review and tighten firewall / IDS rules.")
        lines.append("  5. Reset credentials on affected accounts.")
        return "\n".join(lines)

    def recommend_tools(self, goal: str) -> str:
        """Recommend security tools and a methodology for a given goal."""
        if self._use_openai:
            prompt = (
                "You are a penetration testing expert. The user wants to: "
                f"'{goal}'. Recommend the best security tools (open-source and commercial) "
                "and outline a step-by-step methodology, including both offensive and "
                "defensive considerations."
            )
            result = self._query_openai(prompt)
            if result is not None:
                return result

        lower = goal.lower()
        lines = [f"\n🎯 Tool Recommendations for: {goal}", "=" * 50]

        if any(w in lower for w in ["network", "scan", "port", "host", "recon"]):
            lines += [
                "\nNetwork Reconnaissance:",
                "  • Nmap           – Port scanning and service detection",
                "  • Masscan        – Ultra-fast port scanner",
                "  • Wireshark      – Packet capture and analysis",
                "  • Snort/Suricata – Intrusion detection",
            ]
        if any(w in lower for w in ["wireless", "wifi", "wi-fi", "wpa", "wep"]):
            lines += [
                "\nWireless Security:",
                "  • airmon-ng      – Enable monitor mode",
                "  • airodump-ng    – Capture 802.11 frames",
                "  • aireplay-ng    – Packet injection / deauth",
                "  • aircrack-ng    – WPA/WEP passphrase cracking",
            ]
        if any(w in lower for w in ["password", "credential", "brute", "crack"]):
            lines += [
                "\nCredential Testing:",
                "  • John the Ripper – Offline password cracking",
                "  • Hashcat          – GPU-accelerated hash cracking",
                "  • Hydra            – Online brute-force",
                "  • Medusa           – Parallel login brute-forcer",
            ]
        if any(w in lower for w in ["web", "http", "sql", "injection", "xss", "app"]):
            lines += [
                "\nWeb Application Testing:",
                "  • SQLMap  – Automated SQL injection",
                "  • Nikto   – Web server misconfiguration scanner",
                "  • Burp Suite – HTTP proxy and web vulnerability scanner",
                "  • OWASP ZAP  – Open-source web app scanner",
            ]
        if any(w in lower for w in ["exploit", "pentest", "penetration", "post"]):
            lines += [
                "\nExploitation / Post-Exploitation:",
                "  • Metasploit Framework – Exploit development and execution",
                "  • Cobalt Strike        – Adversary simulation (commercial)",
                "  • Empire               – PowerShell post-exploitation",
            ]
        if any(w in lower for w in ["malware", "forensic", "incident", "reverse"]):
            lines += [
                "\nMalware Analysis / Forensics:",
                "  • ClamAV     – Open-source antivirus scanner",
                "  • Volatility – Memory forensics framework",
                "  • Autopsy    – Digital forensics platform",
                "  • REMnux      – Linux distribution for malware analysis",
                "  • Ghidra     – NSA reverse engineering tool (free)",
            ]
        if any(w in lower for w in ["harden", "defend", "protect", "monitor"]):
            lines += [
                "\nDefensive / Hardening:",
                "  • Fail2Ban   – Block repeated failed logins",
                "  • OpenVAS    – Vulnerability scanner (defensive)",
                "  • Lynis      – System security auditing",
                "  • OSSEC      – Host-based intrusion detection",
                "  • iptables / ufw – Firewall management",
            ]

        if len(lines) == 2:
            lines.append(
                "\nNo specific tool mapping found for your goal.\n"
                "Tip: Set OPENAI_API_KEY for context-aware recommendations."
            )

        return "\n".join(lines)

    def nlp_interface(self):
        """
        Interactive natural-language command interface.

        The user types plain-English requests; the AIExplainer maps them to
        tool recommendations, walkthroughs, or vulnerability explanations.
        """
        print("\n💬 AI NLP Interface")
        print("=" * 50)
        print("Ask anything about cybersecurity.  Type 'quit' to exit.")
        print("Examples:")
        print("  • Explain SQL injection")
        print("  • How do I harden Apache?")
        print("  • Recommend tools for wireless testing")
        print("  • Analyse this log: <paste log data>")

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting NLP interface.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Exiting NLP interface.")
                break

            response = self._route_nlp(user_input)
            print(response)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _route_nlp(self, text: str) -> str:
        """Route a natural language query to the appropriate method."""
        lower = text.lower()

        # Vulnerability explanation
        if any(w in lower for w in ["explain", "what is", "what's", "describe"]):
            vuln_keywords = [k for k in _VULNERABILITY_KB if k in lower]
            if vuln_keywords:
                return self.explain_vulnerability(vuln_keywords[0], context=text)
            tool_keywords = [k for k in _TOOL_KB if k in lower]
            if tool_keywords:
                return self.explain_tool_output(tool_keywords[0])
            # Generic walkthrough check
            for kb_key in _WALKTHROUGH_KB:
                if any(w in lower for w in kb_key.split()):
                    return self.walkthrough(text)

        # Recommend tools
        if any(w in lower for w in ["recommend", "suggest", "which tool", "best tool", "what tool"]):
            return self.recommend_tools(text)

        # Walkthrough requests
        if any(w in lower for w in ["how do i", "how to", "walkthrough", "steps", "guide"]):
            return self.walkthrough(text)

        # Threat/log analysis
        if any(w in lower for w in ["analyse", "analyze", "this log", "threat", "investigate"]):
            return self.analyze_threat(text)

        # Scan / recon shortcuts
        if any(w in lower for w in ["scan", "nmap", "enumerate"]):
            return self.recommend_tools("network scan") + "\n" + self.walkthrough("network scan")

        # Fallback — use OpenAI or generic advice
        if self._use_openai:
            return self._query_openai(
                "You are a cybersecurity expert assistant. "
                "Answer the following question helpfully and concisely:\n\n" + text
            )

        return (
            "\n🤖 I didn't recognise that request in my built-in knowledge base.\n"
            "Try phrasing like:\n"
            "  • 'Explain <vulnerability>'\n"
            "  • 'How to <topic>'\n"
            "  • 'Recommend tools for <goal>'\n"
            "Or set OPENAI_API_KEY for full natural-language support."
        )

    def _query_openai(self, prompt: str):
        """Send *prompt* to the OpenAI API and return the response text, or None on failure."""
        try:
            response = self._openai_client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert cybersecurity analyst and penetration "
                            "tester assisting users through security assessments. "
                            "Provide clear, accurate, and actionable guidance."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return "\n" + response.choices[0].message.content.strip()
        except Exception as exc:
            print(
                f"\n⚠️  OpenAI request failed ({type(exc).__name__}: {exc}). "
                "Using built-in knowledge base."
            )
            self._use_openai = False
            return None

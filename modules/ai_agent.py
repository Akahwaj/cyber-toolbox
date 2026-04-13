"""
AI Agent module integrating Claude (Anthropic) and OpenAI GPT models.
Requires: pip install anthropic openai
API Keys: Set ANTHROPIC_API_KEY and/or OPENAI_API_KEY environment variables.
"""
import os

# --- Graceful imports ---
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai as openai_lib
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

CLAUDE_MODEL = "claude-opus-4-5"
OPENAI_MODEL = "gpt-4o"

CYBERSECURITY_SYSTEM_PROMPT = """You are an expert cybersecurity AI assistant integrated into the Mythos Lab Cyber Toolbox. 
You help security professionals and learners with:
- Understanding cybersecurity concepts and tools
- Analyzing security findings and logs
- Teaching penetration testing methodologies
- Explaining vulnerabilities and mitigations
- Guiding through security assessments

Always emphasize ethical and legal use. Only assist with authorized testing activities.
Be concise, practical, and educational in your responses."""

class AIAgent:
    def __init__(self, prefer="claude"):
        self.prefer = prefer
        self._claude_client = None
        self._openai_client = None
        self._setup_clients()

    def _setup_clients(self):
        if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
            self._claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            self._openai_client = openai_lib.OpenAI(api_key=OPENAI_API_KEY)

    def _is_available(self):
        return self._claude_client is not None or self._openai_client is not None

    def _query_claude(self, prompt, system=None):
        if not self._claude_client:
            return None
        system = system or CYBERSECURITY_SYSTEM_PROMPT
        try:
            message = self._claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception:
            return "[Claude API request failed. Please try again.]"

    def _query_openai(self, prompt, system=None):
        if not self._openai_client:
            return None
        system = system or CYBERSECURITY_SYSTEM_PROMPT
        try:
            response = self._openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception:
            return "[OpenAI API request failed. Please try again.]"

    def query(self, prompt, system=None, use_both=False):
        """Query AI. Uses preferred provider, falls back to other if needed."""
        if not self._is_available():
            return self._offline_response(prompt)

        if use_both and self._claude_client and self._openai_client:
            claude_resp = self._query_claude(prompt, system)
            gpt_resp = self._query_openai(prompt, system)
            return f"--- Claude Analysis ---\n{claude_resp}\n\n--- GPT Analysis ---\n{gpt_resp}"

        if self.prefer == "claude" and self._claude_client:
            resp = self._query_claude(prompt, system)
        elif self._openai_client:
            resp = self._query_openai(prompt, system)
        elif self._claude_client:
            resp = self._query_claude(prompt, system)
        else:
            return self._offline_response(prompt)

        return resp

    def _offline_response(self, prompt):
        p = prompt.lower()
        if "nmap" in p:
            return ("Nmap is a powerful open-source network scanner.\n"
                    "Common usage: nmap -sV -p- <target>\n"
                    "  -sV: detect service versions\n  -p-: scan all 65535 ports\n"
                    "Always use only on networks you own or have written permission to test.")
        if "aircrack" in p or "wireless" in p or "wifi" in p:
            return ("Aircrack-ng is a wireless security toolkit.\n"
                    "Workflow: airmon-ng > airodump-ng > aireplay-ng > aircrack-ng\n"
                    "Only use on wireless networks you own or have explicit permission to test.")
        if "password" in p:
            return ("Strong passwords: 12+ chars, mix of upper/lower/digits/symbols.\n"
                    "Tools: John the Ripper, Hashcat (for authorized audits only).\n"
                    "Defense: use a password manager, enable MFA.")
        if "sql" in p or "injection" in p:
            return ("SQL Injection allows attackers to manipulate database queries.\n"
                    "Detection: SQLMap (authorized use only).\n"
                    "Prevention: parameterized queries, input validation, WAF.")
        if "apk" in p or "android" in p:
            return ("Android APK analysis: use MobSF, apktool, dex2jar.\n"
                    "Static analysis: decompile APK, review permissions and code.\n"
                    "Dynamic analysis: Frida, Drozer for runtime inspection.")
        if "ios" in p or "ipa" in p:
            return ("iOS IPA analysis: use MobSF, objection, Frida.\n"
                    "Runtime analysis: objection for runtime hooking.\n"
                    "Binary analysis: class-dump, Hopper, IDA Pro.")
        return ("AI API keys not configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.\n"
                "Run: export ANTHROPIC_API_KEY=your-key\n"
                "   or: export OPENAI_API_KEY=your-key\n"
                "Install: pip install anthropic openai")

    def chat(self):
        """Interactive chat mode."""
        print("\n💬 AI Chat Mode (type 'exit' to quit)")
        print("Using: " + self._get_provider_info())
        print("-" * 40)
        history = []
        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting chat mode.")
                break
            history.append({"role": "user", "content": user_input})
            if self._claude_client:
                try:
                    msg = self._claude_client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=2048,
                        system=CYBERSECURITY_SYSTEM_PROMPT,
                        messages=history,
                    )
                    response = msg.content[0].text
                except Exception:
                    response = self._query_openai(user_input) or "[Request failed. Please try again.]"
            elif self._openai_client:
                msgs = [{"role": "system", "content": CYBERSECURITY_SYSTEM_PROMPT}] + history
                try:
                    resp = self._openai_client.chat.completions.create(
                        model=OPENAI_MODEL, messages=msgs, max_tokens=2048
                    )
                    response = resp.choices[0].message.content
                except Exception:
                    response = "[Request failed. Please try again.]"
            else:
                response = self._offline_response(user_input)
            history.append({"role": "assistant", "content": response})
            print(f"\nAI: {response}")

    def teach_tool(self, tool_name):
        """Provide a comprehensive teaching session for a tool."""
        prompt = (f"Give a comprehensive beginner-friendly tutorial for '{tool_name}' "
                  f"as a cybersecurity tool. Include: what it is, why it matters, "
                  f"installation, basic usage with example commands, common use cases, "
                  f"and safety/legal considerations. Format with clear sections.")
        return self.query(prompt)

    def explain_topic(self, topic):
        """Explain a cybersecurity topic."""
        prompt = (f"Explain '{topic}' in the context of cybersecurity. Include: "
                  f"what it is, why it matters, how it works, examples, and how to "
                  f"defend against or use it appropriately.")
        return self.query(prompt)

    def analyze_log(self, log_content):
        """Analyze log content for security issues."""
        if len(log_content) > 8000:
            log_content = log_content[:8000] + "\n[... truncated ...]"
        prompt = (f"Analyze this log file for security issues:\n\n{log_content}\n\n"
                  f"Identify: suspicious patterns, attack indicators, anomalies, "
                  f"brute-force attempts, injection attempts, and recommended actions.")
        return self.query(prompt)

    def analyze_apk_info(self, app_name, permissions=None):
        """Analyze Android app security based on name and permissions."""
        perm_str = "\n".join(permissions) if permissions else "Not provided"
        prompt = (f"Perform a security assessment for Android app: {app_name}\n"
                  f"Permissions: {perm_str}\n\n"
                  f"Assess: dangerous permissions, privacy risks, security recommendations.")
        return self.query(prompt)

    def generate_report_insights(self, scan_results):
        """Generate AI insights for a security report."""
        prompt = (f"Based on these security scan results:\n\n{scan_results}\n\n"
                  f"Provide: executive summary, critical findings, risk prioritization "
                  f"(Critical/High/Medium/Low), recommended remediation steps, "
                  f"and next steps for the security team.")
        return self.query(prompt, use_both=True)

    def _get_provider_info(self):
        providers = []
        if self._claude_client:
            providers.append(f"Claude ({CLAUDE_MODEL})")
        if self._openai_client:
            providers.append(f"OpenAI GPT ({OPENAI_MODEL})")
        return ", ".join(providers) if providers else "Offline mode (no API keys set)"


def run():
    """Interactive AI assistant entry point."""
    print("\n🤖 AI Cybersecurity Assistant")
    print("==============================")
    agent = AIAgent()
    print(f"Provider: {agent._get_provider_info()}")
    print("\nOptions:")
    print("  1. Chat mode")
    print("  2. Teach a tool")
    print("  3. Explain a topic")
    print("  4. Analyze a log file")
    choice = input("\nSelect option: ").strip()
    if choice == "1":
        agent.chat()
    elif choice == "2":
        tool = input("Tool name (e.g., nmap, aircrack-ng, metasploit): ").strip()
        if tool:
            print(f"\n{agent.teach_tool(tool)}")
    elif choice == "3":
        topic = input("Topic (e.g., SQL injection, CVSS, zero-day): ").strip()
        if topic:
            print(f"\n{agent.explain_topic(topic)}")
    elif choice == "4":
        path = input("Log file path: ").strip()
        if path and os.path.isfile(path):
            with open(path, 'r', errors='replace') as f:
                content = f.read()
            print(f"\n{agent.analyze_log(content)}")
        else:
            print("File not found.")

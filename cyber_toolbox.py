"""
Mythos Lab Cybersecurity Toolbox
Advanced AI-powered cybersecurity platform integrating Claude and OpenAI agents.

Usage:
    python cyber_toolbox.py                    # Interactive menu
    python cyber_toolbox.py --chat             # AI chat mode
    python cyber_toolbox.py --teach <tool>     # AI teaching session
    python cyber_toolbox.py --explain <topic>  # Explain a topic
    python cyber_toolbox.py --analyze-logs <file>  # Analyze a log file
    python cyber_toolbox.py --enable-server    # Start web interface
    python cyber_toolbox.py --quick-start      # Guided setup
    python cyber_toolbox.py --report           # Generate security report

API Keys (optional, for AI features):
    export ANTHROPIC_API_KEY=your-claude-api-key
    export OPENAI_API_KEY=your-openai-api-key
"""

import sys
import os
import argparse
import subprocess

from modules.password import run as password_tool
from modules.hashing import run as hash_tool
from modules.ai_agent import AIAgent, run as ai_tool
from modules.network import run as network_tool
from modules.wireless import run as wireless_tool
from modules.mobile import run as mobile_tool
from modules.log_analysis import run as log_tool, analyze_file
from modules.reporting import run as report_tool
from modules.web_interface import run as web_tool
from modules.mythos import run as mythos_tool


AI_AGENT = None


def get_agent():
    global AI_AGENT
    if AI_AGENT is None:
        AI_AGENT = AIAgent()
    return AI_AGENT


MENU_ACTIONS = {
    "1": (password_tool, "Password Strength Checker"),
    "2": (hash_tool, "Hash Generator"),
    "3": (network_tool, "Network Security Tools"),
    "4": (wireless_tool, "Wireless Security Tools"),
    "5": (mobile_tool, "Mobile Security Tools (Android/iOS)"),
    "6": (log_tool, "Log Analysis"),
    "7": (report_tool, "Report Generator"),
    "8": (ai_tool, "AI Cybersecurity Assistant"),
    "9": (web_tool, "Web Interface (Mobile Access)"),
    "10": (mythos_tool, "Mythos Integration (Anthropic Claude SDK)"),
}


def pause():
    input("\nPress Enter to return to the menu...")


def run_teach_mode():
    print("\n🎓 AI-Powered Teach Mode")
    print("------------------------")
    print("Available topics:")
    print("  - password, hash, network, nmap, wireless, aircrack-ng")
    print("  - mobile, android, ios, apk, frida, metasploit")
    print("  - sql-injection, xss, buffer-overflow, cvss, zero-day")
    print("  - log-analysis, incident-response, forensics")
    print("  - (or enter any cybersecurity topic)")

    task = input("\nTeach me about: ").strip().lower()

    if not task:
        print("\nNo topic entered.")
        return

    agent = get_agent()
    print(f"\n📚 Teaching: {task}")
    print("-" * 40)
    print(agent.teach_tool(task))


def run_expert_mode():
    print("\n⚡ Expert Tools Mode")
    print("--------------------")
    print("Available tools:")
    for key, (_, desc) in MENU_ACTIONS.items():
        print(f"  {key}. {desc}")
    print("\nOr type a tool name directly:")
    print("  password, hash, network, wireless, mobile, logs, report, ai, web")

    task = input("\nExpert task: ").strip().lower()

    tool_map = {
        "password": password_tool,
        "hash": hash_tool,
        "network": network_tool,
        "wireless": wireless_tool,
        "mobile": mobile_tool,
        "logs": log_tool,
        "log": log_tool,
        "report": report_tool,
        "ai": ai_tool,
        "web": web_tool,
    }

    if task in tool_map:
        try:
            tool_map[task]()
        except Exception as e:
            print(f"\nError running tool: {e}")
    elif task.isdigit() and task in MENU_ACTIONS:
        try:
            MENU_ACTIONS[task][0]()
        except Exception as e:
            print(f"\nError: {e}")
    elif not task:
        print("\nNo task entered.")
    else:
        # Try AI assistance for unknown tools
        agent = get_agent()
        print(f"\n🤖 Looking up '{task}' with AI...")
        print(agent.teach_tool(task))


def run_scenario_mode():
    print("\n🎯 Scenario-Based Learning")
    print("--------------------------")
    scenarios = {
        "1": ("Network Reconnaissance", "Learn to map a network using Nmap and identify open services."),
        "2": ("Wireless Network Audit", "Step-by-step WPA2 handshake capture and analysis."),
        "3": ("Web Application Testing", "Test for SQL injection, XSS, and misconfigurations."),
        "4": ("Mobile App Analysis", "Static and dynamic analysis of an Android APK."),
        "5": ("Log Analysis & Incident Response", "Detect attacks in server log files."),
        "6": ("Password Security Audit", "Crack hashes and test password policies."),
    }
    for key, (name, desc) in scenarios.items():
        print(f"  {key}. {name}")
        print(f"     {desc}")

    choice = input("\nSelect scenario: ").strip()
    if choice in scenarios:
        name, desc = scenarios[choice]
        agent = get_agent()
        print(f"\n📖 Scenario: {name}")
        print("=" * 50)
        prompt = (f"Walk me through a complete hands-on scenario for: {name}. "
                  f"Description: {desc}. "
                  f"Include: objectives, tools needed, step-by-step instructions with commands, "
                  f"what to look for, and learning outcomes. Make it practical and educational.")
        print(agent.query(prompt))
    else:
        print("Invalid choice.")


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    for key, (_, description) in MENU_ACTIONS.items():
        print(f"{key}. {description}")
    print("11. Teach Mode (AI-guided)")
    print("12. Expert Tools")
    print("13. Scenario-Based Learning")
    print("0.  Exit")


def quick_start():
    print("\n🚀 Quick Start - Mythos Lab Cyber Toolbox")
    print("==========================================")
    print("\nStep 1: Checking Python environment...")
    print(f"  Python {sys.version}")

    print("\nStep 2: Checking optional AI dependencies...")
    try:
        import anthropic
        print(f"  ✓ anthropic (Claude / Mythos) installed [version {anthropic.__version__}]")
    except ImportError:
        print("  ✗ anthropic not installed (pip install anthropic>=0.40.0)")

    try:
        import openai
        print("  ✓ openai installed")
    except ImportError:
        print("  ✗ openai not installed (pip install openai)")

    try:
        import flask
        print("  ✓ flask installed (web interface available)")
    except ImportError:
        print("  ✗ flask not installed (pip install flask)")

    print("\nStep 3: Checking API keys...")
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  ✓ ANTHROPIC_API_KEY is set")
    else:
        print("  ✗ ANTHROPIC_API_KEY not set")
        print("    Set with: export ANTHROPIC_API_KEY=your-key")

    if os.environ.get("OPENAI_API_KEY"):
        print("  ✓ OPENAI_API_KEY is set")
    else:
        print("  ✗ OPENAI_API_KEY not set")
        print("    Set with: export OPENAI_API_KEY=your-key")

    print("\nStep 4: Checking security tools...")
    tools = ["nmap", "aircrack-ng", "adb", "frida", "apktool", "wireshark"]
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, timeout=3)
            print(f"  ✓ {tool}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"  ✗ {tool} (not installed)")

    print("\n✅ Quick Start Complete!")
    print("\nRecommended next steps:")
    print("  1. Install Mythos/AI packages: pip install anthropic>=0.40.0 openai flask")
    print("  2. Set API keys in your environment")
    print("  3. Try the Mythos integration: python cyber_toolbox.py  → option 10")
    print("  4. Try the AI Chat: python cyber_toolbox.py --chat")
    print("  5. Read USAGE_GUIDE.txt for full documentation")


def main():
    parser = argparse.ArgumentParser(
        description="Mythos Lab Cybersecurity Toolbox - Advanced AI-powered security platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cyber_toolbox.py                          # Interactive menu
  python cyber_toolbox.py --chat                   # AI chat mode
  python cyber_toolbox.py --teach nmap             # Learn about nmap
  python cyber_toolbox.py --explain "SQL injection" # Explain a topic
  python cyber_toolbox.py --analyze-logs server.log # Analyze log file
  python cyber_toolbox.py --enable-server           # Start web interface
  python cyber_toolbox.py --quick-start             # Setup check
  python cyber_toolbox.py --report                  # Generate report
        """
    )
    parser.add_argument("--chat", action="store_true", help="Start AI chat mode")
    parser.add_argument("--teach", metavar="TOOL", help="AI teaching session for a tool/topic")
    parser.add_argument("--ai-teach", metavar="TOPIC", dest="ai_teach", help="AI-guided teaching session")
    parser.add_argument("--explain", metavar="TOPIC", help="Explain a cybersecurity topic")
    parser.add_argument("--analyze-logs", metavar="FILE", dest="analyze_logs", help="Analyze a log file")
    parser.add_argument("--enable-server", action="store_true", dest="enable_server",
                        help="Start web interface for mobile access")
    parser.add_argument("--quick-start", action="store_true", dest="quick_start", help="Run quick start setup check")
    parser.add_argument("--report", action="store_true", help="Generate a security report")
    parser.add_argument("--scenario", action="store_true", help="Start scenario-based learning")

    args = parser.parse_args()

    if args.quick_start:
        quick_start()
        return

    if args.chat:
        agent = get_agent()
        agent.chat()
        return

    if args.teach or args.ai_teach:
        topic = args.teach or args.ai_teach
        agent = get_agent()
        print(f"\n📚 AI Teaching: {topic}")
        print("=" * 50)
        print(agent.teach_tool(topic))
        return

    if args.explain:
        agent = get_agent()
        print(f"\n💡 Explaining: {args.explain}")
        print("=" * 50)
        print(agent.explain_topic(args.explain))
        return

    if args.analyze_logs:
        agent = get_agent()
        analyze_file(args.analyze_logs, ai_agent=agent)
        return

    if args.enable_server:
        web_tool()
        return

    if args.report:
        agent = get_agent()
        report_tool(ai_agent=agent)
        return

    if args.scenario:
        run_scenario_mode()
        return

    # Interactive menu
    while True:
        show_menu()
        choice = input("\nChoose an option: ").strip()

        if choice in MENU_ACTIONS:
            try:
                if choice == "6":  # Log analysis - pass AI agent
                    log_tool(ai_agent=get_agent())
                elif choice == "7":  # Report - pass AI agent
                    report_tool(ai_agent=get_agent())
                else:
                    MENU_ACTIONS[choice][0]()
            except Exception as e:
                print(f"\nAn error occurred: {e}")
            pause()

        elif choice == "11":
            run_teach_mode()
            pause()

        elif choice == "12":
            run_expert_mode()
            pause()

        elif choice == "13":
            run_scenario_mode()
            pause()

        elif choice == "0":
            while True:
                confirm = input("\nAre you sure you want to exit? (yes/no): ").strip().lower()
                if confirm in ("yes", "y"):
                    print("\nGoodbye. Stay legal and stay sharp.")
                    return
                if confirm in ("no", "n"):
                    print("\nReturning to menu.")
                    break
                print("\nInvalid input. Please answer yes or no.")

        elif not choice:
            print("\nNo option selected.")
            pause()

        else:
            print(f"\nInvalid choice '{choice}'. Please select from the menu.")
            pause()


if __name__ == "__main__":
    main()
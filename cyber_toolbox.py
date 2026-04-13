"""
cyber_toolbox.py – Mythos Lab Cybersecurity Toolbox

Interactive menu-driven toolkit with an integrated AI Explainer that can
walk users through vulnerabilities, tool outputs, and security assessments.

Usage (interactive):
    python cyber_toolbox.py

Usage (command-line flags):
    python cyber_toolbox.py --ai-explain --vulnerability "SQL Injection"
    python cyber_toolbox.py --ai-explain --vulnerability "CVE-2021-44228" --context "Log4Shell"
    python cyber_toolbox.py --ai-explain --tool nmap --output "Open ports: 22, 80, 443"
    python cyber_toolbox.py --ai-walkthrough "Explain how to harden an Apache server."
    python cyber_toolbox.py --recommend-tools --goal "wireless penetration testing"
    python cyber_toolbox.py --detect-threats --input-file logs.txt
    python cyber_toolbox.py --nlp-interface
"""

import argparse
import sys

from modules.password import run as password_tool
from modules.hashing import run as hash_tool
from modules.ai_explainer import AIExplainer


MENU_ACTIONS = {
    "1": (password_tool, "Password Strength Checker"),
    "2": (hash_tool, "Hash Generator"),
}


def pause():
    input("\nPress Enter to return to the menu...")


# ---------------------------------------------------------------------------
# Teach Mode
# ---------------------------------------------------------------------------

def run_teach_mode(ai: AIExplainer):
    print("\n🎓 Teach Mode")
    print("Type what you want to do:")
    print("- password")
    print("- hash")
    print("- wireless")
    print("- vulnerability <name>")
    print("- tool <name>")

    task = input("\nTeach Mode task: ").strip().lower()

    if "password" in task:
        print("\n[Teach Mode]")
        print("This tool checks password strength and explains why it is strong or weak.")
        print(ai.explain_vulnerability("weak password"))
        try:
            password_tool()
        except Exception as e:
            print(f"\nAn error occurred while running the password tool: {e}")

    elif "hash" in task:
        print("\n[Teach Mode]")
        print("This tool generates hashes such as MD5, SHA1, and SHA256 for learning and verification.")
        try:
            hash_tool()
        except Exception as e:
            print(f"\nAn error occurred while running the hash tool: {e}")

    elif "wireless" in task or "wifi" in task:
        print("\n[Teach Mode]")
        print(ai.walkthrough("wireless assessment"))

    elif task.startswith("vulnerability"):
        parts = task.split(None, 1)
        vuln = parts[1] if len(parts) > 1 else ""
        if vuln:
            print(ai.explain_vulnerability(vuln))
        else:
            print("\nPlease specify a vulnerability name, e.g.: vulnerability sql injection")

    elif task.startswith("tool"):
        parts = task.split(None, 1)
        tool_name = parts[1] if len(parts) > 1 else ""
        if tool_name:
            print(ai.explain_tool_output(tool_name))
        else:
            print("\nPlease specify a tool name, e.g.: tool nmap")

    elif not task:
        print("\nNo task entered.")

    else:
        print(ai.walkthrough(task))


# ---------------------------------------------------------------------------
# Expert Mode
# ---------------------------------------------------------------------------

def run_expert_mode(ai: AIExplainer):
    print("\n⚡ Expert Tools")
    print("Type the exact tool you want:")
    print("- password")
    print("- hash")
    print("- wireless")
    print("- nmap / wireshark / metasploit / hydra / john / sqlmap / snort")
    print("- airmon-ng / airodump-ng / aireplay-ng / aircrack-ng")

    task = input("\nExpert task: ").strip().lower()

    if task == "password":
        try:
            password_tool()
        except Exception as e:
            print(f"\nAn error occurred while running the password tool: {e}")

    elif task == "hash":
        try:
            hash_tool()
        except Exception as e:
            print(f"\nAn error occurred while running the hash tool: {e}")

    elif task in ("wireless", "airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng"):
        tool = task if task != "wireless" else "aircrack-ng"
        print(ai.explain_tool_output(tool))
        if task == "wireless":
            print(ai.walkthrough("wireless assessment"))

    elif task in ("nmap", "wireshark", "metasploit", "hydra", "john", "sqlmap", "snort"):
        print(ai.explain_tool_output(task))

    elif not task:
        print("\nNo task entered.")

    else:
        print(ai.explain_tool_output(task))


# ---------------------------------------------------------------------------
# AI Explainer Mode (interactive menu option)
# ---------------------------------------------------------------------------

def run_ai_mode(ai: AIExplainer):
    print("\n🤖 AI Security Assistant")
    print("=" * 50)
    print("1. Explain a vulnerability")
    print("2. Explain a tool")
    print("3. Step-by-step walkthrough")
    print("4. Recommend tools for a goal")
    print("5. Analyse a threat / log")
    print("6. NLP chat interface")
    print("7. Back to main menu")

    choice = input("\nChoose an option (1-7): ").strip()

    if choice == "1":
        vuln = input("Vulnerability name or CVE: ").strip()
        context = input("Additional context (optional): ").strip()
        print(ai.explain_vulnerability(vuln, context))

    elif choice == "2":
        tool_name = input("Tool name (e.g. nmap, aircrack-ng): ").strip()
        output = input("Paste tool output to analyse (optional – press Enter to skip):\n").strip()
        print(ai.explain_tool_output(tool_name, output))

    elif choice == "3":
        topic = input("Topic (e.g. 'wireless assessment', 'harden apache'): ").strip()
        print(ai.walkthrough(topic))

    elif choice == "4":
        goal = input("Goal (e.g. 'network recon', 'password audit'): ").strip()
        print(ai.recommend_tools(goal))

    elif choice == "5":
        print("Paste log data or describe the threat (end with an empty line):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        print(ai.analyze_threat("\n".join(lines)))

    elif choice == "6":
        ai.nlp_interface()

    elif choice == "7":
        return

    else:
        print("\nInvalid choice.")


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    for key, (_, description) in MENU_ACTIONS.items():
        print(f"{key}. {description}")
    print("3. Teach Mode")
    print("4. Expert Tools")
    print("5. 🤖 AI Security Assistant")
    print("6. Exit")


def main():
    # -----------------------------------------------------------------------
    # CLI argument handling
    # -----------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Mythos Lab Cybersecurity Toolbox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cyber_toolbox.py\n"
            "  python cyber_toolbox.py --ai-explain --vulnerability 'SQL Injection'\n"
            "  python cyber_toolbox.py --ai-explain --tool nmap --output 'Open ports: 22,80'\n"
            "  python cyber_toolbox.py --ai-walkthrough 'harden apache'\n"
            "  python cyber_toolbox.py --recommend-tools --goal 'wireless pentest'\n"
            "  python cyber_toolbox.py --detect-threats --input-file logs.txt\n"
            "  python cyber_toolbox.py --nlp-interface\n"
        ),
    )
    parser.add_argument(
        "--ai-explain",
        action="store_true",
        help="Use the AI explainer on a vulnerability or tool.",
    )
    parser.add_argument(
        "--vulnerability",
        metavar="NAME",
        help="Vulnerability name or CVE ID to explain (use with --ai-explain).",
    )
    parser.add_argument(
        "--context",
        metavar="TEXT",
        help="Additional context for the AI explainer.",
        default="",
    )
    parser.add_argument(
        "--tool",
        metavar="NAME",
        help="Security tool name to explain (use with --ai-explain).",
    )
    parser.add_argument(
        "--output",
        metavar="TEXT",
        help="Tool output to analyse (use with --tool).",
        default="",
    )
    parser.add_argument(
        "--ai-walkthrough",
        metavar="TOPIC",
        help="Print a step-by-step walkthrough for the given topic.",
    )
    parser.add_argument(
        "--recommend-tools",
        action="store_true",
        help="Recommend tools for a security goal.",
    )
    parser.add_argument(
        "--goal",
        metavar="GOAL",
        help="Security goal to get tool recommendations for.",
        default="",
    )
    parser.add_argument(
        "--detect-threats",
        action="store_true",
        help="Analyse a log file for threat indicators.",
    )
    parser.add_argument(
        "--input-file",
        metavar="FILE",
        help="Path to a log file for threat analysis (use with --detect-threats).",
    )
    parser.add_argument(
        "--nlp-interface",
        action="store_true",
        help="Start the interactive NLP chat interface.",
    )

    args = parser.parse_args()
    ai = AIExplainer()

    # Handle non-interactive CLI flags
    if args.ai_explain:
        if args.vulnerability:
            print(ai.explain_vulnerability(args.vulnerability, args.context))
            sys.exit(0)
        if args.tool:
            print(ai.explain_tool_output(args.tool, args.output))
            sys.exit(0)
        parser.error("--ai-explain requires --vulnerability NAME or --tool NAME")

    if args.ai_walkthrough:
        print(ai.walkthrough(args.ai_walkthrough))
        sys.exit(0)

    if args.recommend_tools:
        goal = args.goal or input("Enter your security goal: ").strip()
        print(ai.recommend_tools(goal))
        sys.exit(0)

    if args.detect_threats:
        if args.input_file:
            try:
                with open(args.input_file, encoding="utf-8", errors="replace") as fh:
                    log_data = fh.read()
            except OSError as exc:
                print(f"Error reading file {args.input_file}: {exc}")
                sys.exit(1)
        else:
            print("Paste log data (end with an empty line):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            log_data = "\n".join(lines)
        print(ai.analyze_threat(log_data))
        sys.exit(0)

    if args.nlp_interface:
        ai.nlp_interface()
        sys.exit(0)

    # -----------------------------------------------------------------------
    # Interactive menu loop
    # -----------------------------------------------------------------------
    while True:
        show_menu()
        choice = input("\nChoose an option (1-6): ").strip()

        if choice in MENU_ACTIONS:
            try:
                MENU_ACTIONS[choice][0]()
            except Exception as e:
                print(f"\nAn error occurred while running the tool: {e}")
            pause()

        elif choice == "3":
            run_teach_mode(ai)
            pause()

        elif choice == "4":
            run_expert_mode(ai)
            pause()

        elif choice == "5":
            run_ai_mode(ai)
            pause()

        elif choice == "6":
            while True:
                confirm = input("\nAre you sure you want to exit? (yes/no): ").strip().lower()

                if confirm in ["yes", "y"]:
                    print("\nGoodbye. Stay legal and stay sharp.")
                    return
                if confirm in ["no", "n"]:
                    print("\nReturning to menu.")
                    break
                print("\nInvalid input. Please answer yes or no.")
            pause()

        elif not choice:
            print("\nNo option selected. Please choose a number between 1 and 6.")
            pause()

        else:
            print("\nInvalid choice. Please enter a number between 1 and 6.")
            pause()


if __name__ == "__main__":
    main()
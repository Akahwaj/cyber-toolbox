import argparse
import sys

from modules.password import run as password_tool
from modules.hashing import run as hash_tool
from modules.ai_agent import (
    teach_tool,
    answer_question,
    run_walkthrough,
    contextual_explain,
    run_agent_menu,
)


MENU_ACTIONS = {
    "1": (password_tool, "Password Strength Checker"),
    "2": (hash_tool, "Hash Generator"),
}


def pause():
    input("\nPress Enter to return to the menu...")


def run_teach_mode():
    print("\n🎓 Teach Mode")
    print("Type the name of a tool or topic you want to learn about.")
    print("Examples: password, hash, nmap, aircrack-ng, metasploit, wireshark")

    task = input("\nTeach Mode task: ").strip().lower()

    if "password" in task:
        print("\n[Teach Mode]")
        print("This tool checks password strength and explains why it is strong or weak.")
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

    elif task:
        # Delegate to the AI agent for any other tool name
        teach_tool(task)

    else:
        print("\nNo task entered.")


def run_expert_mode():
    print("\n⚡ Expert Tools")
    print("Type the exact tool you want:")
    print("- password")
    print("- hash")
    print("- wireless (aircrack-ng suite)")

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

    elif task in ("wireless", "wifi", "aircrack-ng", "aircrack"):
        teach_tool("aircrack-ng")

    elif not task:
        print("\nNo task entered.")

    else:
        print(f"\nNo direct module found for '{task}'. Checking AI knowledge base…")
        teach_tool(task)


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    for key, (_, description) in MENU_ACTIONS.items():
        print(f"{key}. {description}")
    print("3. Teach Mode")
    print("4. Expert Tools")
    print("5. AI Security Agent")
    print("6. Exit")


def main():
    parser = argparse.ArgumentParser(
        description="Mythos Lab Cybersecurity Toolbox with AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cyber_toolbox.py --teach-tool nmap
  python cyber_toolbox.py --teach-tool aircrack-ng
  python cyber_toolbox.py --qa "How do I crack WPA passwords?"
  python cyber_toolbox.py --qa "What does a CVSS score of 7.5 mean?"
  python cyber_toolbox.py --walkthrough "linux privilege escalation"
  python cyber_toolbox.py --walkthrough "web application owasp top 10"
  python cyber_toolbox.py --contextual-explain --input logs/access.log
        """,
    )

    parser.add_argument(
        "--teach-tool",
        metavar="TOOL",
        help="Teach about a specific security tool (e.g. nmap, aircrack-ng, metasploit)",
    )
    parser.add_argument(
        "--qa",
        metavar="QUESTION",
        help="Ask the AI agent a security question",
    )
    parser.add_argument(
        "--walkthrough",
        metavar="SCENARIO",
        help="Run an interactive walkthrough for a pentesting scenario",
    )
    parser.add_argument(
        "--contextual-explain",
        action="store_true",
        help="Analyse a log or tool output file for suspicious patterns",
    )
    parser.add_argument(
        "--input",
        metavar="FILE",
        help="Path to the file to analyse (used with --contextual-explain)",
    )

    # If no arguments were given, fall through to the interactive menu
    if len(sys.argv) == 1:
        _run_interactive()
        return

    args = parser.parse_args()

    if args.teach_tool:
        teach_tool(args.teach_tool)

    elif args.qa:
        answer_question(args.qa)

    elif args.walkthrough:
        run_walkthrough(args.walkthrough)

    elif args.contextual_explain:
        if not args.input:
            parser.error("--contextual-explain requires --input <FILE>")
        contextual_explain(args.input)

    else:
        parser.print_help()


def _run_interactive():
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
            run_teach_mode()
            pause()

        elif choice == "4":
            run_expert_mode()
            pause()

        elif choice == "5":
            run_agent_menu()

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
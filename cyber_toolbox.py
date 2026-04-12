from modules.password import run as password_tool
from modules.hashing import run as hash_tool


MENU_ACTIONS = {
    "1": (password_tool, "Password Strength Checker"),
    "2": (hash_tool, "Hash Generator"),
}


def pause():
    input("\nPress Enter to return to the menu...")


def run_teach_mode():
    print("\n🎓 Teach Mode")
    print("Type what you want to do:")
    print("- password")
    print("- hash")
    print("- wireless")

    task = input("\nTeach Mode task: ").strip().lower()

    if "password" in task:
        print("\n[Teach Mode]")
        print("This tool checks password strength and explains why it is strong or weak.")
        password_tool()

    elif "hash" in task:
        print("\n[Teach Mode]")
        print("This tool generates hashes (MD5, SHA1, SHA256).")
        hash_tool()

    elif "wireless" in task or "wifi" in task:
        print("\n[Teach Mode]")
        print("Wireless Toolkit will be connected here soon.")

    else:
        print("\nNo matching teach-mode tool found.")


def run_expert_mode():
    print("\n⚡ Expert Tools")
    print("Type exact tool:")
    print("- password")
    print("- hash")
    print("- wireless")

    task = input("\nExpert task: ").strip().lower()

    if task == "password":
        password_tool()

    elif task == "hash":
        hash_tool()

    elif task == "wireless":
        print("\nWireless module not connected yet.")

    else:
        print("\nUnknown expert tool.")


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    for key, (_, description) in MENU_ACTIONS.items():
        print(f"{key}. {description}")
    print("3. Teach Mode")
    print("4. Expert Tools")
    print("5. Exit")


def main():
    while True:
        show_menu()
        choice = input("\nChoose an option (1-5): ").strip()

        if choice in MENU_ACTIONS:
            MENU_ACTIONS[choice][0]()
            pause()

        elif choice == "3":
            run_teach_mode()
            pause()

        elif choice == "4":
            run_expert_mode()
            pause()

        elif choice == "5":
            print("\nGoodbye. Stay legal and stay sharp.")
            return

        else:
            print("\nInvalid choice.")
            pause()


if __name__ == "__main__":
    main()
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
        print("Wireless Toolkit will be connected here as part of the group.")
        print("Module not connected yet.")

    elif not task:
        print("\nNo task entered.")

    else:
        print("\nNo matching teach-mode tool found.")


def run_expert_mode():
    print("\n⚡ Expert Tools")
    print("Type the exact tool you want:")
    print("- password")
    print("- hash")
    print("- wireless")

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

    elif task == "wireless":
        print("\nWireless expert module not connected yet.")

    elif not task:
        print("\nNo task entered.")

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
            print("\nNo option selected. Please choose a number between 1 and 5.")
            pause()

        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")
            pause()


if __name__ == "__main__":
    main()
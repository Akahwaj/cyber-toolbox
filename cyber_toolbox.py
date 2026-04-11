from modules.password import run as password_tool
from modules.hashing import run as hash_tool


MENU_ACTIONS = {
    "1": (password_tool, "Password Strength Checker"),
    "2": (hash_tool, "Hash Generator"),
}


def pause():
    input("\nPress Enter to return to the menu...")


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    for key, (_, description) in MENU_ACTIONS.items():
        print(f"{key}. {description}")
    print("3. Exit")


def main():
    while True:
        show_menu()
        choice = input("\nChoose an option (1-3): ").strip()

        if choice in MENU_ACTIONS:
            try:
                MENU_ACTIONS[choice][0]()
            except Exception as e:
                print(f"\nAn error occurred while running the tool: {e}")
            pause()

        elif choice == "3":
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
            print("\nNo option selected. Please choose a number between 1 and 3.")
            pause()

        else:
            print("\nInvalid choice. Please enter a number between 1 and 3.")
            pause()


if __name__ == "__main__":
    main()
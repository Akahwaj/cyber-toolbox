from modules.password import run as password_tool
from modules.hashing import run as hash_tool


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    print("1. Password Strength Checker")
    print("2. Hash Generator")
    print("3. Exit")


def main():
    while True:
        show_menu()
        choice = input("\nChoose an option (1-3): ").strip()

        if choice == "1":
            password_tool()
        elif choice == "2":
            hash_tool()
        elif choice == "3":
            print("\nGoodbye. Stay legal and stay sharp.")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()

import hashlib
import ipaddress
import os
import re
import socket


COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3389: "RDP",
}


def password_strength_checker():
    print("\n🛡️ Password Strength Checker")
    print("--------------------------------")

    password = input("Enter a password to evaluate: ").strip()
    score = 0
    feedback = []

    checks = [
        (len(password) >= 12, "Use at least 12 characters."),
        (re.search(r"[A-Z]", password), "Add at least one uppercase letter."),
        (re.search(r"[a-z]", password), "Add at least one lowercase letter."),
        (re.search(r"\d", password), "Add at least one number."),
        (re.search(r'[!@#$%^&*(),.?":{}|<>]', password), "Add at least one special character."),
    ]

    for passed, message in checks:
        if passed:
            score += 1
        else:
            feedback.append(message)

    if score == 5:
        strength = "Strong"
    elif score >= 3:
        strength = "Moderate"
    else:
        strength = "Weak"

    print(f"\nPassword Strength: {strength}")

    if feedback:
        print("\nSuggestions:")
        for item in feedback:
            print(f"- {item}")
    else:
        print("Your password meets all recommended checks.")


def hash_generator():
    print("\n🔐 Hash Generator")
    print("--------------------------------")

    text = input("Enter text to hash: ").strip()
    data = text.encode("utf-8")

    print("\nResults:")
    print(f"MD5:    {hashlib.md5(data).hexdigest()}")
    print(f"SHA1:   {hashlib.sha1(data).hexdigest()}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")


def scan_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex((host, port)) == 0
    except OSError:
        return False


def lab_port_scanner():
    print("\n🌐 Lab Port Scanner")
    print("--------------------------------")
    print("Use only on systems you own or are authorized to test.\n")

    host = input("Enter a host (example: 127.0.0.1): ").strip()

    if not host:
        print("No host entered.")
        return

    print(f"\nScanning common ports on {host}...\n")
    open_ports = []

    for port, service in COMMON_PORTS.items():
        if scan_port(host, port):
            open_ports.append((port, service))
            print(f"[OPEN]   Port {port} ({service})")
        else:
            print(f"[CLOSED] Port {port} ({service})")

    print("\nScan complete.")

    if open_ports:
        print("\nOpen ports found:")
        for port, service in open_ports:
            print(f"- {port} ({service})")
    else:
        print("No common open ports were found.")


def subnet_helper():
    print("\n📡 Subnet Helper")
    print("--------------------------------")

    cidr = input("Enter a network in CIDR format (example: 192.168.1.0/24): ").strip()

    try:
        network = ipaddress.ip_network(cidr, strict=False)
        print(f"\nNetwork Address:   {network.network_address}")
        print(f"Broadcast Address: {network.broadcast_address}")
        print(f"Netmask:           {network.netmask}")
        print(f"Total Addresses:   {network.num_addresses}")
    except ValueError:
        print("Invalid CIDR format.")


def sha256_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_integrity_checker():
    print("\n📁 File Integrity Checker")
    print("--------------------------------")

    file_path = input("Enter the full path to a file: ").strip()

    if not os.path.isfile(file_path):
        print("File not found.")
        return

    try:
        sha256_hash = sha256_file(file_path)
        print("\nFile SHA256:")
        print(sha256_hash)
        print("\nSave this hash and compare it later to check if the file changes.")
    except OSError as error:
        print(f"Error: {error}")


def show_menu():
    print("\n🧰 Mythos Lab Cybersecurity Toolbox")
    print("====================================")
    print("1. Password Strength Checker")
    print("2. Hash Generator")
    print("3. Lab Port Scanner")
    print("4. Subnet Helper")
    print("5. File Integrity Checker")
    print("6. Exit")


def main():
    while True:
        show_menu()
        choice = input("\nChoose an option (1-6): ").strip()

        if choice == "1":
            password_strength_checker()
        elif choice == "2":
            hash_generator()
        elif choice == "3":
            lab_port_scanner()
        elif choice == "4":
            subnet_helper()
        elif choice == "5":
            file_integrity_checker()
        elif choice == "6":
            print("\nGoodbye. Stay legal and stay sharp.")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main()

import socket
import hashlib
import re
import ipaddress


def password_strength_checker():
    print("\n🛡️ Password Strength Checker")
    print("--------------------------------")

    password = input("Enter a password to evaluate: ").strip()
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 1
    else:
        feedback.append("Use at least 12 characters.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add at least one uppercase letter.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add at least one lowercase letter.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add at least one number.")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add at least one special character.")

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

    print("\nResults:")
    print(f"MD5:    {hashlib.md5(text.encode()).hexdigest()}")
    print(f"SHA1:   {hashlib.sha1(text.encode()).hexdigest()}")
    print(f"SHA256: {hashlib.sha256(text.encode()).hexdigest()}")


def scan_port(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def lab_port_scanner():
    print("\n🌐 Lab Port Scanner")
    print("--------------------------------")
    print("Use only on systems you own or are authorized to test.\n")

    host = input("Enter a host (example: 127.0.0.1): ").strip()

    common_ports = {
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
        3389: "RDP"
    }

    print(f"\nScanning common ports on {host}...\n")
    open_ports = []

    for port, service in common_ports.items():
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


def main():
    while True:
        print("\n🧰 Mythos Lab Cybersecurity Toolbox")
        print("====================================")
        print("1. Password Strength Checker")
        print("2. Hash Generator")
        print("3. Lab Port Scanner")
        print("4. Subnet Helper")
        print("5. Exit")

        choice = input("\nChoose an option (1-5): ").strip()

        if choice == "1":
            password_strength_checker()
        elif choice == "2":
            hash_generator()
        elif choice == "3":
            lab_port_scanner()
        elif choice == "4":
            subnet_helper()
        elif choice == "5":
            print("\nGoodbye. Stay legal and stay sharp.")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()

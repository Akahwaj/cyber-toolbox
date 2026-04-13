"""Wireless security tools module."""
import subprocess

TOOLS = {
    "airmon-ng": "Enable/disable monitor mode on wireless interfaces.",
    "airodump-ng": "Capture 802.11 frames and show access points/clients.",
    "aireplay-ng": "Inject frames for various wireless attacks.",
    "aircrack-ng": "Crack WEP/WPA-PSK keys from captured packets.",
    "iwconfig": "Configure wireless network interface parameters.",
    "iwlist": "Scan and list available wireless networks.",
}

def check_tool(tool):
    try:
        subprocess.run([tool, "--help"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def list_interfaces():
    """List wireless interfaces."""
    try:
        result = subprocess.run(["iwconfig"], capture_output=True, text=True, timeout=10)
        print(result.stdout)
        if result.returncode != 0 and not result.stdout.strip():
            print("No wireless interfaces found or iwconfig not installed.")
    except FileNotFoundError:
        print("iwconfig not found. Install: sudo apt install wireless-tools")

def enable_monitor_mode(interface):
    """Enable monitor mode on an interface."""
    if not check_tool("airmon-ng"):
        print("airmon-ng not found. Install: sudo apt install aircrack-ng")
        return
    print(f"\nEnabling monitor mode on {interface}...")
    result = subprocess.run(["sudo", "airmon-ng", "start", interface],
                            capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

def capture_packets(interface, output_file="capture"):
    """Start packet capture with airodump-ng."""
    if not check_tool("airodump-ng"):
        print("airodump-ng not found. Install: sudo apt install aircrack-ng")
        return
    print(f"\nStarting capture on {interface} (Ctrl+C to stop)...")
    try:
        subprocess.run(["sudo", "airodump-ng", "-w", output_file, interface],
                       timeout=300)
    except KeyboardInterrupt:
        print(f"\nCapture stopped. Files saved as {output_file}-*")
    except Exception as e:
        print(f"Error: {e}")

def run():
    print("\n📡 Wireless Security Tools")
    print("--------------------------")
    print("⚠️  Only use on networks you own or have explicit permission to test.\n")
    print("Available tools:")
    for tool, desc in TOOLS.items():
        status = "✓" if check_tool(tool) else "✗"
        print(f"  [{status}] {tool}: {desc}")
    print("\nOptions:")
    print("  1. List wireless interfaces")
    print("  2. Enable monitor mode")
    print("  3. Start packet capture (airodump-ng)")
    print("  4. Crack WPA handshake (aircrack-ng)")
    choice = input("\nSelect: ").strip()
    if choice == "1":
        list_interfaces()
    elif choice == "2":
        iface = input("Interface (e.g., wlan0): ").strip()
        if iface:
            enable_monitor_mode(iface)
    elif choice == "3":
        iface = input("Interface (e.g., wlan0mon): ").strip()
        out = input("Output filename prefix [capture]: ").strip() or "capture"
        if iface:
            capture_packets(iface, out)
    elif choice == "4":
        cap = input("Capture file (.cap): ").strip()
        wordlist = input("Wordlist path: ").strip()
        bssid = input("BSSID (target AP MAC): ").strip()
        if cap and wordlist and bssid:
            if not check_tool("aircrack-ng"):
                print("aircrack-ng not found.")
                return
            print(f"\nRunning aircrack-ng...")
            try:
                subprocess.run(["aircrack-ng", "-b", bssid, "-w", wordlist, cap])
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Missing required inputs.")
    else:
        print("Invalid option.")

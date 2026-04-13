"""Network security tools module."""
import subprocess
import socket
import ipaddress

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]

def check_tool(tool):
    try:
        subprocess.run([tool, "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def port_scan(host, ports=None):
    """Simple TCP port scanner."""
    ports = ports or COMMON_PORTS
    open_ports = []
    print(f"\nScanning {host}...")
    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=1):
                open_ports.append(port)
                print(f"  [OPEN]   {port}")
        except (ConnectionRefusedError, OSError, TimeoutError):
            pass
    return open_ports

def run_nmap(target, flags="-sV"):
    """Run nmap if available."""
    if not check_tool("nmap"):
        print("\nNmap not installed. Install with: sudo apt install nmap")
        return
    print(f"\nRunning: nmap {flags} {target}")
    try:
        result = subprocess.run(["nmap"] + flags.split() + [target],
                                capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Scan timed out.")
    except Exception as e:
        print(f"Error: {e}")

def subnet_info(cidr):
    """Display subnet information."""
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        print(f"\nNetwork:    {net.network_address}")
        print(f"Broadcast:  {net.broadcast_address}")
        print(f"Netmask:    {net.netmask}")
        print(f"Hosts:      {net.num_addresses - 2}")
        print(f"First host: {list(net.hosts())[0]}")
        print(f"Last host:  {list(net.hosts())[-1]}")
    except ValueError as e:
        print(f"Invalid CIDR: {e}")

def run():
    print("\n🌐 Network Security Tools")
    print("--------------------------")
    print("  1. Port Scanner")
    print("  2. Nmap Scan")
    print("  3. Subnet Helper")
    choice = input("\nSelect tool: ").strip()
    if choice == "1":
        host = input("Target host (IP or hostname): ").strip()
        if host:
            open_ports = port_scan(host)
            print(f"\nFound {len(open_ports)} open port(s).")
        else:
            print("No host entered.")
    elif choice == "2":
        target = input("Target: ").strip()
        flags = input("Nmap flags [-sV]: ").strip() or "-sV"
        if target:
            run_nmap(target, flags)
        else:
            print("No target entered.")
    elif choice == "3":
        cidr = input("CIDR notation (e.g., 192.168.1.0/24): ").strip()
        if cidr:
            subnet_info(cidr)
        else:
            print("No CIDR entered.")
    else:
        print("Invalid option.")

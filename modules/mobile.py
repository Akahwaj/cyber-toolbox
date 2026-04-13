"""Mobile security tools module (Android and iOS)."""
import subprocess
import os
import zipfile
import json

ANDROID_TOOLS = {
    "adb": "Android Debug Bridge - communicate with Android devices.",
    "apktool": "Decompile/recompile Android APK files.",
    "dex2jar": "Convert Dalvik bytecode (.dex) to Java bytecode (.jar).",
    "mobsf": "Mobile Security Framework - static and dynamic analysis.",
    "frida": "Dynamic instrumentation toolkit for mobile apps.",
}

IOS_TOOLS = {
    "frida": "Dynamic instrumentation toolkit for iOS apps.",
    "objection": "Runtime mobile exploration powered by Frida.",
    "ideviceinfo": "Query information from connected iOS devices.",
}

def check_tool(tool):
    try:
        subprocess.run([tool, "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return False

def analyze_apk_static(apk_path):
    """Perform basic static analysis of an APK."""
    if not os.path.isfile(apk_path):
        print(f"File not found: {apk_path}")
        return
    print(f"\n📱 Static APK Analysis: {apk_path}")
    print("-" * 40)
    # APKs are ZIP files
    try:
        with zipfile.ZipFile(apk_path, 'r') as zf:
            files = zf.namelist()
            print(f"Files in APK: {len(files)}")
            # Check for AndroidManifest.xml
            if "AndroidManifest.xml" in files:
                print("✓ AndroidManifest.xml found")
            # Check for native libs
            native_libs = [f for f in files if f.endswith(".so")]
            if native_libs:
                print(f"Native libraries: {len(native_libs)}")
                for lib in native_libs[:5]:
                    print(f"  - {lib}")
            # Check for interesting files
            interesting = [f for f in files if any(
                f.endswith(ext) for ext in ['.db', '.sqlite', '.json', '.xml', '.pem', '.key']
            )]
            if interesting:
                print(f"\nInteresting files ({len(interesting)}):")
                for f in interesting[:10]:
                    print(f"  - {f}")
    except (zipfile.BadZipFile, Exception) as e:
        print(f"Error reading APK: {e}")
    # Run apktool if available
    if check_tool("apktool"):
        print("\nRunning apktool decode...")
        out_dir = apk_path.replace(".apk", "_decoded")
        result = subprocess.run(["apktool", "d", apk_path, "-o", out_dir, "-f"],
                                capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"Decoded to: {out_dir}")
        else:
            print(f"apktool error: {result.stderr[:200]}")
    else:
        print("\nInstall apktool for deeper analysis: sudo apt install apktool")

def list_android_devices():
    """List connected Android devices via ADB."""
    if not check_tool("adb"):
        print("ADB not installed. Install: sudo apt install adb")
        return
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
    print(result.stdout)

def frida_list_apps(platform="android"):
    """List running apps via Frida."""
    if not check_tool("frida"):
        print("Frida not installed. Install: pip install frida-tools")
        return
    usb_flag = "-U"
    result = subprocess.run(["frida-ps", usb_flag, "-a"], capture_output=True, text=True, timeout=10)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)

def run():
    print("\n📱 Mobile Security Tools")
    print("------------------------")
    print("Android Tools:")
    for tool, desc in ANDROID_TOOLS.items():
        status = "✓" if check_tool(tool) else "✗"
        print(f"  [{status}] {tool}: {desc}")
    print("\niOS Tools:")
    for tool, desc in IOS_TOOLS.items():
        status = "✓" if check_tool(tool) else "✗"
        print(f"  [{status}] {tool}: {desc}")
    print("\nOptions:")
    print("  1. Analyze Android APK (static)")
    print("  2. List connected Android devices (ADB)")
    print("  3. List running apps (Frida)")
    print("  4. Download APK from device (ADB)")
    choice = input("\nSelect: ").strip()
    if choice == "1":
        path = input("APK file path: ").strip()
        analyze_apk_static(path)
    elif choice == "2":
        list_android_devices()
    elif choice == "3":
        platform = input("Platform (android/ios) [android]: ").strip() or "android"
        frida_list_apps(platform)
    elif choice == "4":
        if not check_tool("adb"):
            print("ADB not installed.")
            return
        pkg = input("Package name (e.g., com.example.app): ").strip()
        if pkg:
            print(f"Finding APK path for {pkg}...")
            result = subprocess.run(["adb", "shell", "pm", "path", pkg],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                apk_path = result.stdout.strip().split(":")[-1]
                out = f"{pkg}.apk"
                subprocess.run(["adb", "pull", apk_path, out])
                print(f"Downloaded to: {out}")
            else:
                print(f"Package not found: {result.stderr}")
    else:
        print("Invalid option.")

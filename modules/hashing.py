import hashlib

ALGORITHMS = {
    "1": ("MD5", "md5"),
    "2": ("SHA-1", "sha1"),
    "3": ("SHA-256", "sha256"),
    "4": ("SHA-512", "sha512"),
}

def hash_text(text, algorithm):
    h = hashlib.new(algorithm)
    h.update(text.encode())
    return h.hexdigest()

def run():
    print("\n#️⃣  Hash Generator")
    print("------------------")
    text = input("Enter text to hash: ").strip()
    if not text:
        print("No text entered.")
        return
    print("\nSelect algorithm:")
    for key, (name, _) in ALGORITHMS.items():
        print(f"  {key}. {name}")
    choice = input("Choice: ").strip()
    if choice not in ALGORITHMS:
        print("Invalid choice.")
        return
    name, algo = ALGORITHMS[choice]
    result = hash_text(text, algo)
    print(f"\n{name}: {result}")

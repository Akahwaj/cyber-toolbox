import hashlib


ALGORITHMS = {
    "1": ("MD5", "md5"),
    "2": ("SHA-1", "sha1"),
    "3": ("SHA-256", "sha256"),
    "4": ("SHA-512", "sha512"),
}


def hash_text(text, algorithm):
    h = hashlib.new(algorithm)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def run():
    print("\n#️⃣  Hash Generator")
    print("------------------")
    print("Select a hashing algorithm:")
    for key, (name, _) in ALGORITHMS.items():
        print(f"  {key}. {name}")

    choice = input("\nChoose an algorithm (1-4): ").strip()

    if choice not in ALGORITHMS:
        print("\nInvalid choice.")
        return

    name, algo = ALGORITHMS[choice]
    text = input(f"\nEnter the text to hash with {name}: ").strip()

    if not text:
        print("\nNo text entered.")
        return

    result = hash_text(text, algo)
    print(f"\n{name} Hash:")
    print(f"  {result}")

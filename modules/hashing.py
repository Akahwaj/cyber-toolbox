import hashlib


# MD5 and SHA1 are cryptographically broken; they are included here for
# legacy/learning purposes only.  Do NOT use them for password storage,
# digital signatures, or any security-critical operation.
ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]


def hash_text(text, algorithm="sha256"):
    """Return hex digest for *text* using the requested *algorithm*."""
    algorithm = algorithm.lower()
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {ALGORITHMS}")
    h = hashlib.new(algorithm)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def run():
    print("\n#️⃣  Hash Generator")
    print("------------------")
    text = input("Enter text to hash: ").strip()

    if not text:
        print("No text entered.")
        return

    print(f"\n{'Algorithm':<10}  Hash")
    print("-" * 74)
    for algo in ALGORITHMS:
        print(f"{algo.upper():<10}  {hash_text(text, algo)}")

import hashlib


def run():
    print("\n🔐 Hash Generator")
    print("--------------------------------")

    text = input("Enter text to hash: ").strip()
    data = text.encode("utf-8")

    print("\nResults:")
    print(f"MD5:    {hashlib.md5(data).hexdigest()}")
    print(f"SHA1:   {hashlib.sha1(data).hexdigest()}")
    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")

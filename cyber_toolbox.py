def file_integrity_checker():
    print("\n📁 File Integrity Checker")
    print("--------------------------------")

    file_path = input("Enter the full path to a file: ").strip()

    try:
        with open(file_path, "rb") as file:
            data = file.read()

        sha256_hash = hashlib.sha256(data).hexdigest()

        print("\nFile SHA256:")
        print(sha256_hash)
        print("\nSave this hash and compare it later to check if the file changes.")

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error: {e}")

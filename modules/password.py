import re


def check_strength(password):
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters (12+ is recommended).")

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
        feedback.append("Add at least one digit (0-9).")

    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        score += 2
    else:
        feedback.append("Add at least one special character (e.g. !, @, #, $).")

    common_patterns = ["password", "123456", "qwerty", "abc123", "letmein", "admin"]
    if any(p in password.lower() for p in common_patterns):
        score -= 2
        feedback.append("Avoid common password patterns like 'password' or '123456'.")

    if score >= 6:
        strength = "Strong 💪"
    elif score >= 4:
        strength = "Moderate ⚠️"
    else:
        strength = "Weak ❌"

    return strength, feedback


def run():
    print("\n🔒 Password Strength Checker")
    print("----------------------------")
    password = input("Enter a password to evaluate: ").strip()

    if not password:
        print("\nNo password entered.")
        return

    strength, feedback = check_strength(password)

    print(f"\nStrength: {strength}")

    if feedback:
        print("\nSuggestions to improve your password:")
        for tip in feedback:
            print(f"  • {tip}")
    else:
        print("\nYour password looks great! No suggestions.")

import re


def check_strength(password):
    """Return a (score, feedback_list) tuple for the given password."""
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
        feedback.append("Add uppercase letters (A-Z).")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters (a-z).")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add numbers (0-9).")

    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        score += 2
    else:
        feedback.append("Add special characters (e.g. !, @, #, $).")

    common = [
        "password", "123456", "qwerty", "letmein", "welcome",
        "monkey", "dragon", "master", "shadow", "sunshine",
    ]
    if password.lower() in common:
        score = 0
        feedback.append("This is a commonly used password — avoid it entirely.")

    return score, feedback


def run():
    print("\n🔑 Password Strength Checker")
    print("-----------------------------")
    password = input("Enter a password to check: ").strip()

    if not password:
        print("No password entered.")
        return

    score, feedback = check_strength(password)

    if score >= 6:
        rating = "Strong 💪"
    elif score >= 4:
        rating = "Moderate ⚠️"
    else:
        rating = "Weak ❌"

    print(f"\nStrength: {rating}  (score: {score}/7)")

    if feedback:
        print("\nSuggestions:")
        for tip in feedback:
            print(f"  • {tip}")
    else:
        print("\nGreat password! No obvious weaknesses found.")

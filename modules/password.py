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
# Password strength checker with detailed analysis
import re
import string

def analyze_password(password):
    """Analyze password strength and return detailed feedback."""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters.")

    if len(password) >= 12:
        score += 1

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Add uppercase letters.")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Add lowercase letters.")

    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Add numbers.")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Add special characters.")

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Moderate"
    else:
        strength = "Strong"

    return strength, score, feedback

def run():
    print("\n🔐 Password Strength Checker")
    print("-----------------------------")
    password = input("Enter a password to check: ").strip()
    if not password:
        print("No password entered.")
        return
    strength, score, feedback = analyze_password(password)
    print(f"\nStrength: {strength} ({score}/6)")
    if feedback:
        print("Suggestions:")
        for tip in feedback:
            print(f"  - {tip}")
    else:
        print("Great password! No improvements needed.")

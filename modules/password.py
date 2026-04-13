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

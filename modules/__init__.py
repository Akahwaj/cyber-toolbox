import re


def run():
    print("\n🛡️ Password Strength Checker")
    print("--------------------------------")

    password = input("Enter a password to evaluate: ").strip()
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 1
    else:
        feedback.append("Use at least 12 characters.")

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
        feedback.append("Add at least one number.")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add at least one special character.")

    if score == 5:
        strength = "Strong"
    elif score >= 3:
        strength = "Moderate"
    else:
        strength = "Weak"

    print(f"\nPassword Strength: {strength}")

    if feedback:
        print("\nSuggestions:")
        for item in feedback:
            print(f"- {item}")

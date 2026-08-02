import os
import bcrypt
import secure_auth
import mfa
from encryption_examples import make_key, encrypt_message, decrypt_message
from cryptography.fernet import InvalidToken

passed = 0
failed = 0


def check(description, condition):
    global passed, failed
    if condition:
        print(f"[PASS] {description}")
        passed += 1
    else:
        print(f"[FAIL] {description}")
        failed += 1


def cleanup():
    for f in ("users.json", "login_attempts.json"):
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    cleanup()  # start from a clean state

    print("=== 1. Generate bcrypt hash - different hash each time ===")
    h1 = bcrypt.hashpw(b"password123", bcrypt.gensalt())
    h2 = bcrypt.hashpw(b"password123", bcrypt.gensalt())
    check("bcrypt hashes differ for the same password (salting works)", h1 != h2)

    print("\n=== 2. Verify correct password ===")
    result = secure_auth.register("testuser", "SecurePass123!")
    check("Registration succeeded", result["success"])
    login_result = secure_auth.login_step1_password("testuser", "SecurePass123!")
    check("Correct password returns success", login_result["success"])

    print("\n=== 3. Reject wrong password ===")
    secure_auth.reset_attempts("testuser")  # don't let earlier tests lock us out
    wrong_result = secure_auth.login_step1_password("testuser", "WrongPassword")
    check("Wrong password is rejected", wrong_result["success"] is False)

    print("\n=== 4. Encrypt and decrypt data - data recoverable with key ===")
    key = make_key()
    original = "Credit card: 1234-5678-9012-3456"
    encrypted = encrypt_message(original, key)
    decrypted = decrypt_message(encrypted, key)
    check("Decrypted text matches original", decrypted == original)

    print("\n=== 5. Encryption with wrong key - raises exception ===")
    wrong_key = make_key()
    raised = False
    try:
        decrypt_message(encrypted, wrong_key)
    except InvalidToken:
        raised = True
    check("Wrong key raises InvalidToken", raised)

    print("\n=== 6. User registration system - users saved securely ===")
    users = secure_auth.load_users()
    check("User exists in storage", "testuser" in users)
    check("Stored value is a bcrypt hash, not plaintext",
          users["testuser"]["password_hash"] != "SecurePass123!")

    print("\n=== 7. User login verification - correct password + MFA works ===")
    secure_auth.reset_attempts("testuser")
    secure_auth.login_step1_password("testuser", "SecurePass123!")
    secret = users["testuser"]["mfa_secret"]
    code = mfa.get_current_otp(secret)
    mfa_result = secure_auth.login_step2_mfa("testuser", code)
    check("Full login (password + MFA) succeeds", mfa_result["success"])

    print("\n=== 8. Rainbow table resistance - salt prevents lookup ===")
    same_pw_hash1 = bcrypt.hashpw(b"repeat-password", bcrypt.gensalt())
    same_pw_hash2 = bcrypt.hashpw(b"repeat-password", bcrypt.gensalt())
    check("Same password produces different stored hashes",
          same_pw_hash1 != same_pw_hash2)
    check("But both still verify correctly against their own hash",
          bcrypt.checkpw(b"repeat-password", same_pw_hash1) and
          bcrypt.checkpw(b"repeat-password", same_pw_hash2))

    print("\n=== 9. Strong password requirement rejects weak passwords ===")
    weak_result = secure_auth.register("weakuser", "short1!")
    check("Weak password is rejected at registration", weak_result["success"] is False)

    print("\n=== 10. Rate limiting locks account after repeated failures ===")
    secure_auth.reset_attempts("testuser")
    for _ in range(secure_auth.MAX_FAILED_ATTEMPTS):
        secure_auth.login_step1_password("testuser", "wrong")
    locked_result = secure_auth.login_step1_password("testuser", "wrong")
    check("Account locks out after max failed attempts",
          "locked" in locked_result["message"].lower())

    print(f"\n=== RESULTS: {passed} passed, {failed} failed ===")
    cleanup()

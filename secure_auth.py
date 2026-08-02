import json
import os
import time
import bcrypt
import mfa

DB_FILE = "users.json"
ATTEMPTS_FILE = "login_attempts.json"

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_SECONDS = 60
PEPPER = os.environ.get("APP_PEPPER", "cloudexify-dev-pepper-do-not-use-in-prod")


def apply_pepper(password):
    return password + PEPPER


# ---------------- storage helpers ----------------

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=2)


def load_attempts():
    if os.path.exists(ATTEMPTS_FILE):
        with open(ATTEMPTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_attempts(attempts):
    with open(ATTEMPTS_FILE, "w") as f:
        json.dump(attempts, f, indent=2)


# ---------------- password strength ----------------

def is_strong_password(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    if not any(c.isdigit() for c in password):
        return False, "Password must include at least one number."
    if not any(not c.isalnum() for c in password):
        return False, "Password must include at least one symbol."
    return True, "OK"


# ---------------- rate limiting ----------------

def is_locked_out(username):
    attempts = load_attempts()
    record = attempts.get(username)
    if not record:
        return False, 0

    if record["count"] >= MAX_FAILED_ATTEMPTS:
        elapsed = time.time() - record["last_attempt"]
        remaining = LOCKOUT_SECONDS - elapsed
        if remaining > 0:
            return True, int(remaining)
        else:
            # lockout period passed, reset
            attempts[username] = {"count": 0, "last_attempt": 0}
            save_attempts(attempts)
    return False, 0


def record_failed_attempt(username):
    attempts = load_attempts()
    record = attempts.get(username, {"count": 0, "last_attempt": 0})
    record["count"] += 1
    record["last_attempt"] = time.time()
    attempts[username] = record
    save_attempts(attempts)


def reset_attempts(username):
    attempts = load_attempts()
    if username in attempts:
        attempts[username] = {"count": 0, "last_attempt": 0}
        save_attempts(attempts)


# ---------------- registration ----------------

def register(username, password):
    users = load_users()

    if username in users:
        return {"success": False, "message": "Username already exists!"}

    strong, message = is_strong_password(password)
    if not strong:
        return {"success": False, "message": message}

    # bcrypt.gensalt() creates a new random salt each call -> unique per user
    # apply_pepper() mixes in the server-wide secret before hashing
    salt = bcrypt.gensalt()
    peppered_password = apply_pepper(password)
    hashed_password = bcrypt.hashpw(peppered_password.encode(), salt)

    # generate this user's own MFA secret (checklist: multi-factor authentication)
    mfa_secret = mfa.generate_secret()

    users[username] = {
        "password_hash": hashed_password.decode(),
        "mfa_secret": mfa_secret,
    }
    save_users(users)

    # NOTE: we never write `password` itself anywhere - only the hash above.
    return {
        "success": True,
        "message": "Registration successful!",
        "mfa_secret": mfa_secret,   # shown once so the user can save it
    }


# ---------------- login ----------------

def login_step1_password(username, password):
    locked, remaining = is_locked_out(username)
    if locked:
        return {"success": False, "message": f"Account locked. Try again in {remaining}s."}

    users = load_users()
    if username not in users:
        record_failed_attempt(username)
        return {"success": False, "message": "No such user!"}

    stored_hash = users[username]["password_hash"].encode()
    peppered_password = apply_pepper(password)
    if bcrypt.checkpw(peppered_password.encode(), stored_hash):
        return {"success": True, "message": "Password correct. Enter your MFA code."}
    else:
        record_failed_attempt(username)
        return {"success": False, "message": "Wrong password!"}


def login_step2_mfa(username, otp_code):
    users = load_users()
    if username not in users:
        return {"success": False, "message": "No such user!"}

    secret = users[username]["mfa_secret"]
    if mfa.verify_otp(secret, otp_code):
        reset_attempts(username)
        return {"success": True, "message": "MFA verified. Login successful!"}
    else:
        record_failed_attempt(username)
        return {"success": False, "message": "Invalid MFA code!"}


# ---------------- demo when run directly ----------------

if __name__ == "__main__":
    print("=== Registering user ===")
    result = register("alice", "SecurePass123!")
    print(result["message"])
    if result["success"]:
        secret = result["mfa_secret"]
        print("MFA secret (save this in your authenticator app):", secret)

    print("\n=== Trying a weak password ===")
    print(register("bob", "weak")["message"])

    print("\n=== Login: step 1 (password) ===")
    step1 = login_step1_password("alice", "SecurePass123!")
    print(step1["message"])

    print("\n=== Login: step 2 (MFA code) ===")
    # DEMO ONLY: normally the user reads this from their phone app
    current_code = mfa.get_current_otp(secret)
    print("(demo) current valid code:", current_code)
    step2 = login_step2_mfa("alice", current_code)
    print(step2["message"])

    print("\n=== Testing rate limiting (3 wrong passwords) ===")
    for i in range(4):
        result = login_step1_password("alice", "wrongpassword")
        print(f"Attempt {i+1}:", result["message"])

    # cleanup demo files so re-running this script starts fresh
    for f in (DB_FILE, ATTEMPTS_FILE):
        if os.path.exists(f):
            os.remove(f)

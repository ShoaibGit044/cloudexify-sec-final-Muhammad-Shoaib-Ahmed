import pyotp


def generate_secret():
    # random secret, one per user, saved alongside their password hash
    return pyotp.random_base32()


def get_current_otp(secret):
    # DEMO ONLY - simulates "checking your phone" for the current code
    totp = pyotp.TOTP(secret)
    return totp.now()


def verify_otp(secret, code):
    totp = pyotp.TOTP(secret)
    # valid_window=1 allows the code from 30s before/after, like real apps do
    return totp.verify(code, valid_window=1)

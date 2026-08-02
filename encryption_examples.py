from cryptography.fernet import Fernet, InvalidToken


def make_key():
    # this key must be kept secret - anyone with it can decrypt your data
    return Fernet.generate_key()


def encrypt_message(message, key):
    cipher = Fernet(key)
    encrypted = cipher.encrypt(message.encode())
    return encrypted


def decrypt_message(encrypted, key):
    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted)
    return decrypted.decode()


# ---- main program ----
if __name__ == "__main__":
    print("=== Generating key ===")
    key = make_key()
    print("Key:", key.decode())

    print("\n=== Encrypting a message ===")
    secret_message = "Credit card: 1234-5678-9012-3456"
    encrypted = encrypt_message(secret_message, key)
    print("Encrypted:", encrypted.decode())

    print("\n=== Decrypting with correct key ===")
    decrypted = decrypt_message(encrypted, key)
    print("Decrypted:", decrypted)

    print("\n=== Trying to decrypt with wrong key ===")
    wrong_key = make_key()
    try:
        decrypt_message(encrypted, wrong_key)
    except InvalidToken:
        print("Failed as expected - wrong key cannot decrypt the data")

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


def generate_keypair():
    """Creates a matched public/private key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,   # standard fixed value, always this number
        key_size=2048,           # 2048-bit is the current safe minimum
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_with_public_key(message, public_key):
    """Anyone holding the PUBLIC key can encrypt - but not decrypt."""
    ciphertext = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return ciphertext


def decrypt_with_private_key(ciphertext, private_key):
    """Only the matching PRIVATE key can decrypt this."""
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext.decode()


if __name__ == "__main__":
    print("=== Generating RSA key pair (2048-bit) ===")
    private_key, public_key = generate_keypair()
    print("Public key generated  -> safe to share with anyone")
    print("Private key generated -> must stay secret, never shared")

    print("\n=== Encrypting with the PUBLIC key ===")
    message = "Meet at 10pm, bring the login credentials."
    encrypted = encrypt_with_public_key(message, public_key)
    print("Original: ", message)
    print("Encrypted (unreadable without private key):")
    print(encrypted[:50], "...")  # full ciphertext is long, showing a slice

    print("\n=== Decrypting with the matching PRIVATE key ===")
    decrypted = decrypt_with_private_key(encrypted, private_key)
    print("Decrypted:", decrypted)
    print("Matches original?", decrypted == message)

    print("\n=== What if someone else's private key is used? ===")
    _, wrong_public = generate_keypair()
    other_private, _ = generate_keypair()  # unrelated key pair
    try:
        decrypt_with_private_key(encrypted, other_private)
    except ValueError:
        print("Failed as expected - only the ORIGINAL matching private key works")

    print("\n=== Where RSA fits in the bigger picture ===")
    print("- Fernet (encryption_examples.py): 1 shared key, fast, good for bulk data")
    print("- RSA (this file): 2 keys, slower, solves the 'how do we share a key")
    print("  safely in the first place' problem - this is exactly what happens")
    print("  during an HTTPS/TLS handshake before your browser and a website")
    print("  agree on a fast symmetric key to use for the rest of the session.")

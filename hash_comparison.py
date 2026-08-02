import hashlib
import bcrypt

password = "password123"

print("=== SHA-256 (no salt) ===")
hash1 = hashlib.sha256(password.encode()).hexdigest()
hash2 = hashlib.sha256(password.encode()).hexdigest()
print("First hash: ", hash1)
print("Second hash:", hash2)
print("Same both times?", hash1 == hash2)
print("-> Bad: same password always gives same hash, so hackers can use")
print("   a precomputed rainbow table to crack it instantly.\n")

print("=== bcrypt (auto-salted) ===")
hash3 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
hash4 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print("First hash: ", hash3.decode())
print("Second hash:", hash4.decode())
print("Same both times?", hash3 == hash4)
print("-> Good: different hash every time because of the random salt,")
print("   so rainbow tables don't work anymore.")

print("\n=== But both still verify correctly ===")
print("Check hash3:", bcrypt.checkpw(password.encode(), hash3))
print("Check hash4:", bcrypt.checkpw(password.encode(), hash4))

import os
from Crypto.Util import number
from Crypto.Random import random

# ElGamal Parameters for Encrypting AES Keys (Ensure consistency across runs)
p = number.getPrime(512)
g = number.getRandomRange(2, p - 1)

def generate_elgamal_keypair():
    sk = random.randint(2, p - 2)  # Private Key
    pk = pow(g, sk, p)  # Public Key
    return sk, pk

# Encrypt AES Key using ElGamal
def encrypt_aes_key(aes_key, pk):
    r = random.randint(2, p - 2)
    c1 = pow(g, r, p)
    
    # 🔄 FIX: Ensure AES key fits within `p`
    aes_key_int = int.from_bytes(aes_key, 'big') % p
    
    c2 = (pow(pk, r, p) * aes_key_int) % p
    return (c1, c2)


# Decrypt AES Key using ElGamal
def decrypt_aes_key(c1, c2, sk):
    s = pow(c1, sk, p)
    s_inv = number.inverse(s, p)  # Compute modular inverse
    aes_key_int = (c2 * s_inv) % p  # Ensure correct modular inverse

    # 🔄 FIX: Dynamically determine the correct byte size
    aes_key_bytes = aes_key_int.to_bytes((aes_key_int.bit_length() + 7) // 8, 'big')

    # 🔄 FIX: Ensure AES key is exactly 32 bytes
    return aes_key_bytes.rjust(32, b'\x00')

# Generate a Re-Encryption Key (Validate inputs)
def generate_re_encryption_key(sk_A, pk_B):
    if sk_A <= 0 or pk_B <= 0:
        raise ValueError("Invalid keys for re-encryption")
    return pow(pk_B, sk_A, p)  # Shared secret as re-encryption key

# Re-Encrypt AES Key using Proxy Re-Encryption
def re_encrypt_aes_key(c1, c2, re_key):
    if re_key <= 0:
        raise ValueError("Invalid re-encryption key")
    new_c2 = (c2 * number.inverse(re_key, p)) % p
    return (c1, new_c2)

# Convert Encrypted AES Key to String (for database storage)
def encrypted_aes_key_to_str(c1, c2):
    return f"{c1},{c2}"

# Convert String Back to Encrypted AES Key (for retrieval)
def str_to_encrypted_aes_key(enc_str):
    c1, c2 = map(int, enc_str.split(','))
    return c1, c2

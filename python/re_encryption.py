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
    c2 = (pow(pk, r, p) * int.from_bytes(aes_key, 'big')) % p
    return (c1, c2)

# Decrypt AES Key using ElGamal
def decrypt_aes_key(c1, c2, sk):
    s = pow(c1, sk, p)
    aes_key_int = (c2 * number.inverse(s, p)) % p
    return aes_key_int.to_bytes(32, 'big')  # Convert back to bytes

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
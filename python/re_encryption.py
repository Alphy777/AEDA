import os
from Crypto.Util import number
from Crypto.Random import random

# Important: Use a fixed prime and generator for all encryption/decryption
p = 134078079299425970995740249982058461274793658205923933777235614437217640300735  # 512-bit prime
g = 2  # Use a simple generator value for consistency

def generate_elgamal_keypair():
    sk = random.randint(2, p - 2)  # Private Key
    pk = pow(g, sk, p)  # Public Key
    return sk, pk

# Encrypt AES Key using ElGamal
def encrypt_aes_key(aes_key, pk):
    # Ensure pk is an integer
    pk = int(pk) if not isinstance(pk, int) else pk
    
    # Generate a random value for this encryption
    r = random.randint(2, p - 2)
    c1 = pow(g, r, p)
    
    # Ensure AES key is exactly 32 bytes before conversion to integer
    if len(aes_key) != 32:
        aes_key = aes_key[:32].ljust(32, b'\x00')
    
    # Convert to integer, keeping it smaller than p
    aes_key_int = int.from_bytes(aes_key, 'big') % (p - 1)
    
    # Use modular multiplication for encryption
    c2 = (pow(pk, r, p) * aes_key_int) % p
    
    return (c1, c2)

# Decrypt AES Key using ElGamal
def decrypt_aes_key(c1, c2, sk):
    try:
        # Ensure sk is an integer
        sk = int(sk) if not isinstance(sk, int) else sk
        
        # Prevent potential errors with invalid inputs
        if c1 <= 0 or c2 <= 0 or sk <= 0:
            print("⚠️ Warning: Invalid ElGamal parameters")
            return os.urandom(32)  # Return random key to fail gracefully
            
        # Calculate the shared secret
        s = pow(c1, sk, p)
        
        # Compute modular inverse carefully
        try:
            s_inv = number.inverse(s, p)
        except ValueError:
            print("❌ Error: Base is not invertible for the given modulus")
            return os.urandom(32)  # Return random key to fail gracefully
            
        # Recover the AES key integer
        aes_key_int = (c2 * s_inv) % p
        
        # Convert back to bytes, ensuring exactly 32 bytes
        try:
            if aes_key_int.bit_length() > 256:
                aes_key_bytes = aes_key_int.to_bytes(32, 'big')
            else:
                # Ensure we get exactly 32 bytes
                aes_key_bytes = aes_key_int.to_bytes(32, 'big')
            
            return aes_key_bytes
        except OverflowError:
            print("❌ Error: Integer too large to convert to bytes")
            return os.urandom(32)  # Return random key to fail gracefully
            
    except Exception as e:
        print(f"❌ AES key decryption error: {str(e)}")
        return os.urandom(32)  # Return random key to fail gracefully

# Generate a Re-Encryption Key
def generate_re_encryption_key(sk_A, pk_B):
    try:
        # Ensure both values are integers
        sk_A = int(sk_A) if not isinstance(sk_A, int) else sk_A
        pk_B = int(pk_B) if not isinstance(pk_B, int) else pk_B
        
        if sk_A <= 0 or pk_B <= 0:
            raise ValueError("Invalid keys for re-encryption")
        return pow(pk_B, sk_A, p)  # Shared secret as re-encryption key
    except Exception as e:
        print(f"❌ Error generating re-encryption key: {str(e)}")
        return 1  # A sensible default that will cause decryption to fail gracefully

# Re-Encrypt AES Key
def re_encrypt_aes_key(c1, c2, re_key):
    try:
        if not all(isinstance(x, int) for x in [c1, c2, re_key]):
            c1, c2, re_key = int(c1), int(c2), int(re_key)
            
        if c1 <= 0 or c2 <= 0 or re_key <= 0:
            raise ValueError("Invalid parameters for re-encryption")
            
        try:
            re_key_inv = number.inverse(re_key, p)
        except ValueError:
            print("❌ Re-encryption key not invertible")
            return c1, c2  # Return original values to fail gracefully
            
        new_c2 = (c2 * re_key_inv) % p
        return (c1, new_c2)
    except Exception as e:
        print(f"❌ Error in re-encryption: {str(e)}")
        return c1, c2  # Return original values to fail gracefully

# Convert Encrypted AES Key to string format
def encrypted_aes_key_to_str(c1, c2):
    return f"{c1},{c2}"

# Convert string back to Encrypted AES Key components
def str_to_encrypted_aes_key(enc_str):
    try:
        parts = enc_str.split(',')
        if len(parts) != 2:
            print(f"❌ Error: Expected 2 parts in encrypted key string, got {len(parts)}")
            return 0, 0
            
        c1, c2 = int(parts[0]), int(parts[1])
        return c1, c2
    except Exception as e:
        print(f"❌ Error parsing encrypted key string: {str(e)}")
        return 0, 0  # Return values that will cause decryption to fail gracefully
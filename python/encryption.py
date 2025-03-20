import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_aes_key():
    return os.urandom(32)  # Generate a 256-bit AES key for each message

# AES Encryption Function
def encrypt_message(message, aes_key):
    iv = os.urandom(16)  # Generate a random IV (Initialization Vector)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    encrypted_message = cipher.encrypt(pad(message.encode(), AES.block_size))
    
    # Encode using Base64 for storage
    return base64.b64encode(iv + encrypted_message).decode("utf-8")

# AES Decryption Function
def decrypt_message(encrypted_message, aes_key):
    try:
        encrypted_data = base64.b64decode(encrypted_message)
        iv = encrypted_data[:16]  # Extract IV
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_message = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_message.decode("utf-8")
    except Exception as e:
        print(f"❌ Decryption Error: {e}")
        return "[ERROR] Message could not be decrypted."

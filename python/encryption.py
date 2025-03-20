import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def generate_aes_key():
    """Generate a secure 256-bit (32-byte) AES key"""
    return os.urandom(32)

def encrypt_message(message, aes_key):
    """Encrypt a message using AES-256-CBC with proper padding"""
    try:
        # Ensure AES key is exactly 32 bytes
        if len(aes_key) != 32:
            print(f"⚠️ Warning: Adjusting AES key length from {len(aes_key)} to 32 bytes")
            aes_key = aes_key[:32].ljust(32, b'\x00')
            
        # Generate a random IV
        iv = os.urandom(16)
        
        # Create cipher and encrypt
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        
        # Ensure message is properly encoded and padded
        message_bytes = message.encode('utf-8')
        padded_message = pad(message_bytes, AES.block_size)
        
        # Encrypt the message
        encrypted_message = cipher.encrypt(padded_message)
        
        # Combine IV and ciphertext, then encode as base64
        complete_message = iv + encrypted_message
        encoded_message = base64.b64encode(complete_message).decode('utf-8')
        
        return encoded_message
    except Exception as e:
        print(f"❌ Encryption error: {str(e)}")
        # Return a placeholder error message that's still valid base64
        return base64.b64encode(b"ENCRYPTION_ERROR").decode('utf-8')

def decrypt_message(encrypted_message, aes_key):
    """Decrypt a message using AES-256-CBC with proper padding handling"""
    try:
        # Ensure AES key is exactly 32 bytes
        if len(aes_key) != 32:
            print(f"⚠️ Warning: Adjusting AES key length from {len(aes_key)} to 32 bytes")
            aes_key = aes_key[:32].ljust(32, b'\x00')
            
        # Decode the base64 message
        encrypted_data = base64.b64decode(encrypted_message)
        
        # Ensure the message is at least as long as the IV
        if len(encrypted_data) < 16:
            return "[ERROR] Encrypted message too short"
            
        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Create cipher and decrypt
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        try:
            decrypted_padded = cipher.decrypt(ciphertext)
            decrypted_message = unpad(decrypted_padded, AES.block_size)
            return decrypted_message.decode('utf-8')
        except ValueError as padding_error:
            print(f"❌ Padding error: {padding_error}")
            return "[ERROR] Invalid padding - corrupted message or wrong key"
            
    except Exception as e:
        print(f"❌ Decryption error: {str(e)}")
        return "[ERROR] Message could not be decrypted"
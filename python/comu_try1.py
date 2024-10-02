import socket
import random
import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Modular exponentiation function for Diffie-Hellman
def mod_exp(base, exp, mod):
    return pow(base, exp, mod)

# Generate AES key from shared secret using SHA-256
def generate_aes_key(shared_secret):
    shared_secret_bytes = str(shared_secret).encode('utf-8')
    return hashlib.sha256(shared_secret_bytes).digest()

# Encrypt the message using AES
def encrypt_message(aes_key, message):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return iv, encrypted_message

# Alice's Diffie-Hellman key exchange
p = 23
g = 5
a = random.randint(1, p-1)
A = mod_exp(g, a, p)

# Create a server (Alice)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))  # Bind to all interfaces
server_socket.listen(1)

print("Waiting for connection from Bob (phone)...")
conn, addr = server_socket.accept()

# Send Alice's public key to Bob
conn.sendall(str(A).encode())

# Receive Bob's public key
B_from_bob = int(conn.recv(1024).decode())

# Compute shared secret
shared_secret_alice = mod_exp(B_from_bob, a, p)
aes_key = generate_aes_key(shared_secret_alice)
print(f"Alice's shared secret: {shared_secret_alice}")

# Encrypt a message to Bob
message_from_alice = "Hello from Alice!"
iv, encrypted_message = encrypt_message(aes_key, message_from_alice)
conn.sendall(iv + encrypted_message)

# Close connection
conn.close()
server_socket.close()

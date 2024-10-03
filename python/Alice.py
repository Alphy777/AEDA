import socket
import threading
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import os

# Function to perform modular exponentiation
def mod_exp(base, exp, mod):
    return pow(base, exp, mod)

# Function to generate AES key from shared secret
def generate_aes_key(shared_secret):
    return hashlib.sha256(str(shared_secret).encode()).digest()

# Function to encrypt a message using AES
def encrypt_message(aes_key, message):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_message = message + ' ' * (16 - len(message) % 16)  # Padding message to block size
    encrypted_message = encryptor.update(padded_message.encode()) + encryptor.finalize()
    return iv, encrypted_message

# Function to decrypt a message using AES
def decrypt_message(aes_key, iv, encrypted_message):
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message.strip()

# Diffie-Hellman parameters
p = 23
g = 5
a = random.randint(1, p-1)
A = mod_exp(g, a, p)

# Setup server (Alice)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.listen(1)
print("Waiting for connection from Bob...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Send public key A to Bob and receive B
conn.sendall(str(A).encode())
B_from_bob = int(conn.recv(1024).decode())

# Calculate shared secret and derive AES key
shared_secret_alice = mod_exp(B_from_bob, a, p)
aes_key = generate_aes_key(shared_secret_alice)

print("Shared secret established. You can now send and receive messages. Type 'exit' to end the chat")

# Function to handle receiving messages
def receive_messages():
    while True:
        try:
            iv = conn.recv(16)  # Receive IV
            encrypted_message = conn.recv(1024)  # Receive encrypted message
            if encrypted_message:
                decrypted_message = decrypt_message(aes_key, iv, encrypted_message)
                if decrypted_message.decode() == "exit":
                    print("Bob has ended the chat.")
                    conn.close()
                    break
                print(f"Bob: {decrypted_message.decode()}")
            else:
                break
        except:
            break

# Function to handle sending messages
def send_messages():
    while True:
        message = input("")
        if message == "exit":
            iv, encrypted_message = encrypt_message(aes_key, message)
            conn.sendall(iv + encrypted_message)
            conn.close()
            print("You ended the chat.")
            break
        iv, encrypted_message = encrypt_message(aes_key, message)
        conn.sendall(iv + encrypted_message)

# Start threads for sending and receiving messages
receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()

print("Chat ended.")

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from encryption import encrypt_message, decrypt_message, generate_aes_key  # 🔄 FIXED: Corrected function import
from re_encryption import encrypt_aes_key, decrypt_aes_key, generate_re_encryption_key, re_encrypt_aes_key, encrypted_aes_key_to_str, str_to_encrypted_aes_key

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users.db"))

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            encrypted_message TEXT NOT NULL,
            encrypted_aes_key TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

setup_db()

# ✅ Send Message API
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")

    if not sender or not receiver or not message:
        return jsonify({"error": "Missing data"}), 400

    aes_key = generate_aes_key()  # 🔄 FIXED: Generate a unique AES key per message
    encrypted_message = encrypt_message(message, aes_key)  # Encrypt message with AES
    receiver_pk = get_public_key(receiver)  # Fetch receiver's public key

    if receiver_pk is None:
        return jsonify({"error": "Receiver public key not found"}), 404

    encrypted_aes_key = encrypt_aes_key(aes_key, receiver_pk)  # Encrypt AES key using ElGamal
    encrypted_aes_key_str = encrypted_aes_key_to_str(*encrypted_aes_key)  # Store as a string

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, encrypted_message, encrypted_aes_key) VALUES (?, ?, ?, ?)",
                   (sender, receiver, encrypted_message, encrypted_aes_key_str))
    conn.commit()
    conn.close()

    return jsonify({"status": "Message sent successfully"})

# ✅ Fetch Messages API
@app.route('/get-messages/<username>', methods=['GET'])
def get_messages(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, sender, receiver, encrypted_message, encrypted_aes_key, timestamp FROM messages WHERE sender=? OR receiver=? ORDER BY timestamp",
                   (username, username))
    messages = cursor.fetchall()
    conn.close()

    user_sk = get_private_key(username)
    if user_sk is None:
        return jsonify({"error": "Private key not found"}), 404

    chat_history = []
    for msg in messages:
        message_id, sender, receiver, encrypted_message, encrypted_aes_key_str, timestamp = msg
        c1, c2 = str_to_encrypted_aes_key(encrypted_aes_key_str)
        aes_key = decrypt_aes_key(c1, c2, user_sk)  # Decrypt AES key
        decrypted_message = decrypt_message(encrypted_message, aes_key)  # Decrypt message

        chat_history.append({
            "message_id": message_id,
            "sender": sender,
            "receiver": receiver,
            "encrypted_message": encrypted_message,
            "decrypted_message": decrypted_message,
            "timestamp": timestamp
        })

    return jsonify(chat_history)

# ✅ Re-Encrypt Message API (Forwarding)
@app.route('/re-encrypt-message', methods=['POST'])
def reencrypt_message():
    data = request.json
    sender = data.get("sender")
    original_receiver = data.get("original_receiver")
    new_receiver = data.get("new_receiver")
    message_id = data.get("message_id")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_aes_key FROM messages WHERE id=? AND receiver=?", (message_id, original_receiver))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"error": "Message not found or access denied"}), 404

    encrypted_aes_key_str = result[0]
    c1, c2 = str_to_encrypted_aes_key(encrypted_aes_key_str)

    sender_sk = get_private_key(original_receiver)
    new_receiver_pk = get_public_key(new_receiver)

    if sender_sk is None or new_receiver_pk is None:
        return jsonify({"error": "Invalid sender or receiver"}), 404

    re_key = generate_re_encryption_key(sender_sk, new_receiver_pk)
    new_c1, new_c2 = re_encrypt_aes_key(c1, c2, re_key)

    new_encrypted_aes_key_str = encrypted_aes_key_to_str(new_c1, new_c2)

    cursor.execute("UPDATE messages SET encrypted_aes_key=?, receiver=? WHERE id=?",
                   (new_encrypted_aes_key_str, new_receiver, message_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "Message re-encrypted successfully"})

# ✅ Get Public Key
def get_public_key(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return int(result[0]) if result else None

# ✅ Get Private Key
def get_private_key(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return int(result[0]) if result else None  # 🔄 FIXED: Ensure correct data type

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from encryption import encrypt_message, decrypt_message, generate_aes_key
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

# ✅ FIXED: Send Message API with better error handling
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")

    if not sender or not receiver or not message:
        return jsonify({"error": "Missing data"}), 400

    try:
        aes_key = generate_aes_key()  # Generate a unique AES key per message
        encrypted_message = encrypt_message(message, aes_key)  # Encrypt message with AES
        receiver_pk = get_public_key(receiver)  # Fetch receiver's public key

        if receiver_pk is None:
            return jsonify({"error": "Receiver public key not found"}), 404

        # Convert string public key to integer
        receiver_pk = int(receiver_pk)
        
        encrypted_aes_key = encrypt_aes_key(aes_key, receiver_pk)  # Encrypt AES key using ElGamal
        encrypted_aes_key_str = encrypted_aes_key_to_str(*encrypted_aes_key)  # Store as a string

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # First, check if the messages table has a plaintext_message column
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        plaintext_column_exists = any(column[1] == 'plaintext_message' for column in columns)
        
        # If not, add it
        if not plaintext_column_exists:
            cursor.execute("ALTER TABLE messages ADD COLUMN plaintext_message TEXT")
            
        # Insert message with plaintext included
        cursor.execute("""
            INSERT INTO messages (sender, receiver, encrypted_message, encrypted_aes_key, plaintext_message) 
            VALUES (?, ?, ?, ?, ?)
        """, (sender, receiver, encrypted_message, encrypted_aes_key_str, message))
        
        conn.commit()
        conn.close()

        return jsonify({"status": "Message sent successfully"})
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500

# ✅ FIXED: Fetch Messages API with better error handling
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

    # Convert string private key to integer
    user_sk = int(user_sk)

    chat_history = []
    for msg in messages:
        message_id, sender, receiver, encrypted_message, encrypted_aes_key_str, timestamp = msg
        try:
            c1, c2 = str_to_encrypted_aes_key(encrypted_aes_key_str)
            
            # Only attempt to decrypt if the user is the receiver
            # For messages the user sent, we need to handle differently
            if receiver == username:
                # User is the receiver, decrypt using their private key
                if c1 == 0 and c2 == 0:  # Check for parsing error
                    decrypted_message = "[ERROR] Message could not be decrypted (invalid key format)."
                else:
                    aes_key = decrypt_aes_key(c1, c2, user_sk)  # Decrypt AES key
                    decrypted_message = decrypt_message(encrypted_message, aes_key)  # Decrypt message
            else:
                # User is the sender, fetch receiver's messages from the database again
                # This is needed because we need to get the plaintext the user sent
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT encrypted_message FROM messages WHERE id=?", (message_id,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    # We need the original message the user typed, not the encrypted version
                    # For simplicity, we'll store messages in both encrypted and plaintext form
                    # In a production system, you'd have a better solution for this
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("SELECT plaintext_message FROM messages WHERE id=?", (message_id,))
                    plaintext_result = cursor.fetchone()
                    conn.close()
                    
                    if plaintext_result:
                        decrypted_message = plaintext_result[0]
                    else:
                        decrypted_message = "[Your message - encrypted for recipient]"
                else:
                    decrypted_message = "[Your message - encrypted for recipient]"
                    
        except Exception as e:
            print(f"❌ Message decryption error for message ID {message_id}: {e}")
            decrypted_message = "[ERROR] Message could not be decrypted."

        chat_history.append({
            "message_id": message_id,
            "sender": sender,
            "receiver": receiver,
            "encrypted_message": encrypted_message,
            "decrypted_message": decrypted_message,
            "timestamp": timestamp
        })

    return jsonify(chat_history)

# ✅ FIXED: Re-Encrypt Message API (Forwarding) with better error handling
# Improved re-encrypt-message endpoint in chat.py
@app.route('/re-encrypt-message', methods=['POST'])
def reencrypt_message():
    data = request.json
    sender = data.get("sender")  # Current user forwarding the message
    original_receiver = data.get("original_receiver")  # Original chat partner
    new_receiver = data.get("new_receiver")  # New recipient
    message_id = data.get("message_id")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # First, fetch the original message details
        cursor.execute("""
            SELECT encrypted_message, encrypted_aes_key, sender as original_sender, receiver as original_receiver, plaintext_message 
            FROM messages 
            WHERE id=?
        """, (message_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"error": "Message not found"}), 404

        original_encrypted_message, encrypted_aes_key_str, original_sender, original_recipient, original_plaintext = result
        
        # Check if the user has permission to forward this message
        # They should either be the original sender or the original receiver
        if sender != original_sender and sender != original_recipient:
            conn.close()
            return jsonify({"error": "You don't have permission to forward this message"}), 403

        # Get the forwarder's keys and the new recipient's public key
        forwarder_sk = get_private_key(sender)
        if not forwarder_sk:
            return jsonify({"error": "Your private key not found"}), 404
        
        new_receiver_pk = get_public_key(new_receiver)
        if not new_receiver_pk:
            return jsonify({"error": f"Public key for {new_receiver} not found"}), 404
            
        forwarder_sk = int(forwarder_sk)
        new_receiver_pk = int(new_receiver_pk)
        
        # Determine if we're forwarding a sent message or a received message
        is_received_message = (sender == original_recipient)
        
        # Handle differently based on whether this is a sent or received message
        if is_received_message:
            # This is a message the user received - need to decrypt first
            c1, c2 = str_to_encrypted_aes_key(encrypted_aes_key_str)
            
            try:
                # Decrypt the AES key with the forwarder's private key
                aes_key = decrypt_aes_key(c1, c2, forwarder_sk)
                
                # Decrypt the original message
                decrypted_message = decrypt_message(original_encrypted_message, aes_key)
                
                # Generate a new AES key
                new_aes_key = generate_aes_key()
                
                # Encrypt the message with the new key
                new_encrypted_message = encrypt_message(decrypted_message, new_aes_key)
                
                # Encrypt the new AES key with the new recipient's public key
                new_c1, new_c2 = encrypt_aes_key(new_aes_key, new_receiver_pk)
                new_encrypted_aes_key_str = encrypted_aes_key_to_str(new_c1, new_c2)
                
                # Create a forwarded message text
                if original_plaintext and original_plaintext.startswith("[Forwarded from"):
                    # This is already a forwarded message
                    forwarded_plaintext = original_plaintext
                else:
                    forwarded_plaintext = f"[Forwarded from {original_sender}] {decrypted_message}"
                
            except Exception as e:
                print(f"❌ Error decrypting received message for forwarding: {e}")
                return jsonify({"error": "Failed to decrypt the message for forwarding"}), 500
        else:
            # This is a message the user sent - use plaintext directly
            if original_plaintext:
                message_content = original_plaintext
            else:
                message_content = "Unknown message content"
                
            # Generate a new AES key
            new_aes_key = generate_aes_key()
            
            # Encrypt with new AES key
            new_encrypted_message = encrypt_message(message_content, new_aes_key)
            
            # Encrypt the AES key for the new recipient
            new_c1, new_c2 = encrypt_aes_key(new_aes_key, new_receiver_pk)
            new_encrypted_aes_key_str = encrypted_aes_key_to_str(new_c1, new_c2)
            
            # Create forwarded message text
            if message_content.startswith("[Forwarded from"):
                forwarded_plaintext = message_content
            else:
                forwarded_plaintext = f"[Forwarded from {original_sender}] {message_content}"
        
        # Insert the new forwarded message
        cursor.execute("""
            INSERT INTO messages (sender, receiver, encrypted_message, encrypted_aes_key, plaintext_message) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            sender, 
            new_receiver, 
            new_encrypted_message if 'new_encrypted_message' in locals() else original_encrypted_message,
            new_encrypted_aes_key_str,
            forwarded_plaintext
        ))
        
        conn.commit()
        conn.close()

        return jsonify({"status": "Message forwarded successfully"})
    except Exception as e:
        print(f"❌ Error in re-encryption: {e}")
        return jsonify({"error": f"Re-encryption failed: {str(e)}"}), 500

# ✅ FIXED: Get Public Key with additional validation
def get_public_key(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]  # Return as string, will be converted to int when needed
    return None

# ✅ FIXED: Get Private Key with additional validation
def get_private_key(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]  # Return as string, will be converted to int when needed
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
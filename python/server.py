from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import os
from re_encryption import generate_elgamal_keypair  # Import ElGamal key generation

app = Flask(__name__, static_folder="../")  # Serve frontend files
CORS(app)  # Enable CORS for frontend communication

# ✅ Ensure `server.py` uses the correct database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users.db"))

# ✅ Ensure database exists with `is_online` column and encryption keys
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        public_key TEXT NOT NULL,
        private_key TEXT NOT NULL,
        is_online INTEGER DEFAULT 0  -- 0 = Offline, 1 = Online
    )
    ''')

    conn.commit()
    conn.close()

setup_db()

# ✅ Hash passwords before storing
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# ✅ Verify stored hashed password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# ✅ Serve the home page (index.html)
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# ✅ Serve static files (CSS, JS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ✅ User Registration (with password hashing + ElGamal keys)
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = hash_password(password)
    private_key, public_key = generate_elgamal_keypair()  # Generate keys

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, public_key, private_key, is_online) VALUES (?, ?, ?, ?, 0)", 
                       (username, hashed_password, str(public_key), str(private_key)))
        conn.commit()
        return jsonify({"status": "User registered successfully", "public_key": public_key})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

# ✅ User Login (set `is_online = 1`)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result and verify_password(password, result[0]):  # Verify password
        cursor.execute("UPDATE users SET is_online = 1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        return jsonify({"status": "Login successful", "username": username})  # ✅ Return username
    else:
        conn.close()
        return jsonify({"error": "Invalid username or password"}), 401

# ✅ User Logout (set `is_online = 0`)
@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    username = data.get("username")

    if not username:
        print("❌ Logout request missing username")  # Debugging
        return jsonify({"error": "Invalid request"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ Ensure only the logged-out user is affected
    cursor.execute("UPDATE users SET is_online = 0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

    print(f"✅ {username} logged out and marked offline in database.")  # Debugging
    return jsonify({"status": "Logged out successfully"})

# ✅ Fetch Only Active Users
@app.route('/active-users', methods=['GET'])
def get_active_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE is_online = 1")  # ✅ Fetch only online users
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

# ✅ Fetch Public Key of a User
@app.route('/get-public-key/<username>', methods=['GET'])
def get_public_key(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"public_key": result[0]})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

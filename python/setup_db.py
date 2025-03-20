import sqlite3
import os

# Define database path inside the main folder
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users.db"))

# Create or open the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Ensure `users` table has all required columns
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

# ✅ Ensure `messages` table has all required columns, including encrypted AES key
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
print(f"✅ Database setup complete at: {DB_PATH}")

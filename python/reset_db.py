import sqlite3
import os
import random
from re_encryption import generate_elgamal_keypair

# Define database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "users.db"))

def reset_database():
    """Reset the database structure and clear all messages"""
    print(f"⚠️ Resetting database at: {DB_PATH}")
    
    # Check if the database exists, and delete it if it does
    if os.path.exists(DB_PATH):
        try:
            # Create a backup first
            backup_path = f"{DB_PATH}.backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(DB_PATH, backup_path)
            print(f"✅ Database backup created at: {backup_path}")
        except Exception as e:
            print(f"❌ Could not create backup: {e}")
    
    # Create or connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # Create users table with new structure
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        public_key TEXT NOT NULL,
        private_key TEXT NOT NULL,
        is_online INTEGER DEFAULT 0
    )
    ''')
    
    # Create messages table with new structure
    cursor.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        encrypted_message TEXT NOT NULL,
        encrypted_aes_key TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create test users with proper ElGamal keys
    test_users = ["Alice", "Bob", "Charlie", "David", "Eve"]
    for username in test_users:
        # Generate proper ElGamal keypair
        sk, pk = generate_elgamal_keypair()
        
        # Hash password (simple for test)
        password = "password123"
        
        # Store user with proper keys
        cursor.execute(
            "INSERT INTO users (username, password, public_key, private_key, is_online) VALUES (?, ?, ?, ?, 0)",
            (username, password, str(pk), str(sk))
        )
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ Database reset complete. Created {len(test_users)} test users.")
    print("✅ You can now register new users or log in with test users.")

if __name__ == "__main__":
    reset_database()
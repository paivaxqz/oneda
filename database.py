import sqlite3
import hashlib
import secrets
import datetime

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    # Enable WAL mode for better concurrency (Non-blocking reads/writes)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA foreign_keys=ON;')
    c = conn.cursor()
    
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de Bots
    c.execute('''CREATE TABLE IF NOT EXISTS bots (
        user_id INTEGER PRIMARY KEY,
        discord_token TEXT,
        category_ids TEXT,
        response_msg TEXT,
        is_active BOOLEAN DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Tabela de Chaves de Convite
    c.execute('''CREATE TABLE IF NOT EXISTS invite_keys (
        key TEXT PRIMARY KEY,
        is_used BOOLEAN DEFAULT 0,
        used_by_user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(used_by_user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()
    print(f"[+] Banco de dados '{DB_NAME}' inicializado com sucesso.")

def generate_invite_key():
    key = "INVITE-" + secrets.token_hex(4).upper()
    conn = sqlite3.connect(DB_NAME)
    conn.execute('PRAGMA journal_mode=WAL;')
    c = conn.cursor()
    c.execute("INSERT INTO invite_keys (key) VALUES (?)", (key,))
    conn.commit()
    conn.close()
    return key

if __name__ == "__main__":
    init_db()

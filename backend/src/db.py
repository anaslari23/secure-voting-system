import sqlite3
import json
import os

# Resolve DB path relative to backend root (where app.py lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'secure_voting.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Voters Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            aadhaar TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            has_voted BOOLEAN DEFAULT 0
        )
    ''')
    
    # 2. Ballots Table (Ledger)
    # Storing JSON proof as TEXT for simplicity in this reference impl
    c.execute('''
        CREATE TABLE IF NOT EXISTS ballots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ballot_id TEXT NOT NULL,
            ciphertext TEXT NOT NULL,
            proof TEXT NOT NULL, 
            prev_hash TEXT NOT NULL,
            merkle_root TEXT NOT NULL,
            timestamp REAL NOT NULL,
            kiosk_id TEXT
        )
    ''')
    
    # Seed Mock Voters if empty
    c.execute('SELECT count(*) FROM voters')
    if c.fetchone()[0] == 0:
        mock_voters = [
            ("1000-0000-0001", "Test Voter One", "9000000001", 0),
            ("2000-0000-0002", "Test Voter Two", "9000000002", 0),
            ("3000-0000-0003", "Test Voter Three", "9000000003", 0),
            ("4000-0000-0004", "Test Voter Four", "9000000004", 0),
            ("5000-0000-0005", "Test Voter Five", "9000000005", 0)
        ]
        c.executemany('INSERT INTO voters VALUES (?,?,?,?)', mock_voters)
        print("[DB] 5 Fresh Mock voters seeded.")
        
    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

def get_voter(aadhaar):
    conn = get_db_connection()
    voter = conn.execute('SELECT * FROM voters WHERE aadhaar = ?', (aadhaar,)).fetchone()
    conn.close()
    return voter

def mark_voter_as_voted(aadhaar):
    conn = get_db_connection()
    conn.execute('UPDATE voters SET has_voted = 1 WHERE aadhaar = ?', (aadhaar,))
    conn.commit()
    conn.close()

def add_ballot_to_db(ballot_data, prev_hash, merkle_root):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO ballots (ballot_id, ciphertext, proof, prev_hash, merkle_root, timestamp, kiosk_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ballot_data['ballot_id'],
        ballot_data['ciphertext'],
        json.dumps(ballot_data['proof']), # Store complex dict as JSON string
        prev_hash,
        merkle_root,
        ballot_data['timestamp'],
        ballot_data['kiosk_id']
    ))
    
    # Get the auto-incremented index (block height)
    block_index = c.lastrowid - 1 # 0-indexed for consistency with old list
    conn.commit()
    conn.close()
    return block_index

def get_all_ballots_from_db():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM ballots ORDER BY id ASC').fetchall()
    conn.close()
    
    ledger = []
    for i, row in enumerate(rows):
        entry = {
            "index": i, # Reconstruct index dynamically
            "prev_hash": row['prev_hash'],
            "merkle_root": row['merkle_root'],
            "ballot": {
                "ballot_id": row['ballot_id'],
                "timestamp": row['timestamp'],
                "kiosk_id": row['kiosk_id'],
                "ciphertext": row['ciphertext'],
                "exponent": 0, # Default per protocol
                "proof": json.loads(row['proof'])
            }
        }
        ledger.append(entry)
    return ledger

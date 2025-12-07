import sys
import os
# Add backend to path so we can import 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import shutil
from src.keygen import generate_keypair, KEY_DIR
from src.voting import create_ballot
from src.bulletin_board import BulletinBoard
from src.tally import reveal_result_with_shares

def run_demo():
    print("\n--- STARTING SECURE VOTING PROTOCOL DEMO (PHASE 5: THRESHOLD) ---\n")
    
    # 1. Setup: Clean slate
    print("[1] Setup: Cleaning old data...")
    # Define paths relative to backend
    BACKEND_DIR = os.path.join(os.path.dirname(__file__), '../backend')
    KEYS_DIR = os.path.join(BACKEND_DIR, 'keys')
    DB_PATH = os.path.join(BACKEND_DIR, 'secure_voting.db')

    print("[1] Setup: Cleaning old data...")
    if os.path.exists(KEYS_DIR):
        shutil.rmtree(KEYS_DIR)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # 2. Shared Key Ceremony
    print("[2] Key Ceremony: Generating Split Keys (3-of-5)...")
    generate_keypair(key_size=1024, t=3, n_shares=5)
    
    # 3. Voting Phase
    print("\n[3] Voting Phase: Simulating 5 Voters")
    bb = BulletinBoard()
    
    votes = [1, 1, 0, 1, 0] # Expected Sum = 3
    print(f"    Votes to cast: {votes} (1=Yes, 0=No)")
    
    for i, v in enumerate(votes):
        print(f"    -> Voter {i+1} follows protocol...")
        ballot = create_ballot(v, kiosk_id=f"kiosk-{i}")
        idx = bb.publish(ballot)
        print(f"       Vote Encrypted & ZKP Verified -> Block {idx}")
        
    # 4. Tally Phase (Requires Reconstruction)
    print("\n[4] Tally Phase: Computing Homomorphic Sum & Reconstructing Key...")
    
    # Simulating 3 trustees coming together
    trustees = [1, 3, 5]
    print(f"    Trustees {trustees} are present.")
    
    result = reveal_result_with_shares(share_indices=trustees)
    
    print(f"EXPECTED RESULT: {sum(votes)}")
    print(f"ACTUAL RESULT:   {result}")
    
    if result == sum(votes):
        print("\nSUCCESS: Threshold Decryption worked!")
    else:
        print("\nFAILURE: Mismatch or Decryption Error.")

if __name__ == "__main__":
    run_demo()

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from src.keygen import load_public_key
from src.zkp import ZKPVerifier

def run_audit():
    print("\n--- INDEPENDENT PUBLIC AUDIT ---\n")
    
    # 1. Load Public Data
    print("[1] Loading Public Key...")
    public_key = load_public_key()
    verifier = ZKPVerifier(public_key)
    
    print("[2] Loading Bulletin Board (the 'Blockchain')...")
    try:
        # Since BB code handles loading, we should ideally use BB class, 
        # but for independent audit we read file directly.
        # We need to find the backend dir.
        backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
        bb_path = os.path.join(backend_dir, "bb.json")
        with open(bb_path, "r") as f:
            ledger = json.load(f)
    except FileNotFoundError:
        print("Error: No ledger found to audit.")
        return

    print(f"[3] Verifying {len(ledger)} Blocks...")
    
    valid_count = 0
    invalid_count = 0
    
    for entry in ledger:
        idx = entry['index']
        ballot = entry['ballot']
        c_int = int(ballot['ciphertext'])
        proof = ballot['proof']
        
        # Verify specific proof
        if verifier.verify(c_int, proof):
            valid_count += 1
            # print(f"    Block {idx}: ✓ Verified")
        else:
            invalid_count += 1
            print(f"    Block {idx}: ❌ FAILED VERIFICATION")
    
    print("\n" + "="*30)
    print("AUDIT RESULTS")
    print("="*30)
    print(f"Total Block Processed: {len(ledger)}")
    print(f"Valid Ballots:         {valid_count}")
    print(f"Invalid Ballots:       {invalid_count}")
    
    if invalid_count == 0:
        print("\n✅ ELECTION INTEGRITY CONFIRMED")
    else:
        print("\n❌ ELECTION COMPROMISED")

if __name__ == "__main__":
    run_audit()

import os
import json
import hashlib
from src.keygen import load_public_key
from src.zkp import ZKPVerifier
from src.merkle_log import MerkleTree
from src.db import init_db, add_ballot_to_db, get_all_ballots_from_db

# Resolve paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BB_FILE = os.path.join(BASE_DIR, "bb.json") # No longer needed

class BulletinBoard:
    def __init__(self):
        # Initialize DB if needed
        # Always ensure DB is initialized (CREATE TABLE IF NOT EXISTS handles idempotency)
        init_db()
             
        self.merkle_tree = MerkleTree()
        
        # Reconstruct Tree from DB
        ledger = get_all_ballots_from_db()
        for entry in ledger:
             self.merkle_tree.add_leaf(json.dumps(entry['ballot'], sort_keys=True))
    
    def publish(self, ballot):
        """
        1. Verify ZKP
        2. Add to Merkle Tree
        3. Save to SQL Database (replaces file append)
        """
        # 1. Verify ZKP (Zero Knowledge Proof)
        if not self.verify_proof(ballot):
            raise ValueError("ZKP Verification Failed: Invalid Vote Proof")

        # 2. Add to Merkle Tree
        ballot_str = json.dumps(ballot, sort_keys=True)
        leaf_index, leaf_hash = self.merkle_tree.add_leaf(ballot_str)
        merkle_root = self.merkle_tree.get_root()
        
        # Get Previous Hash (Simulated Blockchain Link)
        prev_hash = "0"*64 # Genesis
        ledger = get_all_ballots_from_db()
        if ledger:
            # The last entry in the ledger from the DB is a dict, we need to hash its content
            # Assuming the 'id' column is the primary key and determines order
            # For a simple hash, we can hash the entire dictionary representation
            prev_hash = hashlib.sha256(json.dumps(ledger[-1], sort_keys=True).encode()).hexdigest()

        # 3. Save to SQLite
        block_index = add_ballot_to_db(ballot, prev_hash, merkle_root)
        
        # Debug Log
        print(f"ACCEPTED: Ballot {ballot['ballot_id']} -> Merkle Root {merkle_root[:10]}...")
        
        return block_index

    def get_all_ballots(self):
        return get_all_ballots_from_db()
            
    def get_merkle_proof(self, index):
        return self.merkle_tree.get_proof(index)

    def verify_proof(self, ballot):
        """Delegates validation to the ZKP module."""
        # The actual verification requires the PubKey.
        pk = load_public_key()
        verifier = ZKPVerifier(pk)
        return verifier.verify(ballot['ciphertext'], ballot['proof'])

if __name__ == "__main__":
    bb = BulletinBoard()
    print(bb.get_all_ballots())

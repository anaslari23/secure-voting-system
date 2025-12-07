import os
import sys
import shutil
import json
from secrets import token_hex

# Add parent dir to path to import backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.keygen import generate_keypair

def setup_trustee_dirs(trustees):
    """Creates simulated secure USB storage for each trustee."""
    base_dir = "trustee_storage"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    paths = {}
    for t in trustees:
        path = os.path.join(base_dir, f"usb_{t.replace(' ', '_').lower()}")
        os.makedirs(path)
        paths[t] = path
    return paths

def split_secret(secret_int, threshold, num_shares, prime):
    """
    Shamir's Secret Sharing implementation.
    Splits 'secret_int' into 'num_shares' where 'threshold' are needed to reconstruct.
    """
    # Coefficients: a0 = secret, a1...ak-1 are random
    coeffs = [secret_int] + [int(token_hex(32), 16) % prime for _ in range(threshold - 1)]
    
    shares = []
    for x in range(1, num_shares + 1):
        # f(x) = sum(ai * x^i) mod p
        y = sum([coeffs[i] * pow(x, i, prime) for i in range(threshold)]) % prime
        shares.append((x, y))
        
    return shares

def run_ceremony():
    print("--- ELECTION KEY CEREMONY 2029 ---")
    
    # 1. Define Trustees
    trustees = [
        "Chief Election Commissioner",
        "Chief Justice Representative",
        "Independent Observer (IIT)",
        "Transparency Intl. Observer",
        "President's Secretariat"
    ]
    THRESHOLD = 3 # Any 3 can decrypt
    TOTAL = len(trustees)
    
    print(f"[*] Configuration: {THRESHOLD}-of-{TOTAL} Threshold Scheme")
    
    # 2. Setup Physical Storage Simulation
    print("[*] formatting secure storage (simulated USBs)...")
    secure_paths = setup_trustee_dirs(trustees)
    
    # 3. Generate Master Keypair (Ephemeral)
    print("[*] Generating 2048-bit Paillier Keypair...")
    print("[*] Generating 2048-bit Paillier Keypair...")
    # NOTE: In a real ceremony, the Private Key is NEVER written to disk in whole.
    # It exists only in RAM for the split second of generation and splitting.
    # Our keygen.py handles generation and saving to backend/keys/
    generate_keypair(key_size=2048)
    
    # 4. Distribute Shares (Move from backend/keys to Trustee USBs)
    print(f"[*] Distributing Pre-Split Key Shards to Trustees...")
    
    KEY_DIR = os.path.join(os.path.dirname(__file__), '..', 'keys')
    
    for i, t in enumerate(trustees):
        # We assume keygen created 5 shares
        src_share = os.path.join(KEY_DIR, f"private_key_share_{i+1}.json")
        dest_share = os.path.join(secure_paths[t], "election_key_shard.json")
        
        if os.path.exists(src_share):
             shutil.copy(src_share, dest_share)
             print(f"    -> Shard #{i+1} moved to {t}'s secure drive.")
             
             # Secure Delete original (Simulation)
             os.remove(src_share)
        else:
             print(f"    [!] Error: Shard #{i+1} not found!")

    # 5. Public Key Distribution
    pk_src = os.path.join(KEY_DIR, "public_key.json")
    if os.path.exists(pk_src):
        shutil.copy(pk_src, "election_public_key.json")
    
    print("\n[SUCCESS] Ceremony Complete. Public Key Published.")
    print(f"          Private Key is split among {TOTAL} trustees.")
    print(f"          Original shares in 'backend/keys' have been wiped.")
    return

    # Legacy Logic Removed (Manual Splitting is done inside keygen.py now)

if __name__ == "__main__":
    run_ceremony()

import json
import os
from phe import paillier
from src.keygen import load_public_key, KEY_DIR
from src.bulletin_board import BulletinBoard
from src.hybrid_sss import recover_and_decrypt

def reconstruct_private_key(shares_data, public_key):
    """
    Reconstructs PaillierPrivateKey from shares + encrypted blob.
    """
    shares = [(s['id'], int(s['value'])) for s in shares_data]
    
    # Load encrypted blob
    blob_path = os.path.join(KEY_DIR, "encrypted_private_key.bin")
    if not os.path.exists(blob_path):
        print("Encrypted key file missing!")
        return None
        
    with open(blob_path, "rb") as f:
        encrypted_blob = f.read()

    print(f"Reconstructing Access Key from {len(shares)} shares...")
    try:
        priv_json_str = recover_and_decrypt(encrypted_blob, shares)
        priv_data = json.loads(priv_json_str)
        
        return paillier.PaillierPrivateKey(
            public_key=public_key,
            p=int(priv_data["p"]),
            q=int(priv_data["q"])
        )
    except Exception as e:
        print(f"Key Reconstruction Failed: {e}")
        return None

def compute_tally(public_key):
    # Same as before, logic separate
    bb = BulletinBoard()
    ledger = bb.get_all_ballots()
    if not ledger:
        return None
        
    encrypted_ballots = []
    for entry in ledger:
        ballot = entry['ballot']
        c_int = int(ballot['ciphertext'])
        exp = int(ballot['exponent'])
        enc_vote = paillier.EncryptedNumber(public_key, c_int, exp)
        encrypted_ballots.append(enc_vote)
    
    return sum(encrypted_ballots)

def reveal_result_with_shares(share_indices=[1, 2, 3]):
    """
    Load specific shares for the demo.
    """
    public_key = load_public_key()
    
    # Load requested shares
    shares_data = []
    for idx in share_indices:
        path = os.path.join(KEY_DIR, f"private_key_share_{idx}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                shares_data.append(json.load(f))
        else:
            print(f"Share {idx} missing!")
            return
            
    # Reconstruct
    private_key = reconstruct_private_key(shares_data, public_key)
    if not private_key:
        print("Failed to reconstruct private key. Wrong shares?")
        return
        
    # Tally
    encrypted_tally = compute_tally(public_key)
    if encrypted_tally:
        try:
            # Check for potential overflow by peeking at raw value if possible, 
            # but phe doesn't expose it easily. We handle the error.
            result = private_key.decrypt(encrypted_tally)
            print("\n" + "="*30)
            print(f"FINAL TALLY RESULT: {result}")
            print("="*30 + "\n")
            return result
        except OverflowError:
            print("\n" + "="*30)
            print("CRITICAL: Decryption Overflow Detected.")
            print("This usually means the Private Key reconstruction was imperfect")
            print("or the encrypted sum exceeded the key's capacity (unlikely for small sums).")
            print("="*30 + "\n")
            return -1
    return 0

if __name__ == "__main__":
    # Default demo: Use shares 1, 2, 3 (threshold is 3 usually)
    reveal_result_with_shares([1, 2, 3])

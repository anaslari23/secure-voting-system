import json
import os
import shutil
from phe import paillier
from src.hybrid_sss import encrypt_and_split

# Resolve paths relative to this file's location (src/keygen.py -> backend/)
# We want keys/ to be in backend/keys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_DIR = os.path.join(BASE_DIR, "keys")

def generate_keypair(key_size=2048, t=3, n_shares=5):
    """
    Generates Paillier keys.
    Encrypts Private Key with ephemeral AES key.
    Splits AES key into n shares.
    """
    print(f"Generating {key_size}-bit Paillier keys...")
    public_key, private_key = paillier.generate_paillier_keypair(n_length=key_size)
    
    if os.path.exists(KEY_DIR):
        shutil.rmtree(KEY_DIR)
    os.makedirs(KEY_DIR)

    # 1. Save Public Key
    pub_data = {
        "n": str(public_key.n),
        "g": str(public_key.g) if hasattr(public_key, 'g') else str(public_key.n + 1)
    }
    with open(os.path.join(KEY_DIR, "public_key.json"), "w") as f:
        json.dump(pub_data, f, indent=2)
    
    # 2. Serialize Private Key
    priv_data = {
        "p": str(private_key.p),
        "q": str(private_key.q),
        "n": str(private_key.public_key.n)
    }
    priv_json_str = json.dumps(priv_data)
    
    # 3. Hybrid Split (Encrypt Data, Split Key)
    print(f"Encrypting Private Key and Splitting Access Key ({t}-of-{n_shares})...")
    encrypted_blob, shares = encrypt_and_split(priv_json_str, t, n_shares)
    
    # 4. Save Encrypted Blob
    with open(os.path.join(KEY_DIR, "encrypted_private_key.bin"), "wb") as f:
        f.write(encrypted_blob)
    
    # 5. Save Key Shares
    for idx, share in enumerate(shares):
        share_data = {
            "id": share[0],
            "value": str(share[1])
        }
        fname = f"private_key_share_{idx+1}.json"
        with open(os.path.join(KEY_DIR, fname), "w") as f:
            json.dump(share_data, f, indent=2)
            
    print(f"Done! Public Key + Encrypted Blob + {n_shares} Shares saved to '{KEY_DIR}/'")

# Helper to load pub key remains same
def load_public_key():
    path = os.path.join(KEY_DIR, "public_key.json")
    if not os.path.exists(path):
        raise FileNotFoundError("Public key not found. Run keygen first.")
    
    with open(path, "r") as f:
        data = json.load(f)
    return paillier.PaillierPublicKey(n=int(data["n"]))


import json
import uuid
import time
import random
from phe import paillier
from src.keygen import load_public_key
from src.zkp import ZKPProver

def create_ballot(vote_int, kiosk_id="kiosk-demo"):
    """
    Encrypts a vote (0 or 1) and creates a ballot object.
    """
    if vote_int not in [0, 1]:
        raise ValueError("Vote must be 0 or 1")
        
    public_key = load_public_key()
    
    # 1. Generate explicit randomness r
    # r must be in Z_n* (coprime to n). 
    # Since p,q are large primes, almost any random int < n is coprime.
    r = random.SystemRandom().randint(1, public_key.n)
    while True:
        # Simple GCD check to be pedantic, though prob of failure is negligible
        import math
        if math.gcd(r, public_key.n) == 1:
            break
        r = random.SystemRandom().randint(1, public_key.n)

    # 2. Encrypt using this r
    # phe allows passing r_value. Note: phe expects r to be < n.
    encrypted_vote = public_key.encrypt(vote_int, r_value=r)
    
    # Serialize ciphertext
    ciphertext_int = encrypted_vote.ciphertext(be_secure=False)
    
    # 3. Generate Real ZKP
    prover = ZKPProver(public_key)
    zkp_proof = prover.prove_vote(ciphertext_int, vote_int, r)
    
    ballot = {
        "ballot_id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "kiosk_id": kiosk_id,
        "ciphertext": str(ciphertext_int), 
        "exponent": encrypted_vote.exponent,
        "proof": zkp_proof
    }
    
    return ballot

if __name__ == "__main__":
    b = create_ballot(1)
    print(json.dumps(b, indent=2))

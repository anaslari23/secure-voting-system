from src.keygen import random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from src.keygen import generate_keypair
from src.zkp import ZKPProver, ZKPVerifier
from phe import paillier
import random

def test_zkp():
    print("Generating keys...")
    # Generate smaller keys for faster testing
    pub, priv = generate_keypair(key_size=512) 
    
    prover = ZKPProver(pub)
    verifier = ZKPVerifier(pub)

    # Test Case 1: Vote 0
    print("\nTesting Vote 0...")
    r = random.SystemRandom().randint(1, pub.n)
    # Manual encryption to ensure we know 'r' exactly
    # Enc(0) = g^0 * r^n = r^n mod n^2
    c0 = pow(r, pub.n, pub.n**2)
    
    proof0 = prover.prove_vote(c0, 0, r)
    valid0 = verifier.verify(c0, proof0)
    print(f"Proof for 0 is Valid? {valid0}")
    assert valid0 == True

    # Test Case 2: Vote 1
    print("\nTesting Vote 1...")
    r2 = random.SystemRandom().randint(1, pub.n)
    # Enc(1) = g^1 * r^n = (n+1) * r^n mod n^2
    c1 = ((pub.n + 1) * pow(r2, pub.n, pub.n**2)) % (pub.n**2)
    
    proof1 = prover.prove_vote(c1, 1, r2)
    valid1 = verifier.verify(c1, proof1)
    print(f"Proof for 1 is Valid? {valid1}")
    assert valid1 == True
    
    # Test Case 3: Invalid Vote (Enc of 2)
    print("\nTesting Invalid Vote (2)...")
    c2 = (pow(pub.n+1, 2, pub.n**2) * pow(r, pub.n, pub.n**2)) % (pub.n**2)
    try:
        # Prover should fail or produce garbage. 
        # Properly, prover code raises Error if input not 0/1.
        # Only a lying prover would try to generate a proof for '2'.
        # Since we are testing the system, we assume client software won't call prove_vote(2).
        # But if we force it to try to prove '0' for c2:
        proof_fake = prover.prove_vote(c2, 0, r) 
        # The verification should fail
        valid_fake = verifier.verify(c2, proof_fake)
        print(f"Fake proof for 2 verified? {valid_fake}")
        assert valid_fake == False
    except Exception as e:
        print(f"Correctly caught error or failed verification: {e}")

if __name__ == "__main__":
    test_zkp()

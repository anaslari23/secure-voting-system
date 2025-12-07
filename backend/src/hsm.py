import hashlib
import json
import uuid
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization

class VirtualHSM:
    """
    Simulates a FIPS 140-2 Level 4 Hardware Security Module.
    The private key NEVER leaves the `_private_key` attribute.
    """
    def __init__(self, key_label="MASTER_ELECTION_KEY"):
        self.label = key_label
        self.device_id = str(uuid.uuid4())
        print(f"[HSM] Initializing Secure Enclave: {self.device_id}")
        
        # GENERATE KEYS INSIDE THE HSM
        # We use RSA for digital signatures (simulating the authority key)
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self._private_key.public_key()
        print("[HSM] Keypair Generated internally. Private Key is LOCKED.")

    def get_public_key_pem(self):
        """Export Public Key (Allowed)"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    def sign_data(self, data_bytes):
        """
        Cryptographic Signing Function.
        Input: Raw bytes
        Output: Digital Signature
        """
        signature = self._private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def self_test(self):
        """Simulate Power-On Self Test (POST)"""
        try:
            # Test signing
            msg = b"test"
            sig = self.sign_data(msg)
            self.public_key.verify(
                sig, 
                msg, 
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), 
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"[HSM] SELF TEST FAILED: {e}")
            return False

if __name__ == "__main__":
    hsm = VirtualHSM()
    print("Public Key:\n", hsm.get_public_key_pem())
    
    # Try to access private key (Simulation of failure)
    try:
        print(hsm._private_key) 
        print("Warning: In Python we can't truly hide memory, but logic forbids export.")
    except:
        pass
        
    sig = hsm.sign_data(b"Vote 123")
    print(f"Signature generated: {sig.hex()[:20]}...")

import json
from cryptography.fernet import Fernet
from src.sss import split_secret, recover_secret

# SSS works on integers. Fernet key is 32 bytes (base64 string usually).
# We decode base64 to bytes, treat as int, split it.

def encrypt_and_split(payload_str, t, n):
    """
    Encrypts payload with a fresh key, splits the key.
    Returns: (ciphertext_bytes, shares_list)
    """
    # 1. Generate Symmetric Key
    key = Fernet.generate_key() # 32 bits url-safe base64-encoded bytes
    f = Fernet(key)
    
    # 2. Encrypt Payload
    token = f.encrypt(payload_str.encode())
    
    # 3. Split Key
    # Key is bytes. Convert to int.
    key_int = int.from_bytes(key, 'big')
    shares = split_secret(key_int, t, n)
    
    return token, shares

def recover_and_decrypt(token, shares):
    """
    Recovers key from shares, decrypts token.
    """
    # 1. Recover Key Int
    key_int = recover_secret(shares)
    
    # 2. Convert back to bytes
    # Fernet keys are 32 bytes (url-safe base64), but generate_key returns the b64 string.
    # We need to be careful about length.
    # Fernet.generate_key() returns 44 bytes (32 bytes entropy b64 encoded).
    
    # Reconstruct bytes. bit_length -> bytes
    # It should be 44 bytes exactly for a Fernet key?
    # Let's try flexible conversion.
    bit_len = key_int.bit_length()
    byte_len = (bit_len + 7) // 8
    key_bytes = key_int.to_bytes(byte_len, 'big')
    
    # 3. Decrypt
    f = Fernet(key_bytes)
    payload_bytes = f.decrypt(token)
    return payload_bytes.decode()

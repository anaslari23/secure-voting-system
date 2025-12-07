# Data Formats & Schemas

## 1. Public Key (`key_pub.json`)
Public parameters required for encryption.
```json
{
  "n": "123456789...",      // Hex string of modulus n
  "g": "123456789...",      // Hex string (usually n+1)
  "bits": 2048              // Key size
}
```

## 2. Encrypted Ballot (`ballot.json`)
The vote artifact submitted by the Kiosk.
```json
{
  "ballot_id": "uuid-v4",
  "timestamp": "2024-01-01T12:00:00Z",
  "ciphertext": "abcdef1234...", // Hex of c = g^m * r^n mod n^2
  "kiosk_id": "kiosk-001",
  "signature": "base64-signature" // Signed by Kiosk RSA key
}
```

## 3. Zero-Knowledge Proof (`proof.json`)
Attached to the ballot to prove validity ($v \in \{0, 1\}$).
Using Non-Interactive Zero-Knowledge (NIZK) via Fiat-Shamir.
```json
{
  "challenge_hash": "sha256-hash",
  "response_0": {
    "z": "hex...",
    "e": "hex..."
  },
  "response_1": {
    "z": "hex...",
    "e": "hex..."
  }
}
```

## 4. Bulletin Board Entry
The final record stored on the ledger.
```json
{
  "entry_index": 1,
  "prev_hash": "hash-of-prev-entry",
  "ballot": { ... }, // The ballot object
  "proof": { ... }   // The proof object
}
```

## 5. Tally Result
```json
{
  "total_cipher": "hex...", // Product of all c_i
  "decrypted_count": 42,    // The final count
  "decryption_proof": "hex..." // Proof that decryption key was applied correctly
}
```

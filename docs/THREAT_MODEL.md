# Threat Model

## 1. Assets to Protect
1.  **Vote Privacy**: No one should know how a voter voted.
2.  **Vote Integrity**: The tally must reflect exactly the votes cast.
3.  **System Availability**: The election process must not be disrupted.

## 2. Adversaries
| Adversary | Description | Capability |
| :--- | :--- | :--- |
| **Nation-State Actor** | Highly sophisticated, unlimited resources. | Network DoS, zero-day exploits, advanced malware. |
| **Corrupt Insider** | Election official or sysadmin. | Physical access to servers, knowledge of keys. |
| **Political Coercer** | Local strongman. | Physical intimidation of voters at the moment of voting. |
| **Coordinated Script Kiddies** | Internet trolls. | Basic DDoS, phishing. |

## 3. Attack Vectors & Mitigations

### 3.1 Coercion / Vote Buying
- **Attack**: A "boss" demands the voter show their screen or forces them to vote a certain way.
- **Mitigation (Kiosk)**: Voting happens in a supervised, private booth (physical privacy).
- **Mitigation (Remote - Future)**: "Panic passwords" or "fake credentials" that generate plausible but invalid votes (hard to implement perfectly).

### 3.2 Endpoint Compromise (Malware)
- **Attack**: Malware on the voter's phone flips the vote before encryption.
- **Mitigation (Kiosk)**: Hardened, single-purpose hardware. Boot-loader locking. Regular state resets.
- **Verification**: Voter gets a *paper receipt* (VVPAT-style) or a *verification code* to check on a secondary device that their *encrypted* vote matches intent.

### 3.3 Server-Side Manipulation
- **Attack**: Sysadmin modifies the database to add fake ballots.
- **Mitigation**: **Append-Only Bulletin Board**. All ballots are signed. Public auditors detect insertions that don't match the qualified voter list.
- **Mitigation**: **Zero-Knowledge Proofs**. Any inserted ballot must come with a proof of validity. Fake ballots without valid proofs are rejected by auditors.

### 3.4 Key Compromise
- **Attack**: Attacker steals the private decryption key.
- **Mitigation**: **Threshold Cryptography**. The key is split into $n$ shares. Decryption requires $t$ actors to cooperate. Compromising $t-1$ actors yields nothing.

## 4. Risk Assessment Matrix
| Risk | Probability | Impact | Mitigation Status |
| :--- | :--- | :--- | :--- |
| DDoS on Voting Day | High | High | Distributed Bulletin Board, CDN, Offline Mode (Kiosk stores locally, syncs later). |
| Kiosk Physical Tampering | Medium | Critical | Physical seals, Trusted Platform Module (TPM) attestation. |
| Mathematical Breakthrough (Factorization) | Extremely Low | Critical | Use large key sizes (e.g., Paillier 4096-bit). |

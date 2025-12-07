# System Architecture

## 1. High-Level Overview
The system follows a standard **End-to-End Verifiable** voting architecture.
- **Voters** use **Trusted Kiosks**.
- **Votes** are stored on a public **Bulletin Board**.
- **Tallying** is performed by a distributed **Tally Authority**.
- **Verification** is open to **Public Auditors**.

## 2. Component Diagram

```mermaid
graph TD
    User((Voter)) -->|Authenticates| ID[Identity Provider\n(Aadhaar/Database)]
    User -->|Casts Vote| Kiosk[Supervised Kiosk\n(Client App)]
    
    subgraph Polling Station
    Kiosk -->|Generates| ZKP[Zero-Knowledge Proof]
    Kiosk -->|Encrypts| Ballot[Encrypted Ballot]
    Kiosk -->|Prints| Receipt[Paper Receipt/Hash]
    end
    
    Kiosk -->|Submits| BB[Bulletin Board\n(Public Ledger/Database)]
    
    subgraph Election Commission
    Auth[Tally Authority\n(Key Holders)]
    Auth -->|Reads| BB
    Auth -->|Homomorphic Add| EncTally[Encrypted Tally]
    Auth -->|Threshold Decrypt| Result[Final Result]
    Auth -->|Publishes| Proofs[Decryption Proofs]
    end
    
    subgraph Public
    Auditor((Independent Auditor))
    Auditor -->|Verifies| BB
    Auditor -->|Verifies| Proofs
    Auditor -->|Checks| Receipt
    end
    
    Result -->|Announced| PublicDisplay
```

## 3. Data Flow
1.  **Voter** -> **Kiosk**: Selects candidate (Plaintext: $v$).
2.  **Kiosk** -> **Internal**:
    -   Generates Randomness $r$.
    -   Computes $C = Enc_{pk}(v, r)$.
    -   Computes $\pi = Proof(v \in \{0,1\})$.
3.  **Kiosk** -> **Bulletin Board**: Posts $\{C, \pi\}$.
4.  **Bulletin Board**: Verifies $\pi$. If valid, appends to log. Returns transaction ID/Hash.
5.  **Kiosk** -> **Voter**: Prints Receipt ($Hash(C)$).
6.  **Tally Authority**:
    -   Retrieves all legitimate $C_i$.
    -   Computes $C_{final} = \prod C_i \pmod{n^2}$.
    -   Jointly decrypts $C_{final} \to Tally$.

## 4. Key Technologies
- **Frontend**: Flutter / React (Kiosk Interface).
- **Backend API**: Go / Rust (High performance).
- **Database**: PostgreSQL (with append-only constraints) or Hyperledger Fabric (if blockchain desired).
- **Crypto Library**: `libpaillier` (C++) or `paillier-bigint` (Rust).

# System Requirements Document (SRD)

## 1. Introduction
This document outlines the requirements for the **Secure Online Voting System** targeting Indian national elections. The primary initial deployment model is **Supervised Kiosks** to ensure high security and trust, bridging the gap between traditional EVMs and fully remote voting.

## 2. Scope
The system will enable voters to cast encrypted ballots from authorized Kiosk devices. The votes are homomorphically tallied without decryption. Zero-Knowledge Proofs (ZKPs) ensure vote validity and tally correctness.

## 3. specific Use-Case: Supervised Kiosk
- **Voter Location**: Polling stations equipped with connected Kiosk devices.
- **Why**: Mitigates "device compromise" risks (malware on personal phones) and "coercion" risks (family/boss pressure), while allowing centralized digital counting and verification.

## 4. Functional Requirements

### 4.1 Voter Interface (Kiosk)
- **FR-1**: Authenticate voter using existing ID infrastructure (simulate integration with Aadhaar/EPIC).
- **FR-2**: Display ballot with candidates/parties.
- **FR-3**: Encrypt vote using Paillier Encryption immediately upon selection.
- **FR-4**: Generate a Zero-Knowledge Proof (ZKP) that the encrypted vote is valid (represents a single choice) without revealing the choice.
- **FR-5**: Print (or display code) a "Vote Receipt" containing the tracking hash of the encrypted vote.

### 4.2 Bulletin Board (Public Ledger)
- **FR-6**: Accept encrypted ballots + ZKPs from Kiosks.
- **FR-7**: Verify ZKPs before accepting ballot into the append-only ledger.
- **FR-8**: Provide an API for public auditors to download the full chain of ballots.

### 4.3 Tally Authority
- **FR-9**: Compute the "Encrypted Tally" by homomorphically adding valid encrypted ballots.
- **FR-10**: Perform threshold decryption of the final Encrypted Tally (requires $t$ out of $n$ key holders).
- **FR-11**: Generate a ZKP proving the decryption was correct.

## 5. Non-Functional Requirements
- **NFR-1 (Security)**: End-to-end verifiability (Individually Verifiable + Universally Verifiable).
- **NFR-2 (Privacy)**: Correctness of tally must not reveal individual votes (Receipt-freeness for remote, though Kiosk mitigates this).
- **NFR-3 (Performance)**: Support high throughput (e.g., 1000 votes/sec ingestion).
- **NFR-4 (Accessibility)**: UI must support multiple languages and accessibility modes (audio, high contrast).

## 6. Cryptographic Primitives
- **Encryption**: Paillier Homomorphic Encryption.
- **Proofs**: Schnorr-like / Sigma protocols for range proofs (1-out-of-L).
- **Signatures**: Digital signatures (RSA/ECDSA) for ballot authenticity.

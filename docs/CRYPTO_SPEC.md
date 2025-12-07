# Cryptographic Specification

## 1. System Parameters
- **Security Parameter ($\lambda$)**: 2048 or 4096 bits (Key size).
- **Encryption Scheme**: Paillier Cryptosystem.
- **Vote Encoding**:
  - `0`: Vote for "No" / "Option A" (depending on context).
  - `1`: Vote for "Yes" / "Option B".
  - *Multi-candidate extension*: $Base^k$ encoding (not covered in MVP).

## 2. Paillier Cryptosystem

### 2.1 Key Generation (`KeyGen`)
1.  Choose two large primes $p, q$ of equal length.
2.  Compute $n = p \cdot q$.
3.  Compute $\lambda = \text{lcm}(p-1, q-1)$.
4.  Choose generator $g = n + 1$.
5.  **Public Key**: $PK = (n, g)$.
6.  **Private Key**: $SK = (\lambda, \mu)$ where $\mu = L(g^\lambda \bmod n^2)^{-1} \bmod n$, and $L(x) = \frac{x-1}{n}$.

### 2.2 Encryption (`Enc`)
To encrypt a ballot $m \in \{0, 1\}$:
1.  Select random $r \in \mathbb{Z}_n^*$.
2.  Compute ciphertext $c = g^m \cdot r^n \pmod{n^2}$.

### 2.3 Decryption (`Dec`)
To decrypt $c$:
1.  Compute $m = L(c^\lambda \bmod n^2) \cdot \mu \bmod n$.

### 2.4 Homomorphic Addition (`Add`)
Given encryption of votes $c_1 = E(v_1), c_2 = E(v_2)$:
1.  Compute $C_{sum} = c_1 \cdot c_2 \pmod{n^2}$.
2.  Result is encryption of $v_1 + v_2$.

## 3. Zero-Knowledge Proofs (ZKP)
We need to prove a vote $v$ is either $0$ or $1$ without revealing which.
We use a **Disjunctive Chaum-Pedersen Proof** (Cramer-Damgård-Schoenmakers).

### 3.1 Prover (Voter/Kiosk)
Statement: $c$ is an encryption of $0$ OR $c$ is an encryption of $1$.
Randomness used: $r$.

**Case $v=0$ ($c = r^n \mod n^2$)**:
1.  Real proof for 0: Pick random $w, u_1, z_1$.
    - $a_1 = g^{u_1} \cdot z_1^n \pmod{n^2}$ (Simulation for 1)
    - $b_1 = c^{u_1} \cdot (1+n)^{z_1} \pmod{n^2}$ (Wait, standard Paillier ZKP uses simpler form)

**Simplified Protocol (1-out-of-2)**:
Let $u$ be the ciphertext.
Proof that $\exists r$ such that $u = r^n \pmod{n^2}$ OR $u = (1+n) \cdot r^n \pmod{n^2}$.

1.  **Commit**: Prover picks randoms.
2.  **Challenge**: Verifier (or Fiat-Shamir Hash) sends challenge $e$.
3.  **Response**: Prover sends responses ensuring $e = e_0 + e_1$.
    - If $v=0$, real proof for branch 0, simulate branch 1.
    - If $v=1$, simulate branch 0, real proof for branch 1.

*Note: For the prototype, we will use the specific `1-out-of-2` ZKP implementation provided by the library or implement the CDS94 protocol manually.*

## 4. Tallying Protocol
1.  Aggregator collects valid ciphertexts $C_1, ..., C_k$.
2.  Computes $C_{total} = \prod_{i=1}^k C_i \pmod{n^2}$.
3.  Authority decrypts $C_{total}$ to get total "Yes" votes.

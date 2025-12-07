# Use Case Definitions

## Use Case 1: Voter at Supervised Kiosk (Primary)
**Actor**: Eligible Voter
**Precondition**: Voter physically present at polling station, identity verified by poll worker.

**Main Flow**:
1. **Activation**: Poll worker activates the Kiosk for one session.
2. **Selection**: Voter sees a digital ballot on the touchscreen.
3. **Voting**: Voter selects a candidate.
4. **Encryption**: System generates random randomness $r$, encrypts vote $E(v, r)$.
5. **ProofGen**: System generates ZKP $\pi$ proving $v \in \{0,1\}$.
6. **Submission**: $E(v,r)$ and $\pi$ are sent to the Bulletin Board.
7. **Receipt**: Voter receives a paper receipt with a hash $H(E(v,r))$ to verify their vote was "Included".
8. **Completion**: Session closes; Kiosk ready for next voter.

## Use Case 2: Independent Public Audit
**Actor**: Auditor / Opposition Party / NGO
**Precondition**: Election phase is "Voting" or "Tallying".

**Main Flow**:
1. **Download**: Auditor downloads the full list of encrypted ballots and ZKPs from Bulletin Board.
2. **Verify Ballots**:For each ballot $i$:
   - Check signature of the Kiosk.
   - Verify ZKP $\pi_i$ (proves vote is valid format).
3. **Verify Tally**:
   - Re-compute Homomorphic Sum $E_{total} = \prod E_i$.
   - Verify Tally Decryption Proof released by Election Commission.
4. **Result**: Auditor confirms the announced winner matches the cryptographic evidence.

## Use Case 3: Key Ceremony (Setup)
**Actor**: Election Commissioners (Key Trustees)

**Main Flow**:
1. **Generation**: Trustees run a distributed key generation (DKG) protocol.
2. **Shares**: Each trustee gets a private key share $s_i$.
3. **Public Key**: The master Public Key $PK$ is generated and published.
4. **Backup**: Shares are backed up in Hardware Security Modules (HSMs).

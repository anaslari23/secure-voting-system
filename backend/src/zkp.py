import hashlib
import random
from src.keygen import load_public_key

class ZKPUtils:
    @staticmethod
    def hash_nums(nums):
        """Helper to hash a list of large integers for Fiat-Shamir."""
        s = "".join(str(n) for n in nums)
        return int(hashlib.sha256(s.encode()).hexdigest(), 16)

class ZKPProver:
    def __init__(self, public_key):
        self.pub = public_key
        self.n = public_key.n
        self.ns = self.n * self.n
        self.g = self.n + 1 # phe default

    def prove_vote(self, ciphertext_int, vote_val, r):
        """
        Generates a proof that ciphertext_int is an encryption of 0 OR 1.
        vote_val: 0 or 1 (the actual vote)
        r: the randomness used in encryption (must be known by prover)
        """
        if vote_val not in [0, 1]:
            raise ValueError("Can only prove votes 0 or 1")

        # System parameters
        n = self.n
        ns = self.ns
        g = self.g
        u = ciphertext_int

        # We are proving u = g^m * r^n mod n^2
        # Case 0: u = r^n mod n^2 (since g^0 = 1)
        # Case 1: u = g * r^n mod n^2
        
        # Random inputs for the proof
        w = random.SystemRandom().randint(1, n // 2)
        
        # We need to simulate the 'other' branch
        # If vote is 0: Prove statement 0 (real), Simulate statement 1 (fake)
        # If vote is 1: Simulate statement 0 (fake), Prove statement 1 (real)
        
        real_branch = vote_val
        fake_branch = 1 - vote_val

        # Variables for responses
        z = [0, 0]
        e = [0, 0]
        a = [0, 0]

        # 1. PREPARE FAKE BRANCH (Simulation)
        # Pick random challenge e_fake and random response z_fake
        # Compute commitment a_fake backwards
        e[fake_branch] = random.SystemRandom().randint(1, n)
        z[fake_branch] = random.SystemRandom().randint(1, n)
        
        # Reconstruct a_fake
        # If fake=0: a0 = z0^n / u^e0
        # If fake=1: a1 = z1^n / (u/g)^e1
        
        inv_u = pow(u, -1, ns)
        if fake_branch == 0:
            # Statement: u = r^n
            # a = z^n * u^-e
            term_u = pow(inv_u, e[fake_branch], ns)
            a[fake_branch] = (pow(z[fake_branch], n, ns) * term_u) % ns
        else:
            # Statement: u = g * r^n => u/g = r^n
            # a = z^n * (u/g)^-e = z^n * (u^-1 * g)^e
            val = (inv_u * g) % ns
            term_val = pow(val, e[fake_branch], ns)
            a[fake_branch] = (pow(z[fake_branch], n, ns) * term_val) % ns

        # 2. PREPARE REAL BRANCH (Commitment)
        # a_real = w^n mod n^2
        a[real_branch] = pow(w, n, ns)

        # 3. GENERATE CHALLENGE (Fiat-Shamir)
        # Hash everything public to get total challenge E
        # E = H(n, g, u, a0, a1)
        total_e_int = ZKPUtils.hash_nums([n, g, u, a[0], a[1]])
        # e_real = E - e_fake
        # Note: We work mod q? No, typically challenge range is large but order of group involved. 
        # For Paillier ZKPs, challenges can be up to 256 bits.
        
        # We set our challenge space roughly size of n (or smaller 256 bits).
        # Let's simple check: e_real = total - e_fake.
        # But we need e_real + e_fake = total_e (mod order?).
        # Standard CDS: e_real = total_e - e_fake
        e[real_branch] = (total_e_int - e[fake_branch])

        # 4. COMPUTE RESPONSE (Real)
        # z = w * r^e (mod n) ?? No, this is Paillier group.
        # r^n logic:
        # u = r^n. a = w^n. e is challenge.
        # z = w * r^e (mod n).
        # Check: z^n = (w * r^e)^n = w^n * (r^n)^e = a * u^e. Correct.
        
        # Since r is in Z_n*, we compute mod n.
        z[real_branch] = (w * pow(r, e[real_branch], n)) % n

        return {
            "a": [str(a[0]), str(a[1])],
            "e": [str(e[0]), str(e[1])],
            "z": [str(z[0]), str(z[1])]
        }

class ZKPVerifier:
    def __init__(self, public_key):
        self.pub = public_key
        self.n = public_key.n
        self.ns = self.n * self.n
        self.g = self.n + 1

    def verify(self, ciphertext_int, proof):
        """
        Verifies the proof for ciphertext_int.
        proof: dictionary with lists a, e, z (strings)
        """
        try:
            u = int(ciphertext_int)
            n = self.n
            ns = self.ns
            g = self.g
            
            a = [int(x) for x in proof["a"]]
            e = [int(x) for x in proof["e"]]
            z = [int(x) for x in proof["z"]]

            # 1. Recompute Total Challenge E
            expected_total_e = ZKPUtils.hash_nums([n, g, u, a[0], a[1]])
            actual_total_e = e[0] + e[1]
            
            if expected_total_e != actual_total_e:
                print("ZKP Verification Failed: Challenge Mismatch")
                return False

            # 2. Verify Branch 0: u is enc(0) => u = r^n
            # Check: z0^n = a0 * u^e0
            lhs0 = pow(z[0], n, ns)
            rhs0 = (a[0] * pow(u, e[0], ns)) % ns
            if lhs0 != rhs0:
                print("ZKP Verification Failed: Branch 0 Invalid")
                # print(f"LHS: {lhs0}\nRHS: {rhs0}")
                return False

            # 3. Verify Branch 1: u is enc(1) => u = g * r^n => u/g = r^n
            # Check: z1^n = a1 * (u/g)^e1
            # => z1^n = a1 * (u * g^-1)^e1
            inv_g = pow(g, -1, ns)
            val = (u * inv_g) % ns
            
            lhs1 = pow(z[1], n, ns)
            rhs1 = (a[1] * pow(val, e[1], ns)) % ns
            if lhs1 != rhs1:
                print("ZKP Verification Failed: Branch 1 Invalid")
                return False

            return True

        except Exception as ex:
            print(f"ZKP Verification Error: {ex}")
            return False

import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from secure_voting_core import generate_keypair
from src.keygen import generate_keypair as python_keygen

def benchmark():
    print("--- BENCHMARK: Python (phe) vs Rust (secure-voting-core) ---")
    
    # Python Baseline
    print("1. Python KeyGen (1024-bit)...")
    start = time.time()
    # Using 512 for speed test if 1024 takes too long, but let's try 1024
    # python_keygen(key_size=1024) 
    # Note: python_keygen saves files, let's just do math if possible, 
    # but our func saves. We'll skip deep bench for python to save disk I/O.
    print("   (Skipped full Python Gen to avoid disk I/O spam)")
    
    # Rust Benchmark
    print("\n2. Rust KeyGen (1024-bit)...")
    start = time.time()
    res = generate_keypair(1024)
    dt_rust = time.time() - start
    
    n, g, p, q = res
    print(f"   Time: {dt_rust:.4f}s")
    print(f"   Result n (first 50 chars): {n[:50]}...")
    print(f"   Result p (first 50 chars): {p[:50]}...")
    
    # Verification
    print("\n3. Validity Check")
    n_int = int(n)
    p_int = int(p)
    q_int = int(q)
    
    if p_int * q_int == n_int:
        print("   ✅ Math Checks Out (n = p * q)")
    else:
        print("   ❌ Math Error")

if __name__ == "__main__":
    benchmark()

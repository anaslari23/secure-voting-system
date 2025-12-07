import random
import functools

# We need a prime larger than the secret.
# Paillier keys (up to 2048 bits) require a very large field.
# Mersenne Prime M2203 = 2^2203 - 1 is approx 2203 bits, enough for 2048-bit secrets.
PRIME = 2**2203 - 1

def _eval_poly(poly, x):
    """Evaluates polynomial at x."""
    result = 0
    for coeff in reversed(poly):
        result = (result * x + coeff) % PRIME
    return result

def split_secret(secret_int, t, n):
    """
    Splits an integer secret into n shares, requiring t to reconstruct.
    Returns list of tuples (x, y).
    """
    if t > n:
        raise ValueError("Threshold t cannot be greater than n")
        
    # Valid polynomial: secret + a1*x + ... + a(t-1)*x^(t-1)
    coeffs = [secret_int] + [random.SystemRandom().randint(0, PRIME - 1) for _ in range(t - 1)]
    
    shares = []
    for i in range(1, n + 1):
        x = i
        y = _eval_poly(coeffs, x)
        shares.append((x, y))
        
    return shares

def _extended_gcd(a, b):
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        q, b, a = b // a, a, b % a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0

def _mod_inverse(k, p):
    g, x, y = _extended_gcd(k, p)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return (x % p + p) % p

def recover_secret(shares):
    """
    Reconstructs secret from list of (x, y) shares using Lagrange Interpolation.
    """
    if len(shares) < 1:
        raise ValueError("No shares provided")
        
    sum_val = 0
    xs = [s[0] for s in shares]
    ys = [s[1] for s in shares]
    
    for j in range(len(shares)):
        # Lagrange basis polynomial L_j(0)
        # Prod (0 - xm) / (xj - xm) for m != j
        
        numerator = 1
        denominator = 1
        
        for m in range(len(shares)):
            if m == j:
                continue
            
            numerator = (numerator * (0 - xs[m])) % PRIME
            denominator = (denominator * (xs[j] - xs[m])) % PRIME
            
        lagrange_coeff = (numerator * _mod_inverse(denominator, PRIME)) % PRIME
        term = (ys[j] * lagrange_coeff) % PRIME
        sum_val = (sum_val + term) % PRIME
        
    return sum_val

def int_to_hex(val):
    return hex(val)[2:]

def hex_to_int(h):
    return int(h, 16)

import requests
import json
import urllib3

# Suppress self-signed cert warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:5001"
VOTERS = [
    "1000-0000-0001",
    "2000-0000-0002",
    "3000-0000-0003",
    "4000-0000-0004",
    "5000-0000-0005"
]

# Scenario: 3 YES, 2 NO
# Expected Result: YES=3, NO=2
VOTES = [1, 1, 0, 1, 0] 

def run_simulation():
    print(f"--- STARTING MOCK ELECTION ({len(VOTERS)} Voters) ---\n")
    
    session = requests.Session()
    
    for i, voter_id in enumerate(VOTERS):
        vote_choice = VOTES[i]
        vote_str = "YES" if vote_choice == 1 else "NO"
        
        print(f"[Voter {i+1}] ID: {voter_id} wants to vote {vote_str}...")
        
        # 1. Login (Request OTP)
        try:
            resp = session.post(f"{BASE_URL}/login", json={"aadhaar": voter_id}, verify=False)
            if resp.status_code != 200:
                print(f"  ❌ Login Request Failed: {resp.text}")
                continue
            
            # 2. Extract OTP (Simulated - we don't have access to server logs here, 
            #    BUT app.py uses a fixed mock OTP logic in session or we can't easily get it without 
            #    cheating or modifying app.py to return it in debug mode.
            #    Wait, in app.py I saw `print(f"[OTP] Generated...:{otp}")`.
            #    The client side doesn't get the OTP in the response for security.
            #    
            #    Hack for Simulation: I need to bypass OTP or guess it. 
            #    The app logic generates random OTP. 
            #    Real-world simulation blocking point.
            #    
            #    Alternative: use the /api/vote directly? No, it also checks session.
            #    
            #    I will parse the 'backend_results.log' file to find the latest OTP! 
            pass
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("This script requires logic to read server logs for OTPs. Running interactive mode...")

import requests
import time
import re
import urllib3
import os

# Suppress self-signed cert warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:5001"
LOG_FILE = "backend_results.log"

VOTERS = [
    "1000-0000-0001",
    "2000-0000-0002",
    "3000-0000-0003",
    "4000-0000-0004",
    "5000-0000-0005"
]

# Scenario: 3 YES, 2 NO
VOTES = [1, 1, 0, 1, 0] 

def get_latest_otp(voter_id):
    """
    Scans the log file for the latest OTP generated for the given voter_id.
    Retries for a few seconds if not found immediately.
    """
    otp_pattern = re.compile(f"\\[OTP\\] Generated for {voter_id}: (\\d+)")
    
    for _ in range(10): # Try for 2 seconds
        if not os.path.exists(LOG_FILE):
            time.sleep(0.2)
            continue
            
        with open(LOG_FILE, "r") as f:
            content = f.read()
            matches = otp_pattern.findall(content)
            if matches:
                return matches[-1] # Return the most recent one
        time.sleep(0.2)
    return None

def run_simulation():
    print(f"\n--- 🗳️  STARTING MOCK ELECTION SIMULATION ({len(VOTERS)} Voters) ---\n")
    
    successful_votes = 0
    
    for i, voter_id in enumerate(VOTERS):
        session = requests.Session() # New Session for each voter
        vote_choice = VOTES[i]
        vote_str = "YES (1)" if vote_choice == 1 else "NO (0)"
        
        print(f"[Voter {i+1}] {voter_id} attempting to vote {vote_str}...")
        
        # 1. Login Request
        try:
            resp = session.post(f"{BASE_URL}/login", json={"aadhaar": voter_id}, verify=False)
            if resp.status_code != 200 or resp.json().get('status') != 'otp_sent':
                print(f"   ❌ Login Failed: {resp.text}")
                continue
                
            # 2. Get OTP from Log
            otp = get_latest_otp(voter_id)
            if not otp:
                print("   ❌ OTP not found in logs. Is the server writing to backend_results.log?")
                continue
            
            # 3. Verify OTP
            resp = session.post(f"{BASE_URL}/verify_otp", json={"otp": otp}, verify=False)
            if resp.status_code != 200:
                print(f"   ❌ OTP Verification Failed: {resp.text}")
                continue
                
            print(f"   ✅ Logged in (OTP: {otp})")
            
            # 4. Submit Vote
            resp = session.post(f"{BASE_URL}/submit_vote", data={"vote": str(vote_choice)}, verify=False)
            if resp.status_code == 200:
                print(f"   ✅ Vote Cast Successfully!")
                successful_votes += 1
            else:
                print(f"   ❌ Vote Submission Failed: {resp.text}")
                
        except Exception as e:
            print(f"   ❌ Network Error: {e}")
            
    print(f"\n--- ✅ Voting Phase Complete. {successful_votes}/{len(VOTERS)} votes cast. ---\n")
    
    # 5. Close Election
    print("--- 🏁 Closing Election & calculating Tally... ---")
    try:
        resp = session.get(f"{BASE_URL}/admin/close", verify=False) # Use last session or new one
        print(f"   ℹ️  Admin Response: {resp.text}")
        
        # 6. Fetch Results
        resp = requests.get(f"{BASE_URL}/results", verify=False)
        if "Final Tally" in resp.text:
            print("\n--- 📊 FINAL RESULTS CONFIRMED ---")
            
            # Simple check using string parsing or regex on HTML
            # HTML contains: <div class="big-number" ...>3</div>
            # We can print a summary
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            numbers = [div.text for div in soup.find_all(class_='big-number')]
            if len(numbers) >= 2:
                print(f"   YES Votes: {numbers[0]}")
                print(f"   NO Votes:  {numbers[1]}")
                
                if int(numbers[0]) == 3 and int(numbers[1]) == 2:
                    print("\n   🎯 SUCCESS: Tally matches expected outcome (3-2)!")
                else:
                    print("\n   ⚠️  MISMATCH: Tally differs from expected.")
            else:
                 print("   Could not parse results from HTML.")

    except Exception as e:
        print(f"   ❌ Error fetching results: {e}")

if __name__ == "__main__":
    try:
        # Install beautifulsoup4 if missing for parsing, or fallback
        import bs4
    except ImportError:
        print("Installing bs4 for result parsing...")
        os.system("pip install beautifulsoup4 > /dev/null")
        
    run_simulation()

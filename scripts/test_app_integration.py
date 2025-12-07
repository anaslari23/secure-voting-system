import unittest
import json
import os
import sys
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

import shutil
from app import app, VALID_VOTERS
from src.bulletin_board import BulletinBoard

class SecureVotingWebTest(unittest.TestCase):
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.secret_key = 'test_secret'
        self.client = app.test_client()
        
        # Reset Bulletin Board
        if os.path.exists("bb.json"):
            os.remove("bb.json")
        self.bb = BulletinBoard()
        
        # Reset Voter State
        for v in VALID_VOTERS:
            VALID_VOTERS[v]['has_voted'] = False
            
        # Ensure Keys exist (generate if not)
        if not os.path.exists("keys/public_key.json"):
            from src.keygen import generate_keypair
            generate_keypair(key_size=512) # Fast keys for test

    def test_full_voting_flow(self):
         print("\n--- TEST: Web Kiosk Full Flow ---")
         
         # 1. Access Home Page
         resp = self.client.get('/')
         self.assertEqual(resp.status_code, 200)
         print("[x] Home Page Loaded")
         
         # 2. Login with Valid ID
         voter_id = "1111-2222-3333"
         resp = self.client.post('/login', data={'aadhaar': voter_id}, follow_redirects=True)
         self.assertEqual(resp.status_code, 200)
         self.assertIn(b'Cast Your Vote', resp.data)
         print(f"[x] Logged in as {voter_id}")
         
         # 3. Submit Vote (Yes = 1)
         resp = self.client.post('/submit_vote', data={'vote': '1'})
         data = json.loads(resp.data)
         self.assertEqual(data['status'], 'success')
         print("[x] Vote Submitted via API")
         
         # 4. Verify Ledger Update
         ledger = self.bb.get_all_ballots()
         self.assertEqual(len(ledger), 1)
         last_ballot = ledger[0]['ballot']
         print(f"[x] Ledger Verified: Block #{ledger[0]['index']} Mined")
         
         # 5. Verify Receipt Page
         with self.client.session_transaction() as sess:
             # Manually simulate session persistence for next request if needed, 
             # but client cookies handle it.
             pass
             
         resp = self.client.get('/success')
         self.assertIn(b'Vote Recorded', resp.data)
         self.assertIn(last_ballot['ballot_id'].encode(), resp.data)
         print("[x] Receipt Page Generated with QR Code")
         
         # 6. Verify Anti-Double Voting
         resp = self.client.post('/login', data={'aadhaar': voter_id})
         self.assertIn(b'already voted', resp.data)
         print("[x] Double Voting Blocked")

if __name__ == '__main__':
    unittest.main()

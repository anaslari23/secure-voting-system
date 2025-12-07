from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
import qrcode
import base64
from io import BytesIO
from src.voting import create_ballot
from src.bulletin_board import BulletinBoard

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Mock Database for Identity
import random
from src.voting import create_ballot
from src.bulletin_board import BulletinBoard
from src.db import get_voter, mark_voter_as_voted
from src.tally import reveal_result_with_shares

ELECTION_OPEN = True # Global State Switch

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize DB (if new env)
from src.db import init_db
init_db()

@app.route('/')
def home():
    message = request.args.get('message')
    if 'user' in session:
        return redirect(url_for('vote_page'))
    return render_template('login.html', message=message)

@app.route('/login', methods=['POST'])
def login():
    # Step 1: Verify ID and Send OTP
    data = request.get_json() if request.is_json else request.form
    aadhaar = data.get('aadhaar')
    voter = get_voter(aadhaar)
    
    if voter:
        if voter['has_voted']:
            return jsonify({"error": "This Aadhaar ID has already voted."}) if request.is_json else render_template('login.html', error="Already Voted")
        
        # Security: Generate Mock OTP (In prod, send via SMS)
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['user_pending'] = aadhaar
        session['name_pending'] = voter['name']
        session['phone'] = voter['phone']
        
        print(f"[OTP] Generated for {aadhaar}: {otp}") # Debug log
        
        if request.is_json:
            return jsonify({"status": "otp_sent", "message": "OTP sent to registered mobile."})
        else:
             # Legacy Form support (should barely be used if we switch to api.js full)
             return render_template('login.html', otp_required=True)

    return jsonify({"error": "Invalid Aadhaar Number"}) if request.is_json else render_template('login.html', error="Invalid Aadhaar Number")

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    # Step 2: Verify OTP and Login
    data = request.get_json() if request.is_json else request.form
    user_otp = data.get('otp')
    
    if 'otp' not in session or 'user_pending' not in session:
         return jsonify({"error": "Session Expired. Login again."}), 401
         
    if user_otp == session['otp']:
        # Success! Promote to full session
        session['user'] = session['user_pending']
        session['name'] = session['name_pending']
        
        # Cleanup temp vars
        session.pop('otp', None)
        session.pop('user_pending', None)
        session.pop('name_pending', None)
        
        return jsonify({"status": "success"})
    
    return jsonify({"error": "Invalid OTP. Try again."}), 401

@app.route('/vote')
def vote_page():
    if 'user' not in session:
        return redirect(url_for('home'))
        
    # STRICT CHECK: If already voted, force logout
    user_id = session['user']
    voter = get_voter(user_id) # Re-fetch from DB
    
    if voter and voter['has_voted']:
        session.clear()
        return redirect(url_for('home', message="Security Alert: You have already voted."))
        
    return render_template('vote.html', name=session['name'])

    return render_template('vote.html', name=session['name'])

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    global ELECTION_OPEN
    if not ELECTION_OPEN:
         return jsonify({"error": "Election is Closed."}), 403

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # STRICT CHECK: Prevent Double Voting via API/POST duplication
    user_id = session['user']
    voter = get_voter(user_id)
    if voter and voter['has_voted']:
        return jsonify({"error": "Security: Vote already cast."}), 403
    
    try:
        vote_val = int(request.form.get('vote'))
        if vote_val not in [0, 1]:
            return jsonify({"error": "Invalid Vote"}), 400
            
        # 1. Create Ballot (Encrypt + ZKP)
        # Using a dummy kiosk ID for now
        ballot = create_ballot(vote_val, kiosk_id="kiosk-web-01")
        
        # 2. Publish to Ledger
        bb = BulletinBoard()
        block_index = bb.publish(ballot)
        
        # 3. Mark User as Voted
        user_id = session['user']
        
        # 3. Mark User as Voted
        mark_voter_as_voted(session['user'])
        
        # 4. Generate Receipt Data
        receipt_data = {
            "block": block_index,
            "hash": ballot['ciphertext'][:20] + "...", # Shorten for UI
            "ballot_id": ballot['ballot_id']
        }
        
        # Store in session for success page
        session['receipt'] = receipt_data
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/success')
def success():
    if 'receipt' not in session:
        return redirect(url_for('home'))
        
    receipt = session['receipt']
    
    # Generate QR
    qr_str = f"BALLOT:{receipt['ballot_id']}|BLOCK:{receipt['block']}"
    img = qrcode.make(qr_str)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('success.html', receipt=receipt, qr_code=qr_b64)

@app.route('/logout')
def logout():
    voted = request.args.get('voted')
    session.clear()
    msg = "You have voted successfully" if voted else None
    return redirect(url_for('home', message=msg))

@app.route('/admin/close')
def close_election():
    global ELECTION_OPEN
    ELECTION_OPEN = False
    return "Election Closed! Results are now processed."

@app.route('/results')
def results_page():
    if ELECTION_OPEN:
        # Results hidden while voting is active
        return render_template('results.html', 
                               open=True, 
                               message="Polls are still open. Results hidden.")
    
    # Election Closed -> Compute Tally
    # 1. Get Decrypted Sum (YES votes)
    yes_votes = reveal_result_with_shares([1, 2, 3]) # Using threshold 3
    
    # 2. Get Total Ballots cast to infer NO votes
    bb = BulletinBoard()
    ledger = bb.get_all_ballots()
    total_votes = len(ledger)
    
    no_votes = total_votes - yes_votes
    
    winner = "TIE"
    if yes_votes > no_votes:
        winner = "YES"
    elif no_votes > yes_votes:
        winner = "NO"
        
    return render_template('results.html', 
                           open=False,
                           yes_votes=yes_votes,
                           no_votes=no_votes,
                           total_votes=total_votes,
                           winner=winner)

# --- JSON API for Mobile App ---

@app.route('/api/login', methods=['POST'])
def api_login():
    # Replaced by main /login which now supports JSON
    return login()

@app.route('/api/vote', methods=['POST'])
def api_vote():
    global ELECTION_OPEN
    if not ELECTION_OPEN:
         return jsonify({"error": "Election is Closed."}), 403

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    voter = get_voter(session['user'])

    # STRICT CHECK: API Double Voting
    if voter and voter['has_voted']:
        return jsonify({"error": "Already Voted"}), 403
    
    data = request.get_json()
    try:
        vote_val = int(data.get('vote'))
        if vote_val not in [0, 1]:
            return jsonify({"error": "Invalid Vote"}), 400
            
        ballot = create_ballot(vote_val, kiosk_id="mobile-app")
        bb = BulletinBoard()
        
        block_index = bb.publish(ballot)
        
        mark_voter_as_voted(session['user'])
        
        receipt_data = {
            "block": block_index,
            "hash": ballot['ciphertext'][:20] + "...",
            "ballot_id": ballot['ballot_id']
        }
        return jsonify({"status": "success", "receipt": receipt_data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Kiosk Web Server...")
    
    # Print Actual IDs for User Convenience
    try:
        from src.db import get_db_connection
        conn = get_db_connection()
        rows = conn.execute('SELECT aadhaar FROM voters LIMIT 5').fetchall()
        ids = [r['aadhaar'] for r in rows]
        print(f"Valid Mock IDs: {', '.join(ids)}")
        conn.close()
    except Exception as e:
        print(f"Could not load IDs: {e}")
    # Using port 5001 to avoid macOS AirPlay Receiver conflict on port 5000
    # Turning off debug mode for stability in background execution
    # Enabling HTTPS with self-signed certs
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(BASE_DIR, 'cert.pem')
    key_path = os.path.join(BASE_DIR, 'key.pem')
    app.run(debug=False, port=5001, host='0.0.0.0', ssl_context=(cert_path, key_path))

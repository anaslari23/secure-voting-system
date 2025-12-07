const API_BASE = '/api';

class VotingAPI {
    static async login(aadhaar) {
        try {
            const res = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ aadhaar })
            });
            return await res.json();
        } catch (e) {
            console.error(e);
            return { error: 'Connection Error' };
        }
    }

    static async verifyOtp(otp) {
        try {
            const res = await fetch('/verify_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp })
            });
            return await res.json();
        } catch (e) {
            console.error(e);
            return { error: 'Connection Error' };
        }
    }

    static async vote(voteVal) {
        try {
            const res = await fetch(`${API_BASE}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vote: voteVal })
            });
            if (!res.ok) throw new Error((await res.json()).error || 'Vote Failed');
            return await res.json();
        } catch (e) {
            console.error(e);
            return { error: e.message };
        }
    }
}

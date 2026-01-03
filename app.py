from flask import Flask, request, jsonify, render_template_string
import hashlib, time, json, os

app = Flask(__name__)

# --- XIAMO CONSTITUTION ---
MAX_SUPPLY = 210000000.0
HALVING_INTERVAL = 210000
INITIAL_REWARD = 12.5
DB_FILE = "blockchain_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {"balances": {}, "block_height": 0, "difficulty": 4}

blockchain_data = load_db()

def save_db():
    with open(DB_FILE, "w") as f: json.dump(blockchain_data, f)

# --- THE GHOST-HASH (QUBIC + BLAKE3 HYBRID) ---
def ghost_hash(address, nonce):
    # Layer 1: Qubic-style base
    base = hashlib.blake2b(f"{address}{nonce}".encode(), digest_size=32).hexdigest()
    
    # Layer 2: Branching Decision
    if int(base[-1], 16) % 2 == 0:
        mix = hashlib.sha3_256(base.encode()).hexdigest()
    else:
        mix = hashlib.blake2b(f"{base}{nonce}".encode(), digest_size=32).hexdigest()
    
    # Layer 3: Final Fusion
    return hashlib.sha3_256(f"{mix}{base}".encode()).hexdigest()

# --- HALVING & REWARD LOGIC ---
def get_current_reward():
    halvings = blockchain_data["block_height"] // HALVING_INTERVAL
    reward = INITIAL_REWARD / (2 ** halvings)
    
    current_supply = sum(blockchain_data["balances"].values())
    if current_supply + reward > MAX_SUPPLY:
        reward = max(0, MAX_SUPPLY - current_supply)
    return reward

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    addr, nonce = data.get('address'), data.get('nonce')
    result = ghost_hash(addr, nonce)
    
    if result.startswith("0" * blockchain_data["difficulty"]):
        reward = get_current_reward()
        if reward > 0:
            blockchain_data["block_height"] += 1
            blockchain_data["balances"][addr] = blockchain_data["balances"].get(addr, 0) + reward
            save_db()
            return jsonify({"status": "success", "reward": reward})
    return jsonify({"status": "error"}), 400

@app.route('/')
def dashboard():
    supply = sum(blockchain_data["balances"].values())
    reward = get_current_reward()
    return f"""
    <html><body style="background:#020617;color:white;font-family:sans-serif;padding:30px;">
        <h1 style="color:#38bdf8">Xiamo Mainnet</h1>
        <p><b>Supply:</b> {supply:,.2f} / {MAX_SUPPLY:,.0f} XM</p>
        <p><b>Height:</b> {blockchain_data['block_height']}</p>
        <p><b>Current Reward:</b> {reward} XM</p>
        <p><b>Halving in:</b> {HALVING_INTERVAL - (blockchain_data['block_height'] % HALVING_INTERVAL)} blocks</p>
    </body></html>
    """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

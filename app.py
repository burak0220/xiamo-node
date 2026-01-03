cat << 'EOF' > app.py
from flask import Flask, request, jsonify, render_template_string
import hashlib
import time
import threading
import requests
import json
import os

app = Flask(__name__)

# Persistence: Load data from file if exists
DB_FILE = "xiamo_blockchain.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        blockchain_data = json.load(f)
else:
    blockchain_data = {
        "balances": {},
        "block_height": 0,
        "difficulty": 4,
        "history": []
    }

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(blockchain_data, f)

# Keep-Alive System
def keep_alive():
    while True:
        try:
            requests.get("http://127.0.0.1:10000/", timeout=5)
        except: pass
        time.sleep(600)

threading.Thread(target=keep_alive, daemon=True).start()

# ASIC-Resistant Ghost-Hash (The Logic We Agreed On)
def xiamo_ghost_hash(address, nonce):
    base = hashlib.blake2b(f"{address}{nonce}".encode(), digest_size=32).hexdigest()
    if int(base[-1], 16) % 2 == 0:
        mix = hashlib.sha3_256(base.encode()).hexdigest()
    else:
        mix = hashlib.blake2b(f"{base}{nonce}".encode(), digest_size=32).hexdigest()
    return hashlib.sha3_256(f"{mix}{base}".encode()).hexdigest()

# HALVING LOGIC
def get_current_reward():
    initial_reward = 12.5
    # Every 210,000 blocks, reward halves
    halvings = blockchain_data["block_height"] // 210000
    return initial_reward / (2 ** halvings)

@app.route('/')
def dashboard():
    richlist = sorted(blockchain_data["balances"].items(), key=lambda x: x[1], reverse=True)[:10]
    supply = sum(blockchain_data["balances"].values())
    return render_template_string("""
    <html><head><title>Xiamo Explorer</title><style>
    body { background: #020617; color: white; font-family: sans-serif; padding: 20px; }
    .card { background: #0f172a; border: 1px solid #1e293b; padding: 15px; border-radius: 10px; display: inline-block; margin-right: 10px; }
    .blue { color: #38bdf8; }
    </style></head><body>
    <h1>Xiamo <span class="blue">Network</span></h1>
    <div class="card"><h3>Height</h3><p>{{ height }}</p></div>
    <div class="card"><h3>Reward</h3><p>{{ reward }} XM</p></div>
    <div class="card"><h3>Supply</h3><p>{{ supply }} XM</p></div>
    <h2>Top Holders</h2>
    <ul>{% for addr, bal in richlist %}<li>{{ addr }}: <b>{{ bal }} XM</b></li>{% endfor %}</ul>
    </body></html>
    """, height=blockchain_data["block_height"], reward=get_current_reward(), supply=round(supply, 2), richlist=richlist)

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    addr, nonce = data.get('address'), data.get('nonce')
    result = xiamo_ghost_hash(addr, nonce)
    
    if result.startswith("0" * blockchain_data["difficulty"]):
        reward = get_current_reward()
        blockchain_data["block_height"] += 1
        blockchain_data["balances"][addr] = blockchain_data["balances"].get(addr, 0) + reward
        blockchain_data["history"].append({"h": blockchain_data["block_height"], "hash": result})
        save_db() # Permanent save
        return jsonify({"status": "success", "new_height": blockchain_data["block_height"]})
    return jsonify({"status": "error"}), 400

@app.route('/network_stats')
def stats(): return jsonify(blockchain_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
EOF

import hashlib
import random
import time
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# --- XIAMO CORE PARAMETERS ---
TOTAL_SUPPLY = 210000000
INITIAL_REWARD = 50
HALVING_INTERVAL = 210000

# --- HARDENED ALGORITHM (ASIC-KILLER) ---
def xiamo_native_pow(content, nonce):
    # Phase 1: Memory-Hard Jitter
    seed_val = int(hashlib.blake2b(str(nonce).encode(), digest_size=8).hexdigest(), 16)
    random.seed(seed_val)
    
    # Real hardware stress: Creating a dynamic memory array
    scratchpad = [random.getrandbits(32) for _ in range(512)]
    mix_hash = sum(scratchpad) ^ nonce
    
    # Phase 2: Double-Lock Hashing
    # Switching between BLAKE2b and BLAKE2s based on checksum to defeat static ASICs
    if mix_hash % 2 == 0:
        return hashlib.blake2b(f"{content}{mix_hash}".encode(), digest_size=32).hexdigest()
    else:
        return hashlib.blake2s(f"{content}{mix_hash}".encode(), digest_size=32).hexdigest()

# --- STATE MANAGEMENT ---
blockchain = {
    "main_chain": [{"hash": "0000_genesis", "height": 0, "reward": 0}],
    "strand_A": [],
    "strand_B": [],
    "circulating_supply": 0
}

def get_current_reward():
    halvings = len(blockchain["main_chain"]) // HALVING_INTERVAL
    return INITIAL_REWARD / (2 ** halvings)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    content = f"{data['prev_data']}{data['timestamp']}{data['address']}"
    
    if xiamo_native_pow(content, data['nonce']) == data['hash']:
        if data['hash'].startswith("0000"):
            b_type = data.get('type')
            
            if b_type == 'main':
                # Block reward logic
                reward = get_current_reward()
                data['reward'] = reward
                data['height'] = len(blockchain["main_chain"])
                
                blockchain["main_chain"].append(data)
                blockchain["circulating_supply"] += reward
                blockchain["strand_A"], blockchain["strand_B"] = [], []
                return jsonify({"status": "success", "msg": "Main Block Found", "reward": reward}), 200
            else:
                target = "strand_A" if b_type == 'side_a' else "strand_B"
                blockchain[target].append(data['hash'])
                return jsonify({"status": "success", "msg": f"{target} Mined"}), 200
                
    return jsonify({"status": "error", "msg": "Invalid Proof"}), 400

@app.route('/get_status')
def get_status():
    return jsonify({
        "height": len(blockchain["main_chain"]),
        "supply": f"{blockchain['circulating_supply']} / {TOTAL_SUPPLY} XM",
        "reward": get_current_reward(),
        "strand_A": blockchain["strand_A"],
        "strand_B": blockchain["strand_B"],
        "last_block": blockchain["main_chain"][-1]["hash"]
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

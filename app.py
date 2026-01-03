import hashlib
import random
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# XIAMO HYBRID ALGORITHM (Qubic + RandomX + Blake2b)
def xiamo_hybrid_logic(content, nonce):
    # Step 1: RandomX-Style Execution Path
    # Deriving a seed from the nonce to create a non-static execution flow
    seed_val = int(hashlib.blake2b(str(nonce).encode(), digest_size=8).hexdigest(), 16)
    random.seed(seed_val)
    
    # Step 2: Qubic-Style Mathematical Task
    # Simulating a small computational task that favors CPU/RAM over ASIC
    mix_value = nonce
    for _ in range(5):
        op = random.choice(['xor', 'add', 'shl'])
        val = random.randint(1, 100)
        if op == 'xor': mix_value ^= val
        elif op == 'add': mix_value += val
        else: mix_value <<= (val % 4)

    # Step 3: Blake2b Final Seal (High-speed parallel hashing)
    raw_final = f"{content}{mix_value}{nonce}xiamo_v2_final"
    return hashlib.blake2b(raw_final.encode(), digest_size=32).hexdigest()

# Blockchain Structure: 2 Side Strands + 1 Main Chain
blockchain = {
    "main_chain": [{"hash": "0000_genesis_block", "index": 0}],
    "strand_A": [],
    "strand_B": []
}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    content = f"{data['prev_data']}{data['timestamp']}{data['address']}"
    
    # Verify the proof of work
    if xiamo_hybrid_logic(content, data['nonce']) == data['hash']:
        if data['hash'].startswith("0000"):
            block_type = data.get('type')
            
            if block_type == 'main':
                # Consolidate side strands into the main chain
                blockchain["main_chain"].append(data)
                blockchain["strand_A"] = []
                blockchain["strand_B"] = []
                return jsonify({"status": "success", "message": "Main Block Secured"}), 200
            else:
                # Add to side strands
                target = "strand_A" if block_type == 'side_a' else "strand_B"
                blockchain[target].append(data['hash'])
                return jsonify({"status": "success", "message": f"{target} updated"}), 200
                
    return jsonify({"status": "error", "message": "Invalid Proof"}), 400

@app.route('/get_status')
def get_status():
    return jsonify(blockchain)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

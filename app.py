import hashlib
from flask import Flask, jsonify, request
import time
import os

app = Flask(__name__)

# Chain Data structure
blockchain = {
    "main_chain": [{"hash": "0000xiamo_genesis_block", "index": 0}],
    "strand_A": [],
    "strand_B": []
}

@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify(blockchain)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    b_type = data.get('type') 
    
    # 1. Basic Difficulty Check
    if not data['hash'].startswith("0000"):
        return jsonify({"status": "error", "msg": "Invalid difficulty"}), 400

    # 2. Side Strand Logic (Must be unique)
    if b_type.startswith('side'):
        strand = "strand_A" if 'a' in b_type else "strand_B"
        if len(blockchain[strand]) < 2:
            # Check if this hash is already in the strand to prevent duplicates
            if data['hash'] not in blockchain[strand]:
                blockchain[strand].append(data['hash'])
                return jsonify({"status": "success", "msg": f"{strand} updated"})
    
    # 3. Main Block Logic (Mathematical Mixer)
    elif b_type == 'main':
        a_hashes = blockchain["strand_A"]
        b_hashes = blockchain["strand_B"]
        
        if len(a_hashes) + len(b_hashes) == 4:
            # Mixer Formula: All Side Hashes + Timestamp + Nonce + Address
            mixer_input = f"{''.join(a_hashes)}{''.join(b_hashes)}{data['timestamp']}{data['nonce']}{data['address']}"
            check_hash = hashlib.sha256(mixer_input.encode()).hexdigest()
            
            if check_hash == data['hash']:
                blockchain["main_chain"].append(data)
                blockchain["strand_A"], blockchain["strand_B"] = [], [] # Reset strands
                return jsonify({"status": "success", "msg": "MAIN BLOCK SECURED"})
    
    return jsonify({"status": "wait", "msg": "Conditions not met"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

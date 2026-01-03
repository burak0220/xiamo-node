from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# Professional Blockchain State
blockchain_data = {
    "balances": {},
    "block_height": 0,
    "difficulty": 4, # Initial difficulty
    "last_block_time": time.time(),
    "network_hashrate": 0
}

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    miner_address = data.get('address')
    nonce = data.get('nonce')
    
    # PoW Verification
    check_hash = hashlib.sha256(f"{miner_address}{nonce}".encode()).hexdigest()
    target = "0" * blockchain_data["difficulty"]
    
    if check_hash.startswith(target):
        now = time.time()
        time_diff = now - blockchain_data["last_block_time"]
        
        # Difficulty Adjustment Logic (Dynamic)
        # If blocks are found too fast (less than 10 sec), increase difficulty
        if time_diff < 10:
            blockchain_data["difficulty"] += 1 if blockchain_data["difficulty"] < 8 else 0
        elif time_diff > 30:
            blockchain_data["difficulty"] -= 1 if blockchain_data["difficulty"] > 3 else 0
            
        blockchain_data["block_height"] += 1
        blockchain_data["last_block_time"] = now
        blockchain_data["balances"][miner_address] = blockchain_data["balances"].get(miner_address, 0) + 10.0
        
        return jsonify({
            "status": "success",
            "height": blockchain_data["block_height"],
            "difficulty": blockchain_data["difficulty"],
            "hash": check_hash
        })
    return jsonify({"status": "error"}), 400

@app.route('/network_stats', methods=['GET'])
def get_stats():
    return jsonify(blockchain_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

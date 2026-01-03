from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# Global state
blockchain_data = {
    "balances": {},
    "transactions": [],
    "difficulty": 4  # Difficulty level (number of leading zeros)
}

@app.route('/')
def home():
    return "Xiamo Mainnet Node v1.1 - PoW Active"

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    # No more 100 XM gift. Default is 0.
    balance = blockchain_data["balances"].get(address, 0.0)
    return jsonify({
        "address": address,
        "balance": balance,
        "currency": "XM"
    })

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    miner_address = data.get('address')
    nonce = data.get('nonce')
    
    # Simple Proof of Work verification
    check_hash = hashlib.sha256(f"{miner_address}{nonce}".encode()).hexdigest()
    
    # Check if the hash meets the difficulty (starts with '0000')
    if check_hash.startswith("0" * blockchain_data["difficulty"]):
        reward = 5.0 # Mining reward per block
        
        if miner_address not in blockchain_data["balances"]:
            blockchain_data["balances"][miner_address] = 0.0
            
        blockchain_data["balances"][miner_address] += reward
        
        return jsonify({
            "status": "success",
            "message": f"Block mined! 5.0 XM rewarded to {miner_address}",
            "hash": check_hash
        })
    else:
        return jsonify({"status": "failed", "message": "Invalid proof"}), 400

@app.route('/transfer', methods=['POST'])
def transfer():
    # ... (Same transfer logic as before)
    return jsonify({"status": "active"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

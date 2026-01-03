from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# Core Xiamo Data
blockchain_data = {
    "balances": {},
    "block_height": 0,
    "difficulty": 4, 
    "last_block_time": time.time()
}

def xiamo_hybrid_hash(address, nonce):
    # BLAKE2b - Fast and Secure (Blake influence)
    b2b = hashlib.blake2b(f"{address}{nonce}".encode(), digest_size=32).hexdigest()
    
    # RandomX/Qubic Influence: Re-hashing based on the first result
    # Bu kısım algoritmayı 'Heavy' yapar, sadece hız değil işlemci döngüsü ister
    mix_layer = hashlib.sha3_256(f"{b2b}{nonce}".encode()).hexdigest()
    
    # Final Signature
    final_result = hashlib.blake2b(mix_layer.encode(), digest_size=32).hexdigest()
    return final_result

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    miner_addr = data.get('address')
    nonce = data.get('nonce')
    
    # Xiamo Hybrid Verification
    check_hash = xiamo_hybrid_hash(miner_addr, nonce)
    target = "0" * blockchain_data["difficulty"]
    
    if check_hash.startswith(target):
        blockchain_data["block_height"] += 1
        blockchain_data["balances"][miner_addr] = blockchain_data["balances"].get(miner_addr, 0) + 12.5 # Block Reward
        return jsonify({"status": "success", "height": blockchain_data["block_height"], "hash": check_hash})
    
    return jsonify({"status": "error", "message": "Invalid Hybrid Proof"}), 400

@app.route('/network_stats')
def stats(): return jsonify(blockchain_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

import hashlib
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# XIAMO V2 CUSTOM ALGORITHM
def xiamo_algorithm(content, nonce):
    # Sequential hashing to prevent server parallelism
    layer = f"{content}{nonce}"
    for i in range(3):
        # Adding unique 'xiamo_v2' salt to distinguish from standard SHA256
        layer = hashlib.sha256(f"{layer}{i}xiamo_v2".encode()).hexdigest()
    return layer

blockchain = {
    "main_chain": [{"hash": "0000_xiamo_genesis", "index": 0}],
    "strand_A": [],
    "strand_B": []
}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    # Reconstruct content for verification
    content = f"{data['prev_data']}{data['timestamp']}{data['address']}"
    
    # Verification using the custom Xiamo algorithm
    check_hash = xiamo_algorithm(content, data['nonce'])
    
    if check_hash == data['hash'] and data['hash'].startswith("0000"):
        b_type = data.get('type')
        
        if b_type == 'main':
            blockchain["main_chain"].append(data)
            # Clear strands after a successful merge
            blockchain["strand_A"], blockchain["strand_B"] = [], []
            return jsonify({"status": "success", "msg": "MAIN BLOCK SECURED"}), 200
        else:
            strand = "strand_A" if 'a' in str(b_type) else "strand_B"
            if data['hash'] not in blockchain[strand]:
                blockchain[strand].append(data['hash'])
                return jsonify({"status": "success", "msg": "Side block added"}), 200
            
    return jsonify({"status": "error", "msg": "Math Proof Failed"}), 400

@app.route('/get_status')
def get_status():
    return jsonify(blockchain)

if __name__ == "__main__":
    # Ensure it works on Render's dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

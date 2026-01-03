import hashlib
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# XIAMO ARM-ONLY ALGORITHM (ENGLISH VERSION)
def xiamo_arm_verify(content, nonce, arch_signature):
    # Reject immediately if architecture is not ARM-based
    if "arm" not in arch_signature.lower() and "aarch" not in arch_signature.lower():
        return "invalid_arch"
        
    # Salt the hash with the hardware architecture string
    layer = f"{content}{nonce}{arch_signature}"
    for i in range(3):
        layer = hashlib.sha256(f"{layer}{i}xiamo_v2_mobile_power").encode()
        layer = hashlib.sha256(layer).hexdigest()
    return layer

blockchain = {
    "main_chain": [{"hash": "0000_xiamo_genesis", "index": 0}],
    "strand_A": [],
    "strand_B": []
}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    content = f"{data['prev_data']}{data['timestamp']}{data['address']}"
    
    # Verify using the ARM-locked algorithm
    result_hash = xiamo_arm_verify(content, data['nonce'], data.get('arch', 'unknown'))
    
    if result_hash == data['hash'] and data['hash'].startswith("0000"):
        b_type = data.get('type')
        if b_type == 'main':
            blockchain["main_chain"].append(data)
            blockchain["strand_A"], blockchain["strand_B"] = [], []
            return jsonify({"status": "success", "msg": "MAIN BLOCK SECURED"}), 200
        else:
            strand = "strand_A" if 'a' in str(b_type) else "strand_B"
            if data['hash'] not in blockchain[strand]:
                blockchain[strand].append(data['hash'])
                return jsonify({"status": "success", "msg": "Side block added"}), 200
            
    return jsonify({"status": "error", "msg": "ARM Proof of Work Failed"}), 400

@app.route('/get_status')
def get_status():
    return jsonify(blockchain)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

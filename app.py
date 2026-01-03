from flask import Flask, jsonify, request
import time
import os

app = Flask(__name__)
active_nodes = {}

@app.route('/')
def home():
    return {"status": "Xiamo Network Global Node", "online_nodes": len(active_nodes)}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    addr = data.get('address')
    active_nodes[addr] = time.time()
    return jsonify({"success": True, "message": f"Node {addr} registered"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

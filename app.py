from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Core blockchain data structure
blockchain_data = {
    "balances": {},
    "transactions": []
}

@app.route('/')
def home():
    # Welcome message in English
    return "Xiamo Network Node v1.0 - Status: Operational"

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    # Welcome bonus for new wallet addresses
    if address not in blockchain_data["balances"]:
        blockchain_data["balances"][address] = 100.0
    
    return jsonify({
        "address": address,
        "balance": blockchain_data["balances"][address],
        "currency": "XM"
    })

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount')

    if not sender or not receiver or not amount:
        return jsonify({"error": "Missing transaction data"}), 400

    # Fund verification
    sender_balance = blockchain_data["balances"].get(sender, 0)
    if sender_balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Execute transfer
    blockchain_data["balances"][sender] -= amount
    if receiver not in blockchain_data["balances"]:
        blockchain_data["balances"][receiver] = 0
    blockchain_data["balances"][receiver] += amount

    # Generate transaction ID
    tx_id = f"tx_{int(time.time())}"
    blockchain_data["transactions"].append({
        "tx_id": tx_id,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": int(time.time())
    })

    return jsonify({
        "status": "success",
        "tx_id": tx_id,
        "message": "Transfer completed successfully"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

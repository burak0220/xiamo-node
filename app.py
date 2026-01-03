from flask import Flask, request, jsonify, render_template_string
import hashlib, time, json, os

app = Flask(__name__)

# --- XIAMO CONSTITUTION ---
MAX_SUPPLY = 210000000.0
HALVING_INTERVAL = 210000
INITIAL_REWARD = 12.5
DB_FILE = "blockchain_db.json"

# LÜTFEN BURAYA KENDİ CÜZDAN ADRESİNİ YAZ
FOUNDER_ADDRESS = "XM_48cab684055e214d05421d58" 

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: 
                return json.load(f)
        except: pass
    
    # --- GENESIS BLOCK 0 INITIALIZATION ---
    # Eğer veritabanı yoksa, sistem bu kurucu ayarlarıyla başlar.
    return {
        "balances": {
            FOUNDER_ADDRESS: 0.0  # Kurucu adresi sisteme kaydedildi
        }, 
        "block_height": 0, 
        "difficulty": 4
    }

blockchain_data = load_db()

def save_db():
    with open(DB_FILE, "w") as f: 
        json.dump(blockchain_data, f, indent=4)

# --- THE GHOST-HASH (QUBIC + BLAKE3 HYBRID) ---
def ghost_hash(address, nonce):
    base = hashlib.blake2b(f"{address}{nonce}".encode('utf-8'), digest_size=32).hexdigest()
    if int(base[-1], 16) % 2 == 0:
        mix = hashlib.sha3_256(base.encode('utf-8')).hexdigest()
    else:
        mix = hashlib.blake2b(f"{base}{nonce}".encode('utf-8'), digest_size=32).hexdigest()
    return hashlib.sha3_256(f"{mix}{base}".encode('utf-8')).hexdigest()

# --- HALVING & REWARD LOGIC ---
def get_current_reward():
    halvings = blockchain_data["block_height"] // HALVING_INTERVAL
    reward = INITIAL_REWARD / (2 ** halvings)
    current_supply = sum(blockchain_data["balances"].values())
    if current_supply + reward > MAX_SUPPLY:
        reward = max(0, MAX_SUPPLY - current_supply)
    return reward

# --- MINING ROUTE ---
@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    addr, nonce = data.get('address'), data.get('nonce')
    if not addr or nonce is None: return jsonify({"status": "error"}), 400
    
    result = ghost_hash(addr, nonce)
    if result.startswith("0" * blockchain_data["difficulty"]):
        reward = get_current_reward()
        if reward > 0:
            blockchain_data["block_height"] += 1
            blockchain_data["balances"][addr] = blockchain_data["balances"].get(addr, 0) + reward
            save_db()
            return jsonify({"status": "success", "reward": reward})
    return jsonify({"status": "error"}), 400

# --- EXPLORER UI TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Xiamo Network Explorer</title>
    <style>
        body { background: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; padding: 20px; line-height: 1.5; }
        .container { max-width: 900px; margin: auto; }
        .header { border-bottom: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .card { background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .label { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
        .value { font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: block; margin-top: 4px; }
        h1 { color: #f8fafc; margin: 0; font-size: 1.8rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 30px; background: #0f172a; border-radius: 12px; overflow: hidden; }
        th, td { padding: 12px 20px; text-align: left; border-bottom: 1px solid #1e293b; }
        th { background: #1e293b; color: #94a3b8; font-size: 0.8rem; }
        .address { font-family: 'Courier New', monospace; color: #fbbf24; font-size: 0.9rem; }
        .status-tag { display: inline-block; background: #065f46; color: #34d399; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }
        .founder-tag { background: #1e3a8a; color: #60a5fa; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Xiamo Network <span class="status-tag">Live Mainnet</span></h1>
        </div>
        
        <div class="stats-grid">
            <div class="card"><span class="label">Total Supply</span><span class="value">{{ supply }} / 210M XM</span></div>
            <div class="card"><span class="label">Block Height</span><span class="value">#{{ height }}</span></div>
            <div class="card"><span class="label">Next Reward</span><span class="value">{{ reward }} XM</span></div>
            <div class="card"><span class="label">Halving In</span><span class="value">{{ halving_in }} Blocks</span></div>
        </div>

        <h2 style="margin-top: 40px;">Rich List (Top Holders)</h2>
        <table>
            <thead><tr><th>Wallet Address</th><th>Balance</th></tr></thead>
            <tbody>
                {% for addr, bal in rich_list %}
                <tr>
                    <td class="address">
                        {{ addr }}
                        {% if addr == founder %} <span class="founder-tag">FOUNDER</span> {% endif %}
                    </td>
                    <td><b style="color:#f8fafc">{{ "%.2f"|format(bal) }}</b> XM</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <p style="text-align:center; color:#475569; font-size:0.8rem; margin-top:50px;">Xiamo Core v1.0 - English Language Project</p>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    supply = sum(blockchain_data["balances"].values())
    height = blockchain_data['block_height']
    reward = get_current_reward()
    halving_in = HALVING_INTERVAL - (height % HALVING_INTERVAL)
    rich_list = sorted(blockchain_data["balances"].items(), key=lambda x: x[1], reverse=True)[:10]
    
    return render_template_string(HTML_TEMPLATE, 
                                 supply=f"{supply:,.2f}", 
                                 height=height, 
                                 reward=reward, 
                                 halving_in=halving_in,
                                 rich_list=rich_list,
                                 founder=FOUNDER_ADDRESS)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

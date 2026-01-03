from flask import Flask, jsonify, request, render_template_string
import time
import os

app = Flask(__name__)
# Kazılan blokları hafızada tutan liste
mined_blocks = []

# Görsel Arayüz (HTML)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Xiamo Network Explorer</title>
    <meta http-equiv="refresh" content="10"> <style>
        body { font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        .block-card { background: #333; margin: 10px; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
        .address { color: #4CAF50; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⛏️ Xiamo Global Explorer</h1>
        <p>Ağ Durumu: <span style="color: #4CAF50;">Çevrimiçi</span></p>
        <hr>
        <h3>Son Kazılan Bloklar</h3>
        {% for block in blocks[::-1] %}
        <div class="block-card">
            <strong>Blok Sahibi:</strong> <br>
            <span class="address">{{ block.address }}</span> <br>
            <small>Zaman: {{ block.time }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, blocks=mined_blocks)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if data:
        # Gelen veriyi listeye ekle
        data['time'] = time.strftime('%H:%M:%S')
        mined_blocks.append(data)
        # Sadece son 10 bloğu tut (hafıza dolmasın diye)
        if len(mined_blocks) > 10: mined_blocks.pop(0)
        return jsonify({"success": True})
    return jsonify({"error": "No data"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

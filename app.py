cat << 'EOF' > miner.py
import hashlib, requests, time, json, os

NODE_URL = "https://xiamo-node.onrender.com"

def ghost_hash(address, nonce):
    base = hashlib.blake2b(f"{address}{nonce}".encode(), digest_size=32).hexdigest()
    if int(base[-1], 16) % 2 == 0:
        mix = hashlib.sha3_256(base.encode()).hexdigest()
    else:
        mix = hashlib.blake2b(f"{base}{nonce}".encode(), digest_size=32).hexdigest()
    return hashlib.sha3_256(f"{mix}{base}".encode()).hexdigest()

def start():
    with open("xiamo_vault.json", "r") as f:
        addr = json.load(f)["address"]

    print(f"Xiamo Ghost-Miner Active: {addr}")
    nonce = 0
    start_t = time.time()
    
    while True:
        res_hash = ghost_hash(addr, nonce)
        
        if nonce % 2000 == 0:
            os.system('clear')
            try:
                n = requests.get(f"{NODE_URL}/network_stats", timeout=2).json()
                diff, height = n["difficulty"], n["block_height"]
            except: diff, height = 4, "ERR"
            
            elapsed = time.time() - start_t
            print(f"XIAMO GHOST-HASH | H/s: {int(nonce/elapsed) if elapsed > 0 else 0}")
            print(f"NET HEIGHT: {height} | DIFF: {diff}")
            print(f"LAST HASH: {res_hash[:40]}...")

        if res_hash.startswith("0" * 4): # Diff check
            requests.post(f"{NODE_URL}/mine", json={"address": addr, "nonce": nonce})
            print("\n[!] BLOCK FOUND!")
            
        nonce += 1

if __name__ == "__main__":
    start()
EOF

import urllib.request
import json
import time

print("Testing Sovereign RAG Mobile & Offline Endpoints...")

# 1. Test UI root
res_ui = urllib.request.urlopen("http://127.0.0.1:8000/")
assert res_ui.status == 200
html = res_ui.read().decode('utf-8')
assert "<title>SOVEREIGN RAG" in html
assert "manifest.json" in html
assert "btn-phone-modal" in html
print("  [PASS] Root Web UI & Mobile Manifest tags: OK (200)")

# 2. Test Manifest JSON
res_mf = urllib.request.urlopen("http://127.0.0.1:8000/manifest.json")
assert res_mf.status == 200
manifest_data = json.loads(res_mf.read().decode('utf-8'))
assert manifest_data["display"] == "standalone"
print(f"  [PASS] PWA Manifest: OK (Name: {manifest_data['name']}, Display: {manifest_data['display']})")

# 3. Test Service Worker
res_sw = urllib.request.urlopen("http://127.0.0.1:8000/sw.js")
assert res_sw.status == 200
sw_code = res_sw.read().decode('utf-8')
assert "CACHE_NAME" in sw_code
print("  [PASS] Offline Service Worker (sw.js): OK (200)")

# 4. Test Network Info & Dynamic QR SVG
res_net = urllib.request.urlopen("http://127.0.0.1:8000/api/network-info")
assert res_net.status == 200
net_data = json.loads(res_net.read().decode('utf-8'))
assert "phone_url" in net_data
assert "<svg" in net_data["qr_svg"]
print(f"  [PASS] Network Info & QR Code: OK (Phone URL: {net_data['phone_url']})")

# 5. Test Phone LAN Access (using local IP)
local_ip = net_data["lan_ip"]
port = net_data["port"]
lan_url = f"http://{local_ip}:{port}/api/knowledge"
res_lan = urllib.request.urlopen(lan_url)
assert res_lan.status == 200
kb_data = json.loads(res_lan.read().decode('utf-8'))
print(f"  [PASS] Phone LAN Endpoint ({lan_url}): OK ({len(kb_data)} documents)")

# 6. Test RAG Chat Endpoint from LAN
chat_req = urllib.request.Request(
    f"http://{local_ip}:{port}/api/chat",
    data=json.dumps({"query": "What are the staging database credentials?", "clearance_level": 3}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
res_chat = urllib.request.urlopen(chat_req)
assert res_chat.status == 200
chat_data = json.loads(res_chat.read().decode('utf-8'))
print(f"  [PASS] Phone LAN Chat Query: OK (Latency: {chat_data.get('latency_ms')}ms, Verdict: {chat_data.get('verdict')})")

print("\n>>> ALL MOBILE & OFFLINE VERIFICATIONS PASSED SUCCESSFULLY! <<<")


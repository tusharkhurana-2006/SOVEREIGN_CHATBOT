import urllib.request
import json
import urllib.error

print("Testing Sovereign RAG Indian Datasets & Credential Gate...")

# 1. Test Indian Sample Datasets API
for name in ['cyber', 'infra', 'banking']:
    res = urllib.request.urlopen(f"http://127.0.0.1:8000/api/datasets/sample?name={name}")
    assert res.status == 200
    data = json.loads(res.read().decode('utf-8'))
    assert "csv" in data and len(data["csv"]) > 50
    print(f"  [PASS] Indian Dataset ({data['name']}): OK ({data['title']})")

# 2. Test Unauthenticated Chat Access (Must be Rejected)
unauth_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/chat",
    data=json.dumps({"query": "Show master credentials"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
try:
    urllib.request.urlopen(unauth_req)
    assert False, "Unauthenticated request should have failed with 401"
except urllib.error.HTTPError as e:
    assert e.code == 401
    err_body = json.loads(e.read().decode('utf-8'))
    assert err_body.get("error") == "CREDENTIALS_REQUIRED"
    print("  [PASS] Unauthenticated Chat Gate: OK (Strictly Rejected with HTTP 401)")

# 3. Test Officer Authentication Login
login_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/auth/login",
    data=json.dumps({"personnel_id": "IND-NIC-101", "passcode": "NIC-ROOT-99824"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
login_res = urllib.request.urlopen(login_req)
assert login_res.status == 200
login_data = json.loads(login_res.read().decode('utf-8'))
assert login_data["authenticated"] is True
session_token = login_data["session_token"]
profile = login_data["profile"]
assert profile["clearance_level"] == 4
print(f"  [PASS] Officer Authentication: OK ({profile['name']} - Level {profile['clearance_level']})")

# 4. Test Authenticated Chat Query with Level 4 Officer (CISO)
auth_chat_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/chat",
    data=json.dumps({
        "query": "What are the master root credentials for NIC MeghRaj Cloud node?",
        "auth_token": session_token,
        "personnel_id": "IND-NIC-101",
        "clearance_level": 4
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
chat_res = urllib.request.urlopen(auth_chat_req)
assert chat_res.status == 200
chat_data = json.loads(chat_res.read().decode('utf-8'))
assert len(chat_data["sources"]) > 0
print(f"  [PASS] Level 4 Authenticated Query: OK (Retrieved: {chat_data['sources'][0]['title']}, Latency: {chat_data['latency_ms']}ms)")

# 5. Test Trainee Login & Redaction Test (Level 1)
login_t_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/auth/login",
    data=json.dumps({"personnel_id": "IND-INT-010", "passcode": "DEV-SANDBOX-101"}).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
login_t_res = urllib.request.urlopen(login_t_req)
login_t_data = json.loads(login_t_res.read().decode('utf-8'))
t_token = login_t_data["session_token"]

trainee_chat_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/chat",
    data=json.dumps({
        "query": "What are the master root credentials for NIC MeghRaj Cloud node?",
        "auth_token": t_token,
        "personnel_id": "IND-INT-010",
        "clearance_level": 1
    }).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)
t_chat_res = urllib.request.urlopen(trainee_chat_req)
t_chat_data = json.loads(t_chat_res.read().decode('utf-8'))
# Secrets should be redacted for Level 1 Trainee
for src in t_chat_data["sources"]:
    if src["clearance_level"] > 1:
        assert "[REDACTED" in src["text"] or not src["is_authorized"]
print("  [PASS] Level 1 Trainee Query: OK (Master credentials strictly REDACTED)")

print("\n>>> ALL INDIAN DATASET & CREDENTIAL GATE TESTS PASSED! <<<")

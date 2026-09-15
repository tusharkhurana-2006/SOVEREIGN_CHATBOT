import urllib.request
import traceback

try:
    print("Connecting to http://127.0.0.1:8000/api/network-info ...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/network-info", headers={"User-Agent": "TestClient/1.0"})
    with urllib.request.urlopen(req, timeout=5) as res:
        print("Status:", res.status)
        print("Data:", res.read().decode('utf-8')[:100])
except Exception as e:
    print("Caught Exception:", type(e), e)
    traceback.print_exc()

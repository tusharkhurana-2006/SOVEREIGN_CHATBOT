import http.server
import socketserver
import os
import sys

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        # Keep logs clean
        sys.stdout.write(f"[HTTP] {self.address_string()} - - [{self.log_date_time_string()}] {format%args}\n")
        sys.stdout.flush()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    global PORT
    for attempt_port in range(PORT, PORT + 20):
        try:
            handler = CustomHandler
            with socketserver.TCPServer(("", attempt_port), handler) as httpd:
                print(f"===============================================================")
                print(f"  ANTIGRAV // RESEARCH AI SIMULATION SUITE ACTIVE")
                print(f"  LOCAL SERVER RUNNING AT: http://localhost:{attempt_port}")
                print(f"  LOCAL IP: http://127.0.0.1:{attempt_port}")
                print(f"===============================================================")
                sys.stdout.flush()
                httpd.serve_forever()
        except OSError as e:
            if "address already in use" in str(e).lower() or e.errno == 10048 or e.errno == 98:
                continue
            else:
                raise e

if __name__ == "__main__":
    run_server()

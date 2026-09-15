import http.server
import socketserver
import os
import sys
import socket

PORT = 8000


def _port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((host, port))
            return True
        except OSError:
            return False


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

class ThreadedStaticServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = False
    daemon_threads = True


def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    global PORT
    bind_host = "0.0.0.0"
    chosen_port = None
    for attempt_port in range(PORT, PORT + 20):
        if _port_is_free(bind_host, attempt_port):
            chosen_port = attempt_port
            break

    if chosen_port is None:
        print("[HTTP] ERROR: No free port in range 8000–8019. Stop other local servers and retry.")
        sys.exit(1)

    PORT = chosen_port
    try:
        with ThreadedStaticServer((bind_host, PORT), CustomHandler) as httpd:
            print(f"===============================================================")
            print(f"  ANTIGRAV // RESEARCH AI SIMULATION SUITE ACTIVE")
            print(f"  LOCAL SERVER RUNNING AT: http://localhost:{PORT}")
            print(f"  LOCAL IP: http://127.0.0.1:{PORT}")
            if PORT != 8000:
                print(f"  (Port 8000 was busy — using {PORT} instead.)")
            print(f"===============================================================")
            sys.stdout.flush()
            httpd.serve_forever()
    except OSError as e:
        print(f"[HTTP] Failed to bind {bind_host}:{PORT}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
import os

DATA_DIR = Path(os.environ.get("DATA_DIR", "/tmp/counter-data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
COUNTER_FILE = DATA_DIR / "counter.json"
lock = threading.Lock()

def load_count():
    try:
        return int(json.loads(COUNTER_FILE.read_text()).get("count", 0))
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return 0

count = load_count()

def persist():
    tmp = COUNTER_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"count": count}))
    tmp.replace(COUNTER_FILE)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global count
        if self.path == "/count":
            with lock:
                payload = json.dumps({"count": count}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        with lock:
            count += 1
            persist()
            current = count

        payload = f"Request received. Counter={current}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)

ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

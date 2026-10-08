from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
from engine import Core
from common import chain_ok

C = None

def core():
    global C
    if C is None:
        C = Core(os.environ.get("TITAN_DB", "data/state.db"))
    return C

def read_json(handler):
    n = int(handler.headers.get("content-length") or 0)
    raw = handler.rfile.read(n) if n else b"{}"
    if not raw:
        raw = b"{}"
    return json.loads(raw)

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET,POST,OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET,POST,OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/health", "/healthz"):
            return self._send(200, {"ok": True, "service": "adaptive-ui-sdk", "build": "T21-143"})
        if path == "/events":
            rows = core().s.list()
            return self._send(200, {"ok": True, "chain": chain_ok(core().s), "count": len(rows), "events": rows})
        if path == "/chain":
            return self._send(200, {"ok": chain_ok(core().s), "count": len(core().s.list())})
        if path in ("/", "/index.html"):
            ui = os.path.join(os.path.dirname(__file__), "..", "..", "apps", "web", "index.html")
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("cache-control", "no-store")
            self.end_headers()
            self.wfile.write(open(ui, "rb").read())
            return
        self._send(404, {"error": "no route"})

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            body = read_json(self)
        except Exception as e:
            return self._send(400, {"error": "invalid json", "detail": str(e)})
        try:
            if path == "/proof":
                return self._send(200, core().proof())
            if path == "/resolve":
                session = str(body.get("session") or "").strip()
                device = str(body.get("device") or "").strip()
                task = str(body.get("task") or "").strip()
                if not session or device not in ("phone", "tablet", "desktop") or not task:
                    return self._send(400, {"error": "validation", "fields": ["session", "device", "task"]})
                width = int(body.get("width"))
                if width < 0 or width > 8000:
                    return self._send(400, {"error": "validation", "fields": ["width"]})
                online = bool(body.get("online", True))
                rec = core().resolve(session, device, width, task, online)
                return self._send(200, {"ok": True, "record": rec})
            if path == "/observe":
                session = str(body.get("session") or "").strip()
                if not session:
                    return self._send(400, {"error": "validation", "fields": ["session"]})
                latency = int(body.get("latency_ms"))
                if latency < 0 or latency > 60000:
                    return self._send(400, {"error": "validation", "fields": ["latency_ms"]})
                rec = core().observe(session, latency)
                return self._send(200, {"ok": True, "record": rec})
            if path == "/adapt":
                session = str(body.get("session") or "").strip()
                if not session:
                    return self._send(400, {"error": "validation", "fields": ["session"]})
                rec = core().adapt(session)
                return self._send(200, {"ok": True, "record": rec, "chain": chain_ok(core().s)})
            self._send(404, {"error": "no route"})
        except Exception as e:
            self._send(400, {"error": str(e)})

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8765"))), H).serve_forever()

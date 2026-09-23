
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os
from engine import Core
C=None
def core():
    global C
    if C is None: C=Core(os.environ.get("TITAN_DB","data/state.db"))
    return C
class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        raw=json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type","application/json")
        self.send_header("access-control-allow-origin","*")
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path in ("/health","/healthz"):
            return self._send(200, {"ok":True})
        ui=os.path.join(os.path.dirname(__file__), "..","..","apps","web","index.html")
        self.send_response(200); self.send_header("content-type","text/html"); self.end_headers()
        self.wfile.write(open(ui,"rb").read())
    def do_POST(self):
        n=int(self.headers.get("content-length") or 0)
        json.loads(self.rfile.read(n) or b"{}")
        try:
            if self.path=="/proof":
                return self._send(200, core().proof())
            self._send(404, {"error":"no route"})
        except Exception as e:
            self._send(400, {"error":str(e)})
    def log_message(self,*a): pass
if __name__=="__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT","8765"))), H).serve_forever()

import hashlib, json, sqlite3, time, uuid
from pathlib import Path
class Store:
    def __init__(self, db):
        self.db = Path(db); self.db.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(self.db)); self.con.row_factory = sqlite3.Row
        self.con.execute("CREATE TABLE IF NOT EXISTS recs(id TEXT PRIMARY KEY, kind TEXT, body TEXT, ts TEXT, prev TEXT, h TEXT)")
        self.con.commit()
    def append(self, kind, body):
        prev = self.con.execute("SELECT h FROM recs ORDER BY rowid DESC LIMIT 1").fetchone()
        prevh = prev["h"] if prev else "GENESIS"
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        rid = str(uuid.uuid4())
        payload = json.dumps(body, sort_keys=True)
        h = hashlib.sha256((prevh+rid+kind+payload+ts).encode()).hexdigest()
        self.con.execute("INSERT INTO recs VALUES(?,?,?,?,?,?)", (rid,kind,payload,ts,prevh,h))
        self.con.commit()
        return {"id":rid,"hash":h,"prev":prevh,"ts":ts,"kind":kind,"body":body}
    def list(self, kind=None):
        q = "SELECT * FROM recs" + (" WHERE kind=?" if kind else "") + " ORDER BY rowid"
        return [dict(r) for r in self.con.execute(q, (kind,) if kind else ()).fetchall()]
def chain_ok(store):
    prev="GENESIS"
    for r in store.list():
        if r["prev"]!=prev: return False
        h=hashlib.sha256((r["prev"]+r["id"]+r["kind"]+r["body"]+r["ts"]).encode()).hexdigest()
        if h!=r["h"]: return False
        prev=r["h"]
    return True

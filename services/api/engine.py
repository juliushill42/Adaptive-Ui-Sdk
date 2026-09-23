
from common import Store, chain_ok
import json
def classify(device, width, online):
    if not online: return "offline"
    if device=="phone" or width<600: return "phone-narrow"
    if width<1100: return "tablet"
    return "desktop"
class Core:
    def __init__(self, db): self.s=Store(db)
    def resolve(self, session, device, width, task, online=True):
        return self.s.append("ui.resolved", {"session":session,"profile":classify(device,width,online),"task":task})
    def observe(self, session, latency_ms):
        return self.s.append("ui.observed", {"session":session,"latency_ms":latency_ms})
    def adapt(self, session):
        obs=[json.loads(r["body"]) for r in self.s.list("ui.observed") if json.loads(r["body"])["session"]==session]
        density="compact" if sum(1 for o in obs if o["latency_ms"]>250)>=2 else "comfortable"
        return self.s.append("ui.adapted", {"session":session,"density":density})
    def proof(self):
        self.resolve("s1","phone",390,"compose",True)
        self.observe("s1",40); self.observe("s1",300); self.observe("s1",310)
        a=self.adapt("s1")
        return {"ok":chain_ok(self.s),"adapted":a}

import json, time
from pathlib import Path

def write_audit_log(out_dir: Path, payload: dict):
    log = {"timestamp": int(time.time()), "payload": payload, "version": "0.1.0"}
    with open(out_dir / "audit_log.json","w",encoding="utf-8") as f:
        json.dump(log, f, indent=2)

import os, json, yaml, re

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_texts(folder: str, readers=None):
    readers = readers or ["txt","md"]
    docs = []
    for root, _, files in os.walk(folder):
        for fn in files:
            ext = fn.split(".")[-1].lower()
            if ext in readers:
                p = os.path.join(root, fn)
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
                txt = re.sub(r"\s+", " ", txt)
                docs.append({"path": p, "text": txt})
    return docs

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

#!/usr/bin/env python3
import os, sys, subprocess, base64, requests
from pathlib import Path
from datetime import datetime

def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def api_push(repo, path, content, message, pat):
    headers = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"https://api.github.com/repos/toxicwind/{repo}/contents/{path}", headers=headers, timeout=10)
    sha = r.json().get("sha") if r.status_code == 200 else None
    b64 = base64.b64encode(content.encode() if isinstance(content, str) else content).decode()
    payload = {"message": message, "content": b64}
    if sha: payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/toxicwind/{repo}/contents/{path}", headers=headers, json=payload, timeout=15)
    return r.status_code, r.json()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("repo")
    p.add_argument("file")
    p.add_argument("-m", "--message", default=None)
    p.add_argument("--pat", default=os.environ.get("GITHUB_TOKEN", ""))
    args = p.parse_args()
    content = Path(args.file).read_bytes()
    msg = args.message or f"add {Path(args.file).name}"
    status, result = api_push(args.repo, Path(args.file).name, content, msg, args.pat)
    print(f"[{ts()}] {args.file} -> {args.repo}: {status}")
    if status in [200, 201]:
        print(f"  OK: {result.get('content', {}).get('html_url', 'pushed')}")
    else:
        print(f"  ERR: {result.get('message', result)[:100]}")

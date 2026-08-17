#!/usr/bin/env python3
import os
import time
import urllib.request

url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
interval = int(os.environ.get("RENDER_KEEPALIVE_INTERVAL", "600"))

if not url:
    print("[keepalive] RENDER_EXTERNAL_URL is not available; keepalive disabled.", flush=True)
    raise SystemExit(0)

health_url = url + "/health"
print(f"[keepalive] enabled: {health_url} every {interval}s", flush=True)

while True:
    try:
        with urllib.request.urlopen(health_url, timeout=15) as response:
            print(f"[keepalive] health ping: HTTP {response.status}", flush=True)
    except Exception as exc:
        print(f"[keepalive] health ping failed: {exc}", flush=True)
    time.sleep(interval)

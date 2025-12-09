#!/usr/bin/env python3
import os
import time
import socket
from datetime import datetime, timezone
import psutil
import requests

SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:5000")
API_KEY = os.environ.get("API_KEY", "supersecret")
INTERVAL = int(os.environ.get("INTERVAL", "10"))

def collect_metrics():
    hostname = os.environ.get("AGENT_HOSTNAME", socket.gethostname())
    ts = datetime.now(timezone.utc).isoformat()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count(logical=True)
    vm = psutil.virtual_memory()
    mem_total = vm.total
    mem_used = vm.used
    mem_percent = vm.percent
    du = psutil.disk_usage("/")
    disk_total = du.total
    disk_used = du.used
    disk_percent = du.percent
    try:
        load1, load5, load15 = psutil.getloadavg()
    except:
        load1 = load5 = load15 = 0.0
    net = psutil.net_io_counters()
    return {
        "hostname": hostname,
        "ts": ts,
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "mem_total": mem_total,
        "mem_used": mem_used,
        "mem_percent": mem_percent,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_percent": disk_percent,
        "load1": load1,
        "load5": load5,
        "load15": load15,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
    }

def post_metrics(payload):
    try:
        resp = requests.post(
            f"{SERVER_URL.rstrip('/')}/metrics",
            json=payload,
            headers={"X-API-KEY": API_KEY},
            timeout=10
        )
        return resp.status_code, resp.text
    except Exception as e:
        return None, str(e)

def main():
    print("Agent started...")
    while True:
        m = collect_metrics()
        status, msg = post_metrics(m)
        print(f"{datetime.now()}: {status} {msg}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
List wired and wireless clients from Catalyst Center.
Uses same config as CATC MCP server (.env: CATC_URL, CATC_USERNAME, CATC_PASSWORD).
Uses Data API: GET /dna/data/api/v1/clients with type=Wired | type=Wireless
"""
import os
import sys
import base64
from pathlib import Path

def load_dotenv(env_file: str = ".env") -> None:
    env_path = Path(__file__).resolve().parent / env_file
    if not env_path.exists():
        print(f"Error: {env_file} not found at {env_path}", file=sys.stderr)
        sys.exit(1)
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if "#" in value:
                value = value.split("#")[0]
            value = value.strip().strip("'\"")
            os.environ[key.strip()] = value

load_dotenv()

CATC_URL = os.environ.get("CATC_URL", "").rstrip("/")
CATC_USERNAME = os.environ.get("CATC_USERNAME", "")
CATC_PASSWORD = os.environ.get("CATC_PASSWORD", "")
CATC_VERIFY_SSL = os.environ.get("CATC_VERIFY_SSL", "false").lower() in ("true", "1", "yes")

if not all((CATC_URL, CATC_USERNAME, CATC_PASSWORD)):
    print("Error: Set CATC_URL, CATC_USERNAME, CATC_PASSWORD in .env", file=sys.stderr)
    sys.exit(1)

import requests

if not CATC_VERIFY_SSL:
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

auth_url = f"{CATC_URL}/dna/system/api/v1/auth/token"
credentials = base64.b64encode(f"{CATC_USERNAME}:{CATC_PASSWORD}".encode()).decode()
try:
    r = requests.post(
        auth_url,
        headers={"Content-Type": "application/json", "Authorization": f"Basic {credentials}"},
        verify=CATC_VERIFY_SSL,
        timeout=30,
    )
    r.raise_for_status()
    token = r.json().get("Token")
except Exception as e:
    print(f"Auth failed: {e}", file=sys.stderr)
    sys.exit(1)

# 1) Client health summary (Intent API) – wired vs wireless counts
url_health = f"{CATC_URL}/dna/intent/api/v1/client-health"
headers = {"Content-Type": "application/json", "X-Auth-Token": token}
try:
    r = requests.get(url_health, headers=headers, params={"limit": 100}, verify=CATC_VERIFY_SSL, timeout=30)
    r.raise_for_status()
    health = r.json()
except Exception as e:
    print(f"Client-health API error: {e}", file=sys.stderr)
    sys.exit(1)

# Parse wired/wireless counts from scoreDetail (CLIENT_TYPE = WIRED | WIRELESS)
wired_count = 0
wireless_count = 0
all_count = 0
for site in health.get("response") or []:
    for detail in site.get("scoreDetail") or []:
        cat = detail.get("scoreCategory") or {}
        if cat.get("scoreCategory") != "CLIENT_TYPE":
            continue
        val = (cat.get("value") or "").upper()
        cnt = detail.get("clientCount") or 0
        if val == "WIRED":
            wired_count += cnt
        elif val == "WIRELESS":
            wireless_count += cnt
        elif val == "ALL":
            all_count += cnt

# 2) Optional: try Data API for per-client list (may 404 on some versions)
wired_list = []
wireless_list = []
url_data = f"{CATC_URL}/dna/data/api/v1/clients"
for client_type, out_list in [("Wired", wired_list), ("Wireless", wireless_list)]:
    try:
        r = requests.get(url_data, headers=headers, params={"limit": 500, "type": client_type}, verify=CATC_VERIFY_SSL, timeout=30)
        r.raise_for_status()
        data = r.json()
        out_list.extend(data.get("response") or [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code != 404:
            print(f"Note: Data API clients ({client_type}): {e}", file=sys.stderr)
    except Exception as e:
        print(f"Note: Data API clients ({client_type}): {e}", file=sys.stderr)

# Prefer list from Data API if we got it; otherwise show counts from client-health
has_lists = bool(wired_list or wireless_list)

def fmt(c):
    mac = c.get("macAddress") or "-"
    ip = c.get("ipv4Address") or "-"
    name = (c.get("name") or c.get("username") or "-")
    return f"{mac:<20} {ip:<16} {name}"

print("=" * 80)
print("Catalyst Center – Wired clients" + (" ({})".format(len(wired_list)) if has_lists else " (count: {})".format(wired_count)))
print("=" * 80)
if has_lists and wired_list:
    print(f"{'MAC Address':<20} {'IPv4':<16} Name/Username")
    print("-" * 80)
    for c in wired_list:
        print(fmt(c))
elif not has_lists:
    print("Count (from client-health):", wired_count)
else:
    print("(none)")

print()
print("=" * 80)
print("Catalyst Center – Wireless clients" + (" ({})".format(len(wireless_list)) if has_lists else " (count: {})".format(wireless_count)))
print("=" * 80)
if has_lists and wireless_list:
    print(f"{'MAC Address':<20} {'IPv4':<16} Name/Username")
    print("-" * 80)
    for c in wireless_list:
        print(fmt(c))
elif not has_lists:
    print("Count (from client-health):", wireless_count)
else:
    print("(none)")

print()
total = (len(wired_list) + len(wireless_list)) if has_lists else (wired_count + wireless_count)
print("Summary: wired {} | wireless {} | total {}".format(
    len(wired_list) if has_lists else wired_count,
    len(wireless_list) if has_lists else wireless_count,
    total,
))

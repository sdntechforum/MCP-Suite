#!/usr/bin/env python3
"""
List all devices in Catalyst Center inventory.
Uses same config as CATC MCP server (.env: CATC_URL, CATC_USERNAME, CATC_PASSWORD).
"""
import os
import sys
import base64
from pathlib import Path

# Load .env from project root
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
            # Remove inline comment and strip whitespace/quotes
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

# Auth token
auth_url = f"{CATC_URL}/dna/system/api/v1/auth/token"
credentials = base64.b64encode(f"{CATC_USERNAME}:{CATC_PASSWORD}".encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {credentials}",
}
try:
    r = requests.post(auth_url, headers=headers, verify=CATC_VERIFY_SSL, timeout=30)
    r.raise_for_status()
    token = r.json().get("Token")
except Exception as e:
    print(f"Auth failed: {e}", file=sys.stderr)
    sys.exit(1)

# Get network devices (inventory)
url = f"{CATC_URL}/dna/intent/api/v1/network-device"
headers = {"Content-Type": "application/json", "X-Auth-Token": token}
try:
    r = requests.get(url, headers=headers, verify=CATC_VERIFY_SSL, timeout=60)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print(f"API request failed: {e}", file=sys.stderr)
    sys.exit(1)

devices = data.get("response") or []
print(f"Catalyst Center device inventory ({len(devices)} devices)\n")
print(f"{'Hostname':<30} {'Type':<25} {'IP':<18} {'Serial':<20} {'ID'}")
print("-" * 110)
for d in devices:
    hostname = (d.get("hostname") or d.get("name") or "-")
    dev_type = (d.get("type") or "-")
    ip = (d.get("managementIpAddress") or "-")
    serial = (d.get("serialNumber") or "-")
    dev_id = (d.get("id") or "-")
    print(f"{str(hostname):<30} {str(dev_type):<25} {str(ip):<18} {str(serial):<20} {str(dev_id)}")

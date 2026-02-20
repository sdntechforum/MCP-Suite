#!/usr/bin/env python3
"""
List all Splunk indexes via REST API.
Uses .env: SPLUNK_HOST, SPLUNK_PORT, SPLUNK_API_KEY, SPLUNK_VERIFY_SSL.
Use when the Splunk MCP backend returns 404 (MCP app not installed).
"""
import os
import sys
from pathlib import Path

def load_dotenv(env_file: str = ".env") -> None:
    env_path = Path(__file__).resolve().parent / env_file
    if not env_path.exists():
        print(f"Error: {env_file} not found", file=sys.stderr)
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

host = (os.environ.get("SPLUNK_HOST") or "").rstrip("/").split("/")[0]
port = os.environ.get("SPLUNK_PORT", "443")
api_key = os.environ.get("SPLUNK_API_KEY", "")
verify = os.environ.get("SPLUNK_VERIFY_SSL", "false").lower() in ("true", "1", "yes")

if not host or not api_key:
    print("Error: SPLUNK_HOST and SPLUNK_API_KEY required in .env", file=sys.stderr)
    sys.exit(1)

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

import requests

# Try common Splunk REST paths for indexes
base_url = f"https://{host}:{port}"
data = None
last_error = None
for path in ["/services/data/indexes", "/en-US/services/data/indexes"]:
    url = base_url + path
    try:
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            verify=verify,
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            break
        last_error = f"{path}: HTTP {r.status_code}"
        if r.status_code == 401:
            last_error += " (check SPLUNK_API_KEY)"
        try:
            body = (r.text or "")[:200]
            if body:
                last_error += f" - {body}"
        except Exception:
            pass
    except requests.exceptions.SSLError as e:
        last_error = f"{path}: SSL error - {e}"
    except Exception as e:
        last_error = f"{path}: {e}"

if data is None:
    print("Failed to get indexes from Splunk REST API.", file=sys.stderr)
    if last_error:
        print(f"Last error: {last_error}", file=sys.stderr)
    sys.exit(1)

# Parse entry list (REST returns feed with entry[])
entries = data.get("entry") or []
if not entries and "entry" not in data:
    # Some versions return a different structure
    entries = data.get("content", {}).get("entry", []) if isinstance(data.get("content"), dict) else []

print(f"Splunk indexes ({len(entries)} total)\n")
print(f"{'Index name':<30} {'Current size (MB)':<18} {'Event count':<16} {'Max size (MB)'}")
print("-" * 85)

for e in entries:
    name = e.get("name", "-")
    c = e.get("content") or {}
    if isinstance(c, list):
        c = c[0] if c else {}
    current_mb = c.get("currentDBSizeMB") or c.get("currentDBSizeMB") or "-"
    events = c.get("totalEventCount") or c.get("totalEventCount") or "-"
    max_mb = c.get("maxTotalDataSizeMB") or c.get("maxTotalDataSizeMB") or "-"
    print(f"{str(name):<30} {str(current_mb):<18} {str(events):<16} {str(max_mb)}")

if not entries:
    print("(no indexes or unexpected response structure)")
    print("Raw keys:", list(data.keys()))

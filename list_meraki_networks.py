#!/usr/bin/env python3
"""List Meraki orgs and networks using MERAKI_KEY from .env. No secrets in code."""
import os
import sys

# Load MERAKI_KEY from .env in script directory (no secrets printed)
_env_path = os.path.join(os.path.dirname(__file__) or ".", ".env")
if os.path.isfile(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                if k.strip() in ("MERAKI_KEY", "MERAKI_DASHBOARD_API_KEY"):
                    val = v.strip().strip('"').strip("'").strip()
                    if val:
                        os.environ["MERAKI_KEY"] = val  # last occurrence wins

# Prefer MERAKI_DASHBOARD_API_KEY if set (e.g. from command line)
api_key = (os.getenv("MERAKI_DASHBOARD_API_KEY") or os.getenv("MERAKI_KEY") or "").strip()
_placeholders = ("your_actual_", "your_meraki_", "your_api_key")
if not api_key or any(api_key.lower().startswith(p) for p in _placeholders):
    print("MERAKI_KEY is not set or is a placeholder. Set it in .env and run from project root.")
    sys.exit(1)

import urllib.request
import urllib.error
import json

def meraki_get(path: str) -> dict:
    req = urllib.request.Request(
        f"https://api.meraki.com/api/v1{path}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Network-MCP-Server/1.0 (Meraki API client)",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Meraki API error {e.code}: {e.reason}", file=sys.stderr)
        if body:
            print(f"Response: {body[:500]}", file=sys.stderr)
        raise

def main():
    orgs = meraki_get("/organizations")
    if not orgs:
        print("No organizations found for this API key.")
        return

    # --clients: list clients for a network (by id or name substring)
    if len(sys.argv) >= 3 and sys.argv[1] == "--clients":
        target = sys.argv[2]
        for org in orgs:
            org_id = org.get("id")
            networks = meraki_get(f"/organizations/{org_id}/networks")
            for n in networks:
                nid = n.get("id", "")
                name = n.get("name", "")
                if target == nid or target.upper() in name.upper():
                    clients = meraki_get(f"/networks/{nid}/clients")
                    print(f"Network: {name} (id: {nid})")
                    print(f"Clients: {len(clients)} connected\n")
                    for c in clients:
                        desc = c.get("description") or c.get("mac", "?")
                        ip = c.get("ip", "—")
                        mac = c.get("mac", "—")
                        print(f"  - {desc}  |  MAC: {mac}  |  IP: {ip}")
                    return
        print(f"No network found matching '{target}'.")
        return

    # --find-device: find networks that have devices matching model string (e.g. 9300)
    if len(sys.argv) >= 3 and sys.argv[1] == "--find-device":
        model_substr = sys.argv[2].strip()
        for org in orgs:
            org_id = org.get("id")
            org_name = org.get("name", "?")
            networks = meraki_get(f"/organizations/{org_id}/networks")
            net_id_to_name = {n.get("id"): n.get("name", "?") for n in networks}
            devices = meraki_get(f"/organizations/{org_id}/devices")
            matches = [d for d in devices if model_substr in (d.get("model") or "")]
            if not matches:
                print(f"No devices matching '{model_substr}' in org {org_name}.")
                return
            print(f"Organization: {org_name}")
            print(f"Devices matching '{model_substr}': {len(matches)}\n")
            seen_networks = set()
            for d in matches:
                nid = d.get("networkId")
                net_name = net_id_to_name.get(nid, nid or "?")
                if nid and nid not in seen_networks:
                    seen_networks.add(nid)
                    print(f"  Network: {net_name}  (id: {nid})")
                print(f"    - {d.get('model', '?')}  |  {d.get('name', '?')}  |  serial: {d.get('serial', '?')}")
            return

    for org in orgs:
        org_id = org.get("id")
        org_name = org.get("name", "?")
        print(f"\nOrganization: {org_name} (id: {org_id})")
        try:
            networks = meraki_get(f"/organizations/{org_id}/networks")
            for n in networks:
                name = n.get("name", "?")
                nid = n.get("id", "?")
                product_types = ", ".join(n.get("productTypes", []))
                print(f"  - {name}  (id: {nid})  [{product_types}]")
        except Exception as e:
            print(f"  (error listing networks: {e})")

if __name__ == "__main__":
    main()

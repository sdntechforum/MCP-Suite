# IOS-XE MCP Server — Device Inventory Install Guide

> Companion to `README.md`. This guide covers ONLY the **device-inventory feature** added in `ios_xe_mcp_server.py` v0.2. For first-time install of the suite (Docker, `.env`, etc.) start with the suite-level `README.md` and `.env.example`.

---

## What this feature does

Catalyst Center publishes the inventory of devices it manages — but lots of IOS-XE boxes live **outside** Catalyst Center (super-cores, fusion handoffs, infra/lab routers, legacy WLCs, all SD-WAN edges). Before this patch, an LLM/MCP client had to be told their IPs out-of-band.

The feature adds:

1. **An optional read-only JSON inventory file** (`/app/inventory.json` inside the container) that enumerates known IOS-XE devices with metadata (`name`, `host`, `role`, `site`, `tags`, `enabled`, `notes`).
2. **Two new MCP tools**:
   - `list_devices(name="", role="", site="", tag="")` — filterable listing.
   - `reload_inventory()` — re-read the file at runtime without restarting the container.
3. **Friendly-name resolution** in the existing `show_command` / `config_command`: the `host` arg now accepts either a raw IP/hostname **or** the case-insensitive `name` of an inventory entry (e.g. `"Site-A-Core1"` → `192.0.2.10`).

The inventory file holds **metadata only — never credentials**. Credentials remain in `IOS_XE_USERNAME` / `IOS_XE_PASSWORD` (one shared AAA-backed service account for the whole fleet).

---

## ⚠️ Common pitfalls (read these first)

Three things that bit us during validation. Save yourself the round-trip:

1. **Wrong env-var names.** The credentials are `IOS_XE_USERNAME` and `IOS_XE_PASSWORD` — note the underscore between `IOS` and `XE`. Earlier versions of the master reference (and some older registers) called them `IOSXE_USERNAME` / `IOSXE_PASSWORD`. Those names are **not** read by the server. The container starts fine but every connect attempt returns *"Authentication to device failed"*.
2. **Placeholder credentials in `.env`.** The shipped `.env` has `IOS_XE_USERNAME=admin` and `IOS_XE_PASSWORD=your_default_password`. The container will start, the inventory will load, `list_devices` will work — but `show_command` / `config_command` will fail until you replace these with a real AAA-backed account.
3. **Cursor MCP descriptor cache is sticky.** After rebuilding the container, Cursor often still shows only the old 2 tools (`show_command`, `config_command`). You must Cmd+Shift+P → **"Developer: Reload Window"** to pick up `list_devices` and `reload_inventory`. The server is fine; only Cursor's local descriptor cache is stale.

---

## Prerequisites

- Docker Desktop running, suite already deployed (i.e., `ios-xe-mcp-server` container can be brought up via `docker compose`).
- Python 3 on the host (for the optional smoke-test script — not required for normal use).
- An AAA-backed shared service account with SSH read+config rights on the IOS-XE devices you intend to manage. (TACACS+ via Cisco ISE or RADIUS are both supported.)

---

## Step 1 — Pull the latest code

The patched server, the inventory schema, the example file, and the docker-compose volume mount are already in the repo. From the suite root:

```bash
cd MCP/network-mcp-docker-suite
git status                     # confirm a clean tree
git pull --ff-only             # if you maintain a remote
```

Files involved in this feature:

| Path | Role |
|---|---|
| `ios-xe-mcp-server/ios_xe_mcp_server.py` | Patched server (inventory loader + 2 new tools + friendly-name resolver) |
| `ios-xe-mcp-server/inventory.example.json` | **Committed** reference template (schema + ~9 seeded example devices using RFC5737 documentation IPs) |
| `ios-xe-mcp-server/inventory.json` | **Gitignored** live file the container actually reads |
| `docker-compose.yml` | IOS-XE service: env `IOS_XE_INVENTORY_FILE` + read-only volume mount |
| `.env` | Env block for the IOS-XE MCP, including the new `IOS_XE_INVENTORY_FILE` |
| `.gitignore` | Excludes `ios-xe-mcp-server/inventory.json` |

---

## Step 2 — Seed `inventory.json`

Start from the committed template:

```bash
cd MCP/network-mcp-docker-suite/ios-xe-mcp-server
cp inventory.example.json inventory.json
chmod 600 inventory.json
```

The committed `inventory.example.json` is a **generic template** that uses RFC5737 documentation addresses (192.0.2.0/24) and generic site/device names. It is meant to illustrate the schema and the role variety, not to be deployed as-is. Replace it with your real inventory before running against production devices.

The template seeds ~9 representative entries covering the role variety the inventory was designed for:

| Group | Example devices | What they illustrate |
|---|---|---|
| Cores | `Site-A-Core1`, `Site-A-Core2` | The `core` role, HSRP active/standby tags |
| Fusion / DC handoff | `Site-A-Fusion` | The `fusion` role, per-VRF route-leaking tag |
| SD-WAN edges | `Site-A-Edge1`, `Site-A-Edge2`, `Branch-1-Edge1` | DC anchor vs branch, asymmetric VPN membership |
| SDA fabric (also in CC) | `Site-Fabric-CP-BR-01`, `Site-Fabric-WLC-01` | Devices that are ALSO visible via the Catalyst-Center MCP — friendly-name parity is the value-add here |
| Disabled (`enabled: false`) | `Lab-Router-01` | An entry that exists in topology but is not yet ready for connections |

Edit the file to match your reality:

* **Replace example IPs/names.** All entries use RFC5737 (`192.0.2.x`) and generic names like `Site-A-Core1`. Replace with your real management IPs and hostnames.
* **Disable, do not delete, entries you are still validating.** Set `"enabled": false` to keep the metadata visible without permitting connections.
* **Add or remove devices** as needed. Schema:

  ```json
  {
    "name":    "Site-A-Core1",
    "host":    "192.0.2.10",
    "role":    "core",
    "site":    "Site-A",
    "tags":    ["hsrp-active", "as-64500"],
    "enabled": true,
    "notes":   "L3 super core; HSRP-paired with Site-A-Core2."
  }
  ```

| Field    | Required | Constraints |
|---       |---       |---          |
| `name`   | ✅       | Unique (case-insensitive). Allowed chars `[A-Za-z0-9._-]`, max 64. |
| `host`   | ✅       | IPv4/IPv6 literal **or** RFC 1123 hostname. Re-validated before connect. |
| `role`   | ⬜       | Free-form string, max 64. Used for filtering. |
| `site`   | ⬜       | Free-form string, max 64. Used for filtering. |
| `tags`   | ⬜       | Array of free-form strings (each max 64). Used for filtering. |
| `enabled`| ⬜       | Default `true`. Set `false` to keep an entry visible but block connections. |
| `notes`  | ⬜       | Free-form annotation, max 256. |

> ❌ **Never add credential fields** (`username`, `password`, `key`, etc.). The loader has no concept of credentials and any record-level secret would violate `codeguard-1-hardcoded-credentials`. Credentials go in `.env` only.

---

## Step 3 — Set real credentials in `.env`

Open `MCP/network-mcp-docker-suite/.env` and replace the placeholders. **Do not** rename the variables.

```env
# ========================================
# IOS XE MCP SERVER (Port 8003)
# ========================================
IOS_XE_USERNAME=<your AAA-backed service account>
IOS_XE_PASSWORD=<that account's password>
IOS_XE_INVENTORY_FILE=/app/inventory.json
SSH_TIMEOUT=60
```

Why one shared account, not per-device creds? See the trade-off table at the bottom of the IOS-XE `README.md` ("Why this design"). Short version: per-device creds in a config file would be a `codeguard-1-hardcoded-credentials` violation, and N×containers would explode the port and credential surface. The supported pattern is one TACACS+/RADIUS-backed service account that all targeted IOS-XE devices honor.

> **Security note (codeguard-1-hardcoded-credentials):** the `.env` file is already in `.gitignore`. Confirm with `git check-ignore -v MCP/network-mcp-docker-suite/.env` before committing anything.

---

## Step 4 — Rebuild and restart the container

```bash
cd MCP/network-mcp-docker-suite
docker compose up -d --build ios-xe-mcp-server
```

Check the startup banner for the inventory load line:

```bash
docker logs ios-xe-mcp-server 2>&1 | grep -E "(Loaded credentials|Inventory|Starting SECURE)"
```

You should see:

```text
INFO:__main__:Loaded credentials for user: <your account>
INFO:__main__:Inventory loaded: 9 device(s) from /app/inventory.json
INFO:__main__:Starting SECURE IOS XE MCP server on 0.0.0.0:8003
```

(`9` matches the seeded `inventory.example.json` — your number will differ once you populate `inventory.json` with your own devices.)

If the count is `0` or the line is missing, jump to **Troubleshooting** below.

---

## Step 5 — Reload Cursor's MCP descriptor cache

Cursor caches the tool list it pulled from each MCP server at startup. After rebuilding the container, it usually still shows the old set (`show_command`, `config_command`). To pick up `list_devices` and `reload_inventory`:

* macOS: `Cmd+Shift+P` → **"Developer: Reload Window"**
* Linux/Win: `Ctrl+Shift+P` → **"Developer: Reload Window"**

After the reload, you should see four tools advertised under the `IOS-XE-MCP-Server` entry in Cursor's MCP panel.

---

## Step 6 — Smoke-test from Cursor (or directly via HTTP)

### Option 1 — From Cursor

Ask the agent in this workspace:

> "List all IOS-XE devices in the inventory."
> "Show me only the cores."
> "Run `show ip bgp summary` on Site-A-Core1."

The first two should return device lists; the third will succeed if creds + reachability are good, or return an `Authentication to device failed` envelope (clean error — no credential leakage) if not.

### Option 2 — Direct HTTP smoke test

Save the following as `/tmp/ios_xe_mcp_smoke.py`, then run it with `python3`:

```python
import json, urllib.request

URL = "http://localhost:8003/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}
sid = None

def call(payload):
    h = {**HEADERS, **({"Mcp-Session-Id": sid} if sid else {})}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode(), r.headers.get("Mcp-Session-Id")

def parse_sse(body):
    for line in body.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    return json.loads(body)

body, sid = call({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "smoke", "version": "1.0"},
    },
})
call({"jsonrpc": "2.0", "method": "notifications/initialized"})

body, _ = call({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
tools = sorted(t["name"] for t in parse_sse(body)["result"]["tools"])
print("tools:", tools)

body, _ = call({
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {"name": "list_devices", "arguments": {"role": "core"}},
})
data = json.loads(parse_sse(body)["result"]["content"][0]["text"])
print(f"cores ({data['matched']}/{data['total']}):", [d["name"] for d in data["devices"]])
```

Expected output (with the seeded `inventory.example.json` template):

```text
tools: ['config_command', 'list_devices', 'reload_inventory', 'show_command']
cores (2/9): ['Site-A-Core1', 'Site-A-Core2']
```

---

## Day-2 ops

### Edit the inventory without restarting

The file is mounted read-only into the container, but you can edit it on the **host** at any time. After saving:

* From Cursor: ask "Reload the IOS-XE inventory."
* From HTTP: call the `reload_inventory` tool. Expected response:

  ```json
  { "inventory_loaded": true, "inventory_path": "/app/inventory.json", "total": 9, "error": null }
  ```

No `docker compose restart` needed.

### Disable a device temporarily

Set `"enabled": false` on the entry and call `reload_inventory()`. Subsequent connect attempts to that name will return:

```text
Error: device 'Lab-Router-01' is disabled in the inventory
```

The IP/hostname path is still available — passing a raw IP that happens to match the disabled entry's host **is** allowed (the disable only blocks the friendly-name path). To hard-block, remove the entry.

### Rotate the shared SSH credential

1. Update `IOS_XE_USERNAME` / `IOS_XE_PASSWORD` in `MCP/network-mcp-docker-suite/.env`.
2. `docker compose restart ios-xe-mcp-server` (no rebuild needed for env changes — `env_file` is re-read on container start).
3. Confirm the startup banner shows the new username.

---

## Troubleshooting

### `Inventory file not found at /app/inventory.json (optional — using empty inventory)`

The volume mount didn't land. Confirm:

```bash
docker compose config | grep -A2 'ios-xe-mcp-server' | grep inventory
```

Should show `target: /app/inventory.json`. If not, re-pull the repo (the mount is in `docker-compose.yml`) and `docker compose up -d --build ios-xe-mcp-server`.

Confirm the host file exists and is readable:

```bash
ls -l MCP/network-mcp-docker-suite/ios-xe-mcp-server/inventory.json
```

### `inventory JSON parse error: ...`

You broke JSON syntax. Validate with:

```bash
python3 -m json.tool MCP/network-mcp-docker-suite/ios-xe-mcp-server/inventory.json > /dev/null
```

Fix the line/column the parser reports, then call `reload_inventory()`.

### `inventory schema invalid: top-level must be {'devices': [...]}`

The top-level JSON object must contain a `devices` key whose value is a list. The `_about` and `version` siblings are optional but recommended.

### `Inventory: dropping device with invalid name=...` / `... invalid host=...`

The loader silently drops malformed entries (logged at WARNING). Check `docker logs ios-xe-mcp-server 2>&1 | grep "Inventory:"` to see which records were rejected. Common causes:

* `name` contains spaces or special chars (only `[A-Za-z0-9._-]` allowed, max 64).
* `host` contains a slash, port suffix, URL scheme, or shell metachars (must be an IP literal or RFC 1123 hostname).

### `Authentication to device failed (cisco_ios <host>:22)`

Inventory works; credentials don't. Either:

* The `.env` still has the placeholder password (`your_default_password`).
* Your AAA-backed account doesn't have rights on the target.
* You're using the wrong env-var names (`IOSXE_*` instead of `IOS_XE_*`).

Check what the container actually loaded:

```bash
docker exec ios-xe-mcp-server env | grep IOS_XE
```

### `Error: device '...' is disabled in the inventory`

Expected. Edit `inventory.json`, flip `enabled: true`, call `reload_inventory()`.

### `Error: invalid host '...': not in inventory and not a valid IP/hostname`

The `host` argument you passed isn't an inventory `name` and doesn't pass the IP/RFC-1123 hostname check. Confirm spelling against `list_devices()`.

### Cursor still shows only 2 tools after rebuild

Reload the Cursor window (Step 5).

---

## Rollback

If you need to back out the inventory feature without losing the rest of the IOS-XE MCP server:

1. Revert `ios-xe-mcp-server/ios_xe_mcp_server.py` to the pre-v0.2 version (single commit revert).
2. Revert the `volumes:` and `IOS_XE_INVENTORY_FILE` lines in the IOS-XE service block of `docker-compose.yml`.
3. Optionally revert the `IOS_XE_INVENTORY_FILE` line and the IOS-XE inventory comment block in `.env`.
4. `docker compose up -d --build ios-xe-mcp-server`
5. Reload Cursor.

The `inventory.json` file on the host is harmless to leave behind — without the volume mount and the `IOS_XE_INVENTORY_FILE` env, the server simply won't read it.

---

## Security notes (per always-applied codeguard rules)

* **`codeguard-1-hardcoded-credentials`** — the inventory file holds metadata only. The loader makes no provision for credential fields. Credentials live in `.env` (already gitignored) or, better, in a secrets manager mounted as env vars.
* **`codeguard-0-input-validation-injection`** — every `host` value (whether raw or resolved from a friendly name) is re-validated as either a valid IP literal (`ipaddress.ip_address`) or an RFC 1123 hostname before being passed to Netmiko. Filter strings (`name`, `role`, `site`, `tag`) are constrained to `[A-Za-z0-9._\- ]{0,64}`. Shell metacharacters (`;`, `|`, `&`, backticks, etc.) are rejected with a clean error envelope. Verified against `role='core; rm -rf /'`.
* **`codeguard-0-logging`** — inventory contents are not logged at INFO; only file path and counts. Set `LOG_LEVEL=DEBUG` if you need detail during troubleshooting.
* **`codeguard-0-data-storage`** — file mounted **read-only** inside the container (`:ro`); host file is `chmod 600`; loader caps file size at 1 MiB to bound DoS surface. Live `inventory.json` is gitignored — only `inventory.example.json` is committed.

---

## Cross-references

* `ios-xe-mcp-server/README.md` — full server reference; includes the schema reference, deployment summary, and the A/B/C design trade-off table.
* The suite-level `README.md` and `.env.example` cover Docker / `.env` first-time install.

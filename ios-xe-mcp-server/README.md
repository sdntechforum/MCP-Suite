# IOS XE MCP Server

A Model Context Protocol (MCP) server for managing Cisco IOS XE devices via SSH using Netmiko with enterprise-grade security.

## Overview

This MCP server provides **secure** SSH-based management capabilities for Cisco IOS XE devices, enabling:

- **Device Configuration**: Send configuration commands to IOS XE devices
- **Monitoring Commands**: Execute show commands for device monitoring  
- **Secure Authentication**: Environment-only credentials (no password parameters)
- **Password Protection**: Comprehensive password masking and sanitization
- **Enhanced Security**: SSH-based communication with timeout controls and error protection
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

- **`show_command`**: Execute any show command on an IOS XE device (credentials from environment only)
- **`config_command`**: Send configuration commands to an IOS XE device (credentials from environment only)
- **`list_devices`**: List known IOS XE devices from the local inventory file (filterable by name / role / site / tag)
- **`reload_inventory`**: Re-read the inventory file at runtime without restarting the container

> The `host` argument of `show_command` / `config_command` accepts either an IP/hostname **or** the case-insensitive friendly `name` of a device defined in the inventory file (e.g. `"Site-A-Core1"`).

### Security Features

- 🔐 **Environment-only credentials** - No password parameters accepted  
- 🔐 **Password masking** - Passwords masked in all logs (`your_default_password` → `y*********`)
- 🔐 **Error sanitization** - Passwords removed from error messages (`***REDACTED***`)
- 🔐 **Startup validation** - Server fails securely if credentials missing
- ✅ **SSH timeout controls** - Configurable connection timeouts
- ✅ **Enhanced error handling** - Safe error reporting without credential exposure
- ✅ **Non-root container execution** - Minimal privilege operation
- ✅ **Automatic configuration saving** - Changes persisted automatically

## Usage Examples

**SECURITY:** All credentials are loaded from environment variables only. No password parameters are accepted for maximum security.

### Show Commands

```python
# By raw IP / hostname
result = show_command("show version", "192.0.2.10")
result = show_command("show ip interface brief", "switch.company.com")

# By friendly name from inventory.json (case-insensitive)
result = show_command("show ip bgp summary", "Site-A-Core1")          # → 192.0.2.10
result = show_command("show standby brief",   "Site-A-Core2")          # → 192.0.2.11
result = show_command("show ip vrf detail",   "Site-A-Fusion")         # → 192.0.2.5
result = show_command("show running-config interface gi0/1", "Site-A-Edge1")
```

### Configuration Commands

```python
# Secure: Only commands and host required (credentials from .env)
result = config_command([
    "interface GigabitEthernet0/1",
    "description Connected to Server", 
    "no shutdown"
], "switch.company.com")

# Network configuration
result = config_command([
    "ip route 10.1.0.0 255.255.0.0 10.1.1.1"
], "switch.company.com")

# Multiple interface configuration
result = config_command([
    "interface range GigabitEthernet0/1-4",
    "switchport mode access",
    "switchport access vlan 100"
], "switch.company.com")
```

### Security Logs Example

```log
INFO: Loaded credentials for user: admin
INFO: Secure mode: Credentials loaded from environment only
INFO: Connecting to switch.company.com as 'admin' (pwd: y*********) to execute: show ip bgp summary
INFO: Successfully executed command on switch.company.com
```

## Configuration

### Environment Variables

**REQUIRED:** The server requires credentials in environment variables for security. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

#### Core Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCP_HOST` | Server bind address | `0.0.0.0` | No |
| `MCP_PORT` | Server port | `8003` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

#### Required Security Credentials

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| **`IOS_XE_USERNAME`** | **SSH username** | **`admin`** | **REQUIRED - Server fails without this** |
| **`IOS_XE_PASSWORD`** | **SSH password** | **`your_default_password`** | **REQUIRED - Server fails without this** |

#### Optional Advanced Settings

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `SSH_TIMEOUT` | SSH connection timeout | `60` | Seconds |
| `DEFAULT_DEVICE_TYPE` | Netmiko device type | `cisco_ios` | Usually `cisco_ios` for IOS XE |

### Example .env File

```bash
# IOS XE MCP Server Configuration
# =====================================================

# REQUIRED: Device credentials (server fails without these)
IOS_XE_USERNAME=admin
IOS_XE_PASSWORD=your_default_password

# Optional: Server configuration  
MCP_HOST=0.0.0.0
MCP_PORT=8003
LOG_LEVEL=INFO
```

See `.env.example` for a comprehensive list of all available configuration options including security settings, performance tuning, and multiple device scenarios.

### Device Requirements

- Cisco IOS XE device with SSH enabled
- Valid SSH credentials (username/password)
- Network connectivity from the MCP server to the device
- SSH port (22) accessible

## Deployment

### Using Docker Compose

The server is included in the main `docker-compose.yml`:

```bash
# Start only IOS XE MCP server
docker-compose up -d ios-xe-mcp-server

# View logs
docker-compose logs -f ios-xe-mcp-server

# Stop server
docker-compose stop ios-xe-mcp-server
```

### Standalone Docker

```bash
# Build image
docker build -t ios-xe-mcp-server .

# Run container
docker run -d \
  --name ios-xe-mcp-server \
  -p 8003:8003 \
  ios-xe-mcp-server
```

### Development Mode

```bash
# Install dependencies
uv sync

# Run server directly
uv run python ios_xe_mcp_server.py
```

## Security Considerations

### Secure Authentication

- 🔐 **Environment-Only Credentials**: Passwords never appear in function parameters or traces
- 🔐 **Startup Validation**: Server fails securely if credentials are missing from environment  
- 🔐 **Password Masking**: All passwords masked in logs (`your_default_password` → `y*********`)
- 🔐 **Error Sanitization**: Passwords automatically removed from error messages (`***REDACTED***`)
- 🔐 **No Credential Storage**: Device credentials loaded from environment only
- 🔐 **SSH Only**: Secure encrypted communication to devices
- 🔐 **Timeout Controls**: SSH connections have configurable timeouts

### Network Security

- Server runs on configurable port (default 8003)
- Supports Docker network isolation  
- SSH connections use standard port 22
- All device communication is encrypted
- No credentials transmitted in API calls

### Container Security

- Runs as non-root user
- Security options enabled (`no-new-privileges`)
- Resource limits configured
- Minimal attack surface
- Environment variables isolated per container

### Security Logs

All operations are logged securely without exposing credentials:

```log
INFO: Loaded credentials for user: admin
INFO: Secure mode: Credentials loaded from environment only
INFO: Starting SECURE IOS XE MCP server on 0.0.0.0:8003
INFO: Security: Environment-only credentials, no password parameters accepted
```

## Troubleshooting

### Common Issues

**🔐 Environment Credential Errors**
```bash
# Server fails to start with missing credentials
ERROR: IOS_XE_USERNAME and IOS_XE_PASSWORD must be set in environment!

# Solution: Check .env file exists and has correct values
cat ios-xe-mcp-server/.env

# Verify environment variables are loaded
docker-compose exec ios-xe-mcp-server env | grep IOS_XE
```

**🔐 MCP Client Parameter Errors**  
```bash
# Error: Validation errors for call[show_command] - username/password unexpected
# This happens when using old function signatures

# Solution: Use new secure syntax (no credentials)
show_command("show version", "switch.company.com")  # ✅ Correct
show_command("show version", "switch.company.com", username="user", password="pass")  # ❌ Wrong
```

**SSH Connection Failures**
```bash
# Check network connectivity
ping <device-ip>

# Verify SSH service
telnet <device-ip> 22

# Check device SSH configuration
show ip ssh

# Verify credentials work manually
ssh admin@switch.company.com
```

**Authentication Errors**
```bash
# Check if credentials in .env match device
# Look for sanitized error messages (passwords are hidden)
Authentication to device failed.
Common causes:
1. Invalid credentials in environment
2. Device SSH configuration  
3. Network connectivity
```

**Timeout Issues**
```bash
# Increase timeout in environment variables
SSH_TIMEOUT=120

# Or check device response time
time ssh admin@switch.company.com "show version"
```

### Debug Logging

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in environment variables.

```bash
# View detailed logs with password masking
docker-compose logs -f ios-xe-mcp-server

# Example secure log output:
# INFO: Connecting to switch.company.com as 'admin' (pwd: y*********) to execute: show version
```

### Security Validation

```bash
# Test that password masking works
docker-compose exec ios-xe-mcp-server uv run python -c "
from ios_xe_mcp_server import mask_password
print('Password masking test:', mask_password('your_default_password'))
"
# Output: Password masking test: y*********
```

## API Reference

### Tool: show_command

Execute a show command on an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**Parameters:**
- `command` (string): Show command to execute (e.g., `"show ip bgp summary"`)
- `host` (string): Device IP address or hostname (e.g., `"switch.company.com"`)

**Returns:** Command output as string

**Example:**
```python
result = show_command("show version", "switch.company.com")
```

### Tool: config_command

Send configuration commands to an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**Parameters:**
- `commands` (list): List of configuration commands to send
- `host` (string): Device IP address or hostname

**Returns:** Configuration results and save status

**Example:**
```python
result = config_command([
    "interface GigabitEthernet0/1", 
    "no shutdown"
], "switch.company.com")
```

### Security Features

Both tools automatically:
- ✅ Load credentials from `IOS_XE_USERNAME` and `IOS_XE_PASSWORD` environment variables
- ✅ Mask passwords in logs (`y*********`)  
- ✅ Sanitize error messages (`***REDACTED***`)
- ✅ Validate environment setup on server startup
- ✅ Save configuration changes automatically

---

## Device Inventory (devices NOT in Catalyst Center)

Catalyst Center already publishes its managed inventory through the Catalyst-Center MCP. Many lab/production devices, however, live **outside** Catalyst Center — for example:

* L3 super-cores (e.g. `Site-A-Core1`, `Site-A-Core2`)
* Fusion / DC handoff routers (e.g. `Site-A-Fusion`)
* Infra / lab routers (e.g. `Lab-Router-01`)
* Legacy centralised WLCs (e.g. `Site-A-WLC-01`)
* SD-WAN edges across sites and branches (e.g. `Site-A-Edge1`, `Branch-1-Edge1`)

To make these discoverable to the MCP client, the IOS-XE MCP server can load a JSON inventory file at startup.

### Schema (`inventory.json`)

```json
{
  "version": 1,
  "devices": [
    {
      "name":    "Site-A-Core1",
      "host":    "192.0.2.10",
      "role":    "core",
      "site":    "Site-A",
      "tags":    ["hsrp-active", "as-64500"],
      "enabled": true,
      "notes":   "L3 super core; HSRP-paired with Site-A-Core2."
    }
  ]
}
```

| Field    | Required | Notes |
|---       |---       |---    |
| `name`   | yes      | Case-insensitive unique. Allowed chars: `[A-Za-z0-9._-]`, max 64. |
| `host`   | yes      | IPv4/IPv6 literal **or** RFC 1123 hostname. Re-validated before connect. |
| `role`   | no       | Free-form, e.g. `core`, `fusion`, `sdwan-edge`, `wlc`, `infra`, `sda-border`, `sda-distribution`. |
| `site`   | no       | Free-form, e.g. `Site-A`, `Site-B`, `Branch-1`. |
| `tags`   | no       | List of short string tags. |
| `enabled`| no       | Default `true`. Set `false` to keep an entry visible but block connections. |
| `notes`  | no       | Free-form annotation (max 256 chars). |

> ⚠️ **Never put credentials in this file.** Credentials come from `IOS_XE_USERNAME` / `IOS_XE_PASSWORD` only. Records with credential-like fields are ignored / rejected by the loader.

### Deployment

1. Start from the committed reference template:
   ```bash
   cd network-mcp-docker-suite/ios-xe-mcp-server
   cp inventory.example.json inventory.json
   chmod 600 inventory.json
   # edit inventory.json on the host to match your environment
   ```
2. The suite `docker-compose.yml` already mounts the file **read-only** into the container:
   ```yaml
   volumes:
     - ./ios-xe-mcp-server/inventory.json:/app/inventory.json:ro
   environment:
     - IOS_XE_INVENTORY_FILE=${IOS_XE_INVENTORY_FILE:-/app/inventory.json}
   ```
3. Rebuild + restart the IOS-XE container:
   ```bash
   docker compose up -d --build ios-xe-mcp-server
   ```
4. From the MCP client, call `list_devices` to confirm the entries are loaded.
5. After editing `inventory.json` on the host, call `reload_inventory` to refresh — no container restart required.

### Tools

#### `list_devices(name="", role="", site="", tag="")`

Filters are optional, case-insensitive (`name` is a substring match; `role` / `site` / `tag` are equality matches).

```python
list_devices(role="core")            # all cores
list_devices(site="Site-A")          # all devices in Site-A
list_devices(tag="dc-anchor")        # all DC-anchor edges
list_devices(name="edge")            # any device whose name contains "edge"
```

Returns:

```json
{
  "inventory_loaded": true,
  "inventory_path":   "/app/inventory.json",
  "total":            20,
  "matched":          4,
  "filters":          {"name": "", "role": "core", "site": "", "tag": ""},
  "devices":          [ ... ],
  "error":            null
}
```

#### `reload_inventory()`

Re-reads the mounted `inventory.json` from disk. Returns `{ inventory_loaded, inventory_path, total, error }`.

#### Friendly-name resolution

`show_command` and `config_command` accept either an IP/hostname **or** a friendly inventory `name`:

```python
show_command("show ip bgp summary", "Site-A-Core1")           # resolves to 192.0.2.10
show_command("show ip ospf neighbor", "192.0.2.5")            # raw IP also works
config_command(["interface Lo99", "description test"], "Site-A-Core1")
```

If a name is not found in the inventory, the value is treated as an IP/hostname and validated against an RFC 1123 / `ipaddress.ip_address()` allow-list before being passed to Netmiko (defense against shell-metachar injection). If a matched device has `"enabled": false`, the call is rejected with a clear error.

### Security model

* The inventory file is **mounted read-only** inside the container (`:ro`).
* Loader caps file size at **1 MiB** to bound DoS surface.
* Each `host` value is re-validated as either a valid IP literal or an RFC 1123 hostname before being passed to Netmiko.
* Inventory contents are **not** logged at INFO level — only counts and the file path. (Set `LOG_LEVEL=DEBUG` if you need detail during troubleshooting.)
* The host-side `inventory.json` is added to `.gitignore`; only `inventory.example.json` is committed.

### Why this design (vs. multiple MCP containers)

We considered three options for managing many IOS XE devices:

| Option | Description | Trade-off |
|---|---|---|
| A | One AAA-backed shared service account; one MCP container; inventory file enumerates devices | ✅ One credential to rotate · ✅ Single endpoint for the MCP client · ❌ Requires AAA / consistent local user |
| B | Multiple MCP containers, one per device or device group, each with its own `.env` and port | ❌ N×port sprawl · ❌ N credential blobs to rotate · ❌ Cursor descriptor cache thrash |
| C | Per-device credential map embedded in the inventory file | ❌ Credentials in a config file (violates `codeguard-1-hardcoded-credentials`) |

**This patch implements Option A.** Cred sprawl stays out of the codebase and out of `.env`; the only thing the inventory file knows about is *what* the devices are, never *how* to log into them.

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.

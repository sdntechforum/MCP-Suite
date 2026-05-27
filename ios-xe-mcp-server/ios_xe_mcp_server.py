"""
Cisco IOS XE MCP Server

A Model Context Protocol (MCP) server that provides direct SSH-based management capabilities for Cisco IOS XE devices.
This server allows AI assistants and other MCP clients to execute show commands and configuration changes
on IOS XE devices through secure SSH connections with enterprise-grade security.

Features:
- Direct SSH-based device management
- Show command execution for monitoring and troubleshooting
- Configuration change deployment with automatic save
- Secure credential management (environment variables only)
- Password sanitization in logs and error messages
- Connection error handling and diagnostics
- Read and write operations with proper authentication
- HTTP transport for modern MCP client compatibility

Environment Variables:
- IOS_XE_USERNAME: Required. Default IOS XE username for device access
- IOS_XE_PASSWORD: Required. Default IOS XE password for device access
- IOS_XE_INVENTORY_FILE: Optional. Path to a JSON inventory file describing
    known IOS XE devices that are NOT registered in Catalyst Center
    (cores, fusion handoffs, infra routers, legacy WLCs, SD-WAN edges, ...).
    Defaults to /app/inventory.json (when running in the suite container).
    File is loaded read-only at startup; reload at runtime with the
    `reload_inventory` tool. The file MUST NOT contain credentials.
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost
- MCP_PORT: Optional. Port for MCP server. Defaults to 8003

Tools exposed:
- show_command(command, host)            : run a `show` command via SSH
- config_command(commands, host)         : push a config block via SSH
- list_devices(filter, role, site, tag)  : list known devices from inventory
- reload_inventory()                     : re-read the inventory file at runtime

Friendly-name resolution: `host` may be either an IP/hostname OR the
case-insensitive `name` of a device in the inventory file (e.g. "Site-A-Core1").
The server resolves the friendly name to its `host` value before connecting.

Author: Patrick Mosimann
Based on: SSH device management concepts by tspuhler
"""

from fastmcp import FastMCP
from netmiko import ConnectHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load default credentials from environment
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

DEFAULT_USERNAME = os.getenv("IOS_XE_USERNAME")
DEFAULT_PASSWORD = os.getenv("IOS_XE_PASSWORD")

# Validate environment credentials (required for secure operation)
if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
    logger.error("SECURITY ERROR: IOS_XE_USERNAME and IOS_XE_PASSWORD must be set in environment!")
    logger.error("This secure version requires credentials in .env file only.")
    raise ValueError("Missing required environment credentials")

logger.info(f"Loaded credentials for user: {DEFAULT_USERNAME}")
logger.info("Secure mode: Credentials loaded from environment only")


# =============================================================================
# Device inventory (optional) — for IOS XE devices NOT in Catalyst Center
# =============================================================================
# Schema (JSON):
#   {
#     "version": 1,
#     "devices": [
#       {
#         "name":    "Site-A-Core1",     # required, case-insensitive unique
#         "host":    "192.0.2.10",       # required, IPv4/IPv6 or hostname
#         "role":    "core",             # optional free-form
#         "site":    "Site-A",           # optional free-form
#         "tags":    ["aaa-managed"],    # optional list of strings
#         "enabled": true,                # optional, default true
#         "notes":   "L3 core, HSRP"     # optional free-form
#       }
#     ]
#   }
#
# Security:
#   * The inventory file MUST NOT contain credentials (no password / key fields).
#   * File is opened read-only with a 1 MiB size cap to bound DoS surface.
#   * Resolved hostnames/IPs are re-validated against strict allow-lists
#     before being passed to Netmiko (defense against shell metachar injection).
import json
import re
import ipaddress
import threading
from typing import Optional

INVENTORY_FILE_PATH = os.getenv("IOS_XE_INVENTORY_FILE", "/app/inventory.json")
INVENTORY_MAX_BYTES = 1 * 1024 * 1024  # 1 MiB hard cap

# Strict hostname regex (RFC 1123 labels, optional dotted FQDN).
_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,62}[A-Za-z0-9])?)*$"
)
# Allowed chars in a friendly device "name" — alphanumeric + dash + underscore + dot.
_NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
# Allowed chars in optional filter strings supplied by the LLM/client.
_FILTER_RE = re.compile(r"^[A-Za-z0-9._\- ]{0,64}$")

_inventory_lock = threading.RLock()
_inventory: dict = {"path": INVENTORY_FILE_PATH, "loaded": False, "by_name": {}, "devices": []}


def _is_valid_host_value(value: str) -> bool:
    """Return True if `value` is a syntactically valid IP literal or hostname."""
    if not isinstance(value, str) or not value:
        return False
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(value))


def _normalize_device(raw: dict) -> Optional[dict]:
    """Sanitize one device record from the inventory file. Returns None if invalid."""
    if not isinstance(raw, dict):
        return None
    name = raw.get("name")
    host = raw.get("host")
    if not isinstance(name, str) or not _NAME_RE.match(name):
        logger.warning("Inventory: dropping device with invalid name=%r", name)
        return None
    if not isinstance(host, str) or not _is_valid_host_value(host):
        logger.warning("Inventory: dropping device %s with invalid host=%r", name, host)
        return None
    role = raw.get("role") if isinstance(raw.get("role"), str) else ""
    site = raw.get("site") if isinstance(raw.get("site"), str) else ""
    notes = raw.get("notes") if isinstance(raw.get("notes"), str) else ""
    enabled = bool(raw.get("enabled", True))
    tags_raw = raw.get("tags", []) or []
    tags = [t for t in tags_raw if isinstance(t, str) and len(t) <= 64]
    return {
        "name": name,
        "host": host,
        "role": role[:64],
        "site": site[:64],
        "tags": tags,
        "enabled": enabled,
        "notes": notes[:256],
    }


def _load_inventory(path: str) -> dict:
    """Load and sanitize the inventory file. Returns a fresh dict; never raises."""
    state = {"path": path, "loaded": False, "by_name": {}, "devices": [], "error": None}
    try:
        if not os.path.exists(path):
            state["error"] = f"inventory file not found at {path} (optional — using empty inventory)"
            logger.info(state["error"])
            return state
        size = os.path.getsize(path)
        if size > INVENTORY_MAX_BYTES:
            state["error"] = f"inventory file too large ({size} bytes > {INVENTORY_MAX_BYTES})"
            logger.error(state["error"])
            return state
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, dict) or not isinstance(raw.get("devices"), list):
            state["error"] = "inventory schema invalid: top-level must be {'devices': [...]}"
            logger.error(state["error"])
            return state
        seen = set()
        normalized = []
        for entry in raw["devices"]:
            dev = _normalize_device(entry)
            if dev is None:
                continue
            key = dev["name"].lower()
            if key in seen:
                logger.warning("Inventory: duplicate device name %s — keeping first occurrence", dev["name"])
                continue
            seen.add(key)
            normalized.append(dev)
            state["by_name"][key] = dev
        state["devices"] = normalized
        state["loaded"] = True
        logger.info("Inventory loaded: %d device(s) from %s", len(normalized), path)
    except json.JSONDecodeError as e:
        state["error"] = f"inventory JSON parse error: {e}"
        logger.error(state["error"])
    except OSError as e:
        state["error"] = f"inventory file read error: {e}"
        logger.error(state["error"])
    except Exception as e:  # noqa: BLE001 — inventory load must never crash startup
        state["error"] = f"unexpected inventory load error: {e}"
        logger.error(state["error"])
    return state


def _resolve_host(host_or_name: str) -> str:
    """Resolve a friendly device name to its IP/hostname; otherwise validate input as-is.

    Raises ValueError if the result is not a syntactically valid host value.
    """
    if not isinstance(host_or_name, str):
        raise ValueError("host must be a string")
    candidate = host_or_name.strip()
    if not candidate:
        raise ValueError("host parameter is required")
    with _inventory_lock:
        dev = _inventory["by_name"].get(candidate.lower())
    if dev:
        if not dev.get("enabled", True):
            raise ValueError(f"device '{dev['name']}' is disabled in the inventory")
        return dev["host"]
    if not _is_valid_host_value(candidate):
        raise ValueError(
            f"invalid host {candidate!r}: not in inventory and not a valid IP/hostname"
        )
    return candidate


# Initial load (synchronous; safe even if file missing).
with _inventory_lock:
    _inventory = _load_inventory(INVENTORY_FILE_PATH)


# Password security utilities
def sanitize_error_message(error_msg: str) -> str:
    """Remove passwords from error messages for security"""
    if DEFAULT_PASSWORD and DEFAULT_PASSWORD in error_msg:
        return error_msg.replace(DEFAULT_PASSWORD, "***REDACTED***")
    return error_msg

def mask_password(password: str) -> str:
    """Mask password for logging (show first char + asterisks)"""
    if not password:
        return "None"
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 1)

def create_safe_device_dict(host: str, username: str, password: str) -> dict:
    """Create device connection dict with password handling"""
    return {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 60,
        "session_timeout": 60,
    }

def log_connection_attempt(host: str, command: str = None):
    """Safely log connection attempts without exposing passwords"""
    masked_pwd = mask_password(DEFAULT_PASSWORD)
    if command:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' (pwd: {masked_pwd}) to execute: {command}")
    else:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' (pwd: {masked_pwd}) for configuration")

# Define MCP Server
mcp = FastMCP("ios-xe-mcp-server")

@mcp.tool()
def show_command(command: str, host: str) -> str:
    """
    Executes a 'show' command via SSH (Netmiko) on an IOS XE device.
    
    SECURITY: Credentials are loaded from environment variables only.
    No password parameters accepted to prevent exposure in logs/traces.
    
    Args:
        command: Show command to execute (e.g., 'show ip interface brief')
        host: IP address, hostname, OR friendly inventory `name`
              (e.g., 'Site-A-Core1') of the IOS XE device.

    Returns:
        Command output as string or error message
    """
    if not host:
        return "Error: host parameter is required"
    try:
        resolved_host = _resolve_host(host)
    except ValueError as e:
        return f"Error: {e}"

    device = create_safe_device_dict(resolved_host, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    try:
        log_connection_attempt(resolved_host, command)

        with ConnectHandler(**device) as conn:
            output = conn.send_command(command)
        logger.info(f"Successfully executed command on {resolved_host}")
        return output
    except Exception as e:
        raw_error = f"Error executing command on {resolved_host}: {e}"
        safe_error = sanitize_error_message(raw_error)
        logger.error(safe_error)

        if "Authentication" in str(e) or "auth" in str(e).lower():
            return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n\nDevice: cisco_ios {resolved_host}:22\n\n{safe_error}"
        else:
            return safe_error

@mcp.tool()
def config_command(commands: list[str], host: str) -> str:
    """
    Sends configuration commands via SSH (Netmiko) to an IOS XE device.
    
    SECURITY: Credentials are loaded from environment variables only.
    No password parameters accepted to prevent exposure in logs/traces.
    
    Args:
        commands: List of configuration commands (e.g., ['interface gi0/1', 'no shutdown'])
        host: IP address, hostname, OR friendly inventory `name`
              (e.g., 'Site-A-Core1') of the IOS XE device.

    Returns:
        Configuration result as string or error message
    """
    if not host:
        return "Error: host parameter is required"
    if not commands or not isinstance(commands, list):
        return "Error: commands must be a non-empty list"
    try:
        resolved_host = _resolve_host(host)
    except ValueError as e:
        return f"Error: {e}"

    device = create_safe_device_dict(resolved_host, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    try:
        log_connection_attempt(resolved_host)

        with ConnectHandler(**device) as conn:
            output = conn.send_config_set(commands)
            save_output = conn.send_command("write memory")

        result = f"Configuration successfully applied to {resolved_host}:\n{output}\n\nSave result:\n{save_output}"
        logger.info(f"Successfully applied configuration to {resolved_host}")
        return result
    except Exception as e:
        raw_error = f"Error during configuration on {resolved_host}: {e}"
        safe_error = sanitize_error_message(raw_error)
        logger.error(safe_error)

        if "Authentication" in str(e) or "auth" in str(e).lower():
            return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n\nDevice: cisco_ios {resolved_host}:22\n\n{safe_error}"
        else:
            return safe_error


@mcp.tool()
def list_devices(name: str = "", role: str = "", site: str = "", tag: str = "") -> dict:
    """List known IOS XE devices from the local inventory file.

    All filters are optional substring/equality matches and are case-insensitive.
    Use this when you need to discover devices that are NOT in Catalyst Center
    (e.g., cores, fusion handoffs, infra routers, legacy WLCs, SD-WAN edges).

    Args:
        name: Optional case-insensitive substring match against device `name`.
        role: Optional case-insensitive exact match against device `role`
              (e.g. 'core', 'fusion', 'edge', 'wlc', 'infra').
        site: Optional case-insensitive exact match against device `site`
              (e.g. 'Site-A', 'Site-B', 'Branch-1').
        tag:  Optional case-insensitive exact match against any entry in `tags`.

    Returns:
        {
          "inventory_loaded": bool,
          "inventory_path":   "/app/inventory.json",
          "total":            int,
          "matched":          int,
          "filters":          {...echoed...},
          "devices":          [ {name, host, role, site, tags, enabled, notes}, ... ],
          "error":            "string or null"
        }
    """
    for label, val in (("name", name), ("role", role), ("site", site), ("tag", tag)):
        if val and not _FILTER_RE.match(val):
            return {
                "inventory_loaded": False,
                "inventory_path": INVENTORY_FILE_PATH,
                "total": 0,
                "matched": 0,
                "filters": {"name": name, "role": role, "site": site, "tag": tag},
                "devices": [],
                "error": f"invalid {label} filter (alphanumeric, dash, dot, space, underscore; max 64 chars)",
            }

    name_q = name.lower().strip()
    role_q = role.lower().strip()
    site_q = site.lower().strip()
    tag_q = tag.lower().strip()

    with _inventory_lock:
        all_devices = list(_inventory["devices"])
        loaded = _inventory.get("loaded", False)
        path = _inventory.get("path", INVENTORY_FILE_PATH)
        load_err = _inventory.get("error")

    matched = []
    for d in all_devices:
        if name_q and name_q not in d["name"].lower():
            continue
        if role_q and d["role"].lower() != role_q:
            continue
        if site_q and d["site"].lower() != site_q:
            continue
        if tag_q and tag_q not in {t.lower() for t in d["tags"]}:
            continue
        matched.append(d)

    return {
        "inventory_loaded": loaded,
        "inventory_path": path,
        "total": len(all_devices),
        "matched": len(matched),
        "filters": {"name": name, "role": role, "site": site, "tag": tag},
        "devices": matched,
        "error": load_err,
    }


@mcp.tool()
def reload_inventory() -> dict:
    """Re-read the inventory file from disk without restarting the container.

    Useful after editing the mounted `inventory.json` (the file is mounted
    read-only into the container; edits happen on the host filesystem).

    Returns: { inventory_loaded, inventory_path, total, error }
    """
    global _inventory
    new_state = _load_inventory(INVENTORY_FILE_PATH)
    with _inventory_lock:
        _inventory = new_state
    return {
        "inventory_loaded": new_state.get("loaded", False),
        "inventory_path": new_state.get("path", INVENTORY_FILE_PATH),
        "total": len(new_state.get("devices", [])),
        "error": new_state.get("error"),
    }


# Start Server (HTTP Mode for MCP client integration)
if __name__ == "__main__":
    import os
    
    # Get configuration from environment
    mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
    mcp_port = int(os.getenv("MCP_PORT", "8003"))
    
    logger.info(f"Starting SECURE IOS XE MCP server on {mcp_host}:{mcp_port}")
    logger.info("Security: Environment-only credentials, no password parameters accepted")
    mcp.run(transport="http", host=mcp_host, port=mcp_port)

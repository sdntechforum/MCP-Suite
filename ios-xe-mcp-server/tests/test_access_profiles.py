import importlib
import json
import os
import sys

import dotenv
import pytest

SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_PW = "default-pw-1"
DC_PW = "dc-pw-2"
DC_SECRET = "dc-enable-3"
LEGACY_PW = "legacy-pw-4"
ALL_SECRETS = (DEFAULT_PW, DC_PW, DC_SECRET, LEGACY_PW)

INVENTORY = {
    "version": 1,
    "access_profiles": {
        "dc-local": {"transport": "ssh", "port": 2222, "credential": "DC"},
        "legacy-telnet": {"transport": "telnet", "credential": "LEGACY"},
        "missing-creds": {"transport": "ssh", "credential": "NOPE"},
        "has-secret": {"transport": "ssh", "credential": "DC", "password": "x"},
    },
    "devices": [
        {"name": "Core1", "host": "192.0.2.10", "role": "core"},
        {"name": "DC1", "host": "192.0.2.20", "role": "fusion", "access_profile": "dc-local"},
        {"name": "Old1", "host": "192.0.2.30", "role": "infra", "access_profile": "Legacy-Telnet"},
        {"name": "NoCreds1", "host": "192.0.2.40", "access_profile": "missing-creds"},
        {"name": "Ghost1", "host": "192.0.2.50", "access_profile": "does-not-exist"},
        {"name": "Leaky1", "host": "192.0.2.60", "access_profile": "has-secret"},
    ],
}

BASE_ENV = {
    "IOS_XE_USERNAME": "default-user",
    "IOS_XE_PASSWORD": DEFAULT_PW,
    "IOS_XE_CRED_DC_USERNAME": "dc-user",
    "IOS_XE_CRED_DC_PASSWORD": DC_PW,
    "IOS_XE_CRED_DC_ENABLE_SECRET": DC_SECRET,
    "IOS_XE_CRED_LEGACY_USERNAME": "legacy-user",
    "IOS_XE_CRED_LEGACY_PASSWORD": LEGACY_PW,
}


class FakeConnection:
    calls: list = []
    fail_with: Exception | None = None

    def __init__(self, **kwargs):
        if FakeConnection.fail_with is not None:
            raise FakeConnection.fail_with
        self.kwargs = kwargs
        self.enabled = False
        FakeConnection.calls.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def enable(self):
        self.enabled = True

    def send_command(self, command):
        return f"output of {command}"

    def send_config_set(self, commands):
        return "config applied"


def _tool(module, name):
    obj = getattr(module, name)
    return getattr(obj, "fn", obj)


@pytest.fixture
def load_server(tmp_path, monkeypatch):
    def _load(extra_env=None, inventory=INVENTORY):
        for key in list(os.environ):
            if key.startswith("IOS_XE_"):
                monkeypatch.delenv(key)
        for key, value in {**BASE_ENV, **(extra_env or {})}.items():
            monkeypatch.setenv(key, value)
        inv_path = tmp_path / "inventory.json"
        inv_path.write_text(json.dumps(inventory))
        monkeypatch.setenv("IOS_XE_INVENTORY_FILE", str(inv_path))
        monkeypatch.setattr(dotenv, "load_dotenv", lambda *a, **k: False)
        monkeypatch.syspath_prepend(SERVER_DIR)
        sys.modules.pop("ios_xe_mcp_server", None)
        module = importlib.import_module("ios_xe_mcp_server")
        FakeConnection.calls = []
        FakeConnection.fail_with = None
        monkeypatch.setattr(module, "ConnectHandler", FakeConnection)
        return module

    yield _load
    sys.modules.pop("ios_xe_mcp_server", None)


def test_device_without_profile_uses_default_ssh(load_server):
    srv = load_server()
    out = _tool(srv, "show_command")("show version", "Core1")
    assert out == "output of show version"
    kw = FakeConnection.calls[0].kwargs
    assert (kw["device_type"], kw["port"], kw["username"], kw["password"]) == (
        "cisco_ios", 22, "default-user", DEFAULT_PW,
    )
    assert "secret" not in kw


def test_host_not_in_inventory_uses_default_profile(load_server):
    srv = load_server()
    _tool(srv, "show_command")("show clock", "198.51.100.7")
    kw = FakeConnection.calls[0].kwargs
    assert (kw["host"], kw["device_type"], kw["username"]) == ("198.51.100.7", "cisco_ios", "default-user")


def test_profile_selects_credential_set_port_and_enable(load_server):
    srv = load_server()
    _tool(srv, "show_command")("show version", "dc1")
    conn = FakeConnection.calls[0]
    assert (conn.kwargs["port"], conn.kwargs["username"], conn.kwargs["password"]) == (2222, "dc-user", DC_PW)
    assert conn.kwargs["secret"] == DC_SECRET
    assert conn.enabled


def test_telnet_refused_unless_allowed(load_server):
    srv = load_server()
    out = _tool(srv, "show_command")("show version", "Old1")
    assert "IOS_XE_ALLOW_TELNET" in out
    assert FakeConnection.calls == []


def test_telnet_allowed_for_show_only(load_server):
    srv = load_server({"IOS_XE_ALLOW_TELNET": "true"})
    show = _tool(srv, "show_command")
    assert show("show version", "Old1") == "output of show version"
    kw = FakeConnection.calls[0].kwargs
    assert (kw["device_type"], kw["port"], kw["username"]) == ("cisco_ios_telnet", 23, "legacy-user")

    for cmd in ("reload", "clear counters", "show run | redirect flash:x.txt", "show run | tee flash:y"):
        assert "only allows 'show' commands" in show(cmd, "Old1"), cmd
    assert "show-only" in _tool(srv, "config_command")(["hostname x"], "Old1")
    assert len(FakeConnection.calls) == 1


def test_missing_credential_set_is_reported_without_connecting(load_server):
    srv = load_server()
    out = _tool(srv, "show_command")("show version", "NoCreds1")
    assert "IOS_XE_CRED_NOPE_USERNAME" in out
    assert FakeConnection.calls == []


def test_unknown_profile_fails_closed(load_server):
    srv = load_server()
    out = _tool(srv, "show_command")("show version", "Ghost1")
    assert "unknown access_profile 'does-not-exist'" in out
    assert FakeConnection.calls == []


def test_profile_with_secret_keys_is_rejected(load_server):
    srv = load_server()
    out = _tool(srv, "show_command")("show version", "Leaky1")
    assert "unknown access_profile 'has-secret'" in out
    assert FakeConnection.calls == []


def test_errors_redact_the_profile_password(load_server):
    srv = load_server()
    FakeConnection.fail_with = RuntimeError(f"Authentication failed for pw={DC_PW} secret={DC_SECRET}")
    out = _tool(srv, "show_command")("show version", "DC1")
    assert DC_PW not in out and DC_SECRET not in out
    assert "cisco_ios 192.0.2.20:2222" in out


def test_config_command_uses_profile(load_server):
    srv = load_server()
    out = _tool(srv, "config_command")(["ntp server 192.0.2.1"], "DC1")
    assert "config applied" in out
    assert FakeConnection.calls[0].kwargs["username"] == "dc-user"


def test_list_devices_reports_access_without_secrets(load_server):
    srv = load_server()
    res = _tool(srv, "list_devices")()
    by_name = {d["name"]: d for d in res["devices"]}
    assert by_name["Core1"]["access_profile"] == "default"
    assert (by_name["DC1"]["transport"], by_name["DC1"]["port"], by_name["DC1"]["access_ready"]) == (
        "ssh", 2222, True,
    )
    assert by_name["Old1"]["access_ready"] is False
    assert "IOS_XE_ALLOW_TELNET" in by_name["Old1"]["access_issue"]
    assert by_name["Ghost1"]["access_ready"] is False
    profiles = {p["name"]: p for p in res["access_profiles"]}
    assert set(profiles) == {"default", "dc-local", "legacy-telnet", "missing-creds"}
    assert profiles["dc-local"]["credential"] == "DC"

    dumped = json.dumps(res)
    for value in (*ALL_SECRETS, "default-user", "dc-user", "legacy-user"):
        assert value not in dumped

    only = _tool(srv, "list_devices")(access_profile="dc-local")
    assert [d["name"] for d in only["devices"]] == ["DC1"]


def test_reload_inventory_reports_profile_issues(load_server):
    srv = load_server()
    res = _tool(srv, "reload_inventory")()
    assert set(res["profile_issues"]) == {"legacy-telnet", "missing-creds"}
    assert res["access_profiles"] == ["dc-local", "default", "legacy-telnet", "missing-creds"]


def test_inventory_without_profiles_keeps_old_behaviour(load_server):
    srv = load_server(inventory={"version": 1, "devices": [{"name": "A", "host": "192.0.2.1"}]})
    _tool(srv, "show_command")("show version", "A")
    kw = FakeConnection.calls[0].kwargs
    assert (kw["device_type"], kw["port"], kw["username"]) == ("cisco_ios", 22, "default-user")

# Splunk MCP Integration: Troubleshooting & How We Solved It

This document describes the issues we hit integrating the Network MCP Docker Suite with a Splunk instance that had the **Splunk MCP app** installed, and how we fixed them. Use it when things don’t work or when setting up a new Splunk+MCP environment.

---

## Goal

- List Splunk indexes (and use other MCP tools) from Cursor via the Splunk MCP server container.
- The proxy in this repo forwards MCP requests to Splunk’s MCP backend at `https://<SPLUNK_HOST>:<SPLUNK_PORT>/services/mcp` with Bearer token auth.

---

## Issue 1: Wrong URL → 404 (trailing slash + wrong port)

**Symptom:** `404 Not Found` for `https://10.100.0.41/en-US/:443/services/mcp` (or similar).

**Root cause:**

1. **Trailing slash in `SPLUNK_HOST`**  
   `.env` had `SPLUNK_HOST=10.100.0.41/`. The code built:
   ```text
   https://10.100.0.41/:443/services/mcp
   ```
   So the port ended up in the path and the URL was invalid.

2. **Wrong port**  
   We used `SPLUNK_PORT=443` (Splunk web UI). The **MCP endpoint** is on the **management port**, usually **8089**, not 443.

**Aha:** The URL you use in the browser to log in (`https://10.100.0.41/en-US/account/login`) is the **web UI (port 443)**. The **MCP service** is a different endpoint on the **management port (8089)**. Same host, different port.

**Fix:**

- Set `SPLUNK_HOST=10.100.0.41` with **no** trailing slash and **no** path.
- Set `SPLUNK_PORT=8089` (confirm from Splunk/MCP app docs; typically `https://<host>:8089/services/mcp`).
- In code, normalize the host (strip trailing slash, take only hostname) so the built URL is always `https://<host>:<port>/services/mcp`.

---

## Issue 2: 401 Unauthorized (wrong token type)

**Symptom:** `401 Unauthorized` for `https://10.100.0.41:8089/services/mcp`.

**Root cause:** We were sending a token that Splunk’s MCP app does not accept as the Bearer secret. Two different values exist:

1. **Token ID** – Short hex string (e.g. `ae20b32942246ffd...`) shown in the **token list** in the MCP app. Used for management (list/delete), **not** for `Authorization: Bearer`.
2. **Encrypted token** – Long base64-like string shown **only once** when you **create** the token. This is the secret you must send as `Authorization: Bearer <this_value>`.

We had put the **token ID** into `SPLUNK_API_KEY`. The app expects the **encrypted token**.

**Aha:** The MCP app’s error `"Authentication failed: encrypted token required"` was the clue: we were sending the wrong kind of value (the ID instead of the one-time secret).

**Fix:**

- In the Splunk MCP app, **create a new token**.
- On the creation screen, **copy the full encrypted token** (the long secret).
- Set in `.env`: `SPLUNK_API_KEY=<paste that full string here>` (no quotes; single line).
- Never use the short “token ID” from the token list as `SPLUNK_API_KEY`.

---

## Issue 3: Tool name mismatch (our proxy vs Splunk MCP app)

**Symptom:** After fixing URL and token, we could get a successful response from Splunk with `curl` (e.g. `tools/list` returned 200 and a list of tools), but our proxy’s “list indexes” still failed or didn’t return index data.

**Root cause:** Our proxy was calling Splunk with **our** tool names (e.g. `get_indexes`, `get_splunk_info`). The **Splunk MCP app** exposes tools with a **`splunk_` prefix** and different names:

- We sent: `get_indexes` → Splunk expects: `splunk_get_indexes`
- We sent: `get_splunk_info` → Splunk expects: `splunk_get_info`
- Same for `run_splunk_query`, `get_metadata`, `get_knowledge_objects`, etc.

**Aha:** Running `curl` with the correct token and `method: "tools/list"` returned the **actual** tool names (`splunk_get_indexes`, `splunk_get_info`, …). That made it obvious we needed a **mapping layer** in the proxy from our names to Splunk’s names.

**Fix:**

- In the proxy, add a mapping from our tool names to the Splunk MCP app’s tool names (e.g. a dict: `get_indexes` → `splunk_get_indexes`, etc.).
- When calling the Splunk backend with `tools/call`, translate the `name` in the params using this map before sending the request.

---

## Issue 4: Argument names don’t match Splunk’s schema

**Symptom:** Even with correct tool names, some tools might fail or return nothing if argument names don’t match what the Splunk MCP app expects.

**Root cause:** Our proxy used different parameter names than the Splunk app’s JSON schema:

- We sent `max_results` → Splunk expects `row_limit` (e.g. for `splunk_run_query`).
- We sent `metadata_type` → Splunk expects `type` (e.g. for `splunk_get_metadata`).
- We sent `object_type` → Splunk expects `type` (e.g. for `splunk_get_knowledge_objects`).

**Fix:**

- When building the `arguments` object for `tools/call`, use the **exact** names from the Splunk tool schema (e.g. `row_limit`, `type`).
- Update the proxy so each tool maps our external parameter names to Splunk’s internal names before calling the backend.

---

## Summary of changes we made

| Area | What we changed |
|------|------------------|
| **URL** | `SPLUNK_HOST` no trailing slash; normalize in code; `SPLUNK_PORT=8089`. |
| **Token** | Use **encrypted token** from token-creation screen in `SPLUNK_API_KEY`, not the token ID from the list. |
| **Tool names** | Map our names to Splunk’s: `get_indexes` → `splunk_get_indexes`, etc. |
| **Arguments** | Use Splunk’s names: `row_limit`, `type` where required. |
| **Optional** | `SPLUNK_MCP_PATH` in code for non-default path; README updated for token and port. |

---

## Quick reference: getting it working

1. **Splunk**
   - Install and enable the **Splunk MCP app**.
   - Note the MCP endpoint URL (typically `https://<host>:8089/services/mcp`).

2. **Token**
   - In the MCP app, create a new token.
   - Copy the **full encrypted token** from the creation screen (once).
   - Put it in `.env` as `SPLUNK_API_KEY=<paste>` (single line, no quotes).

3. **.env**
   - `SPLUNK_HOST=<host>` (no slash, no path).
   - `SPLUNK_PORT=8089` (or whatever port the MCP app uses).
   - `SPLUNK_VERIFY_SSL=false` if using self-signed certs.

4. **Proxy**
   - Rebuild and restart: `docker compose build splunk-mcp-server && docker compose up -d splunk-mcp-server`.
   - Ensure the proxy code maps tool names and arguments as above.

5. **Cursor**
   - Reload the window (Cmd+Shift+P → “Developer: Reload Window”) so it reconnects to the Splunk MCP server.
   - Then use “list all indexes” or other MCP tools.

---

## Verification with curl

To confirm Splunk’s MCP endpoint and token without Cursor:

```bash
curl -k -X POST "https://<SPLUNK_HOST>:8089/services/mcp" \
  -H "Authorization: Bearer <FULL_ENCRYPTED_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

- **200 + JSON with `result.tools`** → URL and token are correct; you can then fix proxy mapping if needed.
- **401** or **"encrypted token required"** → Use the encrypted token from the creation screen, not the token ID.
- **404** → Check host, port, and path (and that the MCP app is installed and enabled).

---

## Aha moments (recap)

1. **Port 443 vs 8089** – Browser login is web UI (443); MCP is management (8089). Same host, different port.
2. **Token ID vs encrypted token** – The list shows an ID; the Bearer secret is the long string shown only at token creation. “Encrypted token required” = we sent the ID.
3. **Tool names** – Splunk’s `tools/list` response shows the real names (`splunk_*`). Our proxy must map our names to those.
4. **Argument names** – Splunk’s schema uses `row_limit` and `type`; we had to align our proxy’s arguments to that schema.

This write-up should make future Splunk MCP setups and debugging much faster.

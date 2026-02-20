# ISE MCP Server: What Was Wrong and How It Was Fixed

This document explains the issue that prevented the Cisco ISE MCP server from connecting to Cursor (and from responding to any HTTP requests), and the changes that fixed it.

---

## 1. Symptoms: What You Saw

- **In Cursor:** The ISE MCP server never appeared in the list of connected servers. Other servers (Splunk, Catalyst Center, ThousandEyes, etc.) connected; ISE did not.
- **Cursor MCP logs** showed errors like:
  - `Error connecting to streamableHttp server, falling back to SSE: fetch failed`
  - `SSE error: TypeError: fetch failed: other side closed`
- **From the command line**, when testing the server directly:
  - `curl -v http://localhost:8005/health` → **Empty reply from server** (connection accepted, then closed with no HTTP response)
  - `curl -v -X POST http://localhost:8005/mcp -H "Content-Type: application/json" -d '{}'` → same **Empty reply from server**
- **Docker:** The ISE container was running (`docker ps` showed it on port 8005), but no HTTP response was ever returned for any request.

So: the process was listening on port 8005 (connections succeeded), but it **never sent any HTTP response** and closed the connection immediately. That’s why Cursor saw “other side closed” and “fetch failed.”

---

## 2. Root Cause: Blocking Startup Check With No Timeout

The real problem was **not** Cursor, the transport (streamable HTTP vs SSE), or Docker networking. It was **when** the HTTP server actually started.

### How the server used to start

On startup, the ISE MCP server did this, in order:

1. Load configuration and create the ISE API client.
2. **Test ISE connectivity** by calling the ISE API:
   ```python
   network_devices = ise_api.get("networkdevice", params={"size": 1})
   ```
3. If that call **failed**, the script called `exit(1)` and the process exited.
4. If it **succeeded**, the script then started the MCP HTTP server (uvicorn):
   ```python
   app = mcp.http_app()
   uvicorn.run(app, host=mcp_host, port=mcp_port, ...)
   ```

Two critical details:

- The `ise_api.get(...)` call was **synchronous** and had **no timeout**. So if the ISE server (e.g. at `10.100.0.10`) was slow or unreachable from inside the container, the call could **hang indefinitely**.
- Until that call finished (success or exception), the code **never reached** `uvicorn.run()`. So **no HTTP server was bound to port 8005** during the hang.

So in practice:

- The container started and the Python process began running.
- It printed a few startup messages (“Starting Cisco ISE MCP Server...”, etc.).
- It then **blocked** inside `ise_api.get("networkdevice", ...)` waiting for a response from `10.100.0.10`.
- From the host, when you ran `curl http://localhost:8005/health`, Docker forwarded the connection to the container. But inside the container **no process had yet called `uvicorn.run()`**, so nothing was listening on 8005 in the normal way. The “empty reply” behavior you saw was consistent with a process that had not fully started the HTTP stack, or with the process being in an inconsistent state (e.g. restart loops) so that the TCP connection was accepted but no HTTP response was ever sent.

In short: **the server was stuck in a blocking, non-time-limited ISE API check and never reached the line that starts the HTTP server.** So Cursor (and curl) never got a proper HTTP response.

---

## 3. Why This Was Hard to See at First

- **Logs looked “normal”:** You saw “Starting Cisco ISE MCP Server...” and “Starting MCP server on 0.0.0.0:8005”, so it looked like the server was starting. But those messages are printed **before** the ISE API check. The next line after the check would be either “✅ Successfully connected to ISE ERS API” or “❌ Failed to connect...”. Those lines **never appeared**, which meant the process never got past the `ise_api.get(...)` call.
- **Empty reply instead of connection refused:** If no process were listening at all, you’d usually get “Connection refused.” The “empty reply” (connection accepted, then closed with no data) suggested something was accepting the connection but not responding—consistent with a process that hadn’t fully started the HTTP server or was in a bad state.
- **Focus on Cursor/transport first:** The first fixes tried were switching to `streamable-http` and adjusting FastMCP version, which didn’t address the fact that the HTTP server often never started at all.

Once we added **flush=True** to the startup prints and **did not exit** on ISE failure, the logs showed the real sequence: either “✅ Successfully connected…” or “⚠️ Could not reach ISE API at startup”, and only then “Uvicorn running on http://0.0.0.0:8005”. That made it clear the server had been blocking on the ISE check.

---

## 4. The Fixes (What Was Actually Changed)

### 4.1. Do not block server startup on ISE connectivity

**Change:** The script no longer calls `exit(1)` when the startup ISE API check fails. It logs a warning and **always** continues to start the MCP HTTP server.

**Reason:** So the MCP server is always available for Cursor (and other clients) even when ISE is temporarily unreachable (e.g. from inside the container). Tool calls to ISE will then succeed or fail at request time, but the connection to Cursor works.

**Code (conceptually):**
```python
# Before: exit(1) on failure → process died, no server
except Exception as e:
    print(f"❌ Failed to connect to ISE API: {e}")
    exit(1)

# After: warn and continue → server always starts
except Exception as e:
    print(f"⚠️  Could not reach ISE API at startup: {e}")
    print("   Server will start anyway; tools will use ISE when called.")
```

### 4.2. Add a timeout to the startup ISE API check

**Change:** The startup call to the ISE API uses a **short timeout** (e.g. 5 seconds):

```python
ise_api.get("networkdevice", params={"size": 1}, timeout=5)
```

**Reason:** Without a timeout, `ise_api.get()` could block forever if ISE was slow or unreachable. With a timeout, the call returns (or raises) quickly, so the process always proceeds to start uvicorn.

### 4.3. Add a timeout to all ISE API calls

**Change:** The `CiscoISEAPI.get()` method now accepts an optional `timeout` and passes it to `requests` (default e.g. 30 seconds):

```python
def get(self, endpoint: str, params: Optional[Dict] = None, timeout: Optional[int] = 30) -> Dict[str, Any]:
    response = self.session.get(url, params=params, timeout=timeout)
```

**Reason:** Prevents any single ISE API request from hanging indefinitely, both at startup and when tools are used.

### 4.4. Run the server via ASGI app + uvicorn (with health route)

**Change:** Instead of only `mcp.run(transport="http", ...)`, the server now:

1. Builds the ASGI app: `app = mcp.http_app()`
2. Registers a **GET /health** route that returns `{"status":"ok","service":"ise-mcp-server"}`
3. Runs with **uvicorn** explicitly: `uvicorn.run(app, host=..., port=..., log_level="info")`

**Reason:**  
- Gives a simple way to verify the HTTP server is up (`curl http://localhost:8005/health`).  
- Ensures uvicorn request/startup logs appear in `docker logs`, which helped confirm that the server was not starting before.

### 4.5. Unbuffered output and error handling in Docker

**Change:**  
- Set **PYTHONUNBUFFERED=1** in the Dockerfile so print/tracebacks show up in `docker logs` immediately.  
- Wrapped `uvicorn.run()` in try/except with traceback so any fatal error during startup is visible in logs.

**Reason:** Makes it easier to see the exact point of failure when something goes wrong in the container.

### 4.6. FastMCP version pin (attempted earlier; not the root cause)

**Change:** In `pyproject.toml`, FastMCP was pinned to `>=2.10.6,<2.13` so the ISE server uses a 2.12.x release (e.g. 2.12.5) instead of 2.13.x.

**Reason:** There were known issues with streamable HTTP / empty responses in some 2.13.x behavior. Pinning didn’t fix the “empty reply” in this case because the real issue was that the server often never started. The pin is still a reasonable choice for stability.

---

## 5. What You Should See After the Fix

- **Container logs** (e.g. `docker logs ise-mcp-server`):
  - Either “✅ Successfully connected to ISE ERS API” or “⚠️ Could not reach ISE API at startup” (and optional “❌ ISE API Error: ...”).
  - Then: “INFO: Uvicorn running on http://0.0.0.0:8005”.
- **Health check:**  
  `curl http://127.0.0.1:8005/health` → **200 OK** and `{"status":"ok","service":"ise-mcp-server"}`.
- **Cursor:** After “Developer: Reload Window”, the ISE MCP server appears in the list of connected MCP servers and its tools are available.

If ISE (e.g. 10.100.0.10) is not reachable from the container, **tool** calls that talk to ISE may still time out or fail; that’s a network/connectivity issue from the container to ISE, not an MCP startup bug.

---

## 6. Summary Table

| What was wrong | How it was fixed |
|----------------|------------------|
| Startup ISE API check could block forever (no timeout) | Added `timeout=5` (or similar) to the startup `ise_api.get(...)` call. |
| Server exited on ISE failure, so no HTTP server ever started | Removed `exit(1)`; on failure we log a warning and still start uvicorn. |
| Any ISE API call could hang indefinitely | Added a `timeout` parameter to `CiscoISEAPI.get()` and use it in all calls. |
| Hard to see where the process was stuck | Use `flush=True` on startup prints; run with uvicorn and PYTHONUNBUFFERED so logs show “Uvicorn running” only after the check. |
| No simple way to verify “is the HTTP server up?” | Added GET /health and run the app with uvicorn so `curl .../health` returns 200 when the server is up. |

---

## 7. Takeaway

The ISE MCP server was not responding because **it often never started the HTTP server**: it blocked (or exited) on a synchronous, non-time-limited connectivity check to ISE before ever reaching `uvicorn.run()`. Fixing the startup sequence (timeout, no exit on failure, and always starting uvicorn) ensured the MCP server always listens and responds, so Cursor can connect and use it even when ISE is temporarily unreachable from the container.

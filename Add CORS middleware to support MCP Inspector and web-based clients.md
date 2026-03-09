## **Issue Title:** `: Add CORS middleware to support MCP Inspector and web-based clients`

## **Issue Description:**

### **The Problem**

The current implementation of the Meraki MCP server does not handle HTTP `OPTIONS` preflight requests. When attempting to connect to the server using the official **MCP Inspector** (or any browser-based client), the connection fails because the server returns a `405 Method Not Allowed` during the CORS preflight check.

### **Error Logs**

```text
meraki-mcp-server | INFO: 172.19.0.1:65094 - "OPTIONS /mcp HTTP/1.1" 405 Method Not Allowed
meraki-mcp-server | INFO: 172.19.0.1:65094 - "OPTIONS /sse HTTP/1.1" 404 Not Found

```

### **Proposed Solution**

Enable `CORSMiddleware` in the FastAPI/Starlette application setup. This allows the server to respond correctly to `OPTIONS` requests from the MCP Inspector (typically running on `localhost:6274` or `localhost:5173`).

### **Suggested Code Change**

In the main server file (e.g., `main.py` or `server.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

# ... after app = FastAPI() ...

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

```

### **Steps to Reproduce**

1. Run the Meraki MCP server in Docker.
2. Attempt to connect via the MCP Inspector: `npx @modelcontextprotocol/inspector http://localhost:8000/mcp`.
3. Observe the `405 Method Not Allowed` error in the server logs and the connection failure in the Inspector UI.

---

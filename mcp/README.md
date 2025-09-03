# MCP Servers (Scaffold)

This directory contains minimal MCP-compatible servers using JSON-RPC 2.0 over stdio.

Servers
- kyros_collab_server.py: collaboration v2 (tasks/locks/agents/events/logs)
- linear_server.py: Linear stub
- coderabbit_server.py: CodeRabbit stub
- railway_server.py: Railway stub
- vercel_server.py: Vercel stub

Protocol
- Simple line-delimited JSON-RPC for scaffolding:
  - Send {"jsonrpc":"2.0","id":1,"method":"initialize"}\n to initialize
  - Call methods with {"jsonrpc":"2.0","id":2,"method":"collab.get_state","params":{"kind":"tasks"}}\n
Environment loading
- Servers auto-load variables from `.env` and `collaboration/.env` if present (no override of existing env).
- IDEs like Cursor can inject env from `.cursor/environment.json`; that remains compatible.

Run
- python -m mcp.kyros_collab_server
- python -m mcp.linear_server
- python -m mcp.coderabbit_server
- python -m mcp.railway_server
- python -m mcp.vercel_server

Notes
- The collab server writes to collaboration/state/* with ETag (sha256) and atomic os.replace.
- Stubs return mock responses; replace with real API calls and tokens via env.

Quick RPC examples (stdio)
```
printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n' | python -m mcp.kyros_collab_server
printf '{"jsonrpc":"2.0","id":2,"method":"collab.list_tasks","params":{}}\n' | python -m mcp.kyros_collab_server
```

Import PR feedback to tasks
```
python scripts/import_coderabbit_feedback.py --owner ORG --repo REPO --pr 123 --assign
```

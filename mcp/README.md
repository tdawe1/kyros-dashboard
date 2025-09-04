# MCP Servers (Model Context Protocol)

This directory contains MCP-compatible servers using JSON-RPC 2.0 over stdio for integration with AI assistants and development tools.

## Available Servers

### Core Server
- **kyros_collab_server.py**: Full collaboration server (tasks/locks/agents/events/logs)
  - Manages project tasks, agent coordination, and state management
  - Atomic file operations with ETag validation
  - Full CRUD operations for collaboration data

### Integration Stubs
- **linear_server.py**: Linear issue management integration
- **coderabbit_server.py**: CodeRabbit code review integration  
- **railway_server.py**: Railway deployment management
- **vercel_server.py**: Vercel deployment management

## Installation

```bash
# Install in editable mode
cd mcp
python -m pip install -e .

# Verify installation
python -m pip show kyros-mcp
```

## Usage

### Running Servers

#### Direct Module Execution
```bash
python -m mcp.kyros_collab_server
python -m mcp.linear_server
python -m mcp.coderabbit_server
python -m mcp.railway_server
python -m mcp.vercel_server
```

#### Command-Line Entry Points (after installation)
```bash
kyros-collab-mcp
mcp-linear
mcp-coderabbit
mcp-railway
mcp-vercel
```

### JSON-RPC Protocol

Servers use line-delimited JSON-RPC 2.0 over stdio:

```bash
# Initialize server
printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n' | python -m mcp.kyros_collab_server

# Call methods
printf '{"jsonrpc":"2.0","id":2,"method":"collab.list_tasks","params":{}}\n' | python -m mcp.kyros_collab_server
printf '{"jsonrpc":"2.0","id":3,"method":"linear.capabilities","params":{}}\n' | python -m mcp.linear_server
```

### Environment Configuration

- Servers auto-load variables from `.env` and `collaboration/.env` (no override of existing env)
- Cursor IDE can inject environment from `.cursor/environment.json`
- See `mcp.config.example.json` for MCP client configuration

### Testing

```bash
# Run comprehensive test suite
./scripts/test-mcp-servers.sh

# Quick verification
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python -m mcp.kyros_collab_server
```

## API Reference

### Collaboration Server Methods
- `collab.list_tasks()` - List all tasks
- `collab.get_state(kind)` - Get state by kind (tasks/locks/agents)
- `collab.create_task(title, labels)` - Create new task
- `collab.transition_task(id, new_status)` - Update task status
- `collab.acquire_lease(path, owner, purpose)` - Acquire file lock
- `collab.release_lease(lock_id, owner)` - Release file lock

### Integration Server Methods
- **Linear**: `linear.capabilities()`, `linear.create_issue(team_id, title)`
- **CodeRabbit**: `coderabbit.request_review(pr)`, `coderabbit.fetch_feedback(owner, repo, pr)`
- **Railway**: `railway.capabilities()`, `railway.get_deployment(deployment_id)`
- **Vercel**: `vercel.get_deployment(deployment_id)`

## Troubleshooting

- **Server won't start**: Check Python dependencies and path
- **JSON-RPC errors**: Verify JSON formatting and method names
- **Permission issues**: Ensure scripts are executable (`chmod +x`)
- **Module not found**: Reinstall with `python -m pip install -e .`

## Development

The collaboration server uses atomic file operations with ETag validation for safe concurrent access. Stub servers return mock responses by default; replace with real API calls using environment variables for authentication tokens.

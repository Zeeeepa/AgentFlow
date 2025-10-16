# MCP Bridge Tool

Connect AgentFlow to any Model Context Protocol (MCP) server, enabling access to a vast ecosystem of MCP tools as native AgentFlow tools.

## Features

- ✅ **Dual Protocol Support**: Works with both stdio and HTTP MCP servers
- ✅ **Automatic Reconnection**: Handles connection failures gracefully
- ✅ **Connection Pooling**: Efficient HTTP connection management
- ✅ **Tool Discovery**: Automatically discovers available MCP tools
- ✅ **Error Recovery**: Comprehensive error handling and retry logic
- ✅ **Configurable Timeouts**: Per-tool and global timeout settings
- ✅ **Zero Code Changes**: Pure environment-based configuration

## Installation

### Prerequisites

Install MCP Python SDK and HTTP client:

```bash
# For stdio MCP servers
pip install mcp

# For HTTP MCP servers
pip install httpx

# Install both for maximum compatibility
pip install mcp httpx
```

### Quick Start

1. **Configure your .env file** (in `agentflow/` directory):

```bash
# For stdio MCP server
MCP_SERVER_TYPE=stdio
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=/path/to/your/mcp_server.py --verbose

# For HTTP MCP server
MCP_SERVER_TYPE=http
MCP_SERVER_URL=http://localhost:8000
MCP_SERVER_TIMEOUT=30
```

2. **Use in AgentFlow**:

```python
from agentflow.agentflow.solver import construct_solver

# Create solver with MCP Bridge Tool
solver = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["MCP_Bridge_Tool", "Base_Generator_Tool"],
    tool_engine=["Default", "gpt-4o-mini"]
)

# Execute MCP tools through natural language
result = solver.solve("Use the MCP search tool to find information about AI agents")
print(result["direct_output"])
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MCP_SERVER_TYPE` | Server protocol: `stdio` or `http` | Yes | `stdio` |
| `MCP_SERVER_COMMAND` | Command to start stdio server | If stdio | - |
| `MCP_SERVER_ARGS` | Space-separated args for stdio | No | - |
| `MCP_SERVER_URL` | Base URL for HTTP server | If http | - |
| `MCP_SERVER_TIMEOUT` | Request timeout (seconds) | No | `30` |
| `MCP_RECONNECT_ATTEMPTS` | Max reconnection attempts | No | `3` |

### Configuration Examples

#### Example 1: Local Python MCP Server (stdio)

```bash
# .env
MCP_SERVER_TYPE=stdio
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=/home/user/mcp_servers/filesystem_server.py
```

#### Example 2: Remote HTTP MCP Server

```bash
# .env
MCP_SERVER_TYPE=http
MCP_SERVER_URL=https://api.example.com/mcp
MCP_SERVER_TIMEOUT=60
```

#### Example 3: Node.js MCP Server (stdio)

```bash
# .env
MCP_SERVER_TYPE=stdio
MCP_SERVER_COMMAND=node
MCP_SERVER_ARGS=/path/to/server.js
```

## Usage Examples

### Direct Tool Usage

```python
from agentflow.agentflow.tools.mcp_bridge.tool import MCP_Bridge_Tool

# Initialize tool
mcp_tool = MCP_Bridge_Tool()

# List available tools from MCP server
available_tools = mcp_tool.get_available_tools()
print(f"Available tools: {[t['name'] for t in available_tools]}")

# Execute a specific MCP tool
result = mcp_tool.execute(
    tool_name="search_files",
    arguments={
        "directory": "/home/user/documents",
        "pattern": "*.pdf"
    }
)

if result["success"]:
    print(f"Search results: {result['result']}")
else:
    print(f"Error: {result['error']}")

# Get server info
server_info = mcp_tool.get_server_info()
print(f"Server connected: {server_info['connected']}")
print(f"Available tools: {server_info['available_tools_count']}")

# Cleanup
mcp_tool.close()
```

### Multi-Agent Workflow with MCP Tools

```python
from agentflow.agentflow.solver import construct_solver

# Research agent with MCP search tools
research_agent = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["MCP_Bridge_Tool"],  # MCP server provides search tools
    tool_engine=["Default"]
)

# Coding agent with native AgentFlow tools
coding_agent = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["Python_Coder_Tool"],
    tool_engine=["dashscope-qwen2.5-coder-7b-instruct"]
)

# Workflow: Research → Code → Summarize
query = "Research Python async patterns and write example code"

# Step 1: Research using MCP tools
research_result = research_agent.solve(
    "Use MCP search tools to find Python async/await best practices"
)

# Step 2: Generate code
code_result = coding_agent.solve(
    f"Based on this research, write example code:\n{research_result['direct_output']}"
)

print(code_result["direct_output"])
```

### Custom Timeout and Error Handling

```python
from agentflow.agentflow.tools.mcp_bridge.tool import MCP_Bridge_Tool

mcp_tool = MCP_Bridge_Tool()

# Execute with custom timeout for long-running operations
result = mcp_tool.execute(
    tool_name="process_large_file",
    arguments={"file_path": "/data/huge_dataset.csv"},
    timeout=300  # 5 minutes
)

if not result["success"]:
    if "timed out" in result["error"]:
        print("Operation timed out, try increasing timeout")
    elif "not found" in result["error"]:
        print(f"Tool not available. Available: {mcp_tool.get_available_tools()}")
    else:
        print(f"Execution error: {result['error']}")
```

## Creating MCP Servers for AgentFlow

### Simple Python MCP Server Example

```python
# my_mcp_server.py
import asyncio
from mcp.server import Server, Tool
from mcp.server.stdio import stdio_server

# Create MCP server
app = Server("my-tools-server")

# Define a tool
@app.tool()
async def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@app.tool()
async def calculate_sum(numbers: list[int]) -> int:
    """Calculate sum of numbers."""
    return sum(numbers)

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

Configure in `.env`:
```bash
MCP_SERVER_TYPE=stdio
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=/path/to/my_mcp_server.py
```

### HTTP MCP Server Example (FastAPI)

```python
# http_mcp_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

@app.post("/tools/list")
async def list_tools():
    return {
        "tools": [
            {
                "name": "search_database",
                "description": "Search database records",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    }
                }
            }
        ]
    }

@app.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    if request.name == "search_database":
        # Your tool logic here
        results = ["result1", "result2"]
        return {
            "content": [
                {"text": {"results": results}}
            ]
        }
    
    return {"error": "Tool not found"}

# Run with: uvicorn http_mcp_server:app --port 8000
```

Configure in `.env`:
```bash
MCP_SERVER_TYPE=http
MCP_SERVER_URL=http://localhost:8000
```

## Testing

Run the test suite:

```bash
cd agentflow/agentflow/tools/mcp_bridge
python test.py
```

Or use the AgentFlow test harness:

```bash
cd agentflow/agentflow
bash ./tools/test_all_tools.sh
```

## Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to MCP server"

**Solutions**:
1. Verify MCP server is running: `ps aux | grep your_server_command`
2. Check environment variables are set correctly
3. Test server independently before integrating
4. Check firewall/network settings for HTTP servers

### Import Errors

**Problem**: "MCP stdio client not available"

**Solution**: Install MCP SDK:
```bash
pip install mcp
```

**Problem**: "httpx not available"

**Solution**: Install httpx:
```bash
pip install httpx
```

### Tool Not Found

**Problem**: "Tool 'xyz' not found on server"

**Solutions**:
1. List available tools: `mcp_tool.get_available_tools()`
2. Verify MCP server exposes the tool
3. Check tool name spelling matches exactly

### Timeout Issues

**Problem**: Tool execution times out

**Solutions**:
1. Increase global timeout: `MCP_SERVER_TIMEOUT=120` in `.env`
2. Use per-call timeout: `tool.execute(..., timeout=120)`
3. Optimize MCP server performance

## Advanced Features

### Connection Health Monitoring

```python
tool = MCP_Bridge_Tool()

# Check connection status
info = tool.get_server_info()
if info['connected']:
    print(f"✓ Connected to {info['type']} server")
    print(f"  Available tools: {info['available_tools_count']}")
else:
    print("✗ Not connected, will auto-reconnect on next execute()")
```

### Automatic Reconnection

The tool automatically attempts reconnection on connection failures:

```python
# Connection lost during execution
result = tool.execute("some_tool", {"arg": "value"})

# Tool automatically tries to reconnect (up to MCP_RECONNECT_ATTEMPTS)
# No manual intervention needed
```

### Multiple MCP Servers

To use multiple MCP servers simultaneously, create separate tool instances:

```python
# Not yet supported - but you can create multiple AgentFlow solvers
# with different .env configurations

# Option 1: Environment switching (manual)
# Set MCP_SERVER_* vars, create tool, use it

# Option 2: Multiple Solvers (recommended)
# Create separate solver instances with different enabled tools
```

## Best Practices

1. **Test MCP Server First**: Verify your MCP server works standalone before integrating
2. **Set Appropriate Timeouts**: Long-running tools need higher timeout values
3. **Handle Errors Gracefully**: Always check `result['success']` before using output
4. **Monitor Connection Health**: Use `get_server_info()` for health checks
5. **Clean Up Connections**: Call `tool.close()` when done (especially in long-running apps)
6. **Use Connection Pooling**: HTTP servers benefit from persistent connections (automatic)

## Limitations

- stdio servers must be executable from command line
- HTTP servers must be network accessible
- Tool names and arguments must match MCP server schema exactly
- Single MCP server per tool instance (use multiple solvers for multiple servers)

## Contributing

To add features or fix bugs:

1. Modify `agentflow/agentflow/tools/mcp_bridge/tool.py`
2. Update tests in `test.py`
3. Run test suite: `python test.py`
4. Update this README with changes

## Support

For issues or questions:
- Check the [MCP Documentation](https://modelcontextprotocol.io/)
- Review AgentFlow issues on GitHub
- Test with the provided example servers first

## License

Same as AgentFlow project license.


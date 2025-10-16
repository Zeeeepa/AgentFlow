# Complete MCP Integration Guide for AgentFlow

This guide shows you exactly how to integrate Model Context Protocol (MCP) servers with AgentFlow, enabling access to a vast ecosystem of external tools.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding MCP Bridge](#understanding-mcp-bridge)
3. [Setting Up MCP Servers](#setting-up-mcp-servers)
4. [Configuration](#configuration)
5. [Using MCP Tools in Workflows](#using-mcp-tools-in-workflows)
6. [Creating Custom Agents](#creating-custom-agents)
7. [Advanced Patterns](#advanced-patterns)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies

```bash
# For stdio MCP servers
pip install mcp

# For HTTP MCP servers  
pip install httpx

# Install both for full support
pip install mcp httpx
```

### 2. Configure Environment

Create or edit `agentflow/.env`:

```bash
# Choose server type: stdio or http
MCP_SERVER_TYPE=stdio

# For stdio servers
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=/path/to/your/mcp_server.py

# For HTTP servers (alternative)
# MCP_SERVER_TYPE=http
# MCP_SERVER_URL=http://localhost:8000

# Optional settings
MCP_SERVER_TIMEOUT=30
MCP_RECONNECT_ATTEMPTS=3
```

### 3. Test the Connection

```bash
cd agentflow/agentflow/tools/mcp_bridge
python test.py
```

### 4. Use in AgentFlow

```python
from agentflow.agentflow.solver import construct_solver

# Create solver with MCP tools
solver = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["MCP_Bridge_Tool"],
    tool_engine=["Default"]
)

# Use MCP tools via natural language
result = solver.solve("Use MCP tools to search for Python tutorials")
print(result["direct_output"])
```

## Understanding MCP Bridge

### What is MCP Bridge?

MCP Bridge is an AgentFlow tool that acts as a connector between AgentFlow and any Model Context Protocol server. It:

- **Discovers** available tools from MCP servers automatically
- **Translates** between AgentFlow's tool interface and MCP's protocol
- **Manages** connections, reconnections, and error handling
- **Provides** a unified interface for both stdio and HTTP MCP servers

### Architecture

```
┌─────────────────┐
│   AgentFlow     │
│   Solver        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Bridge     │
│  Tool           │
└────────┬────────┘
         │
         ├─────────────┐
         ▼             ▼
┌──────────────┐  ┌──────────────┐
│ stdio MCP    │  │  HTTP MCP    │
│ Server       │  │  Server      │
└──────────────┘  └──────────────┘
```

For complete documentation, see `agentflow/agentflow/tools/mcp_bridge/README.md`

## Multi-Agent Workflow Example

```python
from agentflow.agentflow.solver import construct_solver

# Research agent with MCP search tools
research_agent = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["MCP_Bridge_Tool"],
    tool_engine=["Default"]
)

# Coding agent with native AgentFlow tools
coding_agent = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["Python_Coder_Tool"],
    tool_engine=["dashscope-qwen2.5-coder-7b-instruct"]
)

# Summary agent
summary_agent = construct_solver(
    llm_engine_name="gpt-4o",
    enabled_tools=["Base_Generator_Tool"],
    tool_engine=["gpt-4o-mini"]
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

# Step 3: Summarize
summary_result = summary_agent.solve(
    f"Summarize results:\n{research_result['direct_output']}\n{code_result['direct_output']}"
)

print(summary_result["direct_output"])
```

## Resources

- **Full Documentation**: `agentflow/agentflow/tools/mcp_bridge/README.md`
- **Example MCP Server**: `scripts/example_mcp_server.py`
- **Complete Workflow Examples**: `scripts/mcp_multi_agent_workflow.py`
- **MCP Official Docs**: https://modelcontextprotocol.io/
- **Available MCP Servers**: https://github.com/modelcontextprotocol/servers


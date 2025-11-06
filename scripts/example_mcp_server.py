"""
Example MCP Server for Testing AgentFlow MCP Bridge Tool

This is a simple stdio-based MCP server that provides basic tools
for testing the MCP Bridge integration.

Usage:
    python scripts/example_mcp_server.py

Configuration in .env:
    MCP_SERVER_TYPE=stdio
    MCP_SERVER_COMMAND=python
    MCP_SERVER_ARGS=scripts/example_mcp_server.py

Tools provided:
- echo: Echo back a message
- calculate: Perform basic calculations
- get_system_info: Get system information
- text_transform: Transform text (uppercase, lowercase, reverse)
"""

import sys
import json
import asyncio
from typing import Any, Dict, List

# Check for MCP library
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP library not installed", file=sys.stderr)
    print("Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Create server
app = Server("agentflow-example-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="echo",
            description="Echo back the provided message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="calculate",
            description="Perform basic arithmetic calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        ),
        Tool(
            name="get_system_info",
            description="Get information about the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["platform", "python_version", "cwd"],
                        "description": "Type of system information to retrieve"
                    }
                },
                "required": ["info_type"]
            }
        ),
        Tool(
            name="text_transform",
            description="Transform text in various ways",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to transform"
                    },
                    "transformation": {
                        "type": "string",
                        "enum": ["uppercase", "lowercase", "reverse", "length"],
                        "description": "Type of transformation to apply"
                    }
                },
                "required": ["text", "transformation"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool execution."""
    
    if name == "echo":
        message = arguments.get("message", "")
        result = f"Echo: {message}"
        
    elif name == "calculate":
        operation = arguments.get("operation")
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                result = "Error: Division by zero"
            else:
                result = a / b
        else:
            result = f"Error: Unknown operation {operation}"
        
        result = f"Result: {result}"
    
    elif name == "get_system_info":
        import platform
        import os
        
        info_type = arguments.get("info_type")
        
        if info_type == "platform":
            result = f"Platform: {platform.platform()}"
        elif info_type == "python_version":
            result = f"Python Version: {platform.python_version()}"
        elif info_type == "cwd":
            result = f"Current Directory: {os.getcwd()}"
        else:
            result = f"Error: Unknown info type {info_type}"
    
    elif name == "text_transform":
        text = arguments.get("text", "")
        transformation = arguments.get("transformation")
        
        if transformation == "uppercase":
            result = text.upper()
        elif transformation == "lowercase":
            result = text.lower()
        elif transformation == "reverse":
            result = text[::-1]
        elif transformation == "length":
            result = f"Length: {len(text)} characters"
        else:
            result = f"Error: Unknown transformation {transformation}"
    
    else:
        result = f"Error: Unknown tool {name}"
    
    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server."""
    print("Starting AgentFlow Example MCP Server...", file=sys.stderr)
    print("Server is ready. Waiting for connections.", file=sys.stderr)
    print("Press Ctrl+C to stop.", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.", file=sys.stderr)
        sys.exit(0)


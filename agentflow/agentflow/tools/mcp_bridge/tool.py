"""
MCP Bridge Tool - Connect AgentFlow to Model Context Protocol servers

This tool enables AgentFlow to communicate with any MCP server (stdio or HTTP),
allowing you to use MCP tools as native AgentFlow tools.

Environment Variables:
    MCP_SERVER_TYPE: "stdio" or "http" (default: "stdio")
    MCP_SERVER_COMMAND: Command to start stdio MCP server (e.g., "python server.py")
    MCP_SERVER_ARGS: Space-separated args for stdio server (optional)
    MCP_SERVER_URL: URL for HTTP MCP server (e.g., "http://localhost:8000")
    MCP_SERVER_TIMEOUT: Request timeout in seconds (default: 30)
    MCP_RECONNECT_ATTEMPTS: Max reconnection attempts (default: 3)

Example .env configuration:
    # For stdio MCP server
    MCP_SERVER_TYPE=stdio
    MCP_SERVER_COMMAND=python
    MCP_SERVER_ARGS=/path/to/mcp_server.py --verbose

    # For HTTP MCP server
    MCP_SERVER_TYPE=http
    MCP_SERVER_URL=http://localhost:8000
    MCP_SERVER_TIMEOUT=60
"""

import os
import json
import asyncio
import subprocess
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Try importing MCP client libraries
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_STDIO_AVAILABLE = True
except ImportError:
    MCP_STDIO_AVAILABLE = False

try:
    import httpx
    MCP_HTTP_AVAILABLE = True
except ImportError:
    MCP_HTTP_AVAILABLE = False

from agentflow.tools.base import BaseTool

# Load environment variables
load_dotenv()

TOOL_NAME = "MCP_Bridge_Tool"


class MCP_Bridge_Tool(BaseTool):
    """
    Bridge tool that connects AgentFlow to Model Context Protocol servers.
    
    Supports both stdio and HTTP MCP servers with automatic reconnection,
    connection pooling, and comprehensive error handling.
    """
    
    require_llm_engine = False
    
    def __init__(self, model_string: Optional[str] = None):
        """
        Initialize MCP Bridge Tool with environment-based configuration.
        
        Args:
            model_string: Optional LLM model string (not used by this tool)
        """
        super().__init__(
            tool_name=TOOL_NAME,
            tool_description=(
                "Execute tools from a Model Context Protocol (MCP) server. "
                "Supports both stdio and HTTP MCP servers. Automatically discovers "
                "available tools from the server and executes them with proper "
                "parameter handling and error recovery."
            ),
            tool_version="1.0.0",
            input_types={
                "tool_name": "str - Name of the MCP tool to execute",
                "arguments": "dict - Arguments to pass to the MCP tool (optional, default: {})",
                "timeout": "int - Custom timeout in seconds for this call (optional)",
            },
            output_type=(
                "dict - Result from the MCP tool containing:\n"
                "  - 'success': bool - Whether the execution succeeded\n"
                "  - 'result': Any - The tool's output (if successful)\n"
                "  - 'error': str - Error message (if failed)\n"
                "  - 'tool_name': str - Name of the executed tool\n"
                "  - 'server_info': dict - MCP server metadata"
            ),
            demo_commands=[
                {
                    "command": 'execution = tool.execute(tool_name="search", arguments={"query": "AI research"})',
                    "description": "Execute a search tool on the MCP server"
                },
                {
                    "command": 'execution = tool.execute(tool_name="list_files", arguments={"directory": "/tmp"})',
                    "description": "List files using an MCP filesystem tool"
                },
                {
                    "command": 'execution = tool.execute(tool_name="query_database", arguments={"sql": "SELECT * FROM users LIMIT 10"}, timeout=60)',
                    "description": "Run a database query with custom timeout"
                }
            ],
            user_metadata={
                "limitations": [
                    "Requires MCP server to be running and accessible",
                    "stdio servers must be executable from the command line",
                    "HTTP servers must be reachable via network",
                    "Tool names and arguments must match MCP server schema"
                ],
                "best_practices": [
                    "Test MCP server connectivity before production use",
                    "Set appropriate timeouts for long-running operations",
                    "Monitor connection health with the get_server_info method",
                    "Handle errors gracefully with try-except blocks",
                    "Use connection pooling for HTTP servers (automatic)"
                ],
                "dependencies": [
                    "mcp - Model Context Protocol Python SDK (for stdio)",
                    "httpx - Modern HTTP client (for HTTP servers)"
                ]
            }
        )
        
        # Load configuration from environment
        self.server_type = os.getenv("MCP_SERVER_TYPE", "stdio").lower()
        self.server_command = os.getenv("MCP_SERVER_COMMAND")
        self.server_args = os.getenv("MCP_SERVER_ARGS", "").split()
        self.server_url = os.getenv("MCP_SERVER_URL")
        self.timeout = int(os.getenv("MCP_SERVER_TIMEOUT", "30"))
        self.reconnect_attempts = int(os.getenv("MCP_RECONNECT_ATTEMPTS", "3"))
        
        # Connection state
        self._session: Optional[Any] = None
        self._http_client: Optional[Any] = None
        self._available_tools: Dict[str, Dict] = {}
        self._connection_healthy = False
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate MCP server configuration and check dependencies."""
        if self.server_type == "stdio":
            if not MCP_STDIO_AVAILABLE:
                raise ImportError(
                    "MCP stdio client not available. Install with: pip install mcp"
                )
            if not self.server_command:
                raise ValueError(
                    "MCP_SERVER_COMMAND environment variable is required for stdio servers"
                )
        elif self.server_type == "http":
            if not MCP_HTTP_AVAILABLE:
                raise ImportError(
                    "httpx not available. Install with: pip install httpx"
                )
            if not self.server_url:
                raise ValueError(
                    "MCP_SERVER_URL environment variable is required for HTTP servers"
                )
        else:
            raise ValueError(
                f"Invalid MCP_SERVER_TYPE: {self.server_type}. Must be 'stdio' or 'http'"
            )
    
    async def _connect_stdio(self) -> bool:
        """
        Establish connection to stdio MCP server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Build server parameters
            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args,
                env=None  # Inherit current environment
            )
            
            # Create stdio client context
            stdio_transport = stdio_client(server_params)
            
            # Initialize session
            self._session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize the session
            await self._session.initialize()
            
            # Fetch available tools
            tools_list = await self._session.list_tools()
            self._available_tools = {
                tool.name: {
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_list.tools
            }
            
            self._connection_healthy = True
            return True
            
        except Exception as e:
            self._connection_healthy = False
            print(f"Failed to connect to stdio MCP server: {e}")
            return False
    
    async def _connect_http(self) -> bool:
        """
        Establish connection to HTTP MCP server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create persistent HTTP client
            self._http_client = httpx.AsyncClient(
                base_url=self.server_url,
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            # Test connection and fetch available tools
            response = await self._http_client.post(
                "/tools/list",
                json={}
            )
            response.raise_for_status()
            
            tools_data = response.json()
            self._available_tools = {
                tool["name"]: {
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("inputSchema", {})
                }
                for tool in tools_data.get("tools", [])
            }
            
            self._connection_healthy = True
            return True
            
        except Exception as e:
            self._connection_healthy = False
            print(f"Failed to connect to HTTP MCP server: {e}")
            return False
    
    async def _ensure_connection(self) -> bool:
        """
        Ensure MCP server connection is active, reconnect if necessary.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self._connection_healthy:
            return True
        
        # Attempt reconnection
        for attempt in range(self.reconnect_attempts):
            print(f"Reconnecting to MCP server (attempt {attempt + 1}/{self.reconnect_attempts})...")
            
            if self.server_type == "stdio":
                success = await self._connect_stdio()
            else:
                success = await self._connect_http()
            
            if success:
                return True
            
            await asyncio.sleep(1)  # Brief delay between attempts
        
        return False
    
    async def _execute_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool via stdio MCP server.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        result = await self._session.call_tool(tool_name, arguments=arguments)
        return result.content[0].text if result.content else {}
    
    async def _execute_http(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool via HTTP MCP server.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        response = await self._http_client.post(
            "/tools/call",
            json={
                "name": tool_name,
                "arguments": arguments
            }
        )
        response.raise_for_status()
        
        result_data = response.json()
        return result_data.get("content", [{}])[0].get("text", {})
    
    def execute(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.
        
        Args:
            tool_name: Name of the MCP tool to execute
            arguments: Arguments to pass to the tool (default: {})
            timeout: Custom timeout for this call (default: use configured timeout)
            
        Returns:
            Dictionary containing:
                - success: bool - Whether execution succeeded
                - result: Any - Tool output (if successful)
                - error: str - Error message (if failed)
                - tool_name: str - Name of executed tool
                - server_info: dict - Server metadata
        """
        if arguments is None:
            arguments = {}
        
        # Use custom timeout if provided
        exec_timeout = timeout or self.timeout
        
        try:
            # Run async execution with timeout
            result = asyncio.run(
                asyncio.wait_for(
                    self._execute_async(tool_name, arguments),
                    timeout=exec_timeout
                )
            )
            return result
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Tool execution timed out after {exec_timeout} seconds",
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
    
    async def _execute_async(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal async execution method.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Execution result dictionary
        """
        # Ensure connection is active
        if not await self._ensure_connection():
            return {
                "success": False,
                "error": "Failed to connect to MCP server after multiple attempts",
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
        
        # Validate tool exists
        if tool_name not in self._available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found on server. Available: {list(self._available_tools.keys())}",
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
        
        # Execute tool
        try:
            if self.server_type == "stdio":
                result = await self._execute_stdio(tool_name, arguments)
            else:
                result = await self._execute_http(tool_name, arguments)
            
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
            
        except Exception as e:
            # Mark connection as unhealthy on execution errors
            self._connection_healthy = False
            
            return {
                "success": False,
                "error": f"Tool execution error: {str(e)}",
                "tool_name": tool_name,
                "server_info": self.get_server_info()
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools from the MCP server.
        
        Returns:
            List of tool metadata dictionaries
        """
        return [
            {
                "name": name,
                "description": info["description"],
                "input_schema": info["input_schema"]
            }
            for name, info in self._available_tools.items()
        ]
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the MCP server connection.
        
        Returns:
            Dictionary with server metadata
        """
        return {
            "type": self.server_type,
            "connected": self._connection_healthy,
            "available_tools_count": len(self._available_tools),
            "config": {
                "command": self.server_command if self.server_type == "stdio" else None,
                "url": self.server_url if self.server_type == "http" else None,
                "timeout": self.timeout
            }
        }
    
    def close(self):
        """Clean up MCP server connections."""
        if self._http_client:
            asyncio.run(self._http_client.aclose())
        if self._session:
            # stdio session cleanup handled by context manager
            pass
        
        self._connection_healthy = False
    
    def __del__(self):
        """Ensure connections are closed on cleanup."""
        self.close()


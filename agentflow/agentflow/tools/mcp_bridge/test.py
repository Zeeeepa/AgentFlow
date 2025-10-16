"""
Test script for MCP Bridge Tool

This script tests the MCP Bridge Tool with both stdio and HTTP servers.
Requires MCP server configuration in .env file.

Usage:
    python test.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agentflow.tools.mcp_bridge.tool import MCP_Bridge_Tool

# Load environment variables
load_dotenv()

def test_basic_functionality():
    """Test basic MCP Bridge Tool functionality."""
    print("=" * 60)
    print("Testing MCP Bridge Tool - Basic Functionality")
    print("=" * 60)
    
    try:
        # Initialize tool
        print("\n1. Initializing MCP Bridge Tool...")
        tool = MCP_Bridge_Tool()
        
        print(f"   ✓ Tool initialized")
        print(f"   Server Type: {tool.server_type}")
        print(f"   Connection Healthy: {tool._connection_healthy}")
        
        # Get server info
        print("\n2. Getting server information...")
        server_info = tool.get_server_info()
        print(f"   Server Info: {server_info}")
        
        # Get available tools (this triggers connection)
        print("\n3. Fetching available tools from MCP server...")
        available_tools = tool.get_available_tools()
        
        if available_tools:
            print(f"   ✓ Found {len(available_tools)} tools:")
            for tool_info in available_tools[:5]:  # Show first 5
                print(f"     - {tool_info['name']}: {tool_info['description']}")
            if len(available_tools) > 5:
                print(f"     ... and {len(available_tools) - 5} more")
        else:
            print("   ⚠ No tools found or connection failed")
            return False
        
        # Execute a simple tool if available
        if available_tools:
            print(f"\n4. Executing first available tool: {available_tools[0]['name']}...")
            
            # Try to execute with minimal arguments
            result = tool.execute(
                tool_name=available_tools[0]['name'],
                arguments={}
            )
            
            print(f"   Execution Result:")
            print(f"     Success: {result.get('success')}")
            if result.get('success'):
                print(f"     Result: {result.get('result')}")
            else:
                print(f"     Error: {result.get('error')}")
        
        # Cleanup
        print("\n5. Cleaning up...")
        tool.close()
        print("   ✓ Tool closed")
        
        print("\n" + "=" * 60)
        print("✅ MCP Bridge Tool test completed successfully!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nMissing dependencies. Install with:")
        print("  pip install mcp httpx")
        return False
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease configure MCP server in .env file:")
        print("  MCP_SERVER_TYPE=stdio  # or 'http'")
        print("  MCP_SERVER_COMMAND=python")
        print("  MCP_SERVER_ARGS=/path/to/server.py")
        print("\nOr for HTTP:")
        print("  MCP_SERVER_TYPE=http")
        print("  MCP_SERVER_URL=http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n" + "=" * 60)
    print("Testing MCP Bridge Tool - Error Handling")
    print("=" * 60)
    
    try:
        tool = MCP_Bridge_Tool()
        
        # Test 1: Non-existent tool
        print("\n1. Testing non-existent tool...")
        result = tool.execute(
            tool_name="nonexistent_tool_xyz",
            arguments={}
        )
        
        if not result.get('success'):
            print(f"   ✓ Correctly handled non-existent tool")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"   ⚠ Expected failure but got success")
        
        # Test 2: Invalid arguments
        print("\n2. Testing with None arguments (should default to {})...")
        available_tools = tool.get_available_tools()
        if available_tools:
            result = tool.execute(
                tool_name=available_tools[0]['name'],
                arguments=None
            )
            print(f"   Success: {result.get('success')}")
        
        # Test 3: Custom timeout
        print("\n3. Testing custom timeout...")
        if available_tools:
            result = tool.execute(
                tool_name=available_tools[0]['name'],
                arguments={},
                timeout=5
            )
            print(f"   ✓ Custom timeout executed")
            print(f"   Success: {result.get('success')}")
        
        tool.close()
        
        print("\n" + "=" * 60)
        print("✅ Error handling test completed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🚀 Starting MCP Bridge Tool Tests\n")
    
    # Check for configuration
    server_type = os.getenv("MCP_SERVER_TYPE")
    if not server_type:
        print("⚠️  Warning: MCP_SERVER_TYPE not set in environment")
        print("Please configure .env file with MCP server settings\n")
    
    # Run tests
    results = []
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


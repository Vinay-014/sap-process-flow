"""
Robust MCP Tool Wrapper for LangGraph Integration
Handles stdio client lifecycle, tool discovery, and execution with error handling.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

logger = logging.getLogger("aegis.mcp_wrapper")

class MCPToolWrapper:
    """Wraps an MCP server script for tool discovery and execution."""

    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.tools: List[StructuredTool] = []
        self.tool_map: Dict[str, Any] = {}
        self.session: Optional[ClientSession] = None

    async def connect_and_discover(self) -> List[StructuredTool]:
        """Connect to MCP server, discover tools, return LangChain StructuredTool wrappers."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path]
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool in tools_response.tools:
                        self.tools.append(StructuredTool(
                            name=tool.name,
                            description=tool.description or f"MCP Tool: {tool.name}",
                            func=lambda **kw: None,
                            coroutine=self._make_tool_coroutine(session, tool.name)
                        ))
                        self.tool_map[tool.name] = tool
                    logger.info(f"MCP Wrapper: Discovered {len(self.tools)} tools from {self.server_script_path}")
                    return self.tools
        except Exception as e:
            logger.error(f"MCP Wrapper: Failed to connect to {self.server_script_path}: {e}")
            return []

    def _make_tool_coroutine(self, session: ClientSession, tool_name: str):
        """Create a coroutine for tool execution."""
        async def coroutine(**kwargs):
            try:
                result = await session.call_tool(tool_name, kwargs)
                return result.content[0].text if result.content else ""
            except Exception as e:
                logger.error(f"MCP Tool {tool_name} execution failed: {e}")
                return f"ERROR: {str(e)}"
        return coroutine

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Direct tool call with connection lifecycle management."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path]
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, args)
                    return result.content[0].text if result.content else ""
        except Exception as e:
            logger.error(f"MCP Tool {tool_name} call failed: {e}")
            return f"ERROR: {str(e)}"

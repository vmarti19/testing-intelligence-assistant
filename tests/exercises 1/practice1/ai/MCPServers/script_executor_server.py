from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn
import argparse
import subprocess
import sys
import os

# Create a FastMCP server instance
server = FastMCP()

@server.tool("execute_python_script")
def execute_python_script(script_path: str, args: list = None) -> dict:
    """
    Execute a Python script and return its output.

    Args:
        script_path: Path to the Python script
        args: Optional list with arguments to pass to the script

    Returns:
        dict: Result of the execution including stdout, stderr, and return code
    """
    try:
        # Check if file exists
        if not os.path.exists(script_path):
            return {"success": False, "error": f"Script not found: {script_path}"}

        # Prepare command
        cmd = ['.venv\\Scripts\\python.exe', script_path]
        if args:
            for arg in args:
                cmd.append(str(arg))

        # Execute script
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        return {
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8585, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    mcp_server = server._mcp_server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)

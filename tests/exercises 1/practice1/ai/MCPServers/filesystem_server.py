from mcp.server.fastmcp import FastMCP
import os
import json

# Create a FastMCP server instance
server = FastMCP("Filesystem Server")


@server.tool("write_file")
def write_file(file_path: str, content: str) -> dict:
    """
    Write content to a file.

    Args:
        file_path: Path to the file
        content: Content to write to the file

    Returns:
        dict: Result of the operation
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {"success": True, "message": f"File written successfully: {file_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@server.tool("read_file")
def read_file(file_path: str) -> dict:
    """
    Read content from a file.

    Args:
        file_path: Path to the file

    Returns:
        dict: Content of the file
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        # Read content from file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}


@server.tool("delete_file")
def delete_file(file_path: str) -> dict:
    """
    Delete a file.

    Args:
        file_path: Path to the file

    Returns:
        dict: Result of the operation
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return {"success": False, "error": f"File not found: {file_path}"}

        # Delete file
        os.remove(file_path)

        return {"success": True, "message": f"File deleted successfully: {file_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@server.tool("list_directory")
def list_directory(directory_path: str) -> dict:
    """
    List contents of a directory.

    Args:
        directory_path: Path to the directory

    Returns:
        dict: List of files and directories
    """
    try:
        # Check if directory exists
        if not os.path.exists(directory_path):
            return {"success": False, "error": f"Directory not found: {directory_path}"}

        # List contents
        contents = os.listdir(directory_path)

        return {"success": True, "contents": contents}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    server.run(transport='stdio')

from mcp.server.fastmcp import FastMCP
import httpx
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("figma")

# Configuration
FIGMA_TOKEN = os.environ.get("FIGMA_ACCESS_TOKEN")

@mcp.tool()
async def get_figma_file_content(file_key: str) -> dict:
    """
    Fetch the content of a Figma file given its file key.
    The file key can be found in the Figma URL.
    """
    if not FIGMA_TOKEN:
        return {"error": "FIGMA_ACCESS_TOKEN not set in environment"}
    
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to fetch Figma file: {response.status_code}", "details": response.text}

@mcp.tool()
async def get_figma_node(file_key: str, node_id: str) -> dict:
    """
    Fetch specific nodes from a Figma file.
    node_id is the unique identifier for the layer/component.
    """
    if not FIGMA_TOKEN:
        return {"error": "FIGMA_ACCESS_TOKEN not set in environment"}
    
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to fetch Figma node: {response.status_code}", "details": response.text}

@mcp.tool()
def extract_figma_info(text: str) -> list[dict]:
    """
    Extract Figma file keys and node IDs from a string of text.
    """
    # Pattern for Figma URLs: https://www.figma.com/file/[KEY]/[NAME]?node-id=[NODE_ID]
    pattern = r"https://www.figma.com/file/([^/?#]+)[^?#]*(\?node-id=([^&#]+))?"
    matches = re.finditer(pattern, text)
    results = []
    for match in matches:
        file_key = match.group(1)
        node_id = match.group(3) if match.group(3) else None
        results.append({"file_key": file_key, "node_id": node_id.replace('%3A', ':') if node_id else None, "url": match.group(0)})
    return results

if __name__ == "__main__":
    mcp.run()

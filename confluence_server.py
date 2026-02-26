from mcp.server.fastmcp import FastMCP
import httpx
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("confluence")

# Configuration
CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN")

def get_auth_header():
    if not CONFLUENCE_USERNAME or not CONFLUENCE_API_TOKEN:
        return None
    auth_str = f"{CONFLUENCE_USERNAME}:{CONFLUENCE_API_TOKEN}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {encoded_auth}", "Accept": "application/json"}

@mcp.tool()
async def confluence_get_page(page_id: str) -> dict:
    """
    Fetch the content of a Confluence page given its page ID.
    """
    if not CONFLUENCE_URL:
        return {"error": "CONFLUENCE_URL not set in environment"}
    
    headers = get_auth_header()
    if not headers:
        return {"error": "CONFLUENCE_USERNAME or CONFLUENCE_API_TOKEN not set in environment"}
    
    # Use API v2 for getting page content
    url = f"{CONFLUENCE_URL.rstrip('/')}/api/v2/pages/{page_id}?body-format=storage"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to fetch Confluence page: {response.status_code}", "details": response.text}

@mcp.tool()
async def confluence_search(query: str, space_key: str = None) -> dict:
    """
    Search for Confluence pages using CQL (Confluence Query Language).
    Example query: 'title ~ "design"'
    """
    if not CONFLUENCE_URL:
        return {"error": "CONFLUENCE_URL not set in environment"}
    
    headers = get_auth_header()
    if not headers:
        return {"error": "CONFLUENCE_USERNAME or CONFLUENCE_API_TOKEN not set in environment"}
    
    cql = query
    if space_key:
        cql = f'({query}) and space = "{space_key}"'
        
    url = f"{CONFLUENCE_URL.rstrip('/')}/rest/api/content/search"
    params = {"cql": cql}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to search Confluence: {response.status_code}", "details": response.text}

@mcp.tool()
async def confluence_get_space_pages(space_key: str, limit: int = 10) -> dict:
    """
    List pages within a specific Confluence space.
    """
    if not CONFLUENCE_URL:
        return {"error": "CONFLUENCE_URL not set in environment"}
    
    headers = get_auth_header()
    if not headers:
        return {"error": "CONFLUENCE_USERNAME or CONFLUENCE_API_TOKEN not set in environment"}
    
    # Search is more flexible for listing pages
    cql = f'type = "page" and space = "{space_key}"'
    url = f"{CONFLUENCE_URL.rstrip('/')}/rest/api/content/search"
    params = {"cql": cql, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Failed to list space pages: {response.status_code}", "details": response.text}

if __name__ == "__main__":
    mcp.run()

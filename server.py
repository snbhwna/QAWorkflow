from mcp.server.fastmcp import FastMCP
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("azure-devops")

# Configuration via environment variables
ORG_URL = os.environ.get("AZURE_DEVOPS_ORG_URL")
PAT = os.environ.get("AZURE_DEVOPS_PAT")

def get_connection():
    if not ORG_URL or not PAT:
        raise ValueError("AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PAT environment variables must be set")
    credentials = BasicAuthentication('', PAT)
    connection = Connection(base_url=ORG_URL, creds=credentials)
    return connection

@mcp.tool()
def list_projects() -> list[str]:
    """List all projects in the Azure DevOps organization."""
    connection = get_connection()
    core_client = connection.clients.get_core_client()
    projects = core_client.get_projects()
    return [project.name for project in projects]

@mcp.tool()
def get_work_item(id: int) -> dict:
    """Get details of a specific work item by ID."""
    connection = get_connection()
    work_item_client = connection.clients.get_work_item_tracking_client()
    work_item = work_item_client.get_work_item(id)
    return {
        "id": work_item.id,
        "fields": work_item.fields,
        "url": work_item.url
    }

@mcp.tool()
def search_work_items(query: str) -> list[dict]:
    """Search for work items using WIQL (Work Item Query Language)."""
    connection = get_connection()
    work_item_client = connection.clients.get_work_item_tracking_client()
    wiql = {"query": query}
    results = work_item_client.query_by_wiql(wiql).work_items
    return [{"id": item.id, "url": item.url} for item in results]

if __name__ == "__main__":
    mcp.run()

from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("github-actions")

# Configuration via environment variables
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.environ.get("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.environ.get("GITHUB_REPO_NAME")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

@mcp.tool()
async def list_workflows() -> list[dict]:
    """List all GitHub Action workflows for the configured repository."""
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("workflows", [])

@mcp.tool()
async def trigger_workflow(workflow_id: str, ref: str = "main", inputs: dict = None) -> str:
    """Trigger a workflow_dispatch event for a specific workflow."""
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/{workflow_id}/dispatches"
    data = {
        "ref": ref,
        "inputs": inputs or {}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 204:
            return f"Successfully triggered workflow {workflow_id} on ref {ref}."
        else:
            return f"Error triggering workflow: {response.text}"

@mcp.tool()
async def get_workflow_runs(workflow_id: str = None) -> list[dict]:
    """Get recent runs for a specific workflow or all workflows if no ID is provided."""
    if workflow_id:
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/workflows/{workflow_id}/runs"
    else:
        url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/actions/runs"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("workflow_runs", [])

@mcp.tool()
async def create_pull_request(title: str, head: str, base: str = "main", body: str = "") -> dict:
    """Create a new Pull Request in the repository."""
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/pulls"
    data = {
        "title": title,
        "head": head,
        "base": base,
        "body": body
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    mcp.run()

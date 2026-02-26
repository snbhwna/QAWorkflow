from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("playwright")

# Configuration
BASE_URL = os.environ.get("PLAYWRIGHT_BASE_URL", "https://example.com")

@mcp.tool()
async def browse_url(url: str = None) -> str:
    """Browse a URL and return the page title and a summary of the content."""
    target_url = url if url else BASE_URL
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(target_url)
        title = await page.title()
        content = await page.content()
        await browser.close()
        return f"Title: {title}\nURL: {target_url}\nContent Length: {len(content)} characters"

@mcp.tool()
async def take_screenshot(url: str, filename: str = "screenshot.png") -> str:
    """Take a screenshot of a specific URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        path = os.path.join(os.getcwd(), filename)
        await page.screenshot(path=path)
        await browser.close()
        return f"Screenshot saved to {path}"

@mcp.tool()
async def run_test_script(script_content: str) -> str:
    """Execute a Playwright Python script snippet for functional testing."""
    # This is a basic executor for demonstration. 
    # In a real scenario, this would generate and run a .py file or use a pytest runner.
    try:
        # Note: This is a simplified example of dynamic execution
        # For a robust solution, you'd use a subprocess to run a generated file
        with open("temp_test.py", "w") as f:
            f.write(script_content)
        
        # You would then run 'pytest temp_test.py' or similar
        return "Test script saved to temp_test.py. Use 'pytest temp_test.py' to execute."
    except Exception as e:
        return f"Error creating test script: {str(e)}"

if __name__ == "__main__":
    mcp.run()

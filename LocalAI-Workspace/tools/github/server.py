"""
GitHub MCP server.
Provides search and repository listing functionality via the GitHub REST API.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from config.logger import get_logger  # noqa: E402
from config.settings import settings  # noqa: E402

log = get_logger("tools.github")
mcp = FastMCP("github")

GITHUB_API_URL = "https://api.github.com"
# Optional token from environment for higher rate limits
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def get_client() -> httpx.Client:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return httpx.Client(headers=headers, timeout=settings.request_timeout_seconds)


@mcp.tool()
def search_repositories(query: str, max_results: int = 5) -> str:
    """Search for GitHub repositories using a search query."""
    try:
        with get_client() as client:
            resp = client.get(f"{GITHUB_API_URL}/search/repositories", params={"q": query, "per_page": max_results})
            resp.raise_for_status()
            data = resp.json()
            
        items = data.get("items", [])
        if not items:
            return f"No repositories found for query: '{query}'"
            
        lines = []
        for repo in items:
            lines.append(f"- {repo['full_name']} (Stars: {repo['stargazers_count']})")
            lines.append(f"  URL: {repo['html_url']}")
            lines.append(f"  Description: {repo.get('description') or 'No description'}")
            
        return "\n".join(lines)
    except Exception as e:
        log.warning(f"search_repositories failed: {e}")
        return f"Failed to search repositories: {e}"


@mcp.tool()
def list_user_repositories(username: str, max_results: int = 10) -> str:
    """List public repositories for a specific GitHub user."""
    try:
        with get_client() as client:
            resp = client.get(f"{GITHUB_API_URL}/users/{username}/repos", params={"per_page": max_results, "sort": "updated"})
            resp.raise_for_status()
            repos = resp.json()
            
        if not repos:
            return f"No repositories found for user: '{username}'"
            
        lines = []
        for repo in repos:
            lines.append(f"- {repo['name']} (Stars: {repo['stargazers_count']})")
            lines.append(f"  URL: {repo['html_url']}")
            
        return "\n".join(lines)
    except Exception as e:
        log.warning(f"list_user_repositories failed: {e}")
        return f"Failed to list repositories for user {username}: {e}"


if __name__ == "__main__":
    log.info(f"GitHub MCP server starting (Token present: {bool(GITHUB_TOKEN)}).")
    mcp.run(transport="stdio")

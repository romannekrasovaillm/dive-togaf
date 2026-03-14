"""Live GitHub Public API wrappers for DIVE-TOGAF tool pool.

5 retrieval tools wrapping the GitHub REST API (unauthenticated).
Rate limit: 60 requests/hour without auth — sufficient for synthesis.

API docs: https://docs.github.com/en/rest
"""

from __future__ import annotations

import requests

GH_API = "https://api.github.com"
TIMEOUT = 15
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "DIVE-TOGAF/1.0",
}


# ---------------------------------------------------------------------------
# Tool 1: github_search_repositories
# ---------------------------------------------------------------------------
def github_search_repositories(
    query: str,
    sort: str = "stars",
    limit: int = 5,
) -> dict:
    """Search GitHub repositories by query.

    Useful for finding open-source architecture tools, frameworks,
    reference implementations, and solution building blocks.

    Args:
        query: Search query (e.g. "TOGAF", "archimate tool", "enterprise architecture").
        sort: Sort by "stars", "forks", "updated", or "best-match".
        limit: Max results (1-20).

    Returns:
        Dict with repos containing name, description, stars, language, topics.
    """
    params = {
        "q": query,
        "sort": sort if sort != "best-match" else "",
        "per_page": min(limit, 20),
    }
    # Remove empty params
    params = {k: v for k, v in params.items() if v}

    resp = requests.get(f"{GH_API}/search/repositories", params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for repo in data.get("items", []):
        results.append({
            "full_name": repo.get("full_name", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language", ""),
            "topics": repo.get("topics", [])[:10],
            "license": (repo.get("license") or {}).get("spdx_id", ""),
            "updated_at": repo.get("updated_at", ""),
            "url": repo.get("html_url", ""),
            "open_issues": repo.get("open_issues_count", 0),
        })

    return {
        "query": query,
        "results": results,
        "total_count": data.get("total_count", 0),
        "count": len(results),
    }


# ---------------------------------------------------------------------------
# Tool 2: github_get_repository
# ---------------------------------------------------------------------------
def github_get_repository(
    owner: str,
    repo: str,
) -> dict:
    """Get detailed information about a GitHub repository.

    Returns metadata about the repo including size, default branch,
    creation date, and primary language — useful for evaluating
    candidate solution building blocks.

    Args:
        owner: Repository owner (e.g. "opengroup").
        repo: Repository name (e.g. "togaf-content-metamodel").

    Returns:
        Dict with repo details including stars, forks, size, license, topics.
    """
    resp = requests.get(f"{GH_API}/repos/{owner}/{repo}", headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    return {
        "full_name": data.get("full_name", ""),
        "description": data.get("description", ""),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "language": data.get("language", ""),
        "topics": data.get("topics", []),
        "license": (data.get("license") or {}).get("spdx_id", ""),
        "size_kb": data.get("size", 0),
        "default_branch": data.get("default_branch", ""),
        "open_issues": data.get("open_issues_count", 0),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "pushed_at": data.get("pushed_at", ""),
        "url": data.get("html_url", ""),
        "archived": data.get("archived", False),
        "disabled": data.get("disabled", False),
    }


# ---------------------------------------------------------------------------
# Tool 3: github_get_repo_languages
# ---------------------------------------------------------------------------
def github_get_repo_languages(
    owner: str,
    repo: str,
) -> dict:
    """Get the language breakdown of a GitHub repository.

    Shows bytes of code per language — useful for assessing the technology
    stack of candidate building blocks.

    Args:
        owner: Repository owner.
        repo: Repository name.

    Returns:
        Dict with language names and byte counts, plus computed percentages.
    """
    resp = requests.get(f"{GH_API}/repos/{owner}/{repo}/languages", headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    total = sum(data.values()) if data else 1
    languages = []
    for lang, bytes_count in sorted(data.items(), key=lambda x: x[1], reverse=True):
        languages.append({
            "language": lang,
            "bytes": bytes_count,
            "percentage": round(bytes_count / total * 100, 1),
        })

    return {
        "owner": owner,
        "repo": repo,
        "total_bytes": total,
        "languages": languages,
        "count": len(languages),
    }


# ---------------------------------------------------------------------------
# Tool 4: github_get_repo_topics
# ---------------------------------------------------------------------------
def github_get_repo_topics(
    owner: str,
    repo: str,
) -> dict:
    """Get topics (tags) assigned to a GitHub repository.

    Topics reveal how the repository is categorized — useful for
    matching repos to architecture domains and capabilities.

    Args:
        owner: Repository owner.
        repo: Repository name.

    Returns:
        Dict with list of topics.
    """
    resp = requests.get(
        f"{GH_API}/repos/{owner}/{repo}/topics",
        headers={**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "owner": owner,
        "repo": repo,
        "topics": data.get("names", []),
        "count": len(data.get("names", [])),
    }


# ---------------------------------------------------------------------------
# Tool 5: github_list_repo_contents
# ---------------------------------------------------------------------------
def github_list_repo_contents(
    owner: str,
    repo: str,
    path: str = "",
) -> dict:
    """List the top-level or subdirectory contents of a GitHub repository.

    Useful for inspecting the structure of candidate solution building
    blocks — understanding modules, configs, and documentation layout.

    Args:
        owner: Repository owner.
        repo: Repository name.
        path: Subdirectory path (empty for root).

    Returns:
        Dict with list of files/dirs including name, type, size, and path.
    """
    url = f"{GH_API}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        data = [data]

    items = []
    for item in data:
        items.append({
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "size": item.get("size", 0),
            "path": item.get("path", ""),
        })

    return {
        "owner": owner,
        "repo": repo,
        "path": path or "/",
        "items": items,
        "count": len(items),
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
GITHUB_TOOL_DEFINITIONS = [
    {
        "id": "live_github_search_repositories",
        "name": "github_search_repositories",
        "description": "Search GitHub for open-source architecture tools, frameworks, and reference implementations.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": github_search_repositories,
        "parameters": [
            {"name": "query", "type": "string", "description": "Search query", "required": True},
            {"name": "sort", "type": "string", "description": "Sort: stars, forks, updated, best-match", "required": False, "default": "stars"},
            {"name": "limit", "type": "integer", "description": "Max results (1-20)", "required": False, "default": 5},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "results": {"type": "array"},
                "total_count": {"type": "integer"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "github", "search", "repositories"],
    },
    {
        "id": "live_github_get_repository",
        "name": "github_get_repository",
        "description": "Get detailed repo metadata (stars, license, topics, size) for evaluating building blocks.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": github_get_repository,
        "parameters": [
            {"name": "owner", "type": "string", "description": "Repo owner", "required": True},
            {"name": "repo", "type": "string", "description": "Repo name", "required": True},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "description": {"type": "string"},
                "stars": {"type": "integer"},
                "topics": {"type": "array"},
                "license": {"type": "string"},
            },
        },
        "tags": ["live", "github", "repository", "details"],
    },
    {
        "id": "live_github_get_repo_languages",
        "name": "github_get_repo_languages",
        "description": "Get language/technology breakdown of a repository for technology stack assessment.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": github_get_repo_languages,
        "parameters": [
            {"name": "owner", "type": "string", "description": "Repo owner", "required": True},
            {"name": "repo", "type": "string", "description": "Repo name", "required": True},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "total_bytes": {"type": "integer"},
                "languages": {"type": "array"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "github", "languages", "technology"],
    },
    {
        "id": "live_github_get_repo_topics",
        "name": "github_get_repo_topics",
        "description": "Get repository topic tags for domain/capability classification.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": github_get_repo_topics,
        "parameters": [
            {"name": "owner", "type": "string", "description": "Repo owner", "required": True},
            {"name": "repo", "type": "string", "description": "Repo name", "required": True},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "topics": {"type": "array"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "github", "topics", "taxonomy"],
    },
    {
        "id": "live_github_list_repo_contents",
        "name": "github_list_repo_contents",
        "description": "List repository file/directory structure for inspecting building block layout.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": github_list_repo_contents,
        "parameters": [
            {"name": "owner", "type": "string", "description": "Repo owner", "required": True},
            {"name": "repo", "type": "string", "description": "Repo name", "required": True},
            {"name": "path", "type": "string", "description": "Subdirectory path (empty for root)", "required": False, "default": ""},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "items": {"type": "array"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "github", "contents", "structure"],
    },
]

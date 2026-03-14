"""Live Open Library API wrappers for DIVE-TOGAF tool pool.

5 retrieval tools wrapping the Open Library REST API.
All endpoints are open — no authentication required.

API docs: https://openlibrary.org/dev/docs/api/search
"""

from __future__ import annotations

import requests

OL_SEARCH = "https://openlibrary.org/search.json"
OL_API = "https://openlibrary.org"
TIMEOUT = 15
HEADERS = {"User-Agent": "DIVE-TOGAF/1.0 (research project)"}


# ---------------------------------------------------------------------------
# Tool 1: openlibrary_search_books
# ---------------------------------------------------------------------------
def openlibrary_search_books(
    query: str,
    limit: int = 5,
) -> dict:
    """Search Open Library for books matching a query.

    Useful for finding reference publications on enterprise architecture,
    standards, frameworks, and technologies.

    Args:
        query: Search text (e.g. "enterprise architecture", "TOGAF").
        limit: Max results (1-20).

    Returns:
        Dict with results containing title, authors, year, subjects.
    """
    params = {
        "q": query,
        "limit": min(limit, 20),
        "fields": "key,title,author_name,first_publish_year,subject,edition_count,isbn",
    }
    resp = requests.get(OL_SEARCH, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for doc in data.get("docs", []):
        results.append({
            "key": doc.get("key", ""),
            "title": doc.get("title", ""),
            "authors": doc.get("author_name", []),
            "first_publish_year": doc.get("first_publish_year"),
            "subjects": (doc.get("subject") or [])[:10],
            "edition_count": doc.get("edition_count", 0),
            "isbn": (doc.get("isbn") or [])[:3],
        })

    return {
        "query": query,
        "results": results,
        "total_found": data.get("numFound", 0),
        "count": len(results),
    }


# ---------------------------------------------------------------------------
# Tool 2: openlibrary_get_work
# ---------------------------------------------------------------------------
def openlibrary_get_work(
    work_key: str,
) -> dict:
    """Get detailed info about a work (book) from Open Library.

    Args:
        work_key: Open Library work key (e.g. "/works/OL17860744W").

    Returns:
        Dict with title, description, subjects, covers, and links.
    """
    url = f"{OL_API}{work_key}.json"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    description = data.get("description", "")
    if isinstance(description, dict):
        description = description.get("value", "")

    return {
        "key": data.get("key", work_key),
        "title": data.get("title", ""),
        "description": description[:1000] if description else "",
        "subjects": data.get("subjects", [])[:20],
        "subject_places": data.get("subject_places", [])[:10],
        "subject_people": data.get("subject_people", [])[:10],
        "covers": data.get("covers", [])[:5],
        "links": [link.get("url", "") for link in data.get("links", [])[:5]],
        "created": data.get("created", {}).get("value", ""),
    }


# ---------------------------------------------------------------------------
# Tool 3: openlibrary_search_by_subject
# ---------------------------------------------------------------------------
def openlibrary_search_by_subject(
    subject: str,
    limit: int = 5,
) -> dict:
    """Search books by subject/topic classification.

    Subjects map to architecture domains — "enterprise architecture",
    "software architecture", "information technology", "standards", etc.

    Args:
        subject: Subject string (e.g. "enterprise_architecture").
        limit: Max results.

    Returns:
        Dict with works in this subject area.
    """
    url = f"{OL_API}/subjects/{subject.lower().replace(' ', '_')}.json"
    params = {"limit": min(limit, 20)}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    works = []
    for w in data.get("works", []):
        works.append({
            "key": w.get("key", ""),
            "title": w.get("title", ""),
            "authors": [a.get("name", "") for a in w.get("authors", [])],
            "edition_count": w.get("edition_count", 0),
            "first_publish_year": w.get("first_publish_year"),
            "cover_id": w.get("cover_id"),
        })

    return {
        "subject": data.get("name", subject),
        "work_count": data.get("work_count", 0),
        "works": works,
        "count": len(works),
    }


# ---------------------------------------------------------------------------
# Tool 4: openlibrary_get_author
# ---------------------------------------------------------------------------
def openlibrary_get_author(
    author_key: str,
) -> dict:
    """Get author details from Open Library.

    Useful for identifying key contributors to architecture literature.

    Args:
        author_key: Open Library author key (e.g. "/authors/OL3804859A").

    Returns:
        Dict with author name, bio, links, and other details.
    """
    url = f"{OL_API}{author_key}.json"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    bio = data.get("bio", "")
    if isinstance(bio, dict):
        bio = bio.get("value", "")

    return {
        "key": data.get("key", author_key),
        "name": data.get("name", ""),
        "personal_name": data.get("personal_name", ""),
        "bio": bio[:500] if bio else "",
        "birth_date": data.get("birth_date", ""),
        "links": [link.get("url", "") for link in data.get("links", [])[:5]],
        "alternate_names": data.get("alternate_names", [])[:5],
    }


# ---------------------------------------------------------------------------
# Tool 5: openlibrary_search_authors
# ---------------------------------------------------------------------------
def openlibrary_search_authors(
    query: str,
    limit: int = 5,
) -> dict:
    """Search for authors in Open Library.

    Args:
        query: Author name or keyword.
        limit: Max results.

    Returns:
        Dict with matching authors, their work counts, and top subjects.
    """
    url = f"{OL_API}/search/authors.json"
    params = {"q": query, "limit": min(limit, 20)}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for doc in data.get("docs", []):
        results.append({
            "key": f"/authors/{doc.get('key', '')}",
            "name": doc.get("name", ""),
            "work_count": doc.get("work_count", 0),
            "top_work": doc.get("top_work", ""),
            "top_subjects": doc.get("top_subjects", [])[:5],
        })

    return {
        "query": query,
        "results": results,
        "total_found": data.get("numFound", 0),
        "count": len(results),
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
OPENLIBRARY_TOOL_DEFINITIONS = [
    {
        "id": "live_openlibrary_search_books",
        "name": "openlibrary_search_books",
        "description": "Search Open Library for books on architecture, standards, and technologies.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": openlibrary_search_books,
        "parameters": [
            {"name": "query", "type": "string", "description": "Search text", "required": True},
            {"name": "limit", "type": "integer", "description": "Max results (1-20)", "required": False, "default": 5},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "results": {"type": "array"},
                "total_found": {"type": "integer"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "openlibrary", "search", "books"],
    },
    {
        "id": "live_openlibrary_get_work",
        "name": "openlibrary_get_work",
        "description": "Get detailed book/work information including description, subjects, and covers.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": openlibrary_get_work,
        "parameters": [
            {"name": "work_key", "type": "string", "description": "Open Library work key (e.g. /works/OL17860744W)", "required": True},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "subjects": {"type": "array"},
            },
        },
        "tags": ["live", "openlibrary", "work", "details"],
    },
    {
        "id": "live_openlibrary_search_by_subject",
        "name": "openlibrary_search_by_subject",
        "description": "Search books by subject/topic classification (e.g. enterprise_architecture, software_design).",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": openlibrary_search_by_subject,
        "parameters": [
            {"name": "subject", "type": "string", "description": "Subject string", "required": True},
            {"name": "limit", "type": "integer", "description": "Max results", "required": False, "default": 5},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "work_count": {"type": "integer"},
                "works": {"type": "array"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "openlibrary", "subject", "taxonomy"],
    },
    {
        "id": "live_openlibrary_get_author",
        "name": "openlibrary_get_author",
        "description": "Get author details — name, bio, and key publications.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": openlibrary_get_author,
        "parameters": [
            {"name": "author_key", "type": "string", "description": "Author key (e.g. /authors/OL3804859A)", "required": True},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "name": {"type": "string"},
                "bio": {"type": "string"},
            },
        },
        "tags": ["live", "openlibrary", "author"],
    },
    {
        "id": "live_openlibrary_search_authors",
        "name": "openlibrary_search_authors",
        "description": "Search for authors and their work counts and top subjects.",
        "tool_type": "retrieval",
        "domain": "general",
        "callable": openlibrary_search_authors,
        "parameters": [
            {"name": "query", "type": "string", "description": "Author name or keyword", "required": True},
            {"name": "limit", "type": "integer", "description": "Max results", "required": False, "default": 5},
        ],
        "return_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "results": {"type": "array"},
                "total_found": {"type": "integer"},
                "count": {"type": "integer"},
            },
        },
        "tags": ["live", "openlibrary", "author", "search"],
    },
]

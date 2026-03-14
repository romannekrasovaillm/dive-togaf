"""Tests for live API tool wrappers.

These tests make REAL HTTP calls to Open Library and GitHub APIs.
They validate correctness, response structure consistency, and
concurrent safety (multiple calls don't interfere).
"""

import sys
import json
import concurrent.futures
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pools.live_tools.wikidata_tools import (
    openlibrary_search_books,
    openlibrary_get_work,
    openlibrary_search_by_subject,
    openlibrary_get_author,
    openlibrary_search_authors,
    OPENLIBRARY_TOOL_DEFINITIONS,
)
from src.pools.live_tools.wikipedia_tools import (
    github_search_repositories,
    github_get_repository,
    github_get_repo_languages,
    github_get_repo_topics,
    github_list_repo_contents,
    GITHUB_TOOL_DEFINITIONS,
)


# ===== Open Library Tests =====

def test_openlibrary_search_books():
    """Search returns books with correct structure."""
    result = openlibrary_search_books("TOGAF", limit=3)
    assert result["query"] == "TOGAF"
    assert isinstance(result["results"], list)
    assert result["total_found"] > 0
    assert result["count"] > 0
    for item in result["results"]:
        assert "title" in item
        assert "authors" in item
        assert "key" in item
    first = result["results"][0]
    print(f"  PASS: Found {result['total_found']} books for 'TOGAF', first: '{first['title']}' by {first['authors']}")


def test_openlibrary_get_work():
    """Get work returns detailed book info."""
    # First search to get a valid work key
    search = openlibrary_search_books("enterprise architecture", limit=1)
    assert search["count"] > 0
    work_key = search["results"][0]["key"]

    result = openlibrary_get_work(work_key)
    assert result["key"] == work_key
    assert result["title"] != ""
    assert isinstance(result["subjects"], list)
    print(f"  PASS: Work '{result['title']}', {len(result['subjects'])} subjects, desc={len(result['description'])} chars")


def test_openlibrary_search_by_subject():
    """Search by subject returns categorized works."""
    result = openlibrary_search_by_subject("software_architecture", limit=3)
    assert result["subject"] != ""
    assert isinstance(result["works"], list)
    assert result["work_count"] > 0
    for w in result["works"]:
        assert "title" in w
        assert "key" in w
    print(f"  PASS: Subject '{result['subject']}': {result['work_count']} total works, got {result['count']}")


def test_openlibrary_get_author():
    """Get author returns biographical info."""
    # Search to find an author key
    search = openlibrary_search_authors("software architecture", limit=1)
    assert search["count"] > 0
    author_key = search["results"][0]["key"]

    result = openlibrary_get_author(author_key)
    assert result["name"] != ""
    print(f"  PASS: Author '{result['name']}', bio={len(result['bio'])} chars")


def test_openlibrary_search_authors():
    """Search authors returns results."""
    result = openlibrary_search_authors("enterprise architecture", limit=3)
    assert result["query"] == "enterprise architecture"
    assert isinstance(result["results"], list)
    assert result["total_found"] > 0
    for a in result["results"]:
        assert "name" in a
        assert "work_count" in a
    print(f"  PASS: Found {result['total_found']} authors, first: '{result['results'][0]['name']}' ({result['results'][0]['work_count']} works)")


# ===== GitHub Tests =====

def test_github_search_repositories():
    """Search returns repos with correct structure."""
    result = github_search_repositories("archimate", sort="stars", limit=3)
    assert result["query"] == "archimate"
    assert isinstance(result["results"], list)
    assert result["total_count"] > 0
    for repo in result["results"]:
        assert "full_name" in repo
        assert "stars" in repo
        assert "url" in repo
    first = result["results"][0]
    print(f"  PASS: Found {result['total_count']} repos for 'archimate', top: {first['full_name']} ({first['stars']} stars)")


def test_github_get_repository():
    """Get repository returns detailed metadata."""
    # Use search to find a valid repo, then get its details
    search = github_search_repositories("enterprise architecture framework", limit=1)
    assert search["count"] > 0
    full_name = search["results"][0]["full_name"]
    owner, repo = full_name.split("/")

    result = github_get_repository(owner, repo)
    assert result["full_name"] == full_name
    assert isinstance(result["topics"], list)
    assert "created_at" in result
    print(f"  PASS: {result['full_name']} — {result['stars']} stars, {result['language']}, topics={result['topics'][:5]}")


def test_github_get_repo_languages():
    """Get languages returns technology breakdown."""
    # Search first then get languages from a result, to avoid hardcoding repos
    search = github_search_repositories("TOGAF", limit=1)
    assert search["count"] > 0
    full_name = search["results"][0]["full_name"]
    owner, repo = full_name.split("/")

    result = github_get_repo_languages(owner, repo)
    assert result["count"] >= 0
    for lang in result["languages"]:
        assert "language" in lang
        assert "percentage" in lang
    if result["languages"]:
        primary = result["languages"][0]
        print(f"  PASS: {full_name} — {result['count']} languages, primary: {primary['language']} ({primary['percentage']}%)")
    else:
        print(f"  PASS: {full_name} — 0 languages (empty repo)")


def test_github_get_repo_topics():
    """Get topics returns categorization."""
    search = github_search_repositories("archimate tool", limit=1)
    assert search["count"] > 0
    full_name = search["results"][0]["full_name"]
    owner, repo = full_name.split("/")

    result = github_get_repo_topics(owner, repo)
    assert isinstance(result["topics"], list)
    print(f"  PASS: {full_name} — {result['count']} topics: {result['topics']}")


def test_github_list_repo_contents():
    """List repo contents returns file structure."""
    search = github_search_repositories("TOGAF", limit=1)
    assert search["count"] > 0
    full_name = search["results"][0]["full_name"]
    owner, repo = full_name.split("/")

    result = github_list_repo_contents(owner, repo)
    assert result["count"] > 0
    for item in result["items"]:
        assert "name" in item
        assert "type" in item
        assert item["type"] in ("file", "dir")
    print(f"  PASS: {full_name} root — {result['count']} items: {[i['name'] for i in result['items'][:5]]}...")


# ===== Structural Validation Tests =====

def test_tool_definitions_structure():
    """All tool definitions have required fields."""
    all_defs = OPENLIBRARY_TOOL_DEFINITIONS + GITHUB_TOOL_DEFINITIONS
    assert len(all_defs) == 10, f"Expected 10 tool definitions, got {len(all_defs)}"

    for defn in all_defs:
        assert "id" in defn, f"Missing 'id' in {defn.get('name', '?')}"
        assert "name" in defn
        assert "description" in defn
        assert "tool_type" in defn
        assert defn["tool_type"] == "retrieval"
        assert "callable" in defn
        assert callable(defn["callable"])
        assert "parameters" in defn
        assert len(defn["parameters"]) > 0
        assert "return_schema" in defn
        assert "tags" in defn
        assert "live" in defn["tags"]

    print(f"  PASS: All 10 tool definitions valid and callable")


def test_tool_ids_unique():
    """All live tool IDs are unique."""
    all_defs = OPENLIBRARY_TOOL_DEFINITIONS + GITHUB_TOOL_DEFINITIONS
    ids = [d["id"] for d in all_defs]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"
    print(f"  PASS: All {len(ids)} IDs unique")


def test_serializable_results():
    """Tool results are JSON-serializable (critical for trajectory recording)."""
    result1 = openlibrary_search_books("software architecture", limit=2)
    result2 = github_search_repositories("enterprise architecture", limit=2)

    json_str1 = json.dumps(result1, ensure_ascii=False)
    json_str2 = json.dumps(result2, ensure_ascii=False)

    parsed1 = json.loads(json_str1)
    parsed2 = json.loads(json_str2)

    assert parsed1["query"] == "software architecture"
    assert parsed2["query"] == "enterprise architecture"
    print(f"  PASS: Both Open Library and GitHub results serialize to JSON correctly")


# ===== Concurrency Safety Test =====

def test_concurrent_calls():
    """Multiple simultaneous API calls don't interfere with each other."""
    queries = ["TOGAF", "ArchiMate", "microservices", "SOA", "Kubernetes"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        ol_futures = {
            executor.submit(openlibrary_search_books, q, 2): q
            for q in queries
        }
        gh_futures = {
            executor.submit(github_search_repositories, q, "stars", 2): q
            for q in queries
        }

    ol_results = {}
    for future in concurrent.futures.as_completed(ol_futures):
        q = ol_futures[future]
        result = future.result()
        ol_results[q] = result
        assert result["query"] == q

    gh_results = {}
    for future in concurrent.futures.as_completed(gh_futures):
        q = gh_futures[future]
        result = future.result()
        gh_results[q] = result
        assert result["query"] == q

    assert len(ol_results) == 5
    assert len(gh_results) == 5
    print(f"  PASS: 10 concurrent API calls (5 Open Library + 5 GitHub) completed without interference")


# ===== Response Consistency Test =====

def test_response_consistency():
    """Same query returns consistent structure across multiple calls."""
    r1 = openlibrary_search_books("TOGAF", limit=2)
    r2 = openlibrary_search_books("TOGAF", limit=2)

    assert set(r1.keys()) == set(r2.keys())
    assert r1["query"] == r2["query"]
    assert r1["total_found"] == r2["total_found"]
    print(f"  PASS: Two calls to openlibrary_search_books('TOGAF') return consistent structure")


def run_all_tests():
    """Run all live tool tests."""
    tests = [
        # Open Library
        test_openlibrary_search_books,
        test_openlibrary_get_work,
        test_openlibrary_search_by_subject,
        test_openlibrary_get_author,
        test_openlibrary_search_authors,
        # GitHub
        test_github_search_repositories,
        test_github_get_repository,
        test_github_get_repo_languages,
        test_github_get_repo_topics,
        test_github_list_repo_contents,
        # Structural
        test_tool_definitions_structure,
        test_tool_ids_unique,
        test_serializable_results,
        # Quality
        test_concurrent_calls,
        test_response_consistency,
    ]

    print("=" * 60)
    print("DIVE-TOGAF Live Tool Tests (REAL API CALLS)")
    print("=" * 60)

    passed = 0
    failed = 0
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

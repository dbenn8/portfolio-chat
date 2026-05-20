import pytest
from unittest.mock import patch, AsyncMock, MagicMock


def test_system_prompt_no_citation_instructions():
    from app.chat import SYSTEM_PROMPT as sp
    assert "automatically" in sp.lower()


def test_build_context_includes_source_tags():
    from app.chat import build_context
    results = [
        {"text": "Dan built MARVIN", "project": "MARVIN", "source": "summary.md", "section": "Overview", "content_type": "summary", "slug": None, "distance": 0.1},
        {"text": "n8n workflows for MBO", "project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "section": "Approach", "content_type": "portfolio", "slug": "mbo-listing-sync", "distance": 0.2},
    ]
    context = build_context(results)
    assert "Dan built MARVIN" in context
    assert "/projects/mbo-listing-sync" in context


def test_build_source_links_deduplicates():
    from app.chat import build_source_links
    results = [
        {"project": "MARVIN", "source": "summary.md", "slug": None, "distance": 0.1},
        {"project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "slug": "mbo-listing-sync", "distance": 0.2},
        {"project": "MBO Listing Sync", "source": "mbo-listing-sync.astro", "slug": "mbo-listing-sync", "distance": 0.3},
    ]
    links = build_source_links(results)
    assert "[MBO Listing Sync](/projects/mbo-listing-sync)" in links
    assert links.count("MBO Listing Sync") == 1


def test_build_source_links_skips_no_slug():
    from app.chat import build_source_links
    results = [
        {"project": "MARVIN", "source": "summary.md", "slug": None, "distance": 0.1},
    ]
    links = build_source_links(results)
    assert links == ""

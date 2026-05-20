import pytest


def test_strip_html_tags():
    from ingest import strip_html
    html = "<h2>Title</h2>\n<p>Some <strong>bold</strong> text.</p>"
    result = strip_html(html)
    assert "<h2>" not in result
    assert "Title" in result
    assert "bold" in result


def test_extract_project_name_from_summary():
    from ingest import extract_project_name
    assert extract_project_name("AI Builder Summary for MARVIN.md") == "MARVIN"
    assert extract_project_name("AI Builder Summary for Burrfect Backend.md") == "Burrfect Backend"
    assert extract_project_name("AI Builder Summary for MBO n8n Workflows.md") == "MBO n8n Workflows"


def test_extract_sections():
    from ingest import extract_sections
    text = "# Title\n\nIntro paragraph.\n\n## Section One\n\nContent one.\n\n## Section Two\n\nContent two."
    sections = extract_sections(text)
    assert len(sections) >= 2
    assert any("Section One" in s["section"] for s in sections)
    assert any("Content one" in s["text"] for s in sections)


def test_collect_from_rag_content():
    from ingest import collect_rag_content
    from pathlib import Path
    rag_dir = Path("/Users/danielbennett/codeNew/portfolio-chat/rag-content")
    if rag_dir.exists():
        docs = collect_rag_content(rag_dir)
        assert len(docs) > 0
        assert all("text" in d and "source" in d and "project" in d for d in docs)

#!/usr/bin/env python3
"""Ingestion pipeline: reads cleaned content from rag-content/,
chunks text, embeds via GreenPT/OpenAI, upserts to Weaviate."""

import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from app.llm_service import LLMService
from app.weaviate_client import chunk_text, ensure_collection, upsert_chunks, clear_collection

RAG_CONTENT_DIR = Path(__file__).parent / "rag-content"

SLUG_MAP = {
    "overnight-briefing": "/projects/overnight-briefing",
    "mbo-listing-sync": "/projects/mbo-listing-sync",
    "burrfect-pipeline": "/projects/burrfect-pipeline",
    "burrfect-water": "/projects/burrfect-water",
    "btc-backtesting": "/projects/btc-backtesting",
    "woordjes": "/projects/woordjes",
    "claude-slack": "/projects/claude-slack",
    "kumpel-ai": "/projects/kumpel-ai",
    "project-orchestrator": "/projects/project-orchestrator",
    "n8n": "/n8n",
    "index": "/",
}


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\{[^}]*\}", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def extract_project_name(filename: str) -> str:
    match = re.match(r"AI Builder Summary for (.+)\.md$", filename)
    return match.group(1) if match else filename.replace(".md", "")


def extract_sections(text: str) -> list[dict]:
    lines = text.split("\n")
    sections = []
    current_section = "Introduction"
    current_text = []

    for line in lines:
        heading_match = re.match(r"^#{1,3}\s+(.+)$", line)
        if heading_match:
            if current_text:
                joined = "\n".join(current_text).strip()
                if joined:
                    sections.append({"section": current_section, "text": joined})
            current_section = heading_match.group(1)
            current_text = []
        else:
            current_text.append(line)

    if current_text:
        joined = "\n".join(current_text).strip()
        if joined:
            sections.append({"section": current_section, "text": joined})

    return sections


def collect_rag_content(rag_dir: Path) -> list[dict]:
    docs = []

    # Portfolio pages
    pages_dir = rag_dir / "portfolio-pages"
    if pages_dir.exists():
        for md_file in sorted(pages_dir.glob("*.md")):
            content = md_file.read_text()
            text = strip_html(content)
            project = md_file.stem
            if project == "index":
                project = "Portfolio Home"
            elif project == "n8n":
                project = "n8n Application Page"
            slug = SLUG_MAP.get(md_file.stem)

            for section in extract_sections(text):
                docs.append({
                    "text": section["text"],
                    "source": md_file.name,
                    "project": project,
                    "section": section["section"],
                    "content_type": "portfolio",
                    "slug": slug or "",
                })

    # AI Builder Summaries
    summaries_dir = rag_dir / "summaries"
    if summaries_dir.exists():
        for md_file in sorted(summaries_dir.glob("*.md")):
            content = md_file.read_text()
            project = extract_project_name(md_file.name)

            for section in extract_sections(content):
                docs.append({
                    "text": section["text"],
                    "source": md_file.name,
                    "project": project,
                    "section": section["section"],
                    "content_type": "summary",
                    "slug": "",
                })

    # Career background
    career_file = rag_dir / "career-background.md"
    if career_file.exists():
        content = career_file.read_text()
        for section in extract_sections(content):
            docs.append({
                "text": section["text"],
                "source": "career-background.md",
                "project": "Career Background",
                "section": section["section"],
                "content_type": "career",
                "slug": "",
            })

    return docs


async def run_ingestion():
    print("Starting ingestion...")
    llm = LLMService()

    print(f"Reading from {RAG_CONTENT_DIR}...")
    all_docs = collect_rag_content(RAG_CONTENT_DIR)
    print(f"  Found {len(all_docs)} sections total")

    print("Chunking...")
    all_chunks = []
    for doc in all_docs:
        text_chunks = chunk_text(doc["text"], max_tokens=250, overlap_tokens=50)
        for chunk in text_chunks:
            all_chunks.append({**doc, "text": chunk})
    print(f"Total chunks: {len(all_chunks)}")

    print("Embedding chunks...")
    for i, chunk in enumerate(all_chunks):
        chunk["vector"] = await llm.embed(chunk["text"])
        if (i + 1) % 20 == 0:
            print(f"  Embedded {i + 1}/{len(all_chunks)}")
    print(f"  Embedded {len(all_chunks)}/{len(all_chunks)}")

    print("Clearing and re-creating collection...")
    clear_collection()

    print("Upserting to Weaviate...")
    upsert_chunks(all_chunks)
    print(f"Done! {len(all_chunks)} chunks indexed.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ingestion())

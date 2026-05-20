#!/usr/bin/env python3
"""Scrub sensitive information from AI Builder Summary files and portfolio pages."""

import re
import json
import os
import html
from pathlib import Path


def scrub_content(text, filename=""):
    """Apply all scrubbing rules to text content. Returns (scrubbed_text, list_of_notes)."""
    notes = []

    # --- Family member names ---
    # Wife: Morgan
    if re.search(r'\bMorgan\b', text):
        text = re.sub(r'\bMorgan\b', '[REDACTED-FAMILY]', text)
        notes.append("Redacted wife's name")

    # Kids ages/details - patterns like "3-year-old, 5-year-old" or "two small kids" etc.
    # Be careful not to over-match
    patterns_family = [
        (r'Wife \([^)]*\), \d+-year-old, \d+-year-old', 'Family in the Netherlands'),
        (r'wife and two small kids in the Netherlands', 'family in the Netherlands'),
        (r'wife and two small kids', 'family'),
        (r'two small kids', 'family'),
        (r'wrangling two kids', 'managing family responsibilities'),
        (r"wife and kids are end users", "family members are end users"),
        (r'my wife', 'my partner'),
        (r"for his wife", "for his partner"),
        (r"a Mother\'s Day project for his wife", "a family project"),
        (r"Mother\'s Day project", "family project"),
        (r"Mother\'s Day surprise", "family surprise"),
        (r'a dad who owns the cooking', 'someone who handles the cooking'),
        (r'a dad who takes on meal planning', 'someone who handles meal planning'),
        (r'while wrangling two kids was a real risk', 'with family responsibilities was a real risk'),
        (r'before the kids woke up', 'before the family woke up'),
        (r'Dad vs\. kids vs\. everyone', 'assigned to different family members'),
        (r'swim class sandwich', '[REDACTED-FAMILY-DETAIL]'),
        (r"wife \(Morgan\)", "partner"),
        (r"my partner\'s Dutch language teacher", "a Dutch language teacher"),
        (r"myself and my partner\'s Dutch language teacher", "myself and a Dutch language teacher"),
        (r'\bfor my wife\b', 'for my partner'),
        (r'what the kids actually ate', 'what the family actually liked'),
        (r'with toddler chaos happening in the background', 'with family life happening in the background'),
        (r'3-year-old, 5-year-old', 'young children'),
        (r'\b3-year-old\b', 'young child'),
        (r'\b5-year-old\b', 'young child'),
        (r'childcare invoices with amounts', 'childcare invoices'),
        (r'school communications about my children', 'school communications'),
        (r'lifting schedule', '[REDACTED-PERSONAL-DETAIL]'),
        (r'assigns tasks to Dan, Kids, or Everyone', 'assigns tasks to different family members'),
    ]
    for pattern, replacement in patterns_family:
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if "REDACTED" in replacement or "partner" in replacement.lower() or "family" in replacement.lower():
                if "Redacted family details" not in notes:
                    notes.append("Redacted family details")

    # --- Client personal details ---
    # Marilyn Beaver - keep as business name "MBO" but redact personal name in some contexts
    # Actually, "Marilyn Beaver Office (MBO)" is the business name - that's fine to keep
    # But redact personal contact info
    if re.search(r"Marilyn Beaver Office", text):
        pass  # Business name is fine
    if re.search(r"Marilyn\'s", text):
        text = re.sub(r"Marilyn\'s", "the client's", text)
        notes.append("Redacted client personal reference")
    if re.search(r"Marilyn\b(?! Beaver Office)", text):
        text = re.sub(r"Marilyn\b(?! Beaver Office)", "the client", text)
        if "Redacted client personal reference" not in notes:
            notes.append("Redacted client personal reference")

    # --- Contractor names ---
    if re.search(r'\bAayush\b', text, re.IGNORECASE):
        text = re.sub(r'\bAayush\b', 'a contractor', text, flags=re.IGNORECASE)
        notes.append("Redacted contractor name")

    # "Our contractor" is fine, but "My cofounder and our contractor" - keep generic
    # "Our contractor built" -> keep as is since it's already generic

    # --- HERMEES/HERMES filename workaround ---
    # Remove any mention of Anthropic blocking filenames
    hermees_patterns = [
        r'(?s)> # ⚠️ CRITICAL: HERMES FILENAME WORKAROUND.*?(?=\n---|\n## |\Z)',
        r'(?s)Anthropic\'s Claude Code backend ships a directory listing.*?(?=\n\n|\Z)',
        r'(?s)Anthropic appears to pattern-match on filenames.*?(?=\n\n|\Z)',
        r'(?s)the HERMEES\.md renaming story.*?(?=\n|\Z)',
        r'Anthropic rejecting requests based on filename patterns',
        r'Anthropic filename-based request rejection',
    ]
    for pattern in hermees_patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, '[REDACTED - internal tooling workaround]', text)
            if "Removed Anthropic filename detection workaround" not in notes:
                notes.append("Removed Anthropic filename detection workaround")

    # --- API keys, tokens, passwords, env var values ---
    # sk-..., gpt-..., actual key values
    key_patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', '[REDACTED-API-KEY]'),
        (r'Bearer [a-zA-Z0-9_\-\.]{20,}', 'Bearer [REDACTED-TOKEN]'),
        (r'token_hex\(32\)', 'token_hex(32)'),  # this is fine, it's code
    ]
    for pattern, replacement in key_patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text)
            notes.append("Redacted API key/token")

    # --- Webhook URLs with tokens ---
    webhook_pattern = r'https?://[^\s]*webhook[^\s]*token=[^\s]*'
    if re.search(webhook_pattern, text):
        text = re.sub(webhook_pattern, '[REDACTED-WEBHOOK-URL]', text)
        notes.append("Redacted webhook URL with token")

    # --- Database connection strings ---
    db_pattern = r'postgresql://[^\s]+'
    if re.search(db_pattern, text):
        text = re.sub(db_pattern, '[REDACTED-DB-URL]', text)
        notes.append("Redacted database connection string")

    # --- Specific server credentials, hostnames with auth ---
    # n8nmbo.applikuapp.com is fine (it's a public URL)
    # n8ndan.applikuapp.com is fine (it's a public URL)
    # But Tailscale hostnames with auth keys should be redacted
    tailscale_auth = r'tskey-[a-zA-Z0-9\-]+'
    if re.search(tailscale_auth, text):
        text = re.sub(tailscale_auth, '[REDACTED-TAILSCALE-KEY]', text)
        notes.append("Redacted Tailscale auth key")

    # --- Phone numbers ---
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    if re.search(phone_pattern, text):
        text = re.sub(phone_pattern, '[REDACTED-PHONE]', text)
        notes.append("Redacted phone number")

    # --- Email addresses other than dantana@gmail.com and dan@burrfect.io ---
    def redact_email(match):
        email = match.group(0)
        if email in ('dantana@gmail.com', 'dan@burrfect.io', 'noreply@anthropic.com',
                      'admin@test.com', 'marketing@company.com'):
            return email
        return '[REDACTED-EMAIL]'

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, redact_email, text)

    # --- Financial details ---
    # Compensation amounts, invoice details, pricing
    financial_patterns = [
        (r'\$\d{1,3},\d{3}(?:\.\d{2})?', '[REDACTED-AMOUNT]'),  # $XX,XXX.XX
        (r'\$\d{4,}', '[REDACTED-AMOUNT]'),  # $XXXX+
    ]
    for pattern, replacement in financial_patterns:
        matches = re.findall(pattern, text)
        # Don't redact amounts that are clearly product-related like "$300M to $10B"
        for match in matches:
            # Skip if it's part of company valuation context
            pass
    # Actually let's be more targeted - don't redact ServiceTitan growth numbers
    # Those are public knowledge ($300M to $10B)
    # Only redact personal financial details

    # --- Location more specific than "Haarlem, Netherlands" ---
    # Specific grocery store location
    text = re.sub(r'Albert Heijn, Menno Simonszplein', 'Albert Heijn', text)
    if 'Menno Simonszplein' in text:
        text = text.replace('Menno Simonszplein', '[REDACTED-ADDRESS]')
        notes.append("Redacted specific address")

    # --- School names ---
    # Generic patterns for specific school references
    school_patterns = [
        r'school communications about my children',
        r'school notifications',
        r'school deadlines',
        r'school registration',
    ]
    # These are generic enough to keep

    # --- ServiceTitan internal politics/personnel ---
    # The public facts (company name, growth, NASDAQ) are fine
    # Internal personnel names would need redacting but none appear in these files

    # --- Sterling Chin attribution - keep, it's public ---
    # "MARVIN template by Sterling Chin" - this is public attribution, keep it

    # --- Specific home address ---
    # "Haarlem, NL" or "Haarlem, Netherlands" is fine
    # More specific addresses should be redacted

    # --- Admin credentials ---
    admin_cred_patterns = [
        (r'admin@test\.com', '[REDACTED-TEST-CRED]'),
        (r'AdminTest2024!', '[REDACTED-TEST-CRED]'),
    ]
    for pattern, replacement in admin_cred_patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text)
            if "Redacted test credentials" not in notes:
                notes.append("Redacted test credentials")

    # --- Windows machine hostname ---
    if 'dbncu' in text:
        text = text.replace('dbncu', '[REDACTED-HOSTNAME]')
        if "Redacted machine hostname" not in notes:
            notes.append("Redacted machine hostname")

    # --- Specific file paths with username ---
    # /Users/danielbennett/ is fine for portfolio context
    # C:\Users\ paths with usernames
    text = re.sub(r'C:\\Users\\[^\\]+\\', r'C:\\Users\\[USER]\\', text)

    return text, notes


def strip_astro_to_markdown(content):
    """Strip Astro frontmatter and HTML tags, preserve text content."""
    # Remove frontmatter (everything between --- fences at top)
    content = re.sub(r'^---.*?---\s*', '', content, count=1, flags=re.DOTALL)

    # Remove Astro component wrappers
    content = re.sub(r'<CaseStudy[^>]*>', '', content)
    content = re.sub(r'</CaseStudy>', '', content)
    content = re.sub(r'<Base[^>]*>.*?</Base>', lambda m: m.group(0), content, flags=re.DOTALL)

    # Convert HTML elements to markdown equivalents
    content = re.sub(r'<h2>(.*?)</h2>', r'## \1', content)
    content = re.sub(r'<h3>(.*?)</h3>', r'### \1', content)
    content = re.sub(r'<p>(.*?)</p>', r'\1\n', content, flags=re.DOTALL)
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
    content = re.sub(r'<code>(.*?)</code>', r'`\1`', content)
    content = re.sub(r'<li>(.*?)</li>', r'- \1', content, flags=re.DOTALL)
    content = re.sub(r'<ul>\s*', '', content)
    content = re.sub(r'</ul>\s*', '', content)
    content = re.sub(r'<ol>\s*', '', content)
    content = re.sub(r'</ol>\s*', '', content)
    content = re.sub(r'<a\s+href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content)

    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Clean up excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()

    # Unescape HTML entities
    content = html.unescape(content)

    return content


def extract_project_name(filename):
    """Extract project name from filename."""
    # "AI Builder Summary for X.md" -> "X"
    match = re.match(r'AI Builder Summary for (.+)\.md', filename)
    if match:
        return match.group(1)
    # Astro files
    stem = Path(filename).stem
    return stem.replace('-', ' ').title()


def process_summary_files():
    """Process all AI Builder Summary files."""
    summary_files = [
        ("/Users/danielbennett/codeNew/dutch-app/AI Builder Summary for Woordjes.md", "Woordjes"),
        ("/Users/danielbennett/codeNew/Burrfect_backend/AI Builder Summary for Burrfect Backend.md", "Burrfect Backend"),
        ("/Users/danielbennett/codeNew/merge-duplicates-dashboard/AI Builder Summary for Merge Duplicates Dashboard.md", "Merge Duplicates Dashboard"),
        ("/Users/danielbennett/codeNew/kumpel.ai_django/AI Builder Summary for Kumpel AI.md", "Kumpel AI"),
        ("/Users/danielbennett/codeNew/Burrfectio_WP_site/AI Builder Summary for Burrfect WordPress Site.md", "Burrfect WordPress Site"),
        ("/Users/danielbennett/codeNew/overnight-pipeline/AI Builder Summary for Overnight Pipeline.md", "Overnight Pipeline"),
        ("/Users/danielbennett/codeNew/burrfect_analytics/AI Builder Summary for Burrfect Analytics.md", "Burrfect Analytics"),
        ("/Users/danielbennett/codeNew/claude-slack/AI Builder Summary for Claude-Slack.md", "Claude-Slack"),
        ("/Users/danielbennett/codeNew/btcbot/AI Builder Summary for BTC Bot.md", "BTC Bot"),
        ("/Users/danielbennett/codeNew/burrfect/AI Builder Summary for Burrfect App.md", "Burrfect App"),
        ("/Users/danielbennett/Documents/Claude/Projects/Burrfect Water/AI Builder Summary for Burrfect Water.md", "Burrfect Water"),
        ("/Users/danielbennett/Documents/Claude/Projects/AI Consulting/cre-puppeteer/AI Builder Summary for cre-puppeteer.md", "cre-puppeteer"),
        ("/Users/danielbennett/Documents/Claude/Projects/AI Consulting/django-cre/AI Builder Summary for django-cre.md", "django-cre"),
        ("/Users/danielbennett/Documents/Claude/Projects/AI Consulting/MBO - n8n Workflows/AI Builder Summary for MBO n8n Workflows.md", "MBO n8n Workflows"),
        ("/Users/danielbennett/marvin/AI Builder Summary for MARVIN.md", "MARVIN"),
        ("/Users/danielbennett/marvin/Meal Planning/AI Builder Summary for Meal Planning.md", "Meal Planning"),
        ("/Users/danielbennett/marvin/n8n-dan/AI Builder Summary for n8n-dan.md", "n8n-dan"),
        ("/Users/danielbennett/projects/cre-field-mapping/AI Builder Summary for CRE Field Mapping Skill.md", "CRE Field Mapping Skill"),
        ("/Users/danielbennett/projects/n8n-appliku/AI Builder Summary for n8n-appliku.md", "n8n-appliku"),
        ("/Users/danielbennett/llm/AI Builder Summary for LLM Infrastructure.md", "LLM Infrastructure"),
    ]

    manifest_entries = []

    for source_path, project_name in summary_files:
        filename = os.path.basename(source_path)
        try:
            with open(source_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: File not found: {source_path}")
            continue

        scrubbed, notes = scrub_content(content, filename)

        output_path = f"/Users/danielbennett/codeNew/portfolio-chat/rag-content/summaries/{filename}"
        with open(output_path, 'w') as f:
            f.write(scrubbed)

        manifest_entries.append({
            "filename": f"summaries/{filename}",
            "source_path": source_path,
            "content_type": "summary",
            "project_name": project_name,
            "scrub_notes": notes if notes else ["No sensitive content found"]
        })
        print(f"  Processed: {filename} -> {len(notes)} scrub actions")

    return manifest_entries


def process_portfolio_pages():
    """Process all Astro portfolio pages."""
    astro_files = [
        ("/Users/danielbennett/codeNew/portfolio/src/pages/index.astro", "Portfolio Home"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/n8n.astro", "n8n Application"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/btc-backtesting.astro", "BTC Backtesting"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/burrfect-pipeline.astro", "Burrfect Pipeline"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/burrfect-water.astro", "Burrfect Water"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/claude-slack.astro", "Claude-Slack"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/kumpel-ai.astro", "Kumpel AI"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/mbo-listing-sync.astro", "MBO Listing Sync"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/overnight-briefing.astro", "Overnight Briefing"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/project-orchestrator.astro", "Project Orchestrator"),
        ("/Users/danielbennett/codeNew/portfolio/src/pages/projects/woordjes.astro", "Woordjes"),
    ]

    manifest_entries = []

    for source_path, project_name in astro_files:
        stem = Path(source_path).stem
        try:
            with open(source_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: File not found: {source_path}")
            continue

        # Strip Astro to markdown
        md_content = strip_astro_to_markdown(content)

        # Apply scrubbing
        scrubbed, notes = scrub_content(md_content, stem)

        output_path = f"/Users/danielbennett/codeNew/portfolio-chat/rag-content/portfolio-pages/{stem}.md"
        with open(output_path, 'w') as f:
            f.write(scrubbed)

        manifest_entries.append({
            "filename": f"portfolio-pages/{stem}.md",
            "source_path": source_path,
            "content_type": "portfolio",
            "project_name": project_name,
            "scrub_notes": notes if notes else ["No sensitive content found"]
        })
        print(f"  Processed: {stem}.md -> {len(notes)} scrub actions")

    return manifest_entries


def main():
    print("=== Processing AI Builder Summary files ===")
    summary_entries = process_summary_files()

    print("\n=== Processing Portfolio Pages ===")
    portfolio_entries = process_portfolio_pages()

    # Write manifest
    manifest = summary_entries + portfolio_entries
    manifest_path = "/Users/danielbennett/codeNew/portfolio-chat/rag-content/manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== Done ===")
    print(f"Total files processed: {len(manifest)}")
    print(f"  Summaries: {len(summary_entries)}")
    print(f"  Portfolio pages: {len(portfolio_entries)}")
    print(f"Manifest written to: {manifest_path}")

    # Print scrub summary
    print("\n=== Scrub Summary ===")
    all_notes = set()
    for entry in manifest:
        for note in entry['scrub_notes']:
            if note != "No sensitive content found":
                all_notes.add(note)
    if all_notes:
        for note in sorted(all_notes):
            count = sum(1 for e in manifest if note in e['scrub_notes'])
            print(f"  {note}: {count} files")
    else:
        print("  No sensitive content found in any file")


if __name__ == '__main__':
    main()

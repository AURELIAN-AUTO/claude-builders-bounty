"""Unit tests verifying Next.js + SQLite CLAUDE.md template compliance."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "nextjs-sqlite" / "CLAUDE.md"


def test_template_exists():
    assert TEMPLATE_PATH.exists(), f"CLAUDE.md template missing at {TEMPLATE_PATH}"


def test_required_sections_present():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    required_sections = [
        "## 1. Stack & Versions",
        "## 2. Dev Commands",
        "## 3. Project & Folder Structure",
        "## 4. SQL & Migration Conventions",
        "## 5. Component & Architecture Patterns",
        "## 6. What We Don't Do (And Why)",
        "## 7. Operational Guidelines for Claude Code",
    ]
    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_sqlite_pragmas_documented():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "PRAGMA journal_mode = WAL" in content
    assert "PRAGMA foreign_keys = ON" in content
    assert "PRAGMA busy_timeout = 5000" in content


def test_anti_patterns_explained():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    # Verify both the rule and the 'Why' rationale exist
    assert "NO Raw String SQL Interpolation" in content
    assert "SQL injection vulnerability" in content
    assert "amount_cents" in content
    assert "Floating point" in content

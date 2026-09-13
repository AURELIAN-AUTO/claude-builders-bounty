"""Unit tests for claude-review agent."""

import pytest
from claude_review.reviewer import PRReviewer, PRReviewResult
from claude_review.cli import parse_pr_url, main


@pytest.fixture
def reviewer():
    return PRReviewer()


def test_parse_pr_url():
    owner, repo, num = parse_pr_url("https://github.com/octocat/Hello-World/pull/42")
    assert owner == "octocat"
    assert repo == "Hello-World"
    assert num == 42


def test_parse_pr_url_invalid():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/octocat/Hello-World/issues/42")


def test_analyze_empty_diff(reviewer):
    res = reviewer.analyze_diff("")
    assert res.confidence_score == "Low"
    assert res.files_analyzed == 0


def test_detect_secrets(reviewer):
    diff = """diff --git a/config.py b/config.py
--- a/config.py
+++ b/config.py
@@ -1,2 +1,3 @@
+API_KEY = "sk-1234567890abcdef1234567890abcdef"
"""
    res = reviewer.analyze_diff(diff)
    assert any("secret" in r.lower() or "api" in r.lower() for r in res.identified_risks)
    assert res.confidence_score in ("Medium", "Low")


def test_detect_command_injection_risk(reviewer):
    diff = """diff --git a/worker.py b/worker.py
--- a/worker.py
+++ b/worker.py
@@ -1,2 +1,3 @@
+import subprocess
+subprocess.run("rm -rf " + user_input, shell=True)
"""
    res = reviewer.analyze_diff(diff)
    assert any("shell=True" in r for r in res.identified_risks)


def test_detect_code_smells(reviewer):
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,4 @@
+def do_something():
+    print("debugging here")
+    return True
"""
    res = reviewer.analyze_diff(diff)
    assert any("print()" in s for s in res.improvement_suggestions)


def test_clean_diff_with_tests(reviewer):
    diff = """diff --git a/utils.py b/utils.py
--- a/utils.py
+++ b/utils.py
@@ -1,1 +1,3 @@
+def add(a, b):
+    return a + b
diff --git a/test_utils.py b/test_utils.py
--- a/test_utils.py
+++ b/test_utils.py
@@ -1,1 +1,3 @@
+def test_add():
+    assert add(1, 2) == 3
"""
    res = reviewer.analyze_diff(diff)
    assert len(res.identified_risks) == 0
    assert res.confidence_score == "High"


def test_markdown_formatting(reviewer):
    diff = """diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1,1 +1,2 @@
+print("Hello")
"""
    res = reviewer.analyze_diff(diff, pr_url="https://github.com/example/repo/pull/1")
    md = res.to_markdown()
    assert "## 🤖 Claude Code PR Review" in md
    assert "### 📝 Summary of Changes" in md
    assert "### ⚠️ Identified Risks" in md
    assert "### 💡 Improvement Suggestions" in md
    assert "### 📊 Review Confidence" in md


def test_cli_local_diff(tmp_path):
    diff_file = tmp_path / "test.diff"
    diff_file.write_text("""diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -0,0 +1,1 @@
+hello world
""", encoding="utf-8")

    out_file = tmp_path / "review.md"
    exit_code = main(["--diff", str(diff_file), "--output", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    assert "## 🤖 Claude Code PR Review" in out_file.read_text(encoding="utf-8")

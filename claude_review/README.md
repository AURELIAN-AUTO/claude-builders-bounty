# claude-review 🤖

> Claude Code sub-agent that reviews a GitHub Pull Request diff and posts a structured Markdown review comment.

Built for **Issue #4** on [Claude Builders Bounty](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/4).

---

## Features

- 🔍 **Unified Diff Analysis:** Parses standard Git diffs without requiring external checkout.
- ⚠️ **Security & Risk Scanner:** Identifies hardcoded credentials, command injections (`shell=True`, `eval()`, `child_process.exec`), permissive file modes (`chmod 777`), and unhandled errors.
- 💡 **Improvement Suggestions:** Flags leftover debug statements (`console.log`, `print`), missing test coverage, and code smells.
- 📊 **Confidence Scoring:** Outputs high-signal `Low` / `Medium` / `High` confidence ratings grounded in empirical diff metrics.
- 🚀 **Dual Interface:** Works locally via CLI or continuously via automated GitHub Actions workflow.

---

## Installation

```bash
# Install locally in editable mode
pip install -e .
```

---

## Usage

### 1. Review a Remote GitHub PR

```bash
# Review a public or private GitHub PR
claude-review --pr https://github.com/owner/repo/pull/123

# Save review output to a markdown file
claude-review --pr https://github.com/owner/repo/pull/123 -o review.md

# Automatically post review comment back to the PR (requires GITHUB_TOKEN with write permission)
claude-review --pr https://github.com/owner/repo/pull/123 --post-comment
```

### 2. Review a Local Diff File (Offline / Dry Run)

```bash
git diff main > changes.diff
claude-review --diff changes.diff
```

---

## GitHub Actions CI Integration

Add `.github/workflows/claude-review.yml` to your repository:

```yaml
name: Claude Code PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install claude-review
        run: pip install .

      - name: Run Claude Review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude-review --pr "${{ github.event.pull_request.html_url }}" --post-comment
```

---

## Sample Outputs

See verified test outputs on real GitHub PRs in the [`examples/`](../examples/) directory:
- [`sample-review-hook-pr.md`](../examples/sample-review-hook-pr.md) (Tested on `claude-builders-bounty#4236`)
- [`sample-review-commons-pr.md`](../examples/sample-review-commons-pr.md) (Tested on `woahwhattheheck/commons#14047`)

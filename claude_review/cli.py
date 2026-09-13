"""CLI interface for claude-review agent."""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Optional, Tuple
import urllib.request
import urllib.error
import json

from claude_review.reviewer import reviewer, PRReviewResult


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    """Extracts owner, repo, and pull number from a GitHub PR URL."""
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}. Expected format: https://github.com/owner/repo/pull/123")
    return match.group(1), match.group(2), int(match.group(3))


def fetch_pr_diff(owner: str, repo: str, pull_number: int, token: Optional[str] = None) -> str:
    """Fetches the raw unified diff for a GitHub PR."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    req = urllib.request.Request(api_url)
    req.add_header("Accept", "application/vnd.github.v3.diff")
    req.add_header("User-Agent", "claude-review-agent/0.1.0")

    auth_token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("AURELIAN_GITHUB_TOKEN")
    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Fallback to public diff URL
            raw_url = f"https://github.com/{owner}/{repo}/pull/{pull_number}.diff"
            raw_req = urllib.request.Request(raw_url, headers={"User-Agent": "claude-review-agent/0.1.0"})
            with urllib.request.urlopen(raw_req, timeout=30) as raw_resp:
                return raw_resp.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Failed to fetch PR diff from GitHub (HTTP {e.code}): {e.reason}")


def post_pr_comment(owner: str, repo: str, pull_number: int, comment_body: str, token: Optional[str] = None) -> bool:
    """Posts a review comment to a GitHub PR."""
    auth_token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("AURELIAN_GITHUB_TOKEN")
    if not auth_token:
        print("Warning: Cannot post PR comment without GITHUB_TOKEN.", file=sys.stderr)
        return False

    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
    req = urllib.request.Request(api_url, data=json.dumps({"body": comment_body}).encode("utf-8"), method="POST")
    req.add_header("Authorization", f"Bearer {auth_token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "claude-review-agent/0.1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"Failed to post comment to PR #{pull_number}: HTTP {e.code} {e.reason}", file=sys.stderr)
        return False


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="claude-review",
        description="Claude Code agent that analyzes a PR diff and outputs a structured Markdown review comment."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr", type=str, help="GitHub Pull Request URL (e.g. https://github.com/owner/repo/pull/123)")
    group.add_argument("--diff", type=str, help="Path to local unified diff file to review")

    parser.add_argument("--output", "-o", type=str, help="Path to write the review Markdown output")
    parser.add_argument("--post-comment", action="store_true", help="Post the generated review as a comment to the GitHub PR")
    parser.add_argument("--token", type=str, help="GitHub API token (defaults to GITHUB_TOKEN or AURELIAN_GITHUB_TOKEN)")

    args = parser.parse_args(argv)

    try:
        owner, repo, pull_num = "", "", 0
        if args.pr:
            owner, repo, pull_num = parse_pr_url(args.pr)
            print(f"Fetching diff for {owner}/{repo}#{pull_num}...", file=sys.stderr)
            diff_text = fetch_pr_diff(owner, repo, pull_num, token=args.token)
            review_result = reviewer.analyze_diff(diff_text, pr_url=args.pr)
        else:
            with open(args.diff, "r", encoding="utf-8", errors="replace") as f:
                diff_text = f.read()
            review_result = reviewer.analyze_diff(diff_text, pr_url=f"local://{args.diff}")

        markdown_output = review_result.to_markdown()

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(markdown_output)
            print(f"Review written to {args.output}", file=sys.stderr)
        else:
            print(markdown_output)

        if args.post_comment and args.pr:
            success = post_pr_comment(owner, repo, pull_num, markdown_output, token=args.token)
            if success:
                print(f"Successfully posted review comment to {args.pr}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

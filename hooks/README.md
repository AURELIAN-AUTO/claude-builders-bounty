# Claude Code Pre-Tool-Use Hook: Destructive Command Blocker

A safety guard hook for Anthropic's Claude Code CLI that intercepts dangerous bash commands before execution and logs all blocked events.

## Features
- Intercepts destructive patterns:
  - 
m -rf / 
m -fr
  - DROP TABLE
  - git push --force
  - TRUNCATE TABLE
  - DELETE FROM without a WHERE clause
- Logs all blocked attempts to ~/.claude/hooks/blocked.log with timestamp, matched pattern, and working directory.
- Explains to Claude why the command was blocked without terminating the session.
- Passes safe commands through with zero latency.

## Quick Installation (2 commands)
`ash
mkdir -p ~/.claude/hooks && cp hooks/pre_tool_use.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/pre_tool_use.py
`

## Verification & Tests
`ash
pytest tests/test_hook.py -v
`

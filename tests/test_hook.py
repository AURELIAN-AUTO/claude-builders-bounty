import json
import os
import tempfile
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'hooks'))
from pre_tool_use import process_hook

@pytest.fixture
def temp_log(monkeypatch, tmp_path):
    log_file = tmp_path / ".claude" / "hooks" / "blocked.log"
    # Set both HOME and USERPROFILE for cross-platform compatibility
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    return log_file

def test_blocks_rm_rf(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "rm -rf /important/data"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "block"
    assert "dangerous" in result["message"].lower()

def test_blocks_drop_table(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "psql -c 'DROP TABLE users'"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "block"

def test_blocks_git_force_push(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "git push --force origin main"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "block"

def test_blocks_truncate(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "mysql -e 'TRUNCATE TABLE logs'"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "block"

def test_blocks_delete_without_where(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "psql -c 'DELETE FROM users'"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "block"

def test_allows_delete_with_where(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "psql -c 'DELETE FROM users WHERE id=5'"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "continue"

def test_allows_safe_commands(temp_log):
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "ls -la"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "continue"

def test_logging(temp_log, monkeypatch, tmp_path):
    log_path = tmp_path / ".claude" / "hooks" / "blocked.log"
    # Ensure both environment variables are set
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    event = {"type": "tool_use", "tool": "bash", "input": {"command": "rm -rf /data"}}
    process_hook(json.dumps(event))
    assert log_path.exists()
    content = log_path.read_text()
    assert "rm -rf /data" in content
    assert "rm -rf" in content

def test_non_bash_tools_pass_through(temp_log):
    event = {"type": "tool_use", "tool": "editor", "input": {"command": "some action"}}
    result = process_hook(json.dumps(event))
    assert result["action"] == "continue"
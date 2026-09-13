#!/usr/bin/env python3
import json
import sys
import re
from datetime import datetime
import os
from pathlib import Path

DANGEROUS_PATTERNS = [
    (r'rm\s+-rf', 'rm -rf'),
    (r'DROP\s+TABLE', 'DROP TABLE'),
    (r'git\s+push\s+--force', 'git push --force'),
    (r'TRUNCATE\s+TABLE', 'TRUNCATE'),
    (r'DELETE\s+FROM\s+\w+(?!.*WHERE)', 'DELETE FROM without WHERE'),
]

def get_log_path():
    """Get the log file path, respecting test environment."""
    # Check for test environment variables
    if 'HOME' in os.environ:
        home = Path(os.environ['HOME'])
    elif 'USERPROFILE' in os.environ:
        home = Path(os.environ['USERPROFILE'])
    else:
        home = Path.home()
    
    log_dir = home / '.claude' / 'hooks'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / 'blocked.log'

def log_blocked_command(command, pattern, cwd):
    """Log blocked command attempts."""
    log_path = get_log_path()
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} | Pattern: {pattern} | CWD: {cwd} | Command: {command}\n"
    
    with open(log_path, 'a') as f:
        f.write(log_entry)

def is_dangerous_command(command):
    """Check if command matches any dangerous patterns."""
    for pattern, name in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, name
    return False, None

def process_hook(event_json):
    """Process the hook event and return appropriate response."""
    try:
        event = json.loads(event_json)
        
        # Only process bash tool_use events
        if event.get('type') != 'tool_use' or event.get('tool') != 'bash':
            return {"action": "continue"}
        
        command = event.get('input', {}).get('command', '')
        cwd = os.getcwd()
        
        is_dangerous, pattern_name = is_dangerous_command(command)
        
        if is_dangerous:
            log_blocked_command(command, pattern_name, cwd)
            return {
                "action": "block",
                "message": f"⛔ BLOCKED: This command contains a dangerous pattern ({pattern_name}) and has been blocked for safety.\n\nCommand: {command}\n\nIf you need to run this command, please execute it manually outside of Claude Code."
            }
        
        return {"action": "continue"}
    
    except Exception as e:
        # On error, allow the command to proceed to avoid breaking workflows
        print(f"Hook error: {e}", file=sys.stderr)
        return {"action": "continue"}

def main():
    """Main entry point for the hook."""
    event_json = sys.stdin.read()
    result = process_hook(event_json)
    print(json.dumps(result))

if __name__ == '__main__':
    main()

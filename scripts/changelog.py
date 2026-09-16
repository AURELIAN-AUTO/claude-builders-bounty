import subprocess
import re
import os

def generate_changelog(repo_path):
    # Fetching the latest tag
    last_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], cwd=repo_path).strip().decode('utf-8')
    # Getting commit logs since the last tag
    logs = subprocess.check_output(['git', 'log', '--pretty=format:%s', f'{last_tag}..HEAD'], cwd=repo_path).decode('utf-8')
    
    # Regex patterns to categorize
    added_pattern = re.compile(r'^feat:', re.IGNORECASE)
    fixed_pattern = re.compile(r'^fix:', re.IGNORECASE)
    
    # Categorizing logs
    added = []
    fixed = []
    for log in logs.split('\n'):
        if added_pattern.match(log):
            added.append(log)
        elif fixed_pattern.match(log):
            fixed.append(log)
    
    # Writing to CHANGELOG.md
    changelog_content = "## Added\n" + '\n'.join(added) + "\n\n## Fixed\n" + '\n'.join(fixed)
    
    with open(os.path.join(repo_path, 'CHANGELOG.md'), 'w') as changelog_file:
        changelog_file.write(changelog_content)

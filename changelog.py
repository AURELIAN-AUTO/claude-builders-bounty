import subprocess
from git import Repo

CATEGORY_MAPPING = {
    'feat': 'Added',
    'fix': 'Fixed',
    'chore': 'Changed',
    'refactor': 'Changed',
    'perf': 'Changed',
    'docs': 'Changed',
    'style': 'Changed',
    'test': 'Removed',
}


def get_latest_tag(repo):
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    return tags[-1] if tags else None


def categorize_commit(message):
    for prefix, category in CATEGORY_MAPPING.items():
        if message.startswith(prefix):
            return category
    return 'Uncategorized'


def generate_changelog():
    repo = Repo('.')
    latest_tag = get_latest_tag(repo)
    commits = list(repo.iter_commits(f'{latest_tag}..HEAD'))
    changes = {}

    for commit in commits:
        category = categorize_commit(commit.message)
        if category not in changes:
            changes[category] = []
        changes[category].append(commit.message)

    with open('CHANGELOG.md', 'w') as changelog:
        changelog.write(f'## v0.2\n')
        for category, messages in changes.items():
            changelog.write(f'### {category}\n')
            for message in messages:
                changelog.write(f'- {message}\n')


if __name__ == '__main__':
    generate_changelog()
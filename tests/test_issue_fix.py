import os
import subprocess
import pytest

def setup_git_repo():
    os.system('git init')
    os.system('git config user.name "test"')
    os.system('git config user.email "test@test.com"')
    os.system('touch testfile')
    os.system('git add testfile')
    os.system('git commit -m "feat: add testfile"')
    os.system('git tag v0.1')
    os.system('echo change >> testfile')
    os.system('git add testfile')
    os.system('git commit -m "fix: correct typo"')

@pytest.fixture(scope="module")
def changelog_setup():
    setup_git_repo()
    yield
    os.system('rm -rf .git')

@pytest.mark.usefixtures("changelog_setup")
def test_generate_changelog():
    process = subprocess.run(['python', 'changelog.py'], capture_output=True)
    assert process.returncode == 0
    assert os.path.exists('CHANGELOG.md')
    with open('CHANGELOG.md', 'r') as file:
        content = file.read()
    assert '## v0.2' in content
    assert '### Fixed' in content
    assert '- fix: correct typo' in content

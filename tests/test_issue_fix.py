
import pytest

@pytest.fixture
def n8n_workflow():
    return {
        "trigger_type": "cron",
        "trigger_time": "Friday 5pm",
        "actions": [
            {"type": "fetch_github_data", "data_types": ["commits", "closed_issues", "merged_prs"]},
            {"type": "generate_summary", "api": "claude-sonnet-4-20250514"},
            {"type": "send_summary", "method": "webhook_or_email"}
        ]
    }

def test_n8n_workflow(n8n_workflow):
    assert n8n_workflow["trigger_type"] == "cron"
    assert n8n_workflow["trigger_time"] == "Friday 5pm"
    assert {"type": "fetch_github_data", "data_types": ["commits", "closed_issues", "merged_prs"]} in n8n_workflow["actions"]
    assert {"type": "generate_summary", "api": "claude-sonnet-4-20250514"} in n8n_workflow["actions"]
    assert {"type": "send_summary", "method": "webhook_or_email"} in n8n_workflow["actions"]

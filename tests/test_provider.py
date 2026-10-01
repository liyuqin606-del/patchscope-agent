import json
from pathlib import Path
import pytest
from patchscope.provider import BudgetClient


def client(tmp_path, ceiling=15):
    env = tmp_path/'env'
    env.write_text('OPENAI_API_KEY=dummy\nOPENAI_BASE_URL=https://example.invalid/v1\n')
    return BudgetClient(env, tmp_path/'ledger.jsonl', ceiling)


def test_budget_blocks_before_network(tmp_path, monkeypatch):
    import urllib.request
    called = []
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: called.append(True))
    with pytest.raises(RuntimeError, match='budget exhausted'):
        client(tmp_path, .000001).call([{'role':'user','content':'hello'}])
    assert called == []


def test_failed_request_keeps_reservation_and_redacts_error(tmp_path, monkeypatch):
    import urllib.request
    def fail(*a, **k):
        raise ValueError('dummy-secret-in-exception')
    monkeypatch.setattr(urllib.request, 'urlopen', fail)
    c = client(tmp_path)
    with pytest.raises(RuntimeError) as error:
        c.call([{'role':'user','content':'hello'}])
    text = c.ledger.read_text()
    assert 'dummy' not in text and 'dummy' not in str(error.value)
    assert json.loads(text)['reserved_cny'] > 0
    assert json.loads(text)['status'] == 'error'


def test_max_context_and_budget_are_enforced(tmp_path):
    with pytest.raises(ValueError):
        client(tmp_path, 18)
    with pytest.raises(ValueError, match='price tier'):
        client(tmp_path).call([{'role':'user','content':'a'*31000}])

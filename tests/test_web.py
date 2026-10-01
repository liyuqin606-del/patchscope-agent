import json
import pytest
pytest.importorskip('fastapi')
from fastapi.testclient import TestClient
from patchscope.web import create_app


def test_dashboard_is_read_only_and_paths_are_allowlisted(tmp_path):
    c=TestClient(create_app(tmp_path))
    assert c.get('/health').json()['read_only']
    assert c.get('/').status_code==200
    assert c.get('/api/experiments/.env').status_code==404
    assert c.post('/api/experiments/development').status_code==405
    (tmp_path/'adaptive-comparison.json').write_text(json.dumps({'seed_tasks':15}))
    assert c.get('/api/experiments/development').json()['seed_tasks']==15
    assert c.get('/api/cost').json()['requests']==0


def test_partial_report_is_reported_as_unavailable(tmp_path):
    (tmp_path/'adaptive-comparison.json').write_text('{')
    assert TestClient(create_app(tmp_path)).get('/api/experiments/development').status_code==503

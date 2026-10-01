from pathlib import Path
import json
import pytest
from langgraph.checkpoint.sqlite import SqliteSaver
from patchscope.agent import run, build_graph, DemoPlanner
from patchscope.retrieval import RepositoryIndex
from patchscope.evolution import Policy, select, evaluate
from patchscope.checks import run_container


@pytest.fixture
def repo(tmp_path):
    (tmp_path / 'pricing.py').write_text('def discounted_price(price, percent):\n    return price * (1 - percent / 100)\n')
    return tmp_path


def test_retrieval_citations_and_out_of_scope(repo, tmp_path):
    index = RepositoryIndex(repo)
    results = index.search('discounted_price percent')
    assert results[0]['path'] == 'pricing.py'
    assert results[0]['start'] == 1 and len(results[0]['sha256']) == 64
    assert index.search('zzzzqqqqxxxx') == []


def test_symlink_not_indexed(repo, tmp_path):
    (repo / 'linked.py').symlink_to('/etc/passwd')
    assert all(c.path != 'linked.py' for c in RepositoryIndex(repo).chunks)


def test_semantic_bug_does_not_become_acceptance(repo):
    candidate = repo / 'candidate.txt'
    candidate.write_text('def discounted_price(price, percent):\n    return price * percent / 100\n')
    result = run(repo, candidate, 'discounted_price', repo / 'state.db')
    assert result['verdict'] == 'insufficient_evidence'
    assert result['mode'] == 'deterministic_demo'
    assert result['steps'] == 2
    # Reload the graph from a fresh connection: checkpoint survived process-local objects.
    with SqliteSaver.from_conn_string(str(repo / 'state.db')) as saver:
        graph = build_graph(RepositoryIndex(repo), DemoPlanner(), saver)
        saved = graph.get_state({'configurable': {'thread_id': result['thread_id']}})
        assert saved.values['verdict'] == result['verdict']


def test_invalid_syntax_rejected(repo):
    candidate = repo / 'candidate.txt'
    candidate.write_text('def broken(:')
    assert run(repo, candidate, 'broken', repo / 'state.db')['verdict'] == 'reject'


def test_budget_prevents_extra_tools(repo):
    candidate = repo / 'candidate.txt'
    candidate.write_text('def broken(:')
    result = run(repo, candidate, 'broken', repo / 'state.db', budget=1)
    assert result['steps'] == 1
    assert result['verdict'] == 'insufficient_evidence'


def test_container_requires_pin(repo):
    with pytest.raises(ValueError):
        run_container(repo, 'python:latest', ['python', '--version'])


def test_unavailable_container_does_not_pass(repo, monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    assert run_container(repo, 'python@sha256:abc', ['python', '--version'])['status'] == 'unavailable'


@pytest.fixture
def rows():
    return [
        {'id': 'a', 'split': 'development', 'correct': True, 'checks': {'syntax': 'pass', 'contract': 'error'}},
        {'id': 'b', 'split': 'development', 'correct': False, 'checks': {'syntax': 'pass', 'contract': 'fail'}},
    ]


def test_harness_selection_and_leakage_gate(rows):
    base = Policy('base', ('syntax',))
    candidate = Policy('candidate', ('syntax', 'contract'))
    report = select([base, candidate], rows, base)
    assert report['promoted'] and report['development_metrics']['false_rejections'] == 0
    rows[0]['split'] = 'test'
    with pytest.raises(ValueError):
        select([base, candidate], rows, base)


def test_harness_rejects_false_rejection_regression(rows):
    rows[0]['checks']['contract'] = 'fail'
    base = Policy('base', ('syntax',))
    assert not select([base, Policy('bad', ('contract',))], rows, base)['promoted']


def test_error_is_abstention(rows):
    metrics = evaluate(Policy('contract', ('contract',)), rows)
    assert metrics['false_rejections'] == 0 and metrics['abstentions'] == 1


def test_budget_planner_uses_langchain_schema():
    from patchscope.agent import BudgetModelPlanner
    class Client:
        def call(self, messages, max_tokens):
            return {'choices':[{'message':{'content':'{"tool":"finish","rationale":"No more checks"}'}}]}
    action = BudgetModelPlanner(Client())({'task':'sample', 'steps':0, 'budget':1, 'evidence':[]})
    assert action.tool == 'finish'


def test_model_cannot_execute_without_explicit_container(repo):
    from patchscope.agent import Action
    def planner(state):
        return Action(tool='test', cases=[{'args':[10,20],'expected':8}])
    graph = build_graph(RepositoryIndex(repo), planner)
    result = graph.invoke({'task':'test', 'candidate':'def f(a,b): return a', 'steps':0,
                           'budget':1, 'evidence':[]})
    assert result['verdict']=='insufficient_evidence'
    assert result['evidence'][0]['status']=='error'


def test_behavioral_runner_rejects_invalid_cases():
    from patchscope.checks import behavioral_check
    with pytest.raises(ValueError):
        behavioral_check('def f(): pass','f; print(1)',[], 'python@sha256:abc')
    with pytest.raises(ValueError):
        behavioral_check('def f(): pass','f',[{'args':'bad','expected':1}], 'python@sha256:abc')


def test_generated_failure_is_advisory_not_automatic_rejection(repo, monkeypatch):
    from patchscope.agent import Action
    import patchscope.checks
    monkeypatch.setattr(patchscope.checks, 'behavioral_check',
                        lambda *a: {'check':'generated_cases','status':'fail'})
    graph = build_graph(RepositoryIndex(repo), lambda s: Action(tool='test',cases=[{'args':[],'expected':0}]),
                        image='python@sha256:abc')
    result = graph.invoke({'task':'test', 'candidate':'def f(): return 1', 'steps':0,'budget':1,'evidence':[]})
    assert result['verdict']=='review_required'


def test_promotion_gate_blocks_regression_and_small_samples():
    from patchscope.evolution import promotion_gate
    base={'wrong_count':6,'correct_count':6,'detected':6,'false_rejections':3}
    candidate={**base,'false_rejections':4}
    gate=promotion_gate(base,candidate)
    assert not gate['promoted']
    assert set(gate['reasons'])=={'insufficient_evaluation_sample','false_rejection_regression','no_detection_gain'}

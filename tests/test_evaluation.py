import pytest
from patchscope.evaluation import score, validate_repository_split


def test_error_remains_in_denominator():
    labels = [{'id': 'a', 'correct': False}, {'id': 'b', 'correct': False}, {'id': 'c', 'correct': True}]
    outputs = [{'id': 'a', 'verdict': 'reject'}, {'id': 'b', 'verdict': 'error'},
               {'id': 'c', 'verdict': 'insufficient_evidence'}]
    result = score(labels, outputs)
    assert result['detection_rate'] == .5
    assert result['false_rejection_wilson95'][1] > 0
    assert result['verdict_counts']['error'] == 1


def test_missing_and_duplicate_outputs_rejected():
    labels = [{'id': 'a', 'correct': True}]
    with pytest.raises(ValueError):
        score(labels, [])
    with pytest.raises(ValueError):
        score(labels, [{'id': 'a', 'verdict': 'reject'}] * 2)


def test_empty_class_is_not_zero_error_rate():
    report = score([{'id': 'a', 'correct': False}], [{'id': 'a', 'verdict': 'error'}])
    assert report['false_rejection_rate'] is None
    assert report['false_rejection_wilson95'] is None


def test_repository_split_leakage():
    with pytest.raises(ValueError):
        validate_repository_split([{'id': 'a', 'repository': 'repo'}], [{'id': 'b', 'repository': 'repo'}])
    validate_repository_split([{'id': 'a', 'repository': 'one'}], [{'id': 'b', 'repository': 'two'}])

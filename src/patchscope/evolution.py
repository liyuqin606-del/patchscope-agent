"""Harness policy selection on development records with immutable audit artifacts.

This is first-order harness tuning, not evidence of recursive self-improvement.
Final evaluation must use untouched repository-disjoint records after selection.
"""
from dataclasses import dataclass, asdict
import hashlib
import json


@dataclass(frozen=True)
class Policy:
    name: str
    checks: tuple[str, ...]


def evaluate(policy: Policy, rows: list[dict]) -> dict:
    wrong = [r for r in rows if not r['correct']]
    correct = [r for r in rows if r['correct']]
    if not wrong or not correct:
        raise ValueError('Both correct and incorrect patches are required')
    def rejects(row):
        # Missing/error/timeout checks provide no evidence of patch incorrectness.
        return any(row['checks'].get(c) == 'fail' for c in policy.checks)
    detected = sum(rejects(r) for r in wrong)
    false_rejections = sum(rejects(r) for r in correct)
    return {'wrong_count': len(wrong), 'correct_count': len(correct),
            'detected': detected, 'false_rejections': false_rejections,
            'detection_rate': detected / len(wrong), 'false_rejection_rate': false_rejections / len(correct),
            'check_budget': len(policy.checks),
            'abstentions': sum(not rejects(r) for r in rows)}


def select(policies: list[Policy], development: list[dict], baseline: Policy, max_checks: int = 2) -> dict:
    if any(r['split'] != 'development' for r in development):
        raise ValueError('Selection may consume development records only')
    base = evaluate(baseline, development)
    eligible = []
    for p in policies:
        m = evaluate(p, development)
        if len(p.checks) <= max_checks and m['false_rejections'] <= base['false_rejections']:
            eligible.append((m['detected'], -len(p.checks), p.name, p, m))
    if not eligible:
        raise ValueError('No eligible policy')
    _, _, _, winner, metrics = max(eligible, key=lambda x: x[:3])
    promoted = metrics['detected'] > base['detected']
    chosen = winner if promoted else baseline
    return {'policy': asdict(chosen), 'promoted': promoted,
            'development_metrics': evaluate(chosen, development),
            'baseline_metrics': base,
            'development_sha256': hashlib.sha256(json.dumps(development, sort_keys=True).encode()).hexdigest(),
            'claim': 'Development policy selection only; no held-out or recursive improvement claim.'}


def promotion_gate(baseline: dict, candidate: dict, min_per_class: int = 30) -> dict:
    """Block promotion on small samples, false-rejection regression or no gain.

    These are operational minimum requirements, not a significance test or a
    substitute for paired, repository-clustered inference.
    """
    reasons=[]
    if any(baseline[k] != candidate[k] for k in ('wrong_count','correct_count')):
        reasons.append('unmatched_denominators')
    if min(candidate['wrong_count'],candidate['correct_count']) < min_per_class:
        reasons.append('insufficient_evaluation_sample')
    if candidate['false_rejections'] > baseline['false_rejections']:
        reasons.append('false_rejection_regression')
    if candidate['detected'] <= baseline['detected']:
        reasons.append('no_detection_gain')
    return {'promoted':not reasons,'reasons':reasons,'min_per_class':min_per_class,
            'scope':'Operational gate only; not a statistical superiority claim.'}

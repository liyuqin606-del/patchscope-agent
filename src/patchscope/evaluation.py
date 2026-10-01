"""Independent scorer. Labels belong here, never in an agent's task payload.

Pass observations separately from frozen labels. Require exact coverage so failed
or missing runs cannot quietly disappear from the denominator.
"""
from collections import Counter
from math import sqrt


VERDICTS = {'reject', 'insufficient_evidence', 'accept', 'error', 'review_required'}


def wilson(successes: int, total: int) -> list[float] | None:
    """95% Wilson interval for a descriptive binomial proportion.

    Not a repository-clustered interval or evidence of independent tasks.
    """
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    divisor = 1 + z * z / total
    center = (p + z * z / (2 * total)) / divisor
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / divisor
    return [max(0.0, center - half), min(1.0, center + half)]


def score(labels: list[dict], observations: list[dict]) -> dict:
    truth = {row['id']: row for row in labels}
    outputs = {row['id']: row for row in observations}
    if len(truth) != len(labels) or len(outputs) != len(observations):
        raise ValueError('Duplicate task IDs')
    if set(truth) != set(outputs):
        raise ValueError('Exact coverage required: retain missing runs as explicit errors')
    if any(type(row['correct']) is not bool for row in labels):
        raise ValueError('Correctness labels must be booleans')
    if any(row['verdict'] not in VERDICTS for row in observations):
        raise ValueError('Unknown verdict')
    correct = sum(row['correct'] for row in labels)
    wrong = len(labels) - correct
    detected = sum(not truth[k]['correct'] and v['verdict'] == 'reject' for k, v in outputs.items())
    false_rejections = sum(truth[k]['correct'] and v['verdict'] == 'reject' for k, v in outputs.items())
    return {'count': len(labels), 'correct_count': correct, 'wrong_count': wrong,
            'detected': detected, 'false_rejections': false_rejections,
            'detection_rate': detected / wrong if wrong else None,
            'false_rejection_rate': false_rejections / correct if correct else None,
            'detection_wilson95': wilson(detected, wrong),
            'false_rejection_wilson95': wilson(false_rejections, correct),
            'verdict_counts': dict(Counter(row['verdict'] for row in observations)),
            'interval_scope': 'Descriptive binomial intervals; not repository-clustered inference.'}


def validate_repository_split(development: list[dict], heldout: list[dict]) -> None:
    dev = {row['repository'] for row in development}
    test = {row['repository'] for row in heldout}
    if dev & test:
        raise ValueError('Repository leakage across development and held-out sets')
    if {row['id'] for row in development} & {row['id'] for row in heldout}:
        raise ValueError('Task leakage across splits')

"""Strict JSON test schema; tolerate a single full-response Markdown fence."""
import json
import re


def parse_cases(content: str) -> list[dict]:
    text = content.strip()
    match = re.fullmatch(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        text = match.group(1)
    cases = json.loads(text)['cases']
    if not isinstance(cases, list) or not 3 <= len(cases) <= 6:
        raise ValueError('Expected three to six cases')
    if not all(isinstance(c, dict) and isinstance(c.get('args'), list) and 'expected' in c for c in cases):
        raise ValueError('Invalid case schema')
    json.dumps(cases, allow_nan=False)
    return cases

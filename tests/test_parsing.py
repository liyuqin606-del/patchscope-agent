import json
import pytest
from patchscope.parsing import parse_cases


def test_only_full_json_fence_is_tolerated():
    payload=json.dumps({'cases':[{'args':[x],'expected':x} for x in range(3)]})
    assert parse_cases(payload)==parse_cases('```json\n'+payload+'\n```')
    with pytest.raises(ValueError):
        parse_cases('Explanation: '+payload)
    with pytest.raises(ValueError):
        parse_cases(payload[:-5])


def test_case_schema_is_not_relaxed():
    with pytest.raises(ValueError):
        parse_cases('{"cases":[]}')
    with pytest.raises(ValueError):
        parse_cases('{"cases":[null,null,null]}')

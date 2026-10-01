"""Fetch the pinned MIT-licensed public execution-pilot inputs."""
from pathlib import Path
import hashlib
import urllib.request

root=Path(__file__).resolve().parents[1]
commit='6d43fb980f9fee3c892a914eda09951f772ad10d'
url=f'https://raw.githubusercontent.com/openai/human-eval/{commit}/data/HumanEval.jsonl.gz'
(root/'data').mkdir(exist_ok=True)
data=urllib.request.urlopen(url,timeout=30).read()
(root/'data/HumanEval.jsonl.gz').write_bytes(data)
print('HumanEval',commit,hashlib.sha256(data).hexdigest())

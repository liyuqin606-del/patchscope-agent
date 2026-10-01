"""OpenAI-compatible client with pre-request cost reservations and no retries.

Reservations survive errors. One process owns the ledger at a time; an exclusive
lock serializes requests and avoids races. Official list-price estimates are not
account billing receipts. Reserve all input as UTF-8 bytes plus framing overhead,
which deliberately overestimates ordinary text tokenization.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request


class BudgetClient:
    def __init__(self, env: Path, ledger: Path, ceiling: float = 15.0):
        config = dict(line.split('=', 1) for line in env.read_text().splitlines() if '=' in line)
        self.key = config['OPENAI_API_KEY']
        self.base = config['OPENAI_BASE_URL'].rstrip('/')
        self.model = 'qwen3-coder-flash'
        self.ledger = ledger
        # User limit is 18 CNY; application limit reserves a 3 CNY margin.
        if not 0 < ceiling <= 15:
            raise ValueError('Application ceiling must be at most 15 CNY')
        self.ceiling = ceiling

    def call(self, messages: list[dict], max_tokens: int = 1200) -> dict:
        if not 1 <= max_tokens <= 4096:
            raise ValueError('Output token cap out of range')
        payload = {'model': self.model, 'messages': messages, 'temperature': 0,
                   'max_tokens': max_tokens, 'stream': False}
        data = json.dumps(payload).encode()
        upper_input = len(data) + 256
        if upper_input > 30_000:
            raise ValueError('Prompt exceeds the verified <=32K price tier')
        reserve = (upper_input + 4 * max_tokens) / 1_000_000
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            records = [json.loads(s) for s in self.ledger.read_text().splitlines()] if self.ledger.exists() else []
            if sum(r['reserved_cny'] for r in records) + reserve > self.ceiling:
                raise RuntimeError('Experiment budget exhausted')
            record = {'index': len(records), 'model': self.model, 'reserved_cny': reserve,
                      'request_sha256': hashlib.sha256(data).hexdigest(), 'status': 'pending'}
            records.append(record)
            self._save(records)
            start = time.monotonic()
            request = urllib.request.Request(self.base + '/chat/completions', data=data,
                headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    result = json.load(response)
                usage = result.get('usage', {})
                record.update(status='success', usage=usage,
                    estimated_cny=(usage.get('prompt_tokens', upper_input) +
                                   4 * usage.get('completion_tokens', max_tokens)) / 1_000_000)
                return result
            except Exception as exc:
                record.update(status='error', error_type=type(exc).__name__)
                raise RuntimeError('Provider request failed; reservation retained') from None
            finally:
                record['seconds'] = time.monotonic() - start
                self._save(records)

    def _save(self, records):
        temporary = self.ledger.with_suffix('.tmp')
        temporary.write_text(''.join(json.dumps(r) + '\n' for r in records))
        os.replace(temporary, self.ledger)

"""Local hybrid retrieval. Source text is evidence, never agent instructions.

Word TF-IDF captures identifiers; character n-grams tolerate naming variants.
Reciprocal rank fusion combines both without calibrating incompatible scores.
No model download, external service, or repository upload is required.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass(frozen=True)
class Chunk:
    path: str
    start: int
    end: int
    text: str
    sha256: str


class RepositoryIndex:
    def __init__(self, root: Path, max_bytes: int = 1_000_000):
        self.root = root.resolve()
        self.chunks = []
        total = 0
        for path in sorted(root.rglob('*.py')):
            relative = path.relative_to(root)
            if any(part.startswith('.') or part in {'node_modules', '__pycache__'} for part in relative.parts):
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(self.root):
                continue
            if path.stat().st_size > 100_000:
                continue
            data = path.read_bytes()
            total += len(data)
            if total > max_bytes:
                raise ValueError('Repository exceeds indexing budget')
            lines = data.decode('utf-8', errors='replace').splitlines()
            for start in range(0, len(lines), 32):
                text = '\n'.join(lines[start:start + 40])
                self.chunks.append(Chunk(str(relative), start + 1, min(start + 40, len(lines)), text,
                                         hashlib.sha256(data).hexdigest()))
        self.vectorizers = [TfidfVectorizer(token_pattern=r'(?u)\b\w+\b'),
                            TfidfVectorizer(analyzer='char', ngram_range=(3, 5))]
        corpus = [c.text for c in self.chunks]
        self.matrices = []
        if corpus:
            for vectorizer in self.vectorizers:
                try:
                    self.matrices.append(vectorizer.fit_transform(corpus))
                except ValueError:
                    self.matrices.append(None)

    def search(self, query: str, k: int = 4) -> list[dict]:
        if not self.chunks:
            return []
        scores = np.zeros(len(self.chunks))
        for vectorizer, matrix in zip(self.vectorizers, self.matrices):
            if matrix is None:
                continue
            similarities = (matrix @ vectorizer.transform([query]).T).toarray().ravel()
            ranked = sorted(range(len(scores)), key=lambda i: (-similarities[i], i))
            for rank, idx in enumerate(ranked):
                if similarities[idx] > 0:
                    scores[idx] += 1 / (60 + rank + 1)
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
        return [{**asdict(self.chunks[i]), 'score': float(scores[i])}
                for i in order[:k] if scores[i] > 0]

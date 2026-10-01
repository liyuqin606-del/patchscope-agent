"""Build an allowlisted, credential-free source/evidence bundle and SHA256 manifest."""
from pathlib import Path
import hashlib
import json
import tarfile

root=Path(__file__).resolve().parents[1]
files=[]
for folder in ['src','tests','scripts','docs','reports','licenses','examples','.github']:
    files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.lock','.tmp'}]
files += [root/p for p in ['README.md','pyproject.toml','uv.lock','.gitignore']]
files=sorted(files)
secret=''
if (root/'.env').exists():
    secret=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if '=' in line).get('OPENAI_API_KEY','')
for path in files:
    if (path.suffix in {'.db','.lock','.tmp'} and path.name != 'uv.lock') or path.name.startswith('.env'):
        raise ValueError('Disallowed release path')
    if secret and secret.encode() in path.read_bytes():
        raise ValueError('Credential detected; release aborted')
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
dist=root/'dist';dist.mkdir(exist_ok=True)
(dist/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(dist/'patchscope-source-evidence.tar.gz','w:gz') as archive:
    for path in files:
        archive.add(path,arcname='patchscope/'+str(path.relative_to(root)))
    archive.add(dist/'manifest.json',arcname='patchscope/MANIFEST.json')
print(f'Bundled {len(files)} allowlisted files; credential scan passed.')

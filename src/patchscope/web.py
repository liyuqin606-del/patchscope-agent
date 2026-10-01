"""Local read-only evidence dashboard. No API keys or arbitrary paths are exposed."""
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse


def create_app(reports: Path) -> FastAPI:
    app = FastAPI(title='PatchScope Evidence Viewer')
    allowed = {'development':'adaptive-comparison.json', 'transfer':'task-transfer-comparison.json'}

    @app.get('/', response_class=HTMLResponse)
    def home():
        return Path(__file__).with_name('dashboard.html').read_text()

    @app.get('/api/experiments/{name}')
    def experiment(name: str):
        if name not in allowed:
            raise HTTPException(404, 'Unknown experiment')
        path = reports / allowed[name]
        if not path.exists():
            raise HTTPException(404, 'Experiment not available yet')
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            raise HTTPException(503, 'Report update in progress; refresh shortly')

    @app.get('/api/cost')
    def cost():
        path = reports/'api-ledger.jsonl'
        rows = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
        return {'requests':len(rows), 'estimated_cny':sum(r.get('estimated_cny',0) for r in rows),
                'reserved_cny':sum(r['reserved_cny'] for r in rows),'ceiling_cny':15,
                'label':'List-price estimate; not account billing'}

    @app.get('/health')
    def health():
        return {'status':'ok','read_only':True}

    return app


def main():
    import argparse
    import uvicorn
    p=argparse.ArgumentParser()
    p.add_argument('--reports',type=Path,default=Path('reports'))
    p.add_argument('--port',type=int,default=8766)
    args=p.parse_args()
    uvicorn.run(create_app(args.reports.resolve()),host='127.0.0.1',port=args.port)


if __name__=='__main__': main()

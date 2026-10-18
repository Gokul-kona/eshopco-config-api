# eShopCo Effective Configuration API

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/effective-config` or test overrides:
`http://127.0.0.1:8000/effective-config?set=port%3D9000&set=debug%3Dtrue`

## Deploy
Push these files to a GitHub repository, then create a Render Web Service from that repository. Render can detect `render.yaml`; otherwise use:
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Submit the deployed service URL ending in `/effective-config`.

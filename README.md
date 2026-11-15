# Supply Chain Control Center

A full-stack operations console for shipment visibility, inventory risk, and exception triage. It includes a FastAPI REST service, SQLite persistence with event history, an interactive web console, seeded demo records, Docker deployment, and an OpenAPI contract.

## Operations features
- Shipment lifecycle with validated state transitions and immutable status events.
- Late-arrival detection against expected arrival timestamps.
- Inventory reorder alerts and safe stock adjustments.
- Cross-domain dashboard KPIs, filters, and manual shipment intake.
- Persistent local SQLite storage; no third-party service or API key required.

## Start locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn supplychain.main:app --reload
```
Open `http://127.0.0.1:8000`. API docs: `/docs`. Database path defaults to `data/control_center.sqlite3`; override with `SUPPLYCHAIN_DB`.

## Docker
`docker compose up --build` exposes the app at `http://localhost:8005`. See [architecture](docs/architecture.md). MIT license.

## Demo limitations
The seeded mode is a local demonstration. Put the service behind an authenticated gateway and configure backups, retention, and role-based authorization before using it for real operations.

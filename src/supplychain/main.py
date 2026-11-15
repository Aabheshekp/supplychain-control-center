from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
from .database import connect, initialize
from .schemas import InventoryCreate, ShipmentCreate, StatusUpdate, StockAdjustment
from .service import adjust_stock, create_shipment, rows, shipment_summary, update_status

app=FastAPI(title="Supply Chain Control Center", version="1.0.0")
STATIC=Path(__file__).resolve().parents[2]/"web"/"static"
app.mount("/static",StaticFiles(directory=STATIC),name="static")
@app.on_event("startup")
def startup(): initialize()

@app.get("/", include_in_schema=False)
def home(): return FileResponse(Path(__file__).resolve().parents[2]/"web"/"index.html")

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/api/v1/summary")
def summary(): return shipment_summary()

@app.get("/api/v1/shipments")
def shipments(status: str|None=None, q: str|None=Query(default=None,max_length=100)):
    sql="SELECT *, CASE WHEN status!='delivered' AND datetime(expected_arrival)<datetime('now') THEN 1 ELSE 0 END AS is_late FROM shipments"
    clauses=[]; args=[]
    if status: clauses.append("status=?"); args.append(status)
    if q: clauses.append("(reference LIKE ? OR origin LIKE ? OR destination LIKE ?)"); args.extend([f"%{q}%"]*3)
    if clauses: sql += " WHERE "+" AND ".join(clauses)
    return rows(sql+" ORDER BY expected_arrival",args)

@app.post("/api/v1/shipments",status_code=201)
def add_shipment(body: ShipmentCreate):
    try: return create_shipment(body)
    except sqlite3.IntegrityError as exc: raise HTTPException(status_code=409,detail="Reference already exists") from exc

@app.patch("/api/v1/shipments/{shipment_id}/status")
def change_status(shipment_id: int, body: StatusUpdate):
    result,error=update_status(shipment_id,body.status,body.note)
    if error: raise HTTPException(status_code=404 if error.endswith("not found") else 409,detail=error)
    return result

@app.get("/api/v1/shipments/{shipment_id}/events")
def shipment_events(shipment_id: int):
    return rows("SELECT * FROM shipment_events WHERE shipment_id=? ORDER BY created_at,id",(shipment_id,))

@app.get("/api/v1/inventory")
def inventory(): return rows("SELECT *,on_hand<=reorder_point AS reorder_alert FROM inventory ORDER BY on_hand-reorder_point")

@app.post("/api/v1/inventory",status_code=201)
def add_inventory(body: InventoryCreate):
    try:
        with connect() as con:
            con.execute("INSERT INTO inventory(sku,description,on_hand,reorder_point) VALUES(?,?,?,?)",(body.sku,body.description,body.on_hand,body.reorder_point))
        return {"sku":body.sku,"created":True}
    except sqlite3.IntegrityError as exc: raise HTTPException(status_code=409,detail="SKU already exists") from exc

@app.post("/api/v1/inventory/{sku}/adjust")
def stock_adjustment(sku: str, body: StockAdjustment):
    result,error=adjust_stock(sku,body.delta,body.reason)
    if error: raise HTTPException(status_code=404 if error=="SKU not found" else 409,detail=error)
    return result

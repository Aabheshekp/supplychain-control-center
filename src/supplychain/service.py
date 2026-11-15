from datetime import timezone
import sqlite3
from .database import connect

ALLOWED = {"planned": {"in_transit", "exception"}, "in_transit": {"delivered", "exception"}, "exception": {"planned", "in_transit", "delivered"}, "delivered": set()}

def rows(sql, params=()):
    with connect() as con: return [dict(r) for r in con.execute(sql, params).fetchall()]

def shipment_summary():
    with connect() as con:
        total=con.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
        statuses={r[0]:r[1] for r in con.execute("SELECT status,COUNT(*) FROM shipments GROUP BY status")}
        late=con.execute("SELECT COUNT(*) FROM shipments WHERE status NOT IN ('delivered') AND expected_arrival < datetime('now')").fetchone()[0]
        low=con.execute("SELECT COUNT(*) FROM inventory WHERE on_hand <= reorder_point").fetchone()[0]
    return {"shipments":total,"by_status":statuses,"late_shipments":late,"low_stock_skus":low}

def create_shipment(data):
    arrival=data.expected_arrival
    if arrival.tzinfo is None: arrival=arrival.replace(tzinfo=timezone.utc)
    arrival=arrival.astimezone(timezone.utc).replace(tzinfo=None).isoformat(sep=" ",timespec="seconds")
    with connect() as con:
        cur=con.execute("INSERT INTO shipments(reference,origin,destination,carrier,expected_arrival) VALUES(?,?,?,?,?)", (data.reference,data.origin,data.destination,data.carrier,arrival))
        sid=cur.lastrowid
        con.execute("INSERT INTO shipment_events(shipment_id,new_status,note) VALUES(?,?,?)", (sid,"planned","Shipment created"))
        return dict(con.execute("SELECT * FROM shipments WHERE id=?",(sid,)).fetchone())

def update_status(shipment_id, status, note):
    with connect() as con:
        row=con.execute("SELECT * FROM shipments WHERE id=?",(shipment_id,)).fetchone()
        if row is None: return None, "Shipment not found"
        old=row["status"]
        if status == old: return dict(row), None
        if status not in ALLOWED[old]: return None, f"Cannot transition shipment from {old} to {status}"
        con.execute("UPDATE shipments SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(status,shipment_id))
        con.execute("INSERT INTO shipment_events(shipment_id,old_status,new_status,note) VALUES(?,?,?,?)",(shipment_id,old,status,note))
        return dict(con.execute("SELECT * FROM shipments WHERE id=?",(shipment_id,)).fetchone()), None

def adjust_stock(sku, delta, reason):
    with connect() as con:
        row=con.execute("SELECT * FROM inventory WHERE sku=?",(sku,)).fetchone()
        if row is None: return None, "SKU not found"
        new=row["on_hand"]+delta
        if new < 0: return None, "Adjustment would make stock negative"
        con.execute("UPDATE inventory SET on_hand=?,updated_at=CURRENT_TIMESTAMP WHERE sku=?",(new,sku))
        return dict(con.execute("SELECT * FROM inventory WHERE sku=?",(sku,)).fetchone()) | {"adjustment":delta,"reason":reason}, None

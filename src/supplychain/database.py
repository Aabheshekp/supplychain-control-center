from pathlib import Path
import os
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("SUPPLYCHAIN_DB", ROOT / "data" / "control_center.sqlite3"))

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def initialize():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS shipments(
          id INTEGER PRIMARY KEY AUTOINCREMENT, reference TEXT NOT NULL UNIQUE,
          origin TEXT NOT NULL, destination TEXT NOT NULL, carrier TEXT NOT NULL,
          expected_arrival TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'planned',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shipment_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, shipment_id INTEGER NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
          old_status TEXT, new_status TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS inventory(
          sku TEXT PRIMARY KEY, description TEXT NOT NULL, on_hand INTEGER NOT NULL CHECK(on_hand >= 0),
          reorder_point INTEGER NOT NULL CHECK(reorder_point >= 0), updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_shipments_status_eta ON shipments(status, expected_arrival);
        CREATE INDEX IF NOT EXISTS idx_events_shipment ON shipment_events(shipment_id, created_at);
        """)
        if con.execute("SELECT COUNT(*) FROM shipments").fetchone()[0] == 0:
            rows = [("SHP-1001", "Osaka", "Singapore", "Nippon Freight", "+2 days", "in_transit"),
                    ("SHP-1002", "Berlin", "Mumbai", "NorthStar Cargo", "-3 hours", "in_transit"),
                    ("SHP-1003", "Austin", "Toronto", "Maple Logistics", "+1 day", "planned"),
                    ("SHP-1004", "Seoul", "Dubai", "BlueWave", "-1 day", "exception")]
            for ref, origin, dest, carrier, offset, status in rows:
                con.execute("INSERT INTO shipments(reference,origin,destination,carrier,expected_arrival,status) VALUES(?,?,?,?,datetime('now',?),?)", (ref,origin,dest,carrier,offset,status))
                sid=con.execute("SELECT last_insert_rowid()").fetchone()[0]
                con.execute("INSERT INTO shipment_events(shipment_id,old_status,new_status,note) VALUES(?,NULL,?,?)", (sid,status,"Seeded demo record"))
        if con.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
            con.executemany("INSERT INTO inventory(sku,description,on_hand,reorder_point) VALUES(?,?,?,?)", [("PKG-01","Protective packaging",420,150),("SEN-04","Temperature sensor",28,40),("VAL-22","Control valve",73,25),("FLT-17","Replacement filter",12,30)])

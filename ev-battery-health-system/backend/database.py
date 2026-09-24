import sqlite3
import json
import os
from typing import List, Dict, Any

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/battery_records.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "battery_records.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            vehicle_id TEXT,
            vehicle_type TEXT,
            soc_pct REAL,
            soh_pct REAL,
            pack_voltage REAL,
            current_a REAL,
            power_kw REAL,
            pack_temp_c REAL,
            thermal_status TEXT,
            charging_status TEXT,
            cell_delta_v_mv REAL,
            speed_kmh REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            vehicle_id TEXT,
            severity TEXT,
            event_type TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_telemetry(data: Dict[str, Any]):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry_logs (
                timestamp, vehicle_id, vehicle_type, soc_pct, soh_pct,
                pack_voltage, current_a, power_kw, pack_temp_c,
                thermal_status, charging_status, cell_delta_v_mv, speed_kmh
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("timestamp"),
            data.get("vehicle_id"),
            data.get("vehicle_type"),
            data.get("soc_pct"),
            data.get("soh_pct"),
            data.get("pack_voltage"),
            data.get("current_a"),
            data.get("power_kw"),
            data.get("pack_temp_c"),
            data.get("thermal_status"),
            data.get("charging_status"),
            data.get("cell_delta_v_mv"),
            data.get("speed_kmh")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

def get_telemetry_history(vehicle_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM telemetry_logs 
            WHERE vehicle_id = ? 
            ORDER BY id DESC LIMIT ?
        """, (vehicle_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return []

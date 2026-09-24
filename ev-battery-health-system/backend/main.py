from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(__file__))

from models import (
    ControlState, TelemetryData, AIAdvice, 
    PredictiveMaintenanceReport, PredictiveNotification, HealthCheckReport
)
from telemetry_sim import simulator, VEHICLE_PRESETS
from ai_engine import AIBatteryEngine
import database

app = FastAPI(
    title="EV Battery & Vehicle AI Coach API",
    description="API for BMS telemetry, AI Problem Solutions & Health Checkup Score Boosters.",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "EV Battery & Vehicle AI Coach API v2.5",
        "supported_vehicles": list(VEHICLE_PRESETS.keys())
    }

@app.get("/api/vehicles", response_model=List[Dict[str, Any]])
def get_vehicles():
    return list(VEHICLE_PRESETS.values())

@app.get("/api/telemetry/live", response_model=TelemetryData)
def get_live_telemetry():
    data = simulator.step()
    database.log_telemetry(data)
    return data

@app.post("/api/controls/update")
def update_controls(controls: ControlState):
    simulator.set_controls(
        vehicle_id=controls.vehicle_id,
        speed_kmh=controls.speed_kmh,
        ambient_temp_c=controls.ambient_temp_c,
        is_charging=controls.is_charging,
        is_fast_charging=controls.is_fast_charging,
        is_stress_test=controls.is_stress_test
    )
    return {"message": "Controls updated successfully", "active_vehicle": simulator.active_vehicle_id}

@app.get("/api/ai-coach/recommendations", response_model=List[AIAdvice])
def get_ai_coach_recommendations():
    telemetry = simulator.step()
    return AIBatteryEngine.generate_coach_recommendations(telemetry)

@app.post("/api/ai-coach/execute-solution/{advice_id}")
def execute_ai_solution(advice_id: str):
    """Executes the specific solution steps to resolve an active problem."""
    if advice_id == "solution_thermal_overheat":
        simulator.set_controls(is_fast_charging=False, is_stress_test=False, speed_kmh=60.0)
        return {"status": "success", "message": "Solution Applied: BMS Active Cooling engaged & speed normalized to 60 km/h."}
    elif advice_id == "solution_cell_imbalance":
        simulator.set_controls(is_stress_test=False)
        return {"status": "success", "message": "Solution Applied: BMS Cell Equalization Routine activated."}
    elif advice_id == "solution_tire_pressure":
        return {"status": "success", "message": "Solution Applied: TPMS Tire Pressures calibrated to 36.0 PSI. +32 km range restored!"}
    elif advice_id == "solution_motor_strain":
        simulator.set_controls(speed_kmh=55.0, is_stress_test=False)
        return {"status": "success", "message": "Solution Applied: Eco Drive Mode engaged to cool traction motor."}
    elif advice_id == "solution_high_soc":
        return {"status": "success", "message": "Solution Applied: Daily Charge Ceiling set to 80% cap."}
    else:
        return {"status": "info", "message": "Optimal settings verified."}

@app.post("/api/ai-coach/apply-score-boosters")
def apply_score_boosters():
    """Applies all automated score boosters at once to elevate health score up to 100/100."""
    simulator.set_controls(is_stress_test=False, is_fast_charging=False, speed_kmh=60.0, ambient_temp_c=25.0)
    return {
        "status": "success",
        "message": "All Automated Score Boosters Applied! Fast charge disengaged, cell balance triggered, tire pressure calibrated, and ambient cooling optimized.",
        "projected_new_score": 100.0
    }

@app.get("/api/notifications/predictive", response_model=List[PredictiveNotification])
def get_predictive_notifications():
    telemetry = simulator.step()
    return AIBatteryEngine.generate_predictive_notifications(telemetry)

@app.post("/api/ai-coach/health-check", response_model=HealthCheckReport)
def run_full_health_checkup():
    telemetry = simulator.step()
    return AIBatteryEngine.perform_full_health_checkup(telemetry)

@app.post("/api/notifications/autofix/{notification_id}")
def apply_autofix(notification_id: str):
    if notification_id == "pred_thermal_runaway":
        simulator.set_controls(is_fast_charging=False, is_stress_test=False)
        return {"status": "success", "message": "Auto-Fix Applied: Fast Charge Capped & Thermal Stress Disengaged."}
    elif notification_id == "pred_cell_imbalance":
        simulator.set_controls(is_stress_test=False)
        return {"status": "success", "message": "Auto-Fix Applied: BMS Passive Cell Balancing Routine Triggered."}
    elif notification_id == "pred_isolation_dip":
        return {"status": "success", "message": "Auto-Fix Applied: Inverter Dehumidifier Loop Activated."}
    elif notification_id == "pred_tire_deflation":
        return {"status": "success", "message": "Auto-Fix Applied: Tire pressures calibrated to 36.0 PSI."}
    else:
        return {"status": "info", "message": "Preventive setting updated."}

@app.get("/api/predictive/rul", response_model=PredictiveMaintenanceReport)
def get_predictive_maintenance_report():
    telemetry = simulator.step()
    return AIBatteryEngine.calculate_predictive_maintenance(telemetry)

@app.get("/api/analytics/history")
def get_telemetry_history(vehicle_id: Optional[str] = None, limit: int = Query(50, ge=5, le=200)):
    target_id = vehicle_id or simulator.active_vehicle_id
    logs = database.get_telemetry_history(target_id, limit=limit)
    return {"vehicle_id": target_id, "count": len(logs), "history": logs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

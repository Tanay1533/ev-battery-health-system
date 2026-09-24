from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class VehicleProfile(BaseModel):
    id: str
    name: str
    type: str  # "car" or "twowheeler"
    capacity_kwh: float
    nominal_voltage: float
    max_voltage: float
    min_voltage: float
    cell_count: int
    cooling_type: str  # "liquid" or "air"
    rated_range_km: float

class ControlState(BaseModel):
    vehicle_id: str = "car_tesla_model3"
    speed_kmh: float = 65.0
    ambient_temp_c: float = 28.0
    is_charging: bool = False
    is_fast_charging: bool = False
    is_stress_test: bool = False

class CellVoltageMap(BaseModel):
    cell_id: int
    voltage: float
    status: str  # "normal", "warning", "critical"

class TirePressures(BaseModel):
    fl: float
    fr: float
    rl: float
    rr: float

class TelemetryData(BaseModel):
    timestamp: str
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    soc_pct: float
    soh_pct: float
    pack_voltage: float
    current_a: float
    power_kw: float
    estimated_range_km: float
    internal_resistance_mOhm: float
    pack_temp_c: float
    cell_temps_c: List[float]
    bms_temp_c: float
    thermal_status: str
    charging_status: str  # "Discharging", "AC Charging", "DC Fast Charging", "Idle"
    charge_cycles: int
    cell_voltages: List[CellVoltageMap]
    cell_delta_v_mv: float
    speed_kmh: float
    ambient_temp_c: float
    
    tire_pressures_psi: TirePressures
    motor_temp_c: float
    inverter_efficiency_pct: float
    brake_pad_wear_pct: float
    isolation_resistance_mohm: float
    coolant_flow_lmin: float

class AIAdvice(BaseModel):
    id: str
    category: str  # "Battery", "Vehicle", "Driving", "Thermal", "Maintenance"
    priority: str  # "low", "medium", "high", "critical"
    title: str
    message: str
    action_item: str
    solution_steps: List[str]
    impact_score_pts: float
    can_execute_solution: bool

class PredictiveNotification(BaseModel):
    id: str
    severity: str
    category: str
    title: str
    problem_predicted_in: str
    root_cause: str
    preventive_action: str
    can_autofix: bool

class HealthCheckSubsystem(BaseModel):
    name: str
    score: float
    status: str  # "EXCELLENT", "GOOD", "ATTENTION", "CRITICAL"
    summary: str

class ScoreImprovementItem(BaseModel):
    issue: str
    solution: str
    potential_score_gain: float
    can_auto_apply: bool

class HealthCheckReport(BaseModel):
    vehicle_id: str
    timestamp: str
    overall_health_score: float
    health_grade: str  # "A+", "A", "B", "C", "D"
    subsystems: List[HealthCheckSubsystem]
    key_findings: List[str]
    immediate_recommendations: List[str]
    score_improvement_plan: List[ScoreImprovementItem]

class PredictiveMaintenanceReport(BaseModel):
    vehicle_id: str
    soh_pct: float
    estimated_rul_km: float
    estimated_rul_cycles: int
    estimated_months_to_80_soh: float
    cell_imbalance_risk_score: float
    thermal_runaway_risk: str
    degradation_rate_pct_per_10k_km: float
    replacement_advisory: str
    anomalies_detected: List[str]
    capacity_forecast: List[Dict[str, Any]]

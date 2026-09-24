import time
import math
import random
from datetime import datetime
from typing import Dict, Any, List

VEHICLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "car_tesla_model3": {
        "id": "car_tesla_model3",
        "name": "Tesla Model 3 / EV Sedan",
        "type": "car",
        "capacity_kwh": 60.0,
        "nominal_voltage": 350.0,
        "max_voltage": 403.0,
        "min_voltage": 290.0,
        "cell_count": 16,
        "cooling_type": "liquid",
        "rated_range_km": 450.0,
        "base_ir_mOhm": 18.5,
        "base_soh": 94.2,
        "charge_cycles": 340
    },
    "car_leaf": {
        "id": "car_leaf",
        "name": "Compact EV Hatchback",
        "type": "car",
        "capacity_kwh": 40.0,
        "nominal_voltage": 320.0,
        "max_voltage": 360.0,
        "min_voltage": 260.0,
        "cell_count": 16,
        "cooling_type": "air",
        "rated_range_km": 310.0,
        "base_ir_mOhm": 24.0,
        "base_soh": 88.5,
        "charge_cycles": 520
    },
    "scooter_ather450x": {
        "id": "scooter_ather450x",
        "name": "Ather 450X / Gen3 Scooter",
        "type": "twowheeler",
        "capacity_kwh": 3.7,
        "nominal_voltage": 51.1,
        "max_voltage": 58.8,
        "min_voltage": 42.0,
        "cell_count": 14,
        "cooling_type": "air",
        "rated_range_km": 111.0,
        "base_ir_mOhm": 42.0,
        "base_soh": 96.1,
        "charge_cycles": 180
    },
    "scooter_olas1pro": {
        "id": "scooter_olas1pro",
        "name": "Ola S1 Pro / High Performance",
        "type": "twowheeler",
        "capacity_kwh": 4.0,
        "nominal_voltage": 52.0,
        "max_voltage": 59.5,
        "min_voltage": 43.0,
        "cell_count": 14,
        "cooling_type": "air",
        "rated_range_km": 135.0,
        "base_ir_mOhm": 38.0,
        "base_soh": 92.4,
        "charge_cycles": 290
    },
    "scooter_iqube": {
        "id": "scooter_iqube",
        "name": "TVS iQube / City Scooter",
        "type": "twowheeler",
        "capacity_kwh": 3.4,
        "nominal_voltage": 51.0,
        "max_voltage": 58.0,
        "min_voltage": 41.5,
        "cell_count": 14,
        "cooling_type": "air",
        "rated_range_km": 100.0,
        "base_ir_mOhm": 45.0,
        "base_soh": 95.0,
        "charge_cycles": 210
    }
}

class TelemetrySimulator:
    def __init__(self):
        self.active_vehicle_id = "car_tesla_model3"
        self.soc_pct = 72.0
        self.speed_kmh = 60.0
        self.ambient_temp_c = 28.0
        self.is_charging = False
        self.is_fast_charging = False
        self.is_stress_test = False
        self.start_time = time.time()
        self.temp_accumulator = 31.5

    def set_controls(self, vehicle_id: str = None, speed_kmh: float = None, 
                     ambient_temp_c: float = None, is_charging: bool = None, 
                     is_fast_charging: bool = None, is_stress_test: bool = None):
        if vehicle_id and vehicle_id in VEHICLE_PRESETS:
            if vehicle_id != self.active_vehicle_id:
                self.active_vehicle_id = vehicle_id
                self.soc_pct = 75.0
                self.temp_accumulator = ambient_temp_c if ambient_temp_c else 28.0
        if speed_kmh is not None:
            self.speed_kmh = max(0.0, min(180.0, speed_kmh))
        if ambient_temp_c is not None:
            self.ambient_temp_c = max(-10.0, min(50.0, ambient_temp_c))
        if is_charging is not None:
            self.is_charging = is_charging
        if is_fast_charging is not None:
            self.is_fast_charging = is_fast_charging
        if is_stress_test is not None:
            self.is_stress_test = is_stress_test

    def step(self) -> Dict[str, Any]:
        preset = VEHICLE_PRESETS.get(self.active_vehicle_id, VEHICLE_PRESETS["car_tesla_model3"])
        
        # SOC step logic
        dt = 1.0
        if self.is_charging:
            charge_rate = 0.08 if not self.is_fast_charging else 0.35
            self.soc_pct = min(100.0, self.soc_pct + charge_rate * dt)
        else:
            drain_factor = (self.speed_kmh / 60.0) ** 1.3 * 0.015
            if self.is_stress_test:
                drain_factor *= 3.5
            self.soc_pct = max(2.0, self.soc_pct - drain_factor * dt)

        soh = preset["base_soh"]
        if self.is_stress_test:
            soh -= 0.001
        
        v_min, v_max = preset["min_voltage"], preset["max_voltage"]
        ocv = v_min + (v_max - v_min) * (self.soc_pct / 100.0)

        # Current calculation (Amps)
        if self.is_charging:
            charging_status = "DC Fast Charging" if self.is_fast_charging else "AC Charging"
            current_a = -120.0 if (self.is_fast_charging and preset["type"] == "car") else (-40.0 if self.is_fast_charging else -15.0)
        elif self.speed_kmh > 0:
            charging_status = "Discharging"
            base_power_demand_kw = (self.speed_kmh / 100.0) * (50.0 if preset["type"] == "car" else 6.0)
            if self.is_stress_test:
                base_power_demand_kw *= 2.5
            current_a = (base_power_demand_kw * 1000.0) / ocv
        else:
            charging_status = "Idle"
            current_a = 0.5

        power_kw = (ocv * current_a) / 1000.0
        
        # Temperature modeling
        heat_gen = (current_a ** 2) * (preset["base_ir_mOhm"] / 1000.0) * 0.00008
        if self.is_stress_test:
            heat_gen += 0.4
        
        target_temp = self.ambient_temp_c + (heat_gen * 15.0) + (self.speed_kmh * 0.08)
        cooling_power = 0.15 if preset["cooling_type"] == "liquid" else 0.05
        
        self.temp_accumulator += (target_temp - self.temp_accumulator) * cooling_power
        pack_temp = self.temp_accumulator + random.uniform(-0.3, 0.3)

        cell_temps = [
            round(pack_temp + random.uniform(-1.2, 1.5), 1),
            round(pack_temp + random.uniform(-0.8, 1.8) + (3.5 if self.is_stress_test else 0.0), 1),
            round(pack_temp + random.uniform(-1.5, 0.9), 1),
            round(pack_temp + random.uniform(-0.5, 1.2), 1)
        ]
        bms_temp = round(pack_temp + 3.2 + random.uniform(-0.4, 0.4), 1)

        if max(cell_temps) > 52.0 or pack_temp > 50.0:
            thermal_status = "Critical"
        elif max(cell_temps) > 42.0 or pack_temp > 40.0:
            thermal_status = "Warning"
        else:
            thermal_status = "Normal"

        # Cell Voltages
        series_cell_count = 96 if preset["type"] == "car" else 14
        cell_count = preset["cell_count"]
        avg_cell_v = ocv / series_cell_count
        cell_voltages = []
        
        for i in range(1, cell_count + 1):
            drift = 0.0
            if self.is_stress_test and i in [4, 11]:
                drift = -0.18
            v_cell = round(avg_cell_v + random.uniform(-0.012, 0.012) + drift, 3)
            
            c_status = "normal"
            if abs(v_cell - avg_cell_v) > 0.08:
                c_status = "critical"
            elif abs(v_cell - avg_cell_v) > 0.04:
                c_status = "warning"
                
            cell_voltages.append({
                "cell_id": i,
                "voltage": v_cell,
                "status": c_status
            })
        
        volt_list = [c["voltage"] for c in cell_voltages]
        cell_delta_v_mv = round((max(volt_list) - min(volt_list)) * 1000.0, 1)

        # Internal resistance dynamics
        temp_ir_penalty = max(0.0, (25.0 - pack_temp) * 0.4) + max(0.0, (pack_temp - 38.0) * 0.8)
        current_ir = round(preset["base_ir_mOhm"] + temp_ir_penalty + (0.05 * (100 - soh)), 2)

        # Estimated Range
        wh_per_km = 140.0 if preset["type"] == "car" else 30.0
        if self.ambient_temp_c < 10 or self.ambient_temp_c > 38:
            wh_per_km *= 1.15
        usable_kwh = (preset["capacity_kwh"] * (self.soc_pct / 100.0) * (soh / 100.0))
        estimated_range_km = round((usable_kwh * 1000.0) / wh_per_km, 1)

        # Vehicle Diagnostics Simulation
        base_tire_psi = 36.0 if preset["type"] == "car" else 32.0
        rr_drift = -4.5 if self.is_stress_test else 0.0
        tire_pressures_psi = {
            "fl": round(base_tire_psi + random.uniform(-0.4, 0.4), 1),
            "fr": round(base_tire_psi + random.uniform(-0.3, 0.5), 1),
            "rl": round(base_tire_psi + random.uniform(-0.5, 0.2), 1),
            "rr": round(base_tire_psi + rr_drift + random.uniform(-0.4, 0.3), 1)
        }

        motor_temp_c = round(pack_temp + (self.speed_kmh * 0.35) + (18.0 if self.is_stress_test else 5.0), 1)
        inverter_efficiency_pct = round(97.8 - (0.05 * (self.speed_kmh / 10.0)) - (2.5 if self.is_stress_test else 0.0), 1)
        brake_pad_wear_pct = round(18.5 + (preset["charge_cycles"] * 0.02), 1)
        isolation_resistance_mohm = round(480.0 - (50.0 if self.is_stress_test else 0.0) + random.uniform(-5.0, 5.0), 1)
        coolant_flow_lmin = round(8.8 if preset["cooling_type"] == "liquid" else 0.0, 1)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vehicle_id": preset["id"],
            "vehicle_name": preset["name"],
            "vehicle_type": preset["type"],
            "soc_pct": round(self.soc_pct, 1),
            "soh_pct": round(soh, 1),
            "pack_voltage": round(ocv, 1),
            "current_a": round(current_a, 1),
            "power_kw": round(power_kw, 2),
            "estimated_range_km": estimated_range_km,
            "internal_resistance_mOhm": current_ir,
            "pack_temp_c": round(pack_temp, 1),
            "cell_temps_c": cell_temps,
            "bms_temp_c": bms_temp,
            "thermal_status": thermal_status,
            "charging_status": charging_status,
            "charge_cycles": preset["charge_cycles"],
            "cell_voltages": cell_voltages,
            "cell_delta_v_mv": cell_delta_v_mv,
            "speed_kmh": round(self.speed_kmh, 1),
            "ambient_temp_c": round(self.ambient_temp_c, 1),
            
            "tire_pressures_psi": tire_pressures_psi,
            "motor_temp_c": motor_temp_c,
            "inverter_efficiency_pct": inverter_efficiency_pct,
            "brake_pad_wear_pct": brake_pad_wear_pct,
            "isolation_resistance_mohm": isolation_resistance_mohm,
            "coolant_flow_lmin": coolant_flow_lmin
        }

simulator = TelemetrySimulator()

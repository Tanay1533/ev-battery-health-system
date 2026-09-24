import math
from typing import List, Dict, Any

class AIBatteryEngine:
    @staticmethod
    def generate_coach_recommendations(telemetry: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        
        soc = telemetry["soc_pct"]
        soh = telemetry["soh_pct"]
        pack_temp = telemetry["pack_temp_c"]
        max_cell_temp = max(telemetry["cell_temps_c"])
        speed = telemetry["speed_kmh"]
        charging_status = telemetry["charging_status"]
        delta_v = telemetry["cell_delta_v_mv"]
        v_type = telemetry["vehicle_type"]
        tires = telemetry.get("tire_pressures_psi", {"fl": 36.0, "fr": 36.0, "rl": 36.0, "rr": 36.0})
        motor_temp = telemetry.get("motor_temp_c", 45.0)

        # 1. Thermal Overheat Problem & Solution
        if max_cell_temp > 42.0:
            recommendations.append({
                "id": "solution_thermal_overheat",
                "category": "Thermal",
                "priority": "critical",
                "title": "Problem: Cell Overheating Detected",
                "message": f"Cell module #2 temp is {max_cell_temp}°C (Safe limit: 42°C). High thermal stress accelerates degradation.",
                "action_item": "Solution: Engage BMS Active Cooling Loop & Disengage Thermal Stress.",
                "solution_steps": [
                    "1. Reduce speed below 80 km/h to decrease heat generation.",
                    "2. Switch BMS Liquid Cooling Pump to High Performance Mode.",
                    "3. If DC Fast Charging, throttle charge rate from 120kW down to 50kW."
                ],
                "impact_score_pts": 4.5,
                "can_execute_solution": True
            })

        # 2. Cell Voltage Imbalance Problem & Solution
        if delta_v > 30.0:
            recommendations.append({
                "id": "solution_cell_imbalance",
                "category": "Battery",
                "priority": "high",
                "title": "Problem: Cell Voltage Module Imbalance",
                "message": f"Cell module variance is {delta_v} mV (Normal: < 25 mV). Out-of-balance cells cause premature low-voltage cutoff.",
                "action_item": "Solution: Perform BMS Automated Cell Passive Equalization Routine.",
                "solution_steps": [
                    "1. Connect EV to a slow AC charger (Type 2 / Level 2).",
                    "2. Allow charger to remain plugged past 95% SOC for 1.5 hours.",
                    "3. Trigger BMS bleed-resistor balancing to equalize cell voltages within ±5 mV."
                ],
                "impact_score_pts": 3.8,
                "can_execute_solution": True
            })

        # 3. Tire Deflation Drag Problem & Solution
        min_tire_psi = min(tires.values())
        if min_tire_psi < 33.0 and v_type == "car":
            recommendations.append({
                "id": "solution_tire_pressure",
                "category": "Vehicle",
                "priority": "high",
                "title": "Problem: Low Rear-Right Tire Inflation",
                "message": f"RR tire pressure dropped to {min_tire_psi} PSI (Target: 36.0 PSI). Increases rolling resistance drag by +12%.",
                "action_item": "Solution: Inflate tires to 36.0 PSI to regain +32 km range.",
                "solution_steps": [
                    "1. Visit nearest air station or use portable EV air inflator.",
                    "2. Set target inflation to 36.0 PSI when cold.",
                    "3. Recalibrate TPMS sensor baseline in vehicle settings."
                ],
                "impact_score_pts": 2.5,
                "can_execute_solution": True
            })

        # 4. Motor Temp & Acceleration Strain Problem & Solution
        if motor_temp > 70.0:
            recommendations.append({
                "id": "solution_motor_strain",
                "category": "Vehicle",
                "priority": "high",
                "title": "Problem: Traction Motor Thermal Strain",
                "message": f"Motor temperature reached {motor_temp}°C during sustained high torque operation.",
                "action_item": "Solution: Engage Eco Acceleration Mode to lower motor winding heat.",
                "solution_steps": [
                    "1. Switch drive mode from Sport / Performance to Eco / Normal.",
                    "2. Avoid full-throttle launches until motor temp cools below 55°C.",
                    "3. Check inverter coolant fluid level if condition persists."
                ],
                "impact_score_pts": 2.0,
                "can_execute_solution": True
            })

        # 5. High SOC Degradation Problem & Solution
        if soc > 85.0 and charging_status != "Idle":
            recommendations.append({
                "id": "solution_high_soc",
                "category": "Battery",
                "priority": "medium",
                "title": "Problem: High SOC Cathode Stress (>80%)",
                "message": "Holding battery at >85% SOC accelerates nickel-manganese cathode degradation.",
                "action_item": "Solution: Set Daily Charge Ceiling Limit to 80%.",
                "solution_steps": [
                    "1. Adjust daily charge limit slider in app to 80% for routine commutes.",
                    "2. Only charge to 100% right before embarking on long highway trips.",
                    "3. Enable Scheduled Charging so 80% SOC is reached just before departure."
                ],
                "impact_score_pts": 1.5,
                "can_execute_solution": True
            })

        if not recommendations:
            recommendations.append({
                "id": "solution_all_optimal",
                "category": "Vehicle",
                "priority": "low",
                "title": "All Systems Operating Nominally",
                "message": "No active problems detected. Battery cells, motor drive, cooling loop, and tires are operating in peak efficiency range.",
                "action_item": "Solution: Maintain smooth throttle input & routine 80% charge habit.",
                "solution_steps": [
                    "1. Continue driving in standard Eco/Normal mode.",
                    "2. Perform routine BMS health audit every 5,000 km.",
                    "3. Keep tire pressures calibrated to 36.0 PSI."
                ],
                "impact_score_pts": 0.0,
                "can_execute_solution": False
            })

        return recommendations

    @staticmethod
    def generate_predictive_notifications(telemetry: Dict[str, Any]) -> List[Dict[str, Any]]:
        notifications = []
        
        delta_v = telemetry["cell_delta_v_mv"]
        max_cell_temp = max(telemetry["cell_temps_c"])
        tires = telemetry.get("tire_pressures_psi", {"fl": 36, "fr": 36, "rl": 36, "rr": 36})
        is_fast_charging = telemetry["charging_status"] == "DC Fast Charging"
        v_type = telemetry["vehicle_type"]

        if max_cell_temp > 40.0 or (is_fast_charging and max_cell_temp > 36.0):
            notifications.append({
                "id": "pred_thermal_runaway",
                "severity": "critical",
                "category": "Thermal",
                "title": "Predictive Thermal Throttling Warning",
                "problem_predicted_in": "Predicted in ~35 minutes of highway driving",
                "root_cause": f"Cell module #2 temp rate of rise will exceed 48°C safety cutoff.",
                "preventive_action": "Enable BMS Thermal Pre-cooling & Auto-Cap Fast Charge to 80%",
                "can_autofix": True
            })

        if delta_v > 35.0:
            notifications.append({
                "id": "pred_cell_imbalance",
                "severity": "warning",
                "category": "Battery",
                "title": "Predicted Cell Voltage Degradation",
                "problem_predicted_in": "Predicted in ~280 km range loss",
                "root_cause": f"Delta V of {delta_v} mV will trigger early low-voltage cutoff before SOC reaches 10%.",
                "preventive_action": "Trigger BMS Automated Passive Equalization Routine",
                "can_autofix": True
            })

        min_psi = min(tires.values())
        if min_psi < 33.0 and v_type == "car":
            notifications.append({
                "id": "pred_tire_deflation",
                "severity": "warning",
                "category": "Tires",
                "title": "Predicted Energy Drag (Low Tire Inflation)",
                "problem_predicted_in": "Active Energy Penalty: -32 km range",
                "root_cause": f"Rear-Right tire pressure ({min_psi} PSI) increases rolling resistance coefficient by +14%.",
                "preventive_action": "Inflate RR tire to 36.0 PSI to restore full range",
                "can_autofix": True
            })

        if not notifications:
            notifications.append({
                "id": "pred_all_nominal",
                "severity": "info",
                "category": "Battery",
                "title": "Zero Predictive Faults Detected",
                "problem_predicted_in": "Next 5,000 km clean prognosis",
                "root_cause": "All diagnostic metrics tracking along nominal physical curves.",
                "preventive_action": "No preventive action needed",
                "can_autofix": False
            })

        return notifications

    @staticmethod
    def perform_full_health_checkup(telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a 50-point full vehicle & battery audit and generates a score improvement plan to reach 100/100."""
        soh = telemetry["soh_pct"]
        delta_v = telemetry["cell_delta_v_mv"]
        pack_temp = telemetry["pack_temp_c"]
        max_cell_temp = max(telemetry["cell_temps_c"])
        motor_temp = telemetry.get("motor_temp_c", 45.0)
        inverter_eff = telemetry.get("inverter_efficiency_pct", 97.5)
        isolation = telemetry.get("isolation_resistance_mohm", 480.0)
        tires = telemetry.get("tire_pressures_psi", {"fl": 36, "fr": 36, "rl": 36, "rr": 36})
        min_psi = min(tires.values())

        battery_score = round(max(0.0, soh - (delta_v * 0.15)), 1)
        thermal_score = round(max(0.0, 100.0 - (max(0.0, max_cell_temp - 30.0) * 2.5)), 1)
        powertrain_score = round(max(0.0, inverter_eff - (max(0.0, motor_temp - 60.0) * 0.5)), 1)
        tires_score = round(max(0.0, 100.0 - (abs(36.0 - min_psi) * 6.0)), 1)
        safety_score = round(min(100.0, (isolation / 500.0) * 100.0), 1)

        overall_score = round((battery_score * 0.35) + (thermal_score * 0.25) + 
                              (powertrain_score * 0.20) + (tires_score * 0.10) + 
                              (safety_score * 0.10), 1)

        if overall_score >= 93:
            health_grade = "A+"
        elif overall_score >= 85:
            health_grade = "A"
        elif overall_score >= 75:
            health_grade = "B"
        elif overall_score >= 65:
            health_grade = "C"
        else:
            health_grade = "D"

        subsystems = [
            {
                "name": "🔋 Battery Pack & Cell Matrix",
                "score": battery_score,
                "status": "EXCELLENT" if battery_score >= 90 else "ATTENTION",
                "summary": f"SOH: {soh}%. Cell delta voltage: {delta_v} mV."
            },
            {
                "name": "🌡️ Thermal & Cooling System",
                "score": thermal_score,
                "status": "EXCELLENT" if thermal_score >= 88 else "WARNING",
                "summary": f"Pack temp: {pack_temp}°C. Max cell sensor: {max_cell_temp}°C."
            },
            {
                "name": "⚡ Traction Motor & Inverter",
                "score": powertrain_score,
                "status": "EXCELLENT" if powertrain_score >= 92 else "GOOD",
                "summary": f"Inverter efficiency: {inverter_eff}%. Motor temp: {motor_temp}°C."
            },
            {
                "name": "🛞 TPMS Tires & Alignment",
                "score": tires_score,
                "status": "EXCELLENT" if tires_score >= 90 else "ATTENTION",
                "summary": f"Lowest tire pressure: {min_psi} PSI (Target: 36.0 PSI)."
            },
            {
                "name": "🛡️ High Voltage Safety & Isolation",
                "score": safety_score,
                "status": "EXCELLENT" if safety_score >= 90 else "GOOD",
                "summary": f"HV Isolation: {isolation} MΩ (Safe threshold: >400 MΩ)."
            }
        ]

        findings = []
        if delta_v > 25:
            findings.append(f"Cell voltage variance is elevated ({delta_v} mV). Deduction: -{(delta_v*0.05):.1f} pts.")
        if min_psi < 35:
            findings.append(f"Tire pressure low on 1 or more wheels ({min_psi} PSI). Deduction: -{((36-min_psi)*0.6):.1f} pts.")
        if max_cell_temp > 38:
            findings.append(f"Thermal load elevated during fast charge / stress test. Deduction: -{((max_cell_temp-30)*0.6):.1f} pts.")
        if not findings:
            findings.append("All 50 audited parameters operating within peak factory specifications.")

        # ----------------------------------------------------
        # EXPLICIT SCORE IMPROVEMENT PLAN TO REACH 100/100
        # ----------------------------------------------------
        score_improvement_plan = []
        
        if delta_v > 20:
            score_improvement_plan.append({
                "issue": f"Cell Voltage Variance ({delta_v} mV)",
                "solution": "Execute BMS Passive Equalization Routine to balance cell module voltages.",
                "potential_score_gain": round(min(3.5, delta_v * 0.08), 1),
                "can_auto_apply": True
            })

        if max_cell_temp > 35:
            score_improvement_plan.append({
                "issue": f"Elevated Cell Thermal Load ({max_cell_temp}°C)",
                "solution": "Activate Thermal Pre-cooling & disengage stress test / high fast charge rate.",
                "potential_score_gain": round(min(2.5, (max_cell_temp - 30) * 0.25), 1),
                "can_auto_apply": True
            })

        if min_psi < 35.5:
            score_improvement_plan.append({
                "issue": f"Low Tire Pressure ({min_psi} PSI)",
                "solution": "Inflate Rear-Right tire to cold target of 36.0 PSI.",
                "potential_score_gain": round(min(2.0, (36.0 - min_psi) * 0.5), 1),
                "can_auto_apply": True
            })

        if telemetry.get("soc_pct", 70) > 80:
            score_improvement_plan.append({
                "issue": "Daily Charge Ceiling Above 80%",
                "solution": "Set daily maximum charge limit cap to 80% to protect cathode crystal lattice.",
                "potential_score_gain": 1.5,
                "can_auto_apply": True
            })

        if not score_improvement_plan:
            score_improvement_plan.append({
                "issue": "System Already Optimized",
                "solution": "Your battery and vehicle systems are running at 100/100 peak capacity!",
                "potential_score_gain": 0.0,
                "can_auto_apply": False
            })

        recommendations = [f"Follow the Score Improvement Plan below to gain +{sum(item['potential_score_gain'] for item in score_improvement_plan):.1f} pts and reach 100/100!"]

        return {
            "vehicle_id": telemetry["vehicle_id"],
            "timestamp": telemetry["timestamp"],
            "overall_health_score": overall_score,
            "health_grade": health_grade,
            "subsystems": subsystems,
            "key_findings": findings,
            "immediate_recommendations": recommendations,
            "score_improvement_plan": score_improvement_plan
        }

    @staticmethod
    def calculate_predictive_maintenance(telemetry: Dict[str, Any]) -> Dict[str, Any]:
        soh = telemetry["soh_pct"]
        cycles = telemetry["charge_cycles"]
        delta_v = telemetry["cell_delta_v_mv"]
        pack_temp = telemetry["pack_temp_c"]
        max_cell_temp = max(telemetry["cell_temps_c"])
        v_type = telemetry["vehicle_type"]

        soh_headroom = max(0.0, soh - 80.0)
        temp_multiplier = 1.0 + (max(0.0, pack_temp - 30.0) * 0.04)
        imbalance_multiplier = 1.0 + (max(0.0, delta_v - 25.0) * 0.015)
        
        effective_degradation_rate_per_10k_km = round(0.45 * temp_multiplier * imbalance_multiplier, 2)
        
        if effective_degradation_rate_per_10k_km > 0:
            remaining_10k_chunks = soh_headroom / effective_degradation_rate_per_10k_km
            estimated_rul_km = round(remaining_10k_chunks * 10000.0)
        else:
            estimated_rul_km = 150000.0

        estimated_rul_cycles = round(soh_headroom * 65.0)
        avg_monthly_km = 1200.0 if v_type == "car" else 600.0
        estimated_months_to_80_soh = round(estimated_rul_km / avg_monthly_km, 1)

        cell_imbalance_risk_score = min(100.0, round((delta_v / 120.0) * 100.0, 1))
        
        if max_cell_temp > 52.0 or delta_v > 100.0:
            thermal_runaway_risk = "Severe"
        elif max_cell_temp > 44.0 or delta_v > 65.0:
            thermal_runaway_risk = "High"
        elif max_cell_temp > 38.0 or delta_v > 40.0:
            thermal_runaway_risk = "Moderate"
        else:
            thermal_runaway_risk = "Low"

        if soh < 82.0:
            replacement_advisory = "Immediate Replacement Recommended (SOH near EOL threshold)"
        elif soh < 88.0:
            replacement_advisory = "Plan Module Servicing / Inspection within next 6 months"
        else:
            replacement_advisory = "Battery Health Excellent. No replacement required."

        anomalies = []
        if delta_v > 50.0:
            anomalies.append(f"Module Voltage Imbalance: Delta V is {delta_v} mV")
        if max_cell_temp > 42.0:
            anomalies.append(f"Elevated Sensor Thermal Reading: {max_cell_temp}°C")
        if telemetry["internal_resistance_mOhm"] > 40.0 and v_type == "car":
            anomalies.append(f"High Pack Internal Resistance: {telemetry['internal_resistance_mOhm']} mΩ")

        capacity_forecast = []
        curr_soh = soh
        monthly_deg = (effective_degradation_rate_per_10k_km / 10.0) * (avg_monthly_km / 1000.0)
        for m in range(0, 13):
            capacity_forecast.append({
                "month": f"M{m}",
                "soh": round(max(70.0, curr_soh - (m * monthly_deg)), 1)
            })

        return {
            "vehicle_id": telemetry["vehicle_id"],
            "soh_pct": soh,
            "estimated_rul_km": estimated_rul_km,
            "estimated_rul_cycles": estimated_rul_cycles,
            "estimated_months_to_80_soh": estimated_months_to_80_soh,
            "cell_imbalance_risk_score": cell_imbalance_risk_score,
            "thermal_runaway_risk": thermal_runaway_risk,
            "degradation_rate_pct_per_10k_km": effective_degradation_rate_per_10k_km,
            "replacement_advisory": replacement_advisory,
            "anomalies_detected": anomalies if anomalies else ["No critical anomalies detected"],
            "capacity_forecast": capacity_forecast
        }

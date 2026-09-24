// EV Battery & Vehicle AI Coach System - Frontend Controller v3.0
const API_BASE = (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost")
  ? "http://127.0.0.1:8000/api"
  : "/api";

// Global Application State
let currentState = {
  vehicle_id: "car_tesla_model3",
  speed_kmh: 60,
  ambient_temp_c: 28,
  is_charging: false,
  is_fast_charging: false,
  is_stress_test: false,
  coach_mode: "battery"
};

// Chart.js Instances
let cellVoltageChart = null;
let sohHistoryChart = null;
let tempPowerScatterChart = null;
let forecastChart = null;

document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  startTelemetryStream();

  setInterval(fetchAICoachAdvice, 2000);
  setInterval(fetchPredictiveNotifications, 2500);
  setInterval(fetchPredictiveMaintenance, 3000);
  setInterval(fetchAnalyticsHistory, 4000);
  
  fetchQuickHealthScore();
});

// ----------------------------------------------------
// 1. Telemetry Data Stream & Polling
// ----------------------------------------------------
function startTelemetryStream() {
  fetchLiveTelemetry();
  setInterval(fetchLiveTelemetry, 1000);
}

async function fetchLiveTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/telemetry/live`);
    if (!res.ok) throw new Error("Telemetry API failed");
    const data = await res.json();
    updateTelemetryUI(data);
  } catch (err) {
    console.error("Telemetry fetch error:", err);
  }
}

// ----------------------------------------------------
// 2. UI Bindings for Telemetry & Vehicle Diagnostics
// ----------------------------------------------------
function updateTelemetryUI(data) {
  // SOH
  document.getElementById("sohValue").innerHTML = `${data.soh_pct}<span class="compact-stat-unit">%</span>`;
  document.getElementById("cellDeltaV").innerText = `${data.cell_delta_v_mv} mV`;
  document.getElementById("irValue").innerText = `${data.internal_resistance_mOhm} mΩ`;
  
  if (data.soh_pct >= 90) setBadge("sohBadge", "HEALTHY", "badge-green");
  else if (data.soh_pct >= 80) setBadge("sohBadge", "MODERATE", "badge-amber");
  else setBadge("sohBadge", "CRITICAL SOH", "badge-red");

  // SOC & Range
  document.getElementById("socValue").innerHTML = `${data.soc_pct}<span class="compact-stat-unit">%</span>`;
  document.getElementById("estimatedRange").innerText = `${data.estimated_range_km} km`;
  document.getElementById("packVoltage").innerText = `${data.pack_voltage} V`;
  document.getElementById("currentValue").innerText = `${data.current_a > 0 ? '+' : ''}${data.current_a} A`;
  document.getElementById("powerValue").innerText = `${data.power_kw} kW`;
  setBadge("chargingStateBadge", data.charging_status.toUpperCase(), data.charging_status.includes("Charging") ? "badge-green" : "badge-blue");

  // Temperature & Cooling
  document.getElementById("packTemp").innerHTML = `${data.pack_temp_c}<span class="compact-stat-unit">°C</span>`;
  document.getElementById("tempS2").innerText = `${data.cell_temps_c[1]}°C`;
  document.getElementById("tempBMS").innerText = `${data.bms_temp_c}°C`;
  document.getElementById("coolingType").innerText = data.vehicle_type === "car" ? "Liquid Cooling" : "Air Cooling";

  if (data.thermal_status === "Normal") setBadge("thermalStatusBadge", "NORMAL", "badge-green");
  else if (data.thermal_status === "Warning") setBadge("thermalStatusBadge", "WARNING", "badge-amber");
  else setBadge("thermalStatusBadge", "CRITICAL", "badge-red");

  // Vehicle Diagnostics & TPMS
  if (data.tire_pressures_psi) {
    const minPsi = Math.min(...Object.values(data.tire_pressures_psi));
    document.getElementById("psiMin").innerText = `${minPsi} PSI`;
    document.getElementById("psiMin").style.color = minPsi < 33.0 ? "var(--danger-red)" : "var(--accent-neon-green)";
  }

  if (data.motor_temp_c) {
    document.getElementById("motorTemp").innerHTML = `${data.motor_temp_c}<span class="compact-stat-unit">°C</span>`;
    document.getElementById("inverterEff").innerText = `${data.inverter_efficiency_pct}%`;
    document.getElementById("isolationValue").innerText = `${data.isolation_resistance_mohm} MΩ`;
    
    if (data.motor_temp_c > 70.0 || data.cell_delta_v_mv > 50.0) {
      setBadge("vehicleHealthBadge", "ATTENTION", "badge-amber");
    } else {
      setBadge("vehicleHealthBadge", "OPTIMAL", "badge-green");
    }
  }

  updateCellVoltageChart(data.cell_voltages);
}

function setBadge(id, text, badgeClass) {
  const el = document.getElementById(id);
  if (el) {
    el.innerText = text;
    el.className = `card-badge ${badgeClass}`;
  }
}

// ----------------------------------------------------
// 3. Interactive Controls Handlers
// ----------------------------------------------------
function onVehicleChange() {
  const select = document.getElementById("vehicleSelect");
  currentState.vehicle_id = select.value;
  updateControlState();
  fetchQuickHealthScore();
}

function updateControlState() {
  currentState.speed_kmh = parseFloat(document.getElementById("speedSlider").value);
  currentState.ambient_temp_c = parseFloat(document.getElementById("tempSlider").value);

  document.getElementById("speedVal").innerText = `${currentState.speed_kmh} km/h`;
  document.getElementById("tempVal").innerText = `${currentState.ambient_temp_c} °C`;

  fetch(`${API_BASE}/controls/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(currentState)
  });
}

function toggleCharger() {
  currentState.is_charging = !currentState.is_charging;
  const btn = document.getElementById("chargeToggleBtn");
  btn.classList.toggle("active", currentState.is_charging);
  if (!currentState.is_charging && currentState.is_fast_charging) {
    currentState.is_fast_charging = false;
    document.getElementById("fastChargeToggleBtn").classList.remove("active");
  }
  updateControlState();
}

function toggleFastCharge() {
  currentState.is_fast_charging = !currentState.is_fast_charging;
  if (currentState.is_fast_charging) {
    currentState.is_charging = true;
    document.getElementById("chargeToggleBtn").classList.add("active");
  }
  const btn = document.getElementById("fastChargeToggleBtn");
  btn.classList.toggle("active", currentState.is_fast_charging);
  updateControlState();
}

function toggleStressTest() {
  currentState.is_stress_test = !currentState.is_stress_test;
  const btn = document.getElementById("stressTestToggleBtn");
  btn.classList.toggle("danger-active", currentState.is_stress_test);
  updateControlState();
}

// ----------------------------------------------------
// 4. AI Coach Insights & Solution Execution
// ----------------------------------------------------
function switchCoachMode(mode) {
  currentState.coach_mode = mode;
  document.getElementById("modeBatteryBtn").classList.toggle("active", mode === "battery");
  document.getElementById("modeVehicleBtn").classList.toggle("active", mode === "vehicle");
  fetchAICoachAdvice();
}

async function fetchAICoachAdvice() {
  try {
    const res = await fetch(`${API_BASE}/ai-coach/recommendations`);
    if (!res.ok) return;
    const adviceList = await res.json();

    const container = document.getElementById("aiCoachGrid");
    container.innerHTML = "";

    const filtered = adviceList.filter(item => {
      if (currentState.coach_mode === "battery") return item.category === "Battery" || item.category === "Thermal";
      return item.category === "Vehicle" || item.category === "Driving" || item.category === "Maintenance";
    });

    const displayList = filtered.length > 0 ? filtered : adviceList;

    displayList.forEach(item => {
      const card = document.createElement("div");
      card.className = `coach-item-card priority-${item.priority}`;
      
      let stepsHtml = "";
      if (item.solution_steps && item.solution_steps.length > 0) {
        stepsHtml = `
          <div class="solution-box">
            <div class="solution-title">
              <span>📋 Solution Protocol:</span>
              <span style="color: var(--accent-neon-green);">+${item.impact_score_pts} pts</span>
            </div>
            ${item.solution_steps.map(step => `<div class="solution-step-item">${step}</div>`).join('')}
          </div>
        `;
      }

      let executeBtnHtml = "";
      if (item.can_execute_solution) {
        executeBtnHtml = `<button class="btn-execute-solution" onclick="executeAISolution('${item.id}')">⚡ Execute AI Solution (+${item.impact_score_pts} pts)</button>`;
      }

      card.innerHTML = `
        <div class="coach-card-header">
          <span class="coach-card-title">${item.title}</span>
          <span class="coach-card-cat">${item.category}</span>
        </div>
        <div class="coach-card-msg">${item.message}</div>
        <div class="coach-card-action">💡 ${item.action_item}</div>
        ${stepsHtml}
        ${executeBtnHtml}
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error("AI Coach error:", e);
  }
}

async function executeAISolution(adviceId) {
  try {
    const res = await fetch(`${API_BASE}/ai-coach/execute-solution/${adviceId}`, { method: "POST" });
    const data = await res.json();
    alert(`✅ ${data.message}`);

    if (adviceId === "solution_thermal_overheat" || adviceId === "solution_cell_imbalance" || adviceId === "solution_motor_strain") {
      currentState.is_fast_charging = false;
      currentState.is_stress_test = false;
      document.getElementById("fastChargeToggleBtn").classList.remove("active");
      document.getElementById("stressTestToggleBtn").classList.remove("danger-active");
    }

    fetchAICoachAdvice();
    fetchQuickHealthScore();
  } catch (e) {
    console.error("Execute Solution error:", e);
  }
}

async function fetchQuickHealthScore() {
  try {
    const res = await fetch(`${API_BASE}/ai-coach/health-check`, { method: "POST" });
    if (!res.ok) return;
    const report = await res.json();
    document.getElementById("scoreDisplayNum").innerText = report.overall_health_score;
    document.getElementById("scoreGradeBadge").innerText = `GRADE ${report.health_grade}`;
  } catch (e) {
    console.error("Health score error:", e);
  }
}

async function fetchPredictiveNotifications() {
  try {
    const res = await fetch(`${API_BASE}/notifications/predictive`);
    if (!res.ok) return;
    const notifications = await res.json();

    const badge = document.getElementById("notifBadgeCount");
    const validNotifs = notifications.filter(n => n.id !== "pred_all_nominal");
    badge.innerText = validNotifs.length;
    badge.style.display = validNotifs.length > 0 ? "flex" : "none";

    const feed = document.getElementById("notifFeed");
    feed.innerHTML = "";

    notifications.forEach(n => {
      const item = document.createElement("div");
      item.className = `notif-item ${n.severity}`;
      item.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
          <span class="notif-title">${n.title}</span>
          <span class="notif-pred-time">${n.problem_predicted_in}</span>
        </div>
        <div class="notif-cause">${n.root_cause}</div>
        ${n.can_autofix ? `<button class="notif-autofix-btn" onclick="triggerAutoFix('${n.id}')">⚡ Fix Problem Now</button>` : ''}
      `;
      feed.appendChild(item);
    });
  } catch (e) {
    console.error("Predictive Notifications error:", e);
  }
}

async function triggerAutoFix(notifId) {
  try {
    const res = await fetch(`${API_BASE}/notifications/autofix/${notifId}`, { method: "POST" });
    const data = await res.json();
    alert(`✅ ${data.message}`);
    
    if (notifId === "pred_thermal_runaway" || notifId === "pred_cell_imbalance") {
      currentState.is_fast_charging = false;
      currentState.is_stress_test = false;
      document.getElementById("fastChargeToggleBtn").classList.remove("active");
      document.getElementById("stressTestToggleBtn").classList.remove("danger-active");
    }
    
    fetchPredictiveNotifications();
    fetchQuickHealthScore();
  } catch (e) {
    console.error("Autofix error:", e);
  }
}

function toggleNotifDropdown() {
  const dropdown = document.getElementById("notifDropdown");
  dropdown.classList.toggle("show");
}

// ----------------------------------------------------
// 5. Full AI Health Checkup & Score Booster Modal
// ----------------------------------------------------
async function runFullHealthCheckup() {
  try {
    const res = await fetch(`${API_BASE}/ai-coach/health-check`, { method: "POST" });
    if (!res.ok) return;
    const report = await res.json();

    document.getElementById("healthScoreNum").innerText = report.overall_health_score;
    document.getElementById("healthGradeText").innerText = `GRADE ${report.health_grade}`;
    document.getElementById("scoreDisplayNum").innerText = report.overall_health_score;
    document.getElementById("scoreGradeBadge").innerText = `GRADE ${report.health_grade}`;

    const subContainer = document.getElementById("subsystemList");
    subContainer.innerHTML = "";

    report.subsystems.forEach(sub => {
      const item = document.createElement("div");
      item.className = "subsystem-item";
      item.innerHTML = `
        <div class="subsystem-name-score">
          <span>${sub.name}</span>
          <span>${sub.score} / 100 (${sub.status})</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${sub.score}%;"></div>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${sub.summary}</div>
      `;
      subContainer.appendChild(item);
    });

    // Populate Score Improvement Plan
    const boosterContainer = document.getElementById("scoreBoosterList");
    boosterContainer.innerHTML = "";

    report.score_improvement_plan.forEach(b => {
      const item = document.createElement("div");
      item.className = "booster-item";
      item.innerHTML = `
        <div>
          <div style="font-weight: 700; color: #fff;">${b.issue}</div>
          <div style="color: var(--text-muted); font-size: 11px; margin-top: 2px;">${b.solution}</div>
        </div>
        <span class="pts-gain-badge">+${b.potential_score_gain} pts</span>
      `;
      boosterContainer.appendChild(item);
    });

    document.getElementById("healthCheckModal").classList.add("show");
  } catch (e) {
    console.error("Health checkup error:", e);
  }
}

async function applyAllScoreBoosters() {
  try {
    const res = await fetch(`${API_BASE}/ai-coach/apply-score-boosters`, { method: "POST" });
    const data = await res.json();
    alert(`⚡ ${data.message}`);

    currentState.is_fast_charging = false;
    currentState.is_stress_test = false;
    document.getElementById("fastChargeToggleBtn").classList.remove("active");
    document.getElementById("stressTestToggleBtn").classList.remove("danger-active");

    runFullHealthCheckup();
    fetchAICoachAdvice();
  } catch (e) {
    console.error("Apply score boosters error:", e);
  }
}

function closeHealthCheckModal() {
  document.getElementById("healthCheckModal").classList.remove("show");
}

// ----------------------------------------------------
// 6. Predictive Maintenance & Analytics Fetchers
// ----------------------------------------------------
async function fetchPredictiveMaintenance() {
  try {
    const res = await fetch(`${API_BASE}/predictive/rul`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("rulKmVal").innerText = `${data.estimated_rul_km.toLocaleString()} km`;
    document.getElementById("rulCyclesVal").innerText = `${data.estimated_rul_cycles.toLocaleString()} cycles`;
    document.getElementById("rulMonthsVal").innerText = `${data.estimated_months_to_80_soh} mos`;
    document.getElementById("imbalanceScoreVal").innerText = `${data.cell_imbalance_risk_score} / 100`;
    document.getElementById("replacementAdvisoryText").innerText = data.replacement_advisory;

    const anomalyContainer = document.getElementById("anomaliesList");
    anomalyContainer.innerHTML = "";
    data.anomalies_detected.forEach(anom => {
      const item = document.createElement("div");
      item.className = "sub-metric-item";
      item.innerHTML = `<span class="sub-metric-label">⚠️ ${anom}</span>`;
      anomalyContainer.appendChild(item);
    });

    updateForecastChart(data.capacity_forecast);
  } catch (e) {
    console.error("Predictive Maintenance error:", e);
  }
}

async function fetchAnalyticsHistory() {
  try {
    const res = await fetch(`${API_BASE}/analytics/history?vehicle_id=${currentState.vehicle_id}&limit=30`);
    if (!res.ok) return;
    const historyData = await res.json();
    updateAnalyticsCharts(historyData.history);
  } catch (e) {
    console.error("Analytics fetch error:", e);
  }
}

// ----------------------------------------------------
// 7. Chart.js Initialization & Updates
// ----------------------------------------------------
function initCharts() {
  const ctxCell = document.getElementById("cellVoltageChart").getContext("2d");
  cellVoltageChart = new Chart(ctxCell, {
    type: "bar",
    data: {
      labels: Array.from({length: 16}, (_, i) => `C${i+1}`),
      datasets: [{
        label: "Cell Volts (V)",
        data: Array(16).fill(3.8),
        backgroundColor: "rgba(0, 242, 254, 0.6)",
        borderColor: "#00f2fe",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 3.0, max: 4.3, grid: { display: false }, ticks: { display: false } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8", font: { size: 8 } } }
      }
    }
  });

  const ctxSoh = document.getElementById("sohHistoryChart").getContext("2d");
  sohHistoryChart = new Chart(ctxSoh, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "SOH (%)",
        data: [],
        borderColor: "#00f2fe",
        backgroundColor: "rgba(0, 242, 254, 0.15)",
        fill: true,
        tension: 0.2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 70, max: 100, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8", maxTicksLimit: 6 } }
      }
    }
  });

  const ctxScatter = document.getElementById("tempPowerScatterChart").getContext("2d");
  tempPowerScatterChart = new Chart(ctxScatter, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Temp (°C) vs Power (kW)",
        data: [],
        backgroundColor: "#ff0055"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: "Pack Temp (°C)", color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        y: { title: { display: true, text: "Power (kW)", color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } }
      }
    }
  });

  const ctxForecast = document.getElementById("forecastChart").getContext("2d");
  forecastChart = new Chart(ctxForecast, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Projected SOH (%)",
        data: [],
        borderColor: "#7f00ff",
        borderDash: [5, 5],
        backgroundColor: "rgba(127, 0, 255, 0.15)",
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 70, max: 100, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
      }
    }
  });
}

function updateCellVoltageChart(cellVoltages) {
  if (!cellVoltageChart) return;
  cellVoltageChart.data.labels = cellVoltages.map(c => `C${c.cell_id}`);
  cellVoltageChart.data.datasets[0].data = cellVoltages.map(c => c.voltage);
  cellVoltageChart.data.datasets[0].backgroundColor = cellVoltages.map(c => {
    if (c.status === "critical") return "#ff0055";
    if (c.status === "warning") return "#ffb703";
    return "rgba(0, 242, 254, 0.7)";
  });
  cellVoltageChart.update("none");
}

function updateForecastChart(forecastData) {
  if (!forecastChart) return;
  forecastChart.data.labels = forecastData.map(f => f.month);
  forecastChart.data.datasets[0].data = forecastData.map(f => f.soh);
  forecastChart.update();
}

function updateAnalyticsCharts(historyLogs) {
  if (!historyLogs || historyLogs.length === 0) return;
  if (sohHistoryChart) {
    sohHistoryChart.data.labels = historyLogs.map(l => l.timestamp ? l.timestamp.split(" ")[1] : "");
    sohHistoryChart.data.datasets[0].data = historyLogs.map(l => l.soh_pct);
    sohHistoryChart.update();
  }
  if (tempPowerScatterChart) {
    tempPowerScatterChart.data.datasets[0].data = historyLogs.map(l => ({
      x: l.pack_temp_c,
      y: Math.abs(l.power_kw)
    }));
    tempPowerScatterChart.update();
  }
}

function switchTab(tabId, btn) {
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-nav-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
  btn.classList.add("active");
}

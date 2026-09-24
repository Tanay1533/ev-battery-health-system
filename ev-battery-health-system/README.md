# EV Battery & Vehicle Management System with AI Coach

An ultra-modern, interactive **EV Battery & Vehicle Management System (BMS)** dashboard with an **AI Battery & Vehicle Coach**, 50-Point AI Diagnostic Health Checkup, Predictive Anomaly Notifications, and 1-Click Automated Fixes. Designed for both **EV Cars** (e.g., Tesla Model 3, Hyundai Ioniq 5) and **EV 2-Wheelers** (e.g., Ather 450X, Ola S1 Pro).

---

## 🌟 Key Features

- 🤖 **Hero AI Battery & Vehicle Coach**: Real-time actionable insights, driving mode recommendations, thermal pre-conditioning alerts, and 1-click solution execution.
- 🩺 **50-Point AI Diagnostic Health Audit**: Complete health evaluation across Battery (SOH, SOC, delta voltage), Powertrain & Traction Motor, Thermal & HVAC, TPMS Tires, High-Voltage Inverter, and Auxiliary Systems.
- 🔔 **Predictive Problem Notifications**: Early warning index detecting thermal runaway risks, cell voltage divergence, inverter dehumidifier needs, and micro-punctures before failure occurs.
- ⚡ **Automated 1-Click Solution Execution**: Instantly fix active issues and boost health scores back to 100/100.
- 📊 **Multi-Vehicle Support**: Live switching between EV Cars and EV 2-Wheelers with specialized telemetry models.
- 🌐 **Vercel & Cloud Ready**: Pre-configured Python Serverless backend and static frontend for instant deployment.

---

## 📂 Project Structure

```
ev-battery-health-system/
├── api/
│   └── index.py                 # Vercel Python Serverless Function Entry Point
├── backend/
│   ├── main.py                  # FastAPI Core Application & API Routes
│   ├── models.py                # Pydantic Schemas & Data Contracts
│   ├── database.py              # SQLite Telemetry Logging (Serverless Compatible)
│   ├── telemetry_sim.py          # Battery Physics & Vehicle Telemetry Simulator
│   └── ai_engine.py             # AI Coach, 50-Point Audit & Predictive Engine
├── frontend/
│   ├── index.html               # Glassmorphism AI Coach Dashboard UI
│   ├── styles.css               # Design System & Responsive Styling
│   └── app.js                  # Dynamic API Controller & Chart.js Integration
├── vercel.json                  # Vercel Routing & Serverless Configuration
├── .gitignore                   # Git Ignore Specification
├── requirements.txt             # Python Dependencies
└── README.md
```

---

## 🚀 How to Run Locally

### 1. Run Backend Server
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API Docs: `http://127.0.0.1:8000/docs`

### 2. Run Frontend Dashboard
```bash
python -m http.server 8080 --directory frontend
```
Open Dashboard: `http://localhost:8080`

---

## ☁️ How to Deploy to Vercel & GitHub

### Method A: Deploy via GitHub & Vercel Dashboard (Recommended)
1. **Create a GitHub Repository**:
   - Go to [github.com/new](https://github.com/new) and create a repository named `ev-battery-health-system`.
2. **Push Code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial Commit - EV Battery AI Coach System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ev-battery-health-system.git
   git push -u origin main
   ```
3. **Deploy on Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new) and connect your GitHub account.
   - Select the `ev-battery-health-system` repository.
   - Click **Deploy**. Vercel will automatically read `vercel.json` and host your backend API & frontend!

### Method B: Direct Terminal Deployment via Vercel CLI
```bash
npx vercel
```
Follow the interactive prompts to log in and deploy directly from your local terminal.

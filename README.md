# SafeRoute 🛡️

A women's safety navigation platform with AI-driven crime analysis, real-time routing optimization, and live emergency SOS alerts.

---

## Features

- Safety-optimized routes — safest, fastest, or balanced
- Crime heatmap powered by DBSCAN clustering
- Danger-zone detection using scikit-learn
- Real-time SOS alerts via WebSocket
- Emergency contact notifications
- User familiarity-based personalization
- Offline SOS queueing
- Admin dashboard with live heatmap visualization

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, NetworkX, scikit-learn |
| Admin Dashboard | React, TypeScript, Vite, Tailwind CSS |
| Mobile App | React Native (Expo) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Real-time | WebSocket |
| Routing | OpenStreetMap + NetworkX graph |

---

## Architecture

```
Mobile App / Admin Dashboard
         ↓
    FastAPI Backend
         ↓
NetworkX Graph (OpenStreetMap nodes)
         ↓
Safety Engine
  - Crime density  50%
  - Lighting       20%
  - Crowds         15%
  - CCTV           15%
         ↓
Background cron jobs (every 5 min)
→ Recalculate heatmaps + DBSCAN clusters
         ↓
WebSocket → broadcast SOS alerts live
```

---

## Project Structure

```
safe-route/
├── docker-compose.yml
├── SafeRoute_Backend/       ← FastAPI + AI routing engine
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/routes/
│   │   ├── ai_safety.py
│   │   └── crime.py
│   ├── core/
│   │   ├── config.py
│   │   └── safety_config.py
│   ├── services/
│   │   ├── route_safety.py
│   │   ├── safety_engine.py
│   │   ├── crime_heatmap_service.py
│   │   ├── danger_zone_detector.py
│   │   ├── sos_service.py
│   │   └── websocket.py
│   └── tests/
├── SafeRoute_Admin/         ← React admin dashboard
│   └── src/components/
│       ├── GoogleMapView.tsx
│       ├── AnalyticsCards.tsx
│       └── TuningPanel.tsx
└── SafeRoute_Native/        ← React Native mobile app
    └── src/
        ├── screens/
        ├── components/
        └── hooks/
```

---

## How to Run

### Prerequisites

- Python 3.9+
- Node.js v18+
- Expo Go app (for mobile testing)

---

### Backend

```bash
cd SafeRoute_Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start server
python3 main.py
```

Backend runs at: **http://localhost:8000**

---

### Admin Dashboard

Open a new terminal:

```bash
cd SafeRoute_Admin
npm install
npm run dev
```

Dashboard runs at: **http://localhost:5173**

---

### Mobile App

Open a new terminal:

```bash
cd SafeRoute_Native
npm install
npm start
```

Scan the QR code with **Expo Go** on your phone.

---

### Docker (run everything together)

```bash
docker-compose up --build
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System status |
| `/routes/safest` | POST | Safety-optimized route |
| `/routes/fastest` | POST | Shortest route |
| `/routes/heatmap` | GET | Crime density heatmap |
| `/routes/danger-zones` | GET | High-crime DBSCAN clusters |
| `/sos` | POST | Trigger SOS alert |
| `/sos/active` | GET | Live active alerts |
| `/user/register` | POST | Create account |
| `ws://.../sos/stream` | WebSocket | Live SOS stream |

---

## Environment Variables

Copy `SafeRoute_Backend/.env.example` to `SafeRoute_Backend/.env`:

```
SAFETY_API_KEY=dev-key-change-in-production
DATABASE_URL=sqlite:///./safe_routes.db
CRIME_RATE_LIMIT_REQUESTS=10
CRIME_RATE_LIMIT_WINDOW_SECONDS=60
```

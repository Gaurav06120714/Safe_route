"""
Women Safety Smart Route Predictor — Backend API
=================================================
Modular FastAPI server for safe routing, crime reporting, and SOS alerts.
"""

from __future__ import annotations

import logging
import socket
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from core.config import CORS_ALLOWED_ORIGINS, CORS_ALLOWED_ORIGIN_REGEX
from core.safety_config import get_time_multiplier
from api.routes import router as api_router
from services.familiarity_module import router as familiarity_router
from services.sos_service import init_sos_db
from services.route_service import get_all_edges, get_all_junctions
from services.websocket import admin_manager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Women Safety Route Predictor",
    description="AI-powered safest route calculation for women",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_origin_regex=CORS_ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(familiarity_router)
app.include_router(api_router)

# ---------------------------------------------------------------------------
# Global State (for legacy compatibility and performance)
# ---------------------------------------------------------------------------
EDGES = []
JUNCTIONS = []
zeroconf_instance = None

def get_local_ip() -> str:
    """Get the physical LAN IP of the current machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
PORT = 8000

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    global EDGES, JUNCTIONS, zeroconf_instance
    
    # Initialize Databases
    init_sos_db()
    
    # Start background job scheduler
    try:
        from services.background_jobs import start_background_scheduler
        start_background_scheduler()
    except ImportError:
        logger.warning("Background scheduler not found, skipping...")
    
    # Load Road Graph Data
    EDGES = get_all_edges()
    JUNCTIONS = get_all_junctions()
    logger.info(f"Startup: Loaded {len(EDGES)} edges and {len(JUNCTIONS)} junctions.")
    
    # mDNS Registration
    try:
        from zeroconf import ServiceInfo, Zeroconf
        ip = get_local_ip()
        info = ServiceInfo(
            "_http._tcp.local.",
            "saferoute._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=PORT,
            properties={"desc": "SafeRoute API Server"},
            server="saferoute.local."
        )
        zeroconf_instance = Zeroconf()
        zeroconf_instance.register_service(info)
        logger.info(f"mDNS Registered: saferoute.local -> {ip}:{PORT}")
    except Exception as e:
        logger.error(f"Failed to register mDNS: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        from services.background_jobs import stop_background_scheduler
        stop_background_scheduler()
    except ImportError:
        pass
    
    global zeroconf_instance
    if zeroconf_instance:
        try:
            zeroconf_instance.unregister_all_services()
            zeroconf_instance.close()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Basic Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Women Safety Smart Route Predictor API",
        "version": "2.0.0",
        "total_segments": len(EDGES),
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "segments_loaded": len(EDGES),
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/server-info")
async def get_server_info():
    ip = get_local_ip()
    return {
        "host": ip,
        "port": PORT,
        "base_url": f"http://{ip}:{PORT}",
        "ws_url": f"ws://{ip}:{PORT}/ws/admin_alert",
        "ws_sos_url": f"ws://{ip}:{PORT}/sos/stream"
    }

@app.get("/test", response_class=HTMLResponse)
async def realtime_test_page():
    from services.ui_service import get_test_page
    return get_test_page(len(EDGES))

@app.websocket("/ws/sos")
async def sos_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for mobile app to maintain persistent connection.
    This also broadcasts to any admins listening on the same manager if needed.
    """
    await admin_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, can also receive location pulse here
            data = await websocket.receive_text()
            logger.debug(f"WS received: {data}")
    except WebSocketDisconnect:
        admin_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS error: {e}")
        admin_manager.disconnect(websocket)

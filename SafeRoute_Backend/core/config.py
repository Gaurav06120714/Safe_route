"""
core/config.py — Central configuration for SafeRoute backend.

All application-wide constants live here or are re-exported here so
any module can do:  from core.config import BOUNDS, SOS_DB_PATH, ...
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SOS_DB_PATH = BASE_DIR / "data" / "sos_alerts.db"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = ["*"]
CORS_ALLOWED_ORIGIN_REGEX = ".*"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./safe_routes.db"

# ---------------------------------------------------------------------------
# Re-export safety constants so crime.py / other routes can import from here
# ---------------------------------------------------------------------------
from core.safety_config import (          # noqa: E402
    BOUNDS,
    coords_in_bounds,
    API_KEY,
    WEIGHTS,
    get_time_multiplier,
)

# Crime reporting rate-limit defaults (can be overridden via env vars)
CRIME_RATE_LIMIT_REQUESTS: int = int(os.getenv("CRIME_RATE_LIMIT_REQUESTS", "10"))
CRIME_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("CRIME_RATE_LIMIT_WINDOW_SECONDS", "60"))
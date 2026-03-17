"""
CTV Ad Intelligence Platform — FastAPI Application

REST API serving analytics data to the React frontend.
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path for analytics/etl imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes import (
    filters,
    overview,
    campaigns,
    viewability,
    segmentation,
    anomalies,
    attribution,
    ab_testing,
    frequency,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="CTV Ad Intelligence API",
    description="REST API for Connected TV advertising analytics",
    version="1.0.0",
)

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(filters.router, prefix="/api")
app.include_router(overview.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(viewability.router, prefix="/api")
app.include_router(segmentation.router, prefix="/api")
app.include_router(anomalies.router, prefix="/api")
app.include_router(attribution.router, prefix="/api")
app.include_router(ab_testing.router, prefix="/api")
app.include_router(frequency.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "ctv-ad-intelligence"}

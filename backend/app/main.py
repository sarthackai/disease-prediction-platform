"""
main.py
The entry point for the FastAPI backend.
Registers all routes and starts the server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, predictions, hospitals, reports

# ------------------------------------------------------------------
# CREATE APP
# ------------------------------------------------------------------
app = FastAPI(
    title="Disease Prediction API",
    description="AI-Powered Disease Prediction and Hospital Recommendation System",
    version="1.0.0"
)

# ------------------------------------------------------------------
# CORS — allows the React frontend to talk to this backend
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["Predictions"]
)

app.include_router(
    hospitals.router,
    prefix="/api/v1/hospitals",
    tags=["Hospitals"]
)
app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)
# ------------------------------------------------------------------
# HEALTH CHECK — lets you confirm the server is running
# ------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Disease Prediction API is running"}
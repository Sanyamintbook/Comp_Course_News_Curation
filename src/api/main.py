"""
Module: API Entrypoint
Purpose: The main FastAPI application file for the 5-module unified architecture.
Logic: 
- Initializes the FastAPI app.
- Registers routers for the various modules (dashboard, ingestion).
- Starts background schedulers.
"""
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.api.routers import dashboard, admin

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background scheduler...")
    scheduler.start()
    yield
    print("Shutting down scheduler...")
    scheduler.shutdown()

app = FastAPI(title="Unified AI Platform API", lifespan=lifespan)

# Include Routers
app.include_router(dashboard.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

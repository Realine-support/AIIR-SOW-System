"""
FastAPI Application Entry Point
Main application for AIIR SOW System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.webhooks import approve_pricing, approve_sow, google_drive_trigger, pricing_model_approved
from api.cron import watch_transcripts
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AIIR SOW Automation System",
    description="Automated Statement of Work generation from discovery call transcripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(approve_pricing.router, tags=["webhooks"])
app.include_router(approve_sow.router, tags=["webhooks"])
app.include_router(google_drive_trigger.router, tags=["webhooks"])
app.include_router(pricing_model_approved.router, tags=["webhooks"])
app.include_router(watch_transcripts.router, tags=["cron"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AIIR SOW Automation System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "endpoints": {
            "approve_pricing": "/webhooks/approve-pricing",
            "approve_sow": "/webhooks/approve-sow",
            "google_drive_trigger": "/webhooks/google-drive-file-added",
            "google_drive_trigger_test": "/webhooks/google-drive-file-added/test",
            "pricing_model_approved": "/webhooks/pricing-model-approved",
            "pricing_model_approved_test": "/webhooks/pricing-model-approved/test",
            "watch_transcripts": "/cron/watch-transcripts"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

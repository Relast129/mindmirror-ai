"""
MindMirror AI - Main FastAPI Application
Privacy-first, multi-modal emotional reflection dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

# Import routers
from routers import auth, upload, reflect, history

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("🚀 MindMirror AI starting up...")
    logger.info("✅ AI models ready for inference")
    yield
    logger.info("👋 MindMirror AI shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="MindMirror AI API",
    description="Privacy-first, multi-modal emotional reflection dashboard for youth",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(reflect.router, prefix="/reflect", tags=["Reflection"])
app.include_router(history.router, prefix="/history", tags=["History"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "🧠 Welcome to MindMirror AI",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Privacy-first emotional reflection dashboard"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MindMirror AI",
        "ai_models": "ready"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

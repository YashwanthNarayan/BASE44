from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import asyncio
from contextlib import asynccontextmanager

# Import utilities
from backend.utils.database import connect_to_database, close_database_connection, create_indexes

# Import route modules
from backend.routes import auth, student, practice, tutor, teacher, study_planner, notes, practice_scheduler
from backend.routes.student import dashboard_router

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_database()
    await create_indexes()
    print("✅ Backend server started successfully")
    yield
    # Shutdown
    await close_database_connection()
    print("👋 Backend server shutdown complete")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="AIR Project K - Educational Platform API",
    description="Backend API for the AI-powered educational platform",
    version="2.0.0",
    lifespan=lifespan
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔍 REQUEST DEBUG: {request.method} {request.url}")
    print(f"🔍 REQUEST HEADERS: {dict(request.headers)}")
    if "authorization" in request.headers:
        auth_header = request.headers.get("authorization")
        print(f"🔍 AUTH HEADER: {auth_header[:50]}...")
    else:
        print("❌ NO AUTHORIZATION HEADER FOUND")
    
    response = await call_next(request)
    print(f"🔍 RESPONSE: {response.status_code}")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(practice.router)
app.include_router(tutor.router)
app.include_router(teacher.router)
app.include_router(study_planner.router)
app.include_router(notes.router)
app.include_router(dashboard_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AIR Project K Backend",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AIR Project K Backend",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AIR Project K API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
"""
Pharmyrus V5.0 - Patent Intelligence API
Production-ready FastAPI application for Railway deployment
"""
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Pharmyrus V5.0",
    description="Patent Intelligence API for pharmaceutical patent search",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    """Patent search request model"""
    molecule_name: str = Field(..., description="Molecule name (e.g., 'Darolutamide')")
    brand_name: Optional[str] = Field(None, description="Brand name (optional)")
    target_countries: List[str] = Field(default=["BR"], description="Target countries")
    search_mode: str = Field(default="comprehensive", description="Search mode: quick, standard, comprehensive")

class PatentResult(BaseModel):
    """Individual patent result"""
    publication_number: str
    title: str
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    status: Optional[str] = None
    link: str
    source: str

class SearchResponse(BaseModel):
    """Patent search response model"""
    molecule_info: Dict[str, Any]
    search_strategy: Dict[str, Any]
    summary: Dict[str, Any]
    patents: List[PatentResult]
    comparison: Dict[str, Any]
    execution_time: float
    timestamp: str

# Global state
app_state = {
    "startup_time": datetime.now().isoformat(),
    "total_searches": 0,
    "port": int(os.getenv("PORT", 8000))
}

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    port = app_state["port"]
    logger.info("=" * 60)
    logger.info("🚀 Pharmyrus V5.0 Starting...")
    logger.info(f"   Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Version: 5.0.0")
    logger.info(f"   Timestamp: {app_state['startup_time']}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("=" * 60)
    logger.info("🛑 Pharmyrus V5.0 Shutting down...")
    logger.info(f"   Total searches performed: {app_state['total_searches']}")
    logger.info(f"   Uptime: {datetime.now().isoformat()}")
    logger.info("=" * 60)

# Routes
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Pharmyrus V5.0",
        "version": "5.0.0",
        "description": "Patent Intelligence API for pharmaceutical patent search",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "search": "/api/v5/search",
            "status": "/api/v5/status"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway
    Returns 200 if service is healthy
    """
    return {
        "status": "healthy",
        "version": "5.0.0",
        "timestamp": datetime.now().isoformat(),
        "port": app_state["port"],
        "uptime_seconds": (datetime.now() - datetime.fromisoformat(app_state["startup_time"])).total_seconds(),
        "total_searches": app_state["total_searches"]
    }

@app.get("/api/v5/status")
async def get_status():
    """Get API status and configuration"""
    return {
        "api": {
            "name": "Pharmyrus V5.0",
            "version": "5.0.0",
            "status": "operational",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
        },
        "features": {
            "patent_search": True,
            "multi_source": True,
            "br_patents": True,
            "worldwide_applications": True,
            "detailed_extraction": True
        },
        "limits": {
            "max_molecules_per_request": 1,
            "max_countries": 10,
            "timeout_seconds": 300
        },
        "statistics": {
            "total_searches": app_state["total_searches"],
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(app_state["startup_time"])).total_seconds()
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v5/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest):
    """
    Search for pharmaceutical patents
    
    This endpoint searches multiple sources for patent information:
    - PubChem for molecule synonyms and dev codes
    - Google/SerpAPI for WO patent numbers
    - EPO OPS for worldwide patent families
    - INPI crawler for Brazilian patents
    - Google Patents for detailed patent information
    
    Returns comprehensive patent data including BR patents with full details.
    """
    start_time = time.time()
    app_state["total_searches"] += 1
    
    logger.info(f"🔍 New search request: {request.molecule_name}")
    
    try:
        # TODO: Implement actual patent search logic here
        # For now, returning mock response
        
        result = {
            "molecule_info": {
                "chemical_name": request.molecule_name,
                "brand_name": request.brand_name,
                "target_countries": request.target_countries
            },
            "search_strategy": {
                "mode": request.search_mode,
                "sources": ["PubChem", "Google Patents", "EPO OPS", "INPI"],
                "steps": [
                    "Extract dev codes from PubChem",
                    "Search WO numbers via Google/SerpAPI",
                    "Get worldwide families from EPO",
                    "Extract BR patents",
                    "Fetch detailed info from Google Patents"
                ]
            },
            "summary": {
                "wo_numbers_found": 0,
                "br_patents_found": 0,
                "total_patents": 0
            },
            "patents": [],
            "comparison": {
                "expected": 8,
                "found": 0,
                "match_rate": "0%",
                "status": "⚠️ Not implemented yet"
            },
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Search completed in {result['execution_time']:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/v5/molecules")
async def list_molecules():
    """List available test molecules"""
    return {
        "molecules": [
            {"name": "Darolutamide", "brand": "Nubeqa", "expected_br_patents": 8},
            {"name": "Olaparib", "brand": "Lynparza", "expected_br_patents": 12},
            {"name": "Niraparib", "brand": "Zejula", "expected_br_patents": 10}
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

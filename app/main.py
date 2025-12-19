"""
Pharmyrus V5.0 - Production Patent Intelligence API
Complete implementation with all crawlers and APIs
"""
import os
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.models.patent import SearchRequest, SearchResponse
from app.services.orchestrator import PatentSearchOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Pharmyrus V5.0",
    description="Patent Intelligence API - Complete multi-source search system",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
app_state = {
    "startup_time": datetime.now().isoformat(),
    "total_searches": 0,
    "successful_searches": 0,
    "failed_searches": 0,
    "port": int(os.getenv("PORT", 8000))
}

# Initialize orchestrator
orchestrator = PatentSearchOrchestrator()

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    app_state["failed_searches"] += 1
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup/shutdown
@app.on_event("startup")
async def startup_event():
    port = app_state["port"]
    logger.info("=" * 80)
    logger.info("🚀 Pharmyrus V5.0 PRODUCTION Starting...")
    logger.info(f"   Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Version: 5.0.0")
    logger.info(f"   Timestamp: {app_state['startup_time']}")
    logger.info("   Services: PubChem, Google Patents, INPI, EPO, FDA, PubMed, DrugBank")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 80)
    logger.info("🛑 Pharmyrus V5.0 Shutting down...")
    logger.info(f"   Total searches: {app_state['total_searches']}")
    logger.info(f"   Successful: {app_state['successful_searches']}")
    logger.info(f"   Failed: {app_state['failed_searches']}")
    logger.info("=" * 80)

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Pharmyrus V5.0 - Patent Intelligence API",
        "version": "5.0.0",
        "description": "Complete multi-source pharmaceutical patent search system",
        "status": "operational",
        "services": {
            "molecular_intelligence": ["PubChem", "FDA", "PubMed", "DrugBank"],
            "patent_search": ["Google Patents", "EPO OPS", "INPI"],
            "strategies": ["Multi-query WO discovery", "Family navigation", "Direct BR search"]
        },
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "search": "POST /api/v5/search",
            "status": "/api/v5/status",
            "molecules": "/api/v5/molecules"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check for Railway"""
    uptime = (datetime.now() - datetime.fromisoformat(app_state["startup_time"])).total_seconds()
    
    return {
        "status": "healthy",
        "version": "5.0.0",
        "timestamp": datetime.now().isoformat(),
        "port": app_state["port"],
        "uptime_seconds": uptime,
        "statistics": {
            "total_searches": app_state["total_searches"],
            "successful_searches": app_state["successful_searches"],
            "failed_searches": app_state["failed_searches"],
            "success_rate": f"{(app_state['successful_searches'] / max(1, app_state['total_searches']) * 100):.1f}%"
        }
    }

@app.get("/api/v5/status")
async def get_status():
    """Get API status and configuration"""
    uptime = (datetime.now() - datetime.fromisoformat(app_state["startup_time"])).total_seconds()
    
    return {
        "api": {
            "name": "Pharmyrus V5.0",
            "version": "5.0.0",
            "status": "operational",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "local")
        },
        "services": {
            "pubchem": {"status": "active", "description": "Molecular data extraction"},
            "google_patents": {"status": "active", "description": "WO number discovery + Patent details"},
            "inpi": {"status": "active", "description": "Brazilian patent direct search"},
            "epo_ops": {"status": "active", "description": "Patent family navigation"},
            "fda": {"status": "active", "description": "Regulatory data"},
            "pubmed": {"status": "active", "description": "Scientific literature"},
            "drugbank": {"status": "active", "description": "Drug database"}
        },
        "features": {
            "multi_source_wo_discovery": True,
            "br_patent_extraction": True,
            "patent_classification": True,
            "patent_scoring": True,
            "family_navigation": True,
            "detailed_enrichment": True
        },
        "limits": {
            "max_wo_for_epo": 20,
            "max_wo_for_worldwide": 15,
            "max_dev_codes_search": 10,
            "timeout_seconds": 300
        },
        "statistics": {
            "total_searches": app_state["total_searches"],
            "successful_searches": app_state["successful_searches"],
            "failed_searches": app_state["failed_searches"],
            "uptime_seconds": uptime
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v5/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest):
    """
    🚀 COMPLETE PATENT SEARCH
    
    This endpoint executes a comprehensive multi-layer patent search:
    
    PHASE 1: Molecular Intelligence
    - PubChem: CID, dev codes, CAS, molecular properties
    - FDA: Regulatory approvals, Orange Book data
    - PubMed: Scientific literature count
    - DrugBank: Drug database information
    
    PHASE 2: WO Number Discovery (Multi-strategy)
    - Direct molecule search
    - Brand name search
    - Dev code searches (multiple)
    - Year-based searches (2018-2023)
    
    PHASE 3: BR Patent Extraction (Triple approach)
    - INPI Direct: Brazilian patent office direct search
    - EPO Families: Worldwide patent families via EPO OPS
    - Google Worldwide: Worldwide applications extraction
    
    PHASE 4: Patent Enrichment
    - Full details extraction
    - Patent type classification
    - Relevance scoring
    
    Returns comprehensive BR patent data with full details.
    """
    
    start_time = time.time()
    app_state["total_searches"] += 1
    
    logger.info("=" * 80)
    logger.info(f"🔍 NEW SEARCH REQUEST")
    logger.info(f"   Molecule: {request.molecule_name}")
    logger.info(f"   Brand: {request.brand_name}")
    logger.info(f"   Countries: {request.target_countries}")
    logger.info(f"   Mode: {request.search_mode}")
    logger.info("=" * 80)
    
    try:
        # Execute search via orchestrator
        result = await orchestrator.search(
            molecule_name=request.molecule_name,
            brand_name=request.brand_name,
            target_countries=request.target_countries
        )
        
        app_state["successful_searches"] += 1
        
        execution_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info(f"✅ SEARCH COMPLETED SUCCESSFULLY")
        logger.info(f"   BR Patents Found: {result['summary']['total_br_patents']}")
        logger.info(f"   Execution Time: {execution_time:.2f}s")
        logger.info("=" * 80)
        
        return result
        
    except Exception as e:
        app_state["failed_searches"] += 1
        logger.error(f"❌ Search failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/v5/molecules")
async def list_molecules():
    """List available test molecules with expected results"""
    return {
        "molecules": [
            {
                "name": "Darolutamide",
                "brand": "Nubeqa",
                "cas": "1297538-32-9",
                "dev_codes": ["ODM-201", "BAY-1841788"],
                "expected_br_patents": 8,
                "therapeutic_area": "Prostate cancer"
            },
            {
                "name": "Olaparib",
                "brand": "Lynparza",
                "cas": "763113-22-0",
                "dev_codes": ["AZD2281", "KU-0059436"],
                "expected_br_patents": 12,
                "therapeutic_area": "Ovarian cancer, BRCA mutations"
            },
            {
                "name": "Niraparib",
                "brand": "Zejula",
                "cas": "1038915-60-4",
                "dev_codes": ["MK-4827"],
                "expected_br_patents": 10,
                "therapeutic_area": "Ovarian cancer"
            },
            {
                "name": "Venetoclax",
                "brand": "Venclexta",
                "cas": "1257044-40-8",
                "dev_codes": ["ABT-199", "GDC-0199"],
                "expected_br_patents": 15,
                "therapeutic_area": "Chronic lymphocytic leukemia"
            },
            {
                "name": "Axitinib",
                "brand": "Inlyta",
                "cas": "319460-85-0",
                "dev_codes": ["AG-013736"],
                "expected_br_patents": 8,
                "therapeutic_area": "Renal cell carcinoma"
            }
        ],
        "usage": "Use molecule name in POST /api/v5/search",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v5/test")
async def test_services():
    """Quick test of all services"""
    results = {
        "pubchem": "pending",
        "google_patents": "pending",
        "inpi": "pending",
        "epo": "pending",
        "fda": "pending"
    }
    
    try:
        # Test PubChem
        data = orchestrator.pubchem.get_molecule_data("Aspirin")
        results["pubchem"] = "✅ OK" if data.get('cid') else "❌ FAILED"
    except:
        results["pubchem"] = "❌ ERROR"
    
    try:
        # Test FDA
        data = orchestrator.fda.get_drug_info("Aspirin")
        results["fda"] = "✅ OK" if data.get('found') else "⚠️ NOT FOUND"
    except:
        results["fda"] = "❌ ERROR"
    
    # Note: Other services require API keys or may be rate limited
    results["google_patents"] = "⏭️ SKIPPED (requires API key)"
    results["inpi"] = "⏭️ SKIPPED (external service)"
    results["epo"] = "⏭️ SKIPPED (requires authentication)"
    
    return {
        "test_results": results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

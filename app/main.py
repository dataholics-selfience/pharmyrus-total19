"""
Pharmyrus V5.1 - DEBUG - Simplified Fast Version
"""
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.models.patent import SearchRequest, SearchResponse
from app.services.orchestrator import PatentSearchOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pharmyrus V5.1 DEBUG",
    description="Simplified fast version",
    version="5.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app_state = {
    "startup_time": datetime.now().isoformat(),
    "total_searches": 0,
    "port": int(os.getenv("PORT", 8000))
}

orchestrator = PatentSearchOrchestrator()

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🚀 Pharmyrus V5.1 DEBUG Starting...")
    logger.info(f"   Port: {app_state['port']}")
    logger.info(f"   Mode: SIMPLIFIED FAST")
    logger.info("=" * 60)

@app.get("/")
async def root():
    return {
        "name": "Pharmyrus V5.1 DEBUG",
        "version": "5.1.0",
        "mode": "simplified_fast",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "5.1.0",
        "timestamp": datetime.now().isoformat(),
        "port": app_state["port"],
        "total_searches": app_state["total_searches"]
    }

@app.post("/api/v5/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest):
    """
    SIMPLIFIED SEARCH - Optimized for speed
    
    - PubChem: Dev codes only
    - Google: Aggressive WO search
    - INPI: Limited queries (3 max)
    - Google: BR from WO (5 WOs max)
    
    Target: < 60 seconds
    """
    
    start_time = time.time()
    app_state["total_searches"] += 1
    
    logger.info(f"🔍 SEARCH: {request.molecule_name}")
    
    try:
        result = await orchestrator.search(
            molecule_name=request.molecule_name,
            brand_name=request.brand_name,
            target_countries=request.target_countries
        )
        
        logger.info(f"✅ DONE: {len(result['br_patents'])} BR patents in {time.time() - start_time:.1f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v5/test")
async def test():
    """Quick test"""
    try:
        data = orchestrator.pubchem.get_molecule_data("Aspirin")
        return {
            "pubchem": "✅ OK" if data.get('cid') else "❌ FAILED",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

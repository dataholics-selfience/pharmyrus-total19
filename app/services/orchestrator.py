"""
Orchestrator with DIRECT CRAWLER
No SerpAPI dependency
"""
import logging
import time
from typing import Dict, List
from datetime import datetime

from app.services.pubchem import PubChemService
from app.services.google_crawler import GooglePatentsCrawler
from app.services.inpi import INPIService
from app.models.patent import MoleculeInfo

logger = logging.getLogger(__name__)


class PatentSearchOrchestrator:
    """Orchestrator using direct crawlers"""
    
    def __init__(self):
        self.pubchem = PubChemService()
        self.google_crawler = GooglePatentsCrawler()
        self.inpi = INPIService()
    
    async def search(self, molecule_name: str, brand_name: str = None, target_countries: List[str] = None) -> Dict:
        """
        CRAWLER-BASED SEARCH
        1. PubChem: Dev codes
        2. Google Crawler: WO numbers (direct scraping)
        3. INPI: Direct BR search
        4. Google Crawler: BR from WO families
        5. Google Crawler: Direct BR search
        """
        
        start_time = time.time()
        logger.info("=" * 70)
        logger.info(f"🚀 CRAWLER SEARCH: {molecule_name}")
        logger.info("=" * 70)
        
        # PHASE 1: PubChem
        logger.info("\n📊 PHASE 1: PubChem Intelligence")
        pubchem_data = self.pubchem.get_molecule_data(molecule_name)
        
        molecule_info = MoleculeInfo(
            name=molecule_name,
            brand=brand_name,
            cid=pubchem_data.get('cid'),
            cas=pubchem_data.get('cas'),
            molecular_formula=pubchem_data.get('molecular_formula'),
            molecular_weight=pubchem_data.get('molecular_weight'),
            dev_codes=pubchem_data.get('dev_codes', []),
            synonyms=pubchem_data.get('synonyms', [])[:20]
        )
        
        logger.info(f"  ✅ CID={molecule_info.cid}, {len(molecule_info.dev_codes)} dev codes, CAS={molecule_info.cas}")
        
        # PHASE 2: WO Discovery via Google Crawler
        logger.info("\n🔍 PHASE 2: WO Discovery (Direct Crawler)")
        wo_numbers = self.google_crawler.search_wo_numbers(
            molecule=molecule_name,
            dev_codes=molecule_info.dev_codes[:5],
            brand=brand_name
        )
        
        logger.info(f"  ✅ Found {len(wo_numbers)} WO numbers")
        for i, wo in enumerate(wo_numbers[:10], 1):
            logger.info(f"    {i}. {wo}")
        
        # PHASE 3: BR Patent Collection
        logger.info("\n🇧🇷 PHASE 3: BR Patent Collection")
        
        all_br_patents = {}
        
        # Strategy 1: INPI Direct
        logger.info("  Strategy 1: INPI Direct Search (simplified)")
        inpi_patents = self.inpi.search_patents(
            molecule=molecule_name,
            dev_codes=molecule_info.dev_codes[:2],
            brand=brand_name
        )
        
        for p in inpi_patents:
            pub_num = p['publication_number']
            if pub_num not in all_br_patents:
                all_br_patents[pub_num] = p
        
        logger.info(f"    ✅ INPI: {len(inpi_patents)} BR patents")
        
        # Strategy 2: Google Crawler - BR from WO families
        logger.info("  Strategy 2: Google Crawler - BR from WO Families")
        google_wo_count = 0
        
        for wo in wo_numbers[:10]:  # Process up to 10 WOs
            br_patents = self.google_crawler.get_br_patents_from_wo(wo)
            
            for p in br_patents:
                pub_num = p['publication_number']
                if pub_num not in all_br_patents:
                    all_br_patents[pub_num] = p
                    google_wo_count += 1
            
            time.sleep(0.5)  # Rate limit
        
        logger.info(f"    ✅ Google WO Families: {google_wo_count} BR patents")
        
        # Strategy 3: Google Crawler - Direct BR search
        logger.info("  Strategy 3: Google Crawler - Direct BR Search")
        direct_br_patents = self.google_crawler.search_br_patents_direct(molecule_name)
        
        google_direct_count = 0
        for p in direct_br_patents:
            pub_num = p['publication_number']
            if pub_num not in all_br_patents:
                all_br_patents[pub_num] = p
                google_direct_count += 1
        
        logger.info(f"    ✅ Google Direct: {google_direct_count} BR patents")
        
        # PHASE 4: Enrichment
        logger.info("\n⚡ PHASE 4: Patent Enrichment")
        
        enriched_patents = []
        for pub_num, patent in all_br_patents.items():
            # Try to enrich if missing data
            if not patent.get('title') or len(patent.get('title', '')) < 20:
                details = self.google_crawler.enrich_br_patent(pub_num)
                if details:
                    patent.update(details)
            
            enriched_patents.append(patent)
        
        # Sort by score
        enriched_patents.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"  ✅ Total enriched: {len(enriched_patents)} BR patents")
        
        # Calculate stats
        by_source = {}
        for p in enriched_patents:
            src = p.get('source', 'unknown')
            by_source[src] = by_source.get(src, 0) + 1
        
        execution_time = time.time() - start_time
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ CRAWLER SEARCH COMPLETED")
        logger.info(f"  Total BR patents: {len(enriched_patents)}")
        logger.info(f"  By source: {by_source}")
        logger.info(f"  Execution time: {execution_time:.2f}s")
        logger.info("=" * 70)
        
        return {
            'molecule_info': molecule_info.dict(),
            'search_strategy': {
                'mode': 'direct_crawler',
                'sources': ['PubChem', 'Google Patents Crawler', 'INPI Crawler'],
                'note': 'No SerpAPI - direct HTTP scraping'
            },
            'wo_processing': {
                'total_wo_found': len(wo_numbers),
                'wo_numbers': wo_numbers[:20],
                'wo_processed': min(len(wo_numbers), 10)
            },
            'summary': {
                'total_br_patents': len(enriched_patents),
                'from_inpi': len(inpi_patents),
                'from_google_wo': google_wo_count,
                'from_google_direct': google_direct_count,
                'by_source': by_source
            },
            'br_patents': enriched_patents,
            'all_patents': enriched_patents,
            'comparison': {
                'expected': 8,
                'found': len(enriched_patents),
                'match_rate': f"{min(100, int((len(enriched_patents) / 8) * 100))}%",
                'status': '✅ Excellent' if len(enriched_patents) >= 8 else ('⚠️ Good' if len(enriched_patents) >= 4 else '❌ Low')
            },
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }

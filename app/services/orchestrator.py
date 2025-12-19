"""
Simplified Orchestrator - Fast results focus
"""
import logging
import time
from typing import Dict, List
from datetime import datetime

from app.services.pubchem import PubChemService
from app.services.google_patents import GooglePatentsService
from app.services.inpi import INPIService
from app.models.patent import MoleculeInfo

logger = logging.getLogger(__name__)


class PatentSearchOrchestrator:
    """Simplified orchestrator for fast results"""
    
    def __init__(self):
        self.pubchem = PubChemService()
        self.google = GooglePatentsService()
        self.inpi = INPIService()
    
    async def search(self, molecule_name: str, brand_name: str = None, target_countries: List[str] = None) -> Dict:
        """
        SIMPLIFIED WORKFLOW:
        1. PubChem: Get dev codes
        2. Google: Find WO numbers (aggressive)
        3. INPI: Direct BR search (limited queries)
        4. Google: BR from WO numbers
        """
        
        start_time = time.time()
        logger.info("=" * 60)
        logger.info(f"🚀 FAST SEARCH: {molecule_name}")
        logger.info("=" * 60)
        
        # PHASE 1: PubChem
        logger.info("\n📊 PHASE 1: PubChem")
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
        
        logger.info(f"  ✅ CID={molecule_info.cid}, {len(molecule_info.dev_codes)} dev codes")
        
        # PHASE 2: WO Discovery (Google aggressive)
        logger.info("\n🔍 PHASE 2: WO Discovery (Aggressive Google)")
        wo_numbers = self.google.search_wo_numbers(
            molecule=molecule_name,
            dev_codes=molecule_info.dev_codes[:5],
            brand=brand_name
        )
        
        logger.info(f"  ✅ Found {len(wo_numbers)} WO numbers")
        
        # PHASE 3: BR Patents
        logger.info("\n🇧🇷 PHASE 3: BR Patents")
        
        all_br_patents = {}
        
        # Strategy 1: INPI Direct (simplified - only 3 queries)
        logger.info("  Strategy 1: INPI Direct (simplified)")
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
        
        # Strategy 2: Google BR from WO (limited to 5 WOs)
        logger.info("  Strategy 2: Google BR from WO")
        google_count = 0
        for wo in wo_numbers[:5]:
            br_numbers = self.google.get_br_from_wo(wo)
            
            for br_num in br_numbers:
                if br_num not in all_br_patents:
                    all_br_patents[br_num] = {
                        'publication_number': br_num,
                        'title': f'Found via {wo}',
                        'abstract': '',
                        'assignee': '',
                        'filing_date': '',
                        'patent_type': 'GOOGLE_WO',
                        'link': f'https://patents.google.com/patent/{br_num}',
                        'source': 'google_from_wo',
                        'score': 7
                    }
                    google_count += 1
        
        logger.info(f"    ✅ Google: {google_count} BR patents")
        
        # Sort by score
        br_patents = sorted(all_br_patents.values(), key=lambda x: x.get('score', 0), reverse=True)
        
        execution_time = time.time() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ SEARCH COMPLETED")
        logger.info(f"  Total BR patents: {len(br_patents)}")
        logger.info(f"  Execution time: {execution_time:.2f}s")
        logger.info("=" * 60)
        
        return {
            'molecule_info': molecule_info.dict(),
            'search_strategy': {
                'mode': 'simplified_fast',
                'sources': ['PubChem', 'Google (aggressive)', 'INPI (simplified)'],
                'note': 'Optimized for speed - limited queries to avoid timeout'
            },
            'wo_processing': {
                'total_wo_found': len(wo_numbers),
                'wo_numbers': wo_numbers[:10],
                'wo_processed_for_br': min(len(wo_numbers), 5)
            },
            'summary': {
                'total_br_patents': len(br_patents),
                'from_inpi': len(inpi_patents),
                'from_google': google_count
            },
            'br_patents': br_patents,
            'all_patents': br_patents,
            'comparison': {
                'expected': 8,
                'found': len(br_patents),
                'match_rate': f"{min(100, int((len(br_patents) / 8) * 100))}%",
                'status': '✅ Excellent' if len(br_patents) >= 8 else ('⚠️ Good' if len(br_patents) >= 4 else '❌ Low')
            },
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }

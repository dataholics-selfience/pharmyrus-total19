"""
Patent Search Orchestrator
Coordinates all services in the correct order
"""
import logging
import time
from typing import Dict, List
from datetime import datetime

from app.services.pubchem import PubChemService
from app.services.google_patents import GooglePatentsService
from app.services.inpi import INPIService
from app.services.epo import EPOService
from app.services.fda import FDAService, PubMedService, DrugBankService
from app.models.patent import MoleculeInfo, PatentResult

logger = logging.getLogger(__name__)


class PatentSearchOrchestrator:
    """Main orchestrator for patent search"""
    
    def __init__(self):
        self.pubchem = PubChemService()
        self.google_patents = GooglePatentsService()
        self.inpi = INPIService()
        self.epo = EPOService()
        self.fda = FDAService()
        self.pubmed = PubMedService()
        self.drugbank = DrugBankService()
    
    async def search(self, molecule_name: str, brand_name: str = None, target_countries: List[str] = None) -> Dict:
        """
        Execute complete patent search workflow
        
        PHASE 1: Molecular Intelligence
        - PubChem: Get CID, dev codes, CAS, synonyms
        - FDA: Get regulatory data
        - PubMed: Get literature count
        - DrugBank: Get drug database info
        
        PHASE 2: WO Discovery (Multi-strategy)
        - Google Patents: Search WO numbers
        - Multiple query approaches
        - Year-based searches
        
        PHASE 3: BR Patent Extraction
        - EPO: Get BR from WO families
        - INPI: Direct BR search
        - Google Patents: BR from worldwide apps
        
        PHASE 4: Patent Enrichment
        - Get full details for each BR patent
        - Classification and scoring
        """
        
        start_time = time.time()
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING PATENT SEARCH: {molecule_name}")
        logger.info("=" * 80)
        
        target_countries = target_countries or ["BR"]
        
        # ====================================================================
        # PHASE 1: MOLECULAR INTELLIGENCE
        # ====================================================================
        logger.info("\n📊 PHASE 1: MOLECULAR INTELLIGENCE")
        
        # PubChem - Primary source
        pubchem_data = self.pubchem.get_molecule_data(molecule_name)
        
        molecule_info = MoleculeInfo(
            name=molecule_name,
            brand=brand_name,
            cid=pubchem_data.get('cid'),
            cas=pubchem_data.get('cas'),
            molecular_formula=pubchem_data.get('molecular_formula'),
            molecular_weight=pubchem_data.get('molecular_weight'),
            iupac_name=pubchem_data.get('iupac_name'),
            smiles=pubchem_data.get('smiles'),
            inchi=pubchem_data.get('inchi'),
            inchi_key=pubchem_data.get('inchi_key'),
            dev_codes=pubchem_data.get('dev_codes', []),
            synonyms=pubchem_data.get('synonyms', [])[:50]
        )
        
        # FDA data
        fda_data = self.fda.get_drug_info(molecule_name)
        orange_data = self.fda.get_orange_book_data(molecule_name)
        
        # PubMed
        pubmed_data = self.pubmed.search_literature(molecule_name)
        
        # DrugBank
        drugbank_data = self.drugbank.search_drugbank(molecule_name)
        
        logger.info(f"  ✅ PubChem: CID={molecule_info.cid}, {len(molecule_info.dev_codes)} dev codes")
        logger.info(f"  ✅ FDA: {'Found' if fda_data.get('found') else 'Not found'}")
        logger.info(f"  ✅ PubMed: {pubmed_data.get('total_results', 0)} articles")
        logger.info(f"  ✅ DrugBank: {'Found' if drugbank_data.get('found') else 'Not found'}")
        
        # ====================================================================
        # PHASE 2: WO NUMBER DISCOVERY
        # ====================================================================
        logger.info("\n🔍 PHASE 2: WO NUMBER DISCOVERY")
        
        wo_numbers = self.google_patents.search_wo_numbers(
            molecule=molecule_name,
            dev_codes=molecule_info.dev_codes,
            brand=brand_name
        )
        
        logger.info(f"  ✅ Found {len(wo_numbers)} WO numbers")
        for i, wo in enumerate(wo_numbers[:10], 1):
            logger.info(f"    {i}. {wo}")
        
        # ====================================================================
        # PHASE 3: BR PATENT EXTRACTION
        # ====================================================================
        logger.info("\n🇧🇷 PHASE 3: BR PATENT EXTRACTION")
        
        all_br_patents = {}  # Deduplicate by publication_number
        
        # Strategy 1: INPI Direct Search
        logger.info("  Strategy 1: INPI Direct Search")
        inpi_patents = self.inpi.search_patents(
            molecule=molecule_name,
            dev_codes=molecule_info.dev_codes[:10],
            brand=brand_name
        )
        
        for patent in inpi_patents:
            pub_num = patent['publication_number']
            if pub_num not in all_br_patents:
                all_br_patents[pub_num] = patent
                patent['discovery_method'] = 'inpi_direct'
        
        logger.info(f"    ✅ INPI Direct: {len(inpi_patents)} BR patents")
        
        # Strategy 2: EPO Family Search
        logger.info("  Strategy 2: EPO Family Search")
        epo_count = 0
        for wo in wo_numbers[:20]:  # Limit to 20 WOs for EPO
            br_numbers = self.epo.search_br_patents(wo)
            
            for br_num in br_numbers:
                if br_num not in all_br_patents:
                    # Get details from Google Patents
                    details = self.google_patents.get_patent_details(br_num)
                    if details:
                        details['discovery_method'] = f'epo_from_{wo}'
                        details['patent_type'] = 'EPO_FAMILY'
                        details['score'] = 8
                        all_br_patents[br_num] = details
                        epo_count += 1
            
            time.sleep(1)  # Rate limit
        
        logger.info(f"    ✅ EPO Families: {epo_count} BR patents")
        
        # Strategy 3: Google Patents Worldwide Apps
        logger.info("  Strategy 3: Google Patents Worldwide Applications")
        gp_count = 0
        for wo in wo_numbers[:15]:  # Limit to 15 WOs
            br_numbers = self.google_patents.get_worldwide_applications(wo)
            
            for br_num in br_numbers:
                if br_num not in all_br_patents:
                    details = self.google_patents.get_patent_details(br_num)
                    if details:
                        details['discovery_method'] = f'google_worldwide_{wo}'
                        details['patent_type'] = 'WORLDWIDE_APP'
                        details['score'] = 7
                        all_br_patents[br_num] = details
                        gp_count += 1
            
            time.sleep(1)
        
        logger.info(f"    ✅ Google Worldwide: {gp_count} BR patents")
        
        # ====================================================================
        # PHASE 4: ENRICHMENT & CLASSIFICATION
        # ====================================================================
        logger.info("\n⚡ PHASE 4: ENRICHMENT & CLASSIFICATION")
        
        enriched_patents = []
        
        for pub_num, patent_data in all_br_patents.items():
            # Enrich from INPI if needed
            if not patent_data.get('title') or not patent_data.get('abstract'):
                inpi_details = self.inpi.enrich_br_patent(pub_num)
                if inpi_details:
                    patent_data.update(inpi_details)
            
            # Classify patent type
            patent_data['patent_type'] = self._classify_patent(patent_data)
            
            # Calculate final score
            patent_data['score'] = self._calculate_score(patent_data)
            
            enriched_patents.append(patent_data)
        
        # Sort by score (highest first)
        enriched_patents.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"  ✅ Enriched {len(enriched_patents)} BR patents")
        
        # ====================================================================
        # FINAL RESULTS
        # ====================================================================
        execution_time = time.time() - start_time
        
        # Calculate statistics
        by_type = {}
        by_source = {}
        for p in enriched_patents:
            pt = p.get('patent_type', 'UNKNOWN')
            by_type[pt] = by_type.get(pt, 0) + 1
            
            src = p.get('source', 'unknown')
            by_source[src] = by_source.get(src, 0) + 1
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SEARCH COMPLETED")
        logger.info(f"  Total BR patents: {len(enriched_patents)}")
        logger.info(f"  Execution time: {execution_time:.2f}s")
        logger.info(f"  By type: {by_type}")
        logger.info(f"  By source: {by_source}")
        logger.info("=" * 80)
        
        return {
            'molecule_info': molecule_info.dict(),
            'search_strategy': {
                'mode': 'comprehensive',
                'sources': ['PubChem', 'Google Patents', 'EPO OPS', 'INPI', 'FDA', 'PubMed', 'DrugBank'],
                'wo_discovery_strategies': [
                    'Direct molecule search',
                    'Brand name search',
                    'Dev code searches',
                    'Year-based searches'
                ],
                'br_extraction_strategies': [
                    'INPI direct search',
                    'EPO family navigation',
                    'Google Patents worldwide applications'
                ]
            },
            'wo_processing': {
                'total_wo_found': len(wo_numbers),
                'wo_numbers': wo_numbers[:20],
                'wo_processed': min(len(wo_numbers), 20)
            },
            'summary': {
                'total_br_patents': len(enriched_patents),
                'by_type': by_type,
                'by_source': by_source,
                'by_discovery_method': self._count_discovery_methods(enriched_patents)
            },
            'br_patents': enriched_patents,
            'all_patents': enriched_patents,  # For now, only BR
            'comparison': {
                'expected': 8,
                'found': len(enriched_patents),
                'match_rate': f"{min(100, int((len(enriched_patents) / 8) * 100))}%",
                'status': '✅ Excellent' if len(enriched_patents) >= 8 else '⚠️ Below target'
            },
            'fda_data': fda_data,
            'pubmed_data': pubmed_data,
            'drugbank_data': drugbank_data,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_patent(self, patent_data: Dict) -> str:
        """Classify patent type based on title and abstract"""
        text = f"{patent_data.get('title', '')} {patent_data.get('abstract', '')}".lower()
        
        if 'compound' in text or 'molecule' in text or 'chemical' in text:
            return 'COMPOSITION'
        elif 'crystal' in text or 'polymorph' in text:
            return 'CRYSTALLINE'
        elif 'salt' in text:
            return 'SALT'
        elif 'formulation' in text or 'pharmaceutical composition' in text:
            return 'FORMULATION'
        elif 'process' in text or 'synthesis' in text:
            return 'PROCESS'
        elif 'use' in text or 'treatment' in text:
            return 'MEDICAL_USE'
        elif 'combination' in text:
            return 'COMBINATION'
        else:
            return 'OTHER'
    
    def _calculate_score(self, patent_data: Dict) -> int:
        """Calculate patent relevance score"""
        score = patent_data.get('score', 5)
        
        # Bonus for complete data
        if patent_data.get('title'):
            score += 1
        if patent_data.get('abstract'):
            score += 1
        if patent_data.get('assignee'):
            score += 1
        
        # Bonus for patent type
        pt = patent_data.get('patent_type', '')
        if pt == 'COMPOSITION':
            score += 3
        elif pt in ['CRYSTALLINE', 'SALT', 'FORMULATION']:
            score += 2
        
        return min(score, 15)  # Max score 15
    
    def _count_discovery_methods(self, patents: List[Dict]) -> Dict:
        """Count patents by discovery method"""
        methods = {}
        for p in patents:
            method = p.get('discovery_method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
        return methods

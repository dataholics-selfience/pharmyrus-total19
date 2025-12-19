"""
INPI (Brazilian Patent Office) Crawler
Search Brazilian patents directly
"""
import requests
import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)


class INPIService:
    """INPI crawler integration"""
    
    # Your existing INPI crawler on Railway
    CRAWLER_URL = "https://crawler3-production.up.railway.app/api/data/inpi/patents"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def search_patents(self, molecule: str, dev_codes: List[str] = None, brand: str = None) -> List[Dict]:
        """Search INPI using multiple query strategies"""
        logger.info(f"🔍 INPI: Searching {molecule}")
        
        all_patents = []
        queries = []
        
        # Build query list
        queries.append(molecule)
        if brand:
            queries.append(brand)
        if dev_codes:
            queries.extend(dev_codes[:10])  # Limit to 10 dev codes
        
        # Add variations
        queries.append(molecule.lower())
        queries.append(molecule.upper())
        
        seen_numbers = set()
        
        for query in queries:
            patents = self._search_single_query(query)
            
            for patent in patents:
                num = patent.get('publication_number', '')
                if num and num not in seen_numbers:
                    seen_numbers.add(num)
                    all_patents.append(patent)
            
            time.sleep(2)  # Rate limit - INPI crawler pode ser pesado
        
        logger.info(f"✅ INPI: Found {len(all_patents)} unique BR patents")
        return all_patents
    
    def _search_single_query(self, query: str) -> List[Dict]:
        """Search INPI for a single query"""
        try:
            params = {'medicine': query}
            resp = self.session.get(self.CRAWLER_URL, params=params, timeout=60)
            
            if not resp.ok:
                logger.warning(f"⚠️ INPI query '{query}' failed: {resp.status_code}")
                return []
            
            data = resp.json()
            patents_data = data.get('data', [])
            
            if not patents_data:
                return []
            
            # Transform to standard format
            patents = []
            for p in patents_data:
                if not p.get('title', '').startswith('BR'):
                    continue
                
                patents.append({
                    'publication_number': p.get('title', '').replace(' ', '-'),
                    'title': p.get('applicant', ''),
                    'abstract': (p.get('fullText', '') or '')[:500],
                    'assignee': p.get('applicant', ''),
                    'inventors': [],
                    'filing_date': p.get('depositDate', ''),
                    'publication_date': '',
                    'status': '',
                    'patent_type': 'INPI',
                    'link': f"https://busca.inpi.gov.br/pePI/servlet/PatenteServletController?Action=detail&CodPedido={p.get('title', '')}",
                    'source': 'inpi_crawler',
                    'score': 5
                })
            
            logger.info(f"  INPI query '{query}': {len(patents)} results")
            return patents
            
        except Exception as e:
            logger.error(f"❌ INPI search error for '{query}': {str(e)}")
            return []
    
    def enrich_br_patent(self, patent_number: str) -> Dict:
        """Get detailed information for a specific BR patent"""
        try:
            # Extract clean number (e.g., BR112018068911A2 -> BR112018068911A2)
            clean_num = patent_number.replace('-', '').replace(' ', '')
            
            params = {'medicine': clean_num}
            resp = self.session.get(self.CRAWLER_URL, params=params, timeout=60)
            
            if not resp.ok:
                return {}
            
            data = resp.json()
            patents = data.get('data', [])
            
            if not patents:
                return {}
            
            # Find matching patent
            for p in patents:
                if clean_num in p.get('title', '').replace(' ', ''):
                    return {
                        'title': p.get('applicant', ''),
                        'abstract': p.get('fullText', ''),
                        'filing_date': p.get('depositDate', ''),
                        'assignee': p.get('applicant', '')
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ INPI enrich error for {patent_number}: {str(e)}")
            return {}

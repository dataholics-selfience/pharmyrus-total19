"""
FDA APIs - Orange Book and OpenFDA
Get drug approval and regulatory information
"""
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FDAService:
    """FDA APIs integration"""
    
    OPENFDA_URL = "https://api.fda.gov/drug/ndc.json"
    ORANGEBOOK_URL = "https://api.fda.gov/drug/drugsfda.json"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_drug_info(self, molecule: str) -> Dict:
        """Get drug information from OpenFDA"""
        logger.info(f"🔍 FDA: Searching {molecule}")
        
        result = {
            'found': False,
            'nda_numbers': [],
            'brand_names': [],
            'generic_names': [],
            'approval_dates': [],
            'manufacturers': []
        }
        
        try:
            # Search in NDC database
            params = {
                'search': f'generic_name:"{molecule}"',
                'limit': 10
            }
            
            resp = self.session.get(self.OPENFDA_URL, params=params, timeout=30)
            
            if resp.ok:
                data = resp.json()
                results = data.get('results', [])
                
                if results:
                    result['found'] = True
                    
                    for item in results:
                        # Extract relevant info
                        generic = item.get('generic_name', '')
                        if generic:
                            result['generic_names'].append(generic)
                        
                        brand = item.get('brand_name', '')
                        if brand:
                            result['brand_names'].append(brand)
                        
                        labeler = item.get('labeler_name', '')
                        if labeler:
                            result['manufacturers'].append(labeler)
                    
                    # Deduplicate
                    result['generic_names'] = list(set(result['generic_names']))
                    result['brand_names'] = list(set(result['brand_names']))
                    result['manufacturers'] = list(set(result['manufacturers']))
                    
                    logger.info(f"✅ FDA: Found {len(results)} entries")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ FDA error: {str(e)}")
            return result
    
    def get_orange_book_data(self, molecule: str) -> Dict:
        """Get Orange Book patent and exclusivity data"""
        try:
            params = {
                'search': f'openfda.generic_name:"{molecule}"',
                'limit': 5
            }
            
            resp = self.session.get(self.ORANGEBOOK_URL, params=params, timeout=30)
            
            if resp.ok:
                data = resp.json()
                results = data.get('results', [])
                
                if results:
                    # Extract patent/exclusivity info
                    orange_data = {
                        'applications': [],
                        'patents': [],
                        'exclusivities': []
                    }
                    
                    for item in results:
                        app_num = item.get('application_number', '')
                        if app_num:
                            orange_data['applications'].append(app_num)
                    
                    logger.info(f"✅ Orange Book: Found {len(results)} applications")
                    return orange_data
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Orange Book error: {str(e)}")
            return {}


class PubMedService:
    """PubMed literature search"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_literature(self, molecule: str) -> Dict:
        """Search PubMed for scientific literature"""
        logger.info(f"🔍 PubMed: Searching {molecule}")
        
        try:
            url = f"{self.BASE_URL}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'{molecule} patent',
                'retmode': 'json',
                'retmax': 100
            }
            
            resp = self.session.get(url, params=params, timeout=30)
            
            if resp.ok:
                data = resp.json()
                result = data.get('esearchresult', {})
                count = int(result.get('count', 0))
                pmids = result.get('idlist', [])
                
                logger.info(f"✅ PubMed: Found {count} articles")
                
                return {
                    'total_results': count,
                    'pmids': pmids[:20],  # Top 20
                    'query': result.get('querytranslation', '')
                }
            
            return {'total_results': 0, 'pmids': []}
            
        except Exception as e:
            logger.error(f"❌ PubMed error: {str(e)}")
            return {'total_results': 0, 'pmids': []}


class DrugBankService:
    """DrugBank search via web scraping"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_drugbank(self, molecule: str) -> Dict:
        """Search DrugBank via SerpAPI Google search"""
        logger.info(f"🔍 DrugBank: Searching {molecule}")
        
        try:
            # Use SerpAPI to search DrugBank site
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google',
                'q': f'site:go.drugbank.com {molecule}',
                'api_key': '3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d',
                'num': 5
            }
            
            resp = self.session.get(url, params=params, timeout=30)
            
            if resp.ok:
                data = resp.json()
                results = data.get('organic_results', [])
                
                if results:
                    drugbank_data = {
                        'found': True,
                        'links': [r.get('link', '') for r in results],
                        'snippets': [r.get('snippet', '') for r in results]
                    }
                    
                    logger.info(f"✅ DrugBank: Found {len(results)} entries")
                    return drugbank_data
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"❌ DrugBank error: {str(e)}")
            return {'found': False}

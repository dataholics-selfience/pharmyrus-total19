"""
Google Patents via SerpAPI
Search and extract patent families
"""
import requests
import logging
import time
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class GooglePatentsService:
    """Google Patents integration via SerpAPI"""
    
    # Pool of SerpAPI keys (rotate to avoid limits)
    API_KEYS = [
        "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d",
        "bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc",
        # Add more keys from your pool
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.current_key_index = 0
    
    def _get_api_key(self) -> str:
        """Rotate API keys"""
        key = self.API_KEYS[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.API_KEYS)
        return key
    
    def search_wo_numbers(self, molecule: str, dev_codes: List[str], brand: Optional[str] = None) -> List[str]:
        """Search for WO patent numbers using multiple strategies"""
        logger.info(f"🔍 Google Patents: Searching WO numbers for {molecule}")
        
        wo_numbers = set()
        
        # Strategy 1: Direct molecule search
        wos = self._search_patents(molecule, num_results=20)
        wo_numbers.update(wos)
        
        # Strategy 2: Brand name if available
        if brand:
            wos = self._search_patents(brand, num_results=10)
            wo_numbers.update(wos)
        
        # Strategy 3: Dev codes
        for code in dev_codes[:5]:  # Limit to 5 dev codes
            wos = self._search_patents(code, num_results=10)
            wo_numbers.update(wos)
            time.sleep(1)  # Rate limit
        
        # Strategy 4: Year-based searches
        for year in ['2018', '2019', '2020', '2021', '2022', '2023']:
            query = f"{molecule} patent WO{year}"
            wos = self._search_patents(query, num_results=10)
            wo_numbers.update(wos)
            time.sleep(1)
        
        wo_list = sorted(list(wo_numbers))
        logger.info(f"✅ Google Patents: Found {len(wo_list)} WO numbers")
        return wo_list
    
    def _search_patents(self, query: str, num_results: int = 10) -> List[str]:
        """Search patents and extract WO numbers"""
        try:
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google_patents',
                'q': query,
                'api_key': self._get_api_key(),
                'num': num_results
            }
            
            resp = self.session.get(url, params=params, timeout=30)
            if not resp.ok:
                return []
            
            data = resp.json()
            wo_numbers = []
            
            # Extract from results
            for result in data.get('organic_results', []):
                wo = self._extract_wo_number(result.get('patent_id', ''))
                if wo:
                    wo_numbers.append(wo)
                
                # Also check title and snippet
                text = f"{result.get('title', '')} {result.get('snippet', '')}"
                wos = self._extract_wo_from_text(text)
                wo_numbers.extend(wos)
            
            return list(set(wo_numbers))
            
        except Exception as e:
            logger.error(f"❌ Google Patents search error: {str(e)}")
            return []
    
    def _extract_wo_number(self, patent_id: str) -> Optional[str]:
        """Extract WO number from patent ID"""
        if patent_id.startswith('WO'):
            return patent_id.replace('/', '').replace('-', '')
        return None
    
    def _extract_wo_from_text(self, text: str) -> List[str]:
        """Extract WO numbers from text using regex"""
        pattern = r'WO[\s-]?(\d{4})[\s/]?(\d{6})'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"WO{year}{num}" for year, num in matches]
    
    def get_patent_details(self, patent_id: str) -> Optional[Dict]:
        """Get detailed patent information"""
        try:
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google_patents_details',
                'patent_id': patent_id,
                'api_key': self._get_api_key()
            }
            
            resp = self.session.get(url, params=params, timeout=30)
            if not resp.ok:
                return None
            
            data = resp.json()
            return {
                'publication_number': patent_id,
                'title': data.get('title', ''),
                'abstract': data.get('abstract', ''),
                'assignee': data.get('assignee', ''),
                'inventors': data.get('inventors', []),
                'filing_date': data.get('filing_date', ''),
                'publication_date': data.get('publication_date', ''),
                'status': data.get('legal_status', ''),
                'link': data.get('url', f'https://patents.google.com/patent/{patent_id}'),
                'source': 'google_patents'
            }
            
        except Exception as e:
            logger.error(f"❌ Patent details error for {patent_id}: {str(e)}")
            return None
    
    def get_worldwide_applications(self, wo_number: str) -> List[str]:
        """Get worldwide patent family applications"""
        try:
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google_patents',
                'q': wo_number,
                'api_key': self._get_api_key(),
                'num': 1
            }
            
            resp = self.session.get(url, params=params, timeout=30)
            if not resp.ok:
                return []
            
            data = resp.json()
            
            # Get serpapi_link for worldwide apps
            results = data.get('organic_results', [])
            if not results:
                return []
            
            serpapi_link = results[0].get('serpapi_link')
            if not serpapi_link:
                return []
            
            # Fetch worldwide applications
            resp2 = self.session.get(serpapi_link, timeout=30)
            if not resp2.ok:
                return []
            
            details = resp2.json()
            worldwide = details.get('worldwide_applications', {})
            
            # Extract BR patents
            br_patents = []
            for year, apps in worldwide.items():
                if not isinstance(apps, list):
                    continue
                for app in apps:
                    doc_id = app.get('document_id', '')
                    if doc_id.startswith('BR'):
                        br_patents.append(doc_id)
            
            return br_patents
            
        except Exception as e:
            logger.error(f"❌ Worldwide apps error for {wo_number}: {str(e)}")
            return []

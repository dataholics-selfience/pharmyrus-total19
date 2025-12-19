"""
Google Patents - AGGRESSIVE VERSION
Uses Google Search instead of Google Patents engine for better WO discovery
"""
import requests
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class GooglePatentsService:
    """Aggressive Google search for WO numbers"""
    
    API_KEY = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_wo_numbers(self, molecule: str, dev_codes: List[str], brand: str = None) -> List[str]:
        """Aggressive WO number search using Google"""
        logger.info(f"🔍 Google: AGGRESSIVE WO search for {molecule}")
        
        wo_numbers = set()
        
        # Strategy 1: Direct Google search for "molecule patent WO"
        queries = [
            f"{molecule} patent WO",
            f"{molecule} WO patent application",
            f'"{molecule}" patent number WO',
        ]
        
        if brand:
            queries.append(f"{brand} patent WO")
        
        # Add dev codes
        for code in dev_codes[:3]:
            queries.append(f"{code} patent WO")
        
        # Execute searches
        for query in queries:
            wos = self._google_search(query)
            wo_numbers.update(wos)
            if len(wo_numbers) >= 10:
                break
        
        wo_list = sorted(list(wo_numbers))
        logger.info(f"✅ Google: Found {len(wo_list)} WO numbers")
        for wo in wo_list[:5]:
            logger.info(f"   - {wo}")
        
        return wo_list
    
    def _google_search(self, query: str) -> List[str]:
        """Search Google and extract WO numbers from results"""
        try:
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google',
                'q': query,
                'api_key': self.API_KEY,
                'num': 10
            }
            
            resp = self.session.get(url, params=params, timeout=20)
            if not resp.ok:
                logger.warning(f"Google search failed: {resp.status_code}")
                return []
            
            data = resp.json()
            
            # Extract WO numbers from all text
            wo_numbers = []
            
            for result in data.get('organic_results', []):
                text = f"{result.get('title', '')} {result.get('snippet', '')} {result.get('link', '')}"
                wos = self._extract_wo_from_text(text)
                wo_numbers.extend(wos)
            
            # Also check related searches
            for related in data.get('related_searches', []):
                text = related.get('query', '')
                wos = self._extract_wo_from_text(text)
                wo_numbers.extend(wos)
            
            return list(set(wo_numbers))
            
        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return []
    
    def _extract_wo_from_text(self, text: str) -> List[str]:
        """Extract WO numbers using regex"""
        pattern = r'WO[\s-]?(\d{4})[\s/\-]?(\d{6,7})'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"WO{year}{num}" for year, num in matches]
    
    def get_br_from_wo(self, wo_number: str) -> List[str]:
        """Try to find BR patents for a WO number"""
        try:
            # Search "WO number BR patent"
            query = f"{wo_number} BR patent"
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google',
                'q': query,
                'api_key': self.API_KEY,
                'num': 10
            }
            
            resp = self.session.get(url, params=params, timeout=20)
            if not resp.ok:
                return []
            
            data = resp.json()
            
            # Extract BR numbers
            br_numbers = []
            for result in data.get('organic_results', []):
                text = f"{result.get('title', '')} {result.get('snippet', '')}"
                brs = self._extract_br_from_text(text)
                br_numbers.extend(brs)
            
            return list(set(br_numbers))
            
        except:
            return []
    
    def _extract_br_from_text(self, text: str) -> List[str]:
        """Extract BR patent numbers"""
        pattern = r'BR\s?(\d{12,13}[A-Z]\d?)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"BR{num}" for num in matches]

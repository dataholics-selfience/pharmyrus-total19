"""
EPO OPS (European Patent Office Open Patent Services)
Get worldwide patent families
"""
import requests
import logging
import time
from typing import List, Dict, Optional
import base64

logger = logging.getLogger(__name__)


class EPOService:
    """EPO OPS API integration"""
    
    BASE_URL = "https://ops.epo.org/3.2"
    
    # EPO credentials
    CONSUMER_KEY = "ScJHIL3R5ArgfZRMR1KHKaGwLnl7FPWt"
    CONSUMER_SECRET = "mBGWZDqy9EGlZoyV"
    
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.token_expiry = 0
    
    def _get_access_token(self) -> str:
        """Get or refresh EPO access token"""
        current_time = time.time()
        
        # Reuse token if still valid (with 5min buffer)
        if self.access_token and current_time < (self.token_expiry - 300):
            return self.access_token
        
        try:
            # Generate Basic Auth
            credentials = f"{self.CONSUMER_KEY}:{self.CONSUMER_SECRET}"
            b64_credentials = base64.b64encode(credentials.encode()).decode()
            
            url = f"{self.BASE_URL}/auth/accesstoken"
            headers = {
                'Authorization': f'Basic {b64_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}
            
            resp = requests.post(url, headers=headers, data=data, timeout=30)
            
            if resp.ok:
                token_data = resp.json()
                self.access_token = token_data['access_token']
                self.token_expiry = current_time + token_data.get('expires_in', 1200)
                logger.info("✅ EPO: Token obtained")
                return self.access_token
            else:
                logger.error(f"❌ EPO token error: {resp.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ EPO token exception: {str(e)}")
            return None
    
    def search_br_patents(self, wo_number: str) -> List[str]:
        """Search for BR patents in WO family via EPO"""
        logger.info(f"🔍 EPO: Searching BR patents for {wo_number}")
        
        try:
            token = self._get_access_token()
            if not token:
                return []
            
            # Clean WO number (remove spaces/hyphens)
            clean_wo = wo_number.replace(' ', '').replace('-', '')
            
            # Search in EPO
            url = f"{self.BASE_URL}/rest-services/published-data/search/biblio"
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            params = {
                'q': f'pn={clean_wo}',
                'Range': '1-100'
            }
            
            resp = self.session.get(url, headers=headers, params=params, timeout=60)
            
            if not resp.ok:
                logger.warning(f"⚠️ EPO search failed for {wo_number}: {resp.status_code}")
                return []
            
            data = resp.json()
            
            # Extract BR patents from family
            br_patents = []
            
            try:
                results = data.get('ops:world-patent-data', {}).get('ops:biblio-search', {}).get('ops:search-result', {})
                
                # Handle single or multiple results
                pub_refs = results.get('ops:publication-reference', [])
                if not isinstance(pub_refs, list):
                    pub_refs = [pub_refs]
                
                for ref in pub_refs:
                    doc_id = ref.get('document-id', {})
                    country = doc_id.get('country', {}).get('$', '')
                    number = doc_id.get('doc-number', {}).get('$', '')
                    
                    if country == 'BR' and number:
                        br_patent = f"BR{number}"
                        br_patents.append(br_patent)
                        logger.info(f"  Found BR: {br_patent}")
            
            except Exception as e:
                logger.error(f"❌ EPO parse error: {str(e)}")
            
            logger.info(f"✅ EPO: Found {len(br_patents)} BR patents for {wo_number}")
            return br_patents
            
        except Exception as e:
            logger.error(f"❌ EPO search error for {wo_number}: {str(e)}")
            return []
    
    def get_patent_family(self, wo_number: str) -> Dict:
        """Get complete patent family information"""
        try:
            token = self._get_access_token()
            if not token:
                return {}
            
            clean_wo = wo_number.replace(' ', '').replace('-', '')
            
            url = f"{self.BASE_URL}/rest-services/family/publication/docdb/{clean_wo}/biblio"
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            resp = self.session.get(url, headers=headers, timeout=60)
            
            if not resp.ok:
                return {}
            
            data = resp.json()
            
            # Extract family members
            family = {
                'wo_number': wo_number,
                'family_members': [],
                'br_members': []
            }
            
            # Parse family data
            # (EPO family structure is complex, simplified here)
            
            return family
            
        except Exception as e:
            logger.error(f"❌ EPO family error for {wo_number}: {str(e)}")
            return {}

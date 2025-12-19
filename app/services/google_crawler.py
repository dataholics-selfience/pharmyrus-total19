"""
Google Patents Direct Crawler
NO SerpAPI - direct HTTP requests to patents.google.com
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)


class GooglePatentsCrawler:
    """Direct crawler for patents.google.com"""
    
    BASE_URL = "https://patents.google.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def search_wo_numbers(self, molecule: str, dev_codes: List[str] = None, brand: str = None) -> List[str]:
        """
        Search Google Patents directly for WO numbers
        Uses multiple query strategies
        """
        logger.info(f"🔍 Google Patents Crawler: Searching {molecule}")
        
        wo_numbers = set()
        
        # Build search queries
        queries = [
            molecule,
            f"{molecule} patent",
            f"{molecule} pharmaceutical"
        ]
        
        if brand:
            queries.append(brand)
        
        if dev_codes:
            queries.extend(dev_codes[:3])  # Top 3 dev codes
        
        # Execute searches
        for query in queries[:5]:  # Max 5 queries
            logger.info(f"  Searching: {query}")
            wos = self._search_patents(query)
            wo_numbers.update(wos)
            
            if len(wo_numbers) >= 15:
                break
            
            time.sleep(1)  # Rate limit
        
        wo_list = sorted(list(wo_numbers))
        logger.info(f"✅ Found {len(wo_list)} WO numbers")
        
        return wo_list
    
    def _search_patents(self, query: str) -> List[str]:
        """Search Google Patents and extract WO numbers"""
        try:
            # Google Patents search URL
            url = f"{self.BASE_URL}/"
            params = {
                'q': query,
                'oq': query
            }
            
            resp = self.session.get(url, params=params, timeout=20)
            
            if not resp.ok:
                logger.warning(f"Search failed: {resp.status_code}")
                return []
            
            # Parse HTML
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            wo_numbers = []
            
            # Strategy 1: Find all links to patent pages
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Extract WO from URLs like /patent/WO2011104180A1
                if '/patent/WO' in href:
                    wo_match = re.search(r'/patent/(WO\d{4}\d+)', href)
                    if wo_match:
                        wo_numbers.append(wo_match.group(1)[:13])  # WO + year + 6 digits
            
            # Strategy 2: Find WO numbers in text content
            text = soup.get_text()
            wo_pattern = r'WO[\s-]?(\d{4})[\s/\-]?(\d{6,7})'
            matches = re.findall(wo_pattern, text)
            for year, num in matches:
                wo_numbers.append(f"WO{year}{num[:6]}")
            
            # Deduplicate
            return list(set(wo_numbers))
            
        except Exception as e:
            logger.error(f"Search error for '{query}': {str(e)}")
            return []
    
    def get_br_patents_from_wo(self, wo_number: str) -> List[Dict]:
        """
        Get BR patents from a WO patent family
        Scrapes the patent page directly
        """
        try:
            logger.info(f"  Crawling WO: {wo_number}")
            
            # Clean WO number
            clean_wo = wo_number.replace(' ', '').replace('-', '')
            
            # Google Patents URL
            url = f"{self.BASE_URL}/patent/{clean_wo}"
            
            resp = self.session.get(url, timeout=20)
            
            if not resp.ok:
                return []
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            br_patents = []
            
            # Look for patent family section
            # Google Patents shows family members in various sections
            
            # Strategy 1: Find all links with BR prefix
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/patent/BR' in href:
                    br_match = re.search(r'/patent/(BR\d+[A-Z]\d?)', href)
                    if br_match:
                        br_num = br_match.group(1)
                        
                        # Get title from link text or nearby text
                        title = link.get_text(strip=True) or 'Patent family member'
                        
                        br_patents.append({
                            'publication_number': br_num,
                            'title': title[:200],
                            'abstract': '',
                            'assignee': '',
                            'filing_date': '',
                            'patent_type': 'FAMILY_MEMBER',
                            'link': f"{self.BASE_URL}/patent/{br_num}",
                            'source': f'google_crawler_wo_{wo_number}',
                            'score': 8
                        })
            
            # Strategy 2: Look for BR in text content
            text = soup.get_text()
            br_pattern = r'BR[\s-]?(\d{12,13}[A-Z]\d?)'
            matches = re.findall(br_pattern, text)
            
            for match in matches:
                br_num = f"BR{match}"
                
                # Check if not already added
                if not any(p['publication_number'] == br_num for p in br_patents):
                    br_patents.append({
                        'publication_number': br_num,
                        'title': f'Found in {wo_number} family',
                        'abstract': '',
                        'assignee': '',
                        'filing_date': '',
                        'patent_type': 'FAMILY_MEMBER',
                        'link': f"{self.BASE_URL}/patent/{br_num}",
                        'source': f'google_crawler_wo_{wo_number}',
                        'score': 7
                    })
            
            if br_patents:
                logger.info(f"    ✅ Found {len(br_patents)} BR patents")
            
            return br_patents
            
        except Exception as e:
            logger.error(f"Error crawling {wo_number}: {str(e)}")
            return []
    
    def search_br_patents_direct(self, molecule: str) -> List[Dict]:
        """
        Direct search for BR patents (without WO)
        Search: "molecule BR patent"
        """
        try:
            logger.info(f"  Direct BR search: {molecule}")
            
            url = f"{self.BASE_URL}/"
            params = {
                'q': f'{molecule} BR',
                'country': 'BR'
            }
            
            resp = self.session.get(url, params=params, timeout=20)
            
            if not resp.ok:
                return []
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            br_patents = []
            
            # Find all BR patent links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/patent/BR' in href:
                    br_match = re.search(r'/patent/(BR\d+[A-Z]\d?)', href)
                    if br_match:
                        br_num = br_match.group(1)
                        title = link.get_text(strip=True) or 'BR Patent'
                        
                        br_patents.append({
                            'publication_number': br_num,
                            'title': title[:200],
                            'abstract': '',
                            'assignee': '',
                            'filing_date': '',
                            'patent_type': 'DIRECT_SEARCH',
                            'link': f"{self.BASE_URL}/patent/{br_num}",
                            'source': 'google_crawler_direct',
                            'score': 9
                        })
            
            # Deduplicate
            seen = set()
            unique_patents = []
            for p in br_patents:
                if p['publication_number'] not in seen:
                    seen.add(p['publication_number'])
                    unique_patents.append(p)
            
            logger.info(f"    ✅ Direct search: {len(unique_patents)} BR patents")
            
            return unique_patents
            
        except Exception as e:
            logger.error(f"Direct BR search error: {str(e)}")
            return []
    
    def enrich_br_patent(self, br_number: str) -> Dict:
        """
        Get detailed information for a BR patent
        Scrapes the patent detail page
        """
        try:
            url = f"{self.BASE_URL}/patent/{br_number}"
            
            resp = self.session.get(url, timeout=20)
            
            if not resp.ok:
                return {}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Extract details from page
            title = ''
            abstract = ''
            assignee = ''
            filing_date = ''
            
            # Try to find title
            title_elem = soup.find('meta', {'name': 'DC.title'})
            if title_elem:
                title = title_elem.get('content', '')
            
            # Try to find abstract
            abstract_elem = soup.find('meta', {'name': 'DC.description'})
            if abstract_elem:
                abstract = abstract_elem.get('content', '')[:500]
            
            # Try to find assignee
            assignee_elem = soup.find('dd', {'itemprop': 'assigneeCurrent'})
            if assignee_elem:
                assignee = assignee_elem.get_text(strip=True)
            
            return {
                'title': title,
                'abstract': abstract,
                'assignee': assignee,
                'filing_date': filing_date
            }
            
        except Exception as e:
            logger.error(f"Enrich error for {br_number}: {str(e)}")
            return {}

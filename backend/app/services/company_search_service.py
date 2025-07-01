import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from dataclasses import dataclass

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    """Information about a company"""
    name: str
    ticker: str
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    available_documents: int = 0
    latest_filing_date: Optional[str] = None

class CompanySearchService:
    """
    Service for searching companies and their available documents
    """
    
    def __init__(self):
        self.search_client = SearchClient(
            endpoint=settings.search_endpoint,
            index_name=settings.search_index,
            credential=AzureKeyCredential(settings.search_admin_key)
        )
        
        self.company_mappings = {
            'apple': 'AAPL',
            'apple inc': 'AAPL',
            'apple computer': 'AAPL',
            'apple inc.': 'AAPL',
            'microsoft': 'MSFT',
            'microsoft corp': 'MSFT',
            'microsoft corporation': 'MSFT',
            'amazon': 'AMZN',
            'amazon.com': 'AMZN',
            'amazon inc': 'AMZN',
            'amazon.com inc': 'AMZN',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'alphabet inc': 'GOOGL',
            'alphabet inc.': 'GOOGL',
            'tesla': 'TSLA',
            'tesla inc': 'TSLA',
            'tesla motors': 'TSLA',
            'tesla inc.': 'TSLA',
            'facebook': 'META',
            'meta': 'META',
            'meta platforms': 'META',
            'meta platforms inc': 'META',
            'nvidia': 'NVDA',
            'nvidia corp': 'NVDA',
            'nvidia corporation': 'NVDA',
            'netflix': 'NFLX',
            'oracle': 'ORCL',
            'oracle corp': 'ORCL',
            'oracle corporation': 'ORCL',
            'salesforce': 'CRM',
            'salesforce.com': 'CRM',
            'adobe': 'ADBE',
            'adobe inc': 'ADBE',
            'adobe systems': 'ADBE',
            'intel': 'INTC',
            'intel corp': 'INTC',
            'intel corporation': 'INTC',
            'ibm': 'IBM',
            'international business machines': 'IBM',
            'cisco': 'CSCO',
            'cisco systems': 'CSCO',
            'paypal': 'PYPL',
            'paypal holdings': 'PYPL',
            'citigroup': 'C',
            'citi': 'C',
            'citibank': 'C',
            'citicorp': 'C'
        }
    
    async def search_companies(self, query: str) -> List[CompanyInfo]:
        """
        Search for companies by name or ticker
        """
        try:
            logger.info(f"Searching for companies with query: {query}")
            
            companies = await self._search_indexed_companies(query)
            
            if not companies:
                companies = await self._search_fallback_mapping(query)
            
            return companies
            
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []
    
    async def _search_indexed_companies(self, query: str) -> List[CompanyInfo]:
        """
        Search for companies in the existing search index
        """
        try:
            search_results = self.search_client.search(
                search_text=f"company:{query}*",
                select=["company", "source", "filing_date", "document_type"],
                top=50
            )
            
            company_stats = {}
            for result in search_results:
                company_name = result.get("company", "Unknown")
                if company_name and company_name != "Unknown":
                    if company_name not in company_stats:
                        company_stats[company_name] = {
                            "document_count": 0,
                            "latest_date": None
                        }
                    
                    company_stats[company_name]["document_count"] += 1
                    
                    filing_date = result.get("filing_date")
                    if filing_date:
                        if (company_stats[company_name]["latest_date"] is None or 
                            filing_date > company_stats[company_name]["latest_date"]):
                            company_stats[company_name]["latest_date"] = filing_date
            
            companies = []
            for company_name, stats in company_stats.items():
                ticker = self._extract_ticker(company_name)
                
                companies.append(CompanyInfo(
                    name=company_name,
                    ticker=ticker or company_name.upper(),
                    available_documents=stats["document_count"],
                    latest_filing_date=stats["latest_date"]
                ))
            
            return companies
            
        except Exception as e:
            logger.error(f"Error searching indexed companies: {e}")
            return []
    
    async def _search_fallback_mapping(self, query: str) -> List[CompanyInfo]:
        """
        Search using fallback company mappings
        """
        query_lower = query.lower().strip()
        
        if query_lower in self.company_mappings:
            ticker = self.company_mappings[query_lower]
            company_name = self._get_company_name_from_ticker(ticker)
            
            return [CompanyInfo(
                name=company_name,
                ticker=ticker,
                available_documents=0,
                latest_filing_date=None
            )]
        
        return []
    
    def _extract_ticker(self, company_name: str) -> Optional[str]:
        """
        Extract ticker symbol from company name
        """
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(ticker_pattern, company_name)
        
        if matches:
            return matches[-1]  # Return the last match
        
        company_lower = company_name.lower()
        for name, ticker in self.company_mappings.items():
            if name in company_lower or company_lower in name:
                return ticker
        
        return None
    
    def _get_company_name_from_ticker(self, ticker: str) -> str:
        """
        Get company name from ticker symbol
        """
        ticker_to_name = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'NFLX': 'Netflix Inc.',
            'ORCL': 'Oracle Corporation',
            'CRM': 'Salesforce Inc.',
            'ADBE': 'Adobe Inc.',
            'INTC': 'Intel Corporation',
            'IBM': 'International Business Machines Corporation',
            'CSCO': 'Cisco Systems Inc.',
            'PYPL': 'PayPal Holdings Inc.',
            'C': 'Citigroup Inc.'
        }
        
        return ticker_to_name.get(ticker, f"{ticker} Inc.")
    
    async def search_sec_filings(self, company: str, document_types: List[str], years: List[int]) -> List[Dict[str, Any]]:
        """
        Search for SEC filings based on company, document types, and years
        """
        try:
            logger.info(f"Searching SEC filings for {company}, types: {document_types}, years: {years}")
            
            cik = self._get_company_cik(company)
            if not cik:
                logger.warning(f"CIK not found for company: {company}")
                return []
            
            filings = []
            company_name = self._get_company_name_from_ticker(self._extract_ticker(company) or company)
            
            for doc_type in document_types:
                for year in years:
                    filing = {
                        "id": f"{cik}_{doc_type.replace('/', '_')}_{year}",
                        "company": company_name,
                        "title": f"{doc_type} - {self._get_document_title(doc_type)} for {year}",
                        "document_type": doc_type,
                        "filing_date": self._get_filing_date(doc_type, year),
                        "cik": cik,
                        "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/mock-{doc_type.lower().replace('/', '-')}-{year}.htm"
                    }
                    filings.append(filing)
            
            return filings
            
        except Exception as e:
            logger.error(f"Error searching SEC filings for {company}: {e}")
            return []
    
    def _get_company_cik(self, company: str) -> Optional[str]:
        """Get CIK for a company based on name or ticker"""
        company_upper = company.upper().strip()
        
        # CIK mapping for major companies
        cik_map = {
            'AAPL': '320193', 'APPLE': '320193', 'APPLE INC': '320193',
            'MSFT': '789019', 'MICROSOFT': '789019', 'MICROSOFT CORPORATION': '789019',
            'AMZN': '1018724', 'AMAZON': '1018724', 'AMAZON.COM': '1018724',
            'GOOGL': '1652044', 'GOOGLE': '1652044', 'ALPHABET': '1652044',
            'TSLA': '1318605', 'TESLA': '1318605', 'TESLA INC': '1318605',
            'META': '1326801', 'FACEBOOK': '1326801', 'META PLATFORMS': '1326801',
            'NVDA': '1045810', 'NVIDIA': '1045810', 'NVIDIA CORPORATION': '1045810',
            'C': '831001', 'CITI': '831001', 'CITIGROUP': '831001', 'CITIBANK': '831001',
            'JPM': '19617', 'JPMORGAN': '19617', 'JPMORGAN CHASE': '19617'
        }
        
        if company_upper in cik_map:
            return cik_map[company_upper]
        
        for key, cik in cik_map.items():
            if key in company_upper or company_upper in key:
                return cik
        
        return None
    
    def _get_document_title(self, doc_type: str) -> str:
        """Get descriptive title for document type"""
        titles = {
            '10-K': 'Annual Report',
            '10-Q': 'Quarterly Report', 
            '8-K': 'Current Report',
            '10-K/A': 'Annual Report Amendment',
            '10-Q/A': 'Quarterly Report Amendment',
            'DEF 14A': 'Proxy Statement',
            '20-F': 'Foreign Annual Report'
        }
        return titles.get(doc_type, 'SEC Filing')
    
    def _get_filing_date(self, doc_type: str, year: int) -> str:
        """Get typical filing date for document type and year"""
        if doc_type == '10-K':
            return f"{year}-12-31"
        elif doc_type == '10-Q':
            return f"{year}-03-31"
        elif doc_type == '8-K':
            return f"{year}-06-15"
        elif doc_type in ['10-K/A', '10-Q/A']:
            return f"{year}-01-15"
        elif doc_type == 'DEF 14A':
            return f"{year}-04-30"
        elif doc_type == '20-F':
            return f"{year}-12-31"
        else:
            return f"{year}-12-31"

    async def get_company_documents(self, company_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get documents for a specific company
        """
        try:
            search_results = self.search_client.search(
                search_text=f"company:\"{company_name}\"",
                select=["id", "content", "source", "company", "filing_date", "document_type", "chunk_id"],
                top=limit,
                order_by=["filing_date desc"]
            )
            
            documents = []
            for result in search_results:
                documents.append({
                    "id": result.get("id"),
                    "content": result.get("content", "")[:500] + "..." if len(result.get("content", "")) > 500 else result.get("content", ""),
                    "source": result.get("source"),
                    "company": result.get("company"),
                    "filing_date": result.get("filing_date"),
                    "document_type": result.get("document_type"),
                    "chunk_id": result.get("chunk_id")
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting company documents: {e}")
            return []

    async def search_website_content(self, company_or_url: str) -> List[Dict[str, Any]]:
        """
        Search for website content related to a company or URL
        """
        try:
            logger.info(f"Searching website content for: {company_or_url}")
            
            is_url = self._is_url(company_or_url)
            
            if is_url:
                domain = self._extract_domain(company_or_url)
                company_name = self._get_company_from_domain(domain)
                
                results = await self._mock_website_search(company_or_url, company_name)
            else:
                company_name = company_or_url
                website_url = self._get_company_website(company_name)
                results = await self._mock_website_search(website_url, company_name)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching website content: {e}")
            return []
    
    def _is_url(self, text: str) -> bool:
        """Check if text looks like a URL"""
        return text.startswith(('http://', 'https://')) or '.' in text and ' ' not in text
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return url.lower()
    
    def _get_company_from_domain(self, domain: str) -> str:
        """Get company name from domain"""
        domain_to_company = {
            'apple.com': 'Apple Inc.',
            'microsoft.com': 'Microsoft Corporation',
            'amazon.com': 'Amazon.com Inc.',
            'google.com': 'Alphabet Inc.',
            'tesla.com': 'Tesla Inc.',
            'meta.com': 'Meta Platforms Inc.',
            'facebook.com': 'Meta Platforms Inc.',
            'nvidia.com': 'NVIDIA Corporation',
            'netflix.com': 'Netflix Inc.',
            'oracle.com': 'Oracle Corporation',
            'salesforce.com': 'Salesforce Inc.',
            'adobe.com': 'Adobe Inc.',
            'intel.com': 'Intel Corporation',
            'ibm.com': 'International Business Machines Corporation',
            'cisco.com': 'Cisco Systems Inc.',
            'paypal.com': 'PayPal Holdings Inc.',
            'citigroup.com': 'Citigroup Inc.',
            'citi.com': 'Citigroup Inc.'
        }
        
        for known_domain, company in domain_to_company.items():
            if known_domain in domain:
                return company
        
        domain_parts = domain.replace('www.', '').split('.')
        if domain_parts:
            return domain_parts[0].title() + ' Inc.'
        
        return domain.title()
    
    def _get_company_website(self, company_name: str) -> str:
        """Get website URL for a company"""
        company_websites = {
            'apple': 'https://www.apple.com',
            'apple inc': 'https://www.apple.com',
            'microsoft': 'https://www.microsoft.com',
            'microsoft corporation': 'https://www.microsoft.com',
            'amazon': 'https://www.amazon.com',
            'amazon.com': 'https://www.amazon.com',
            'google': 'https://www.google.com',
            'alphabet': 'https://www.google.com',
            'tesla': 'https://www.tesla.com',
            'tesla inc': 'https://www.tesla.com',
            'meta': 'https://www.meta.com',
            'facebook': 'https://www.meta.com',
            'nvidia': 'https://www.nvidia.com',
            'netflix': 'https://www.netflix.com',
            'oracle': 'https://www.oracle.com',
            'salesforce': 'https://www.salesforce.com',
            'adobe': 'https://www.adobe.com',
            'intel': 'https://www.intel.com',
            'ibm': 'https://www.ibm.com',
            'cisco': 'https://www.cisco.com',
            'paypal': 'https://www.paypal.com',
            'citigroup': 'https://www.citigroup.com',
            'citi': 'https://www.citi.com'
        }
        
        company_lower = company_name.lower().strip()
        for key, url in company_websites.items():
            if key in company_lower or company_lower in key:
                return url
        
        return f"https://www.{company_name.lower().replace(' ', '').replace('.', '').replace(',', '')}.com"
    
    async def _mock_website_search(self, url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Mock website search results - in production this would crawl/search actual websites
        """
        mock_results = [
            {
                "id": f"web_{company_name.lower().replace(' ', '_')}_about",
                "title": f"About {company_name}",
                "url": f"{url}/about",
                "content": f"Learn more about {company_name}, our mission, values, and leadership team.",
                "company": company_name,
                "document_type": "Website Content",
                "source": "website",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": f"web_{company_name.lower().replace(' ', '_')}_investor",
                "title": f"{company_name} - Investor Relations",
                "url": f"{url}/investor-relations",
                "content": f"Access {company_name}'s financial reports, earnings calls, and investor information.",
                "company": company_name,
                "document_type": "Website Content",
                "source": "website",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": f"web_{company_name.lower().replace(' ', '_')}_news",
                "title": f"{company_name} - Latest News",
                "url": f"{url}/news",
                "content": f"Stay updated with the latest news and announcements from {company_name}.",
                "company": company_name,
                "document_type": "Website Content",
                "source": "website",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        return mock_results

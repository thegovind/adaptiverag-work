from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel
import logging

from ..services.company_search_service import CompanySearchService

logger = logging.getLogger(__name__)

router = APIRouter()

class CompanySearchRequest(BaseModel):
    query: str

class EnhancedSearchRequest(BaseModel):
    company: str
    searchType: Literal["company", "website"]
    documentTypes: Optional[List[str]] = None
    years: Optional[List[int]] = None

class SECFilingSearchRequest(BaseModel):
    company: str
    document_types: List[str]
    years: List[int]

class CompanySearchResponse(BaseModel):
    companies: List[Dict[str, Any]]

class CompanyDocumentsResponse(BaseModel):
    company: str
    documents: List[Dict[str, Any]]
    total_count: int

class SECFilingSearchResponse(BaseModel):
    status: str
    documents: List[Dict[str, Any]]
    message: Optional[str] = None

class EnhancedSearchResponse(BaseModel):
    status: str
    documents: List[Dict[str, Any]]
    searchType: str
    message: Optional[str] = None

@router.post("/search", response_model=EnhancedSearchResponse)
async def enhanced_search(request: EnhancedSearchRequest):
    """
    Enhanced search for both company documents and website content
    """
    try:
        service = CompanySearchService()
        
        if request.searchType == "company":
            if not request.documentTypes or not request.years:
                raise HTTPException(
                    status_code=400, 
                    detail="Document types and years are required for company search"
                )
            
            documents = await service.search_sec_filings(
                company=request.company,
                document_types=request.documentTypes,
                years=request.years
            )
            message = f"Found {len(documents)} SEC filings for {request.company}"
            
        elif request.searchType == "website":
            documents = await service.search_website_content(
                company_or_url=request.company
            )
            message = f"Found {len(documents)} website results for {request.company}"
            
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        return EnhancedSearchResponse(
            status="success",
            documents=documents,
            searchType=request.searchType,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/search/legacy", response_model=SECFilingSearchResponse)
async def search_sec_filings(request: SECFilingSearchRequest):
    """
    Legacy endpoint for SEC filings search (backwards compatibility)
    """
    try:
        service = CompanySearchService()
        documents = await service.search_sec_filings(
            company=request.company,
            document_types=request.document_types,
            years=request.years
        )
        
        return SECFilingSearchResponse(
            status="success",
            documents=documents,
            message=f"Found {len(documents)} documents for {request.company}"
        )
        
    except Exception as e:
        logger.error(f"Error searching SEC filings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search SEC filings: {str(e)}")

@router.post("/companies/search", response_model=CompanySearchResponse)
async def search_companies(request: CompanySearchRequest):
    """
    Search for companies by name or ticker symbol
    """
    try:
        service = CompanySearchService()
        companies = await service.search_companies(request.query)
        
        companies_data = []
        for company in companies:
            companies_data.append({
                "name": company.name,
                "ticker": company.ticker,
                "industry": company.industry,
                "description": company.description,
                "website": company.website,
                "available_documents": company.available_documents,
                "latest_filing_date": company.latest_filing_date
            })
        
        return CompanySearchResponse(companies=companies_data)
        
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search companies: {str(e)}")

@router.get("/documents/{company_name}", response_model=CompanyDocumentsResponse)
async def get_company_documents(
    company_name: str,
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Get documents for a specific company
    """
    try:
        service = CompanySearchService()
        documents = await service.get_company_documents(company_name, limit)
        
        return CompanyDocumentsResponse(
            company=company_name,
            documents=documents,
            total_count=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Error getting company documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get company documents: {str(e)}")

@router.get("/suggestions")
async def get_company_suggestions(q: str = Query(..., min_length=2)):
    """
    Get company name suggestions for autocomplete
    """
    try:
        service = CompanySearchService()
        companies = await service.search_companies(q)
        
        suggestions = []
        for company in companies[:10]:  # Limit to 10 suggestions
            suggestions.append({
                "name": company.name,
                "ticker": company.ticker,
                "document_count": company.available_documents
            })
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting company suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

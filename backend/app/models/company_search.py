from pydantic import BaseModel
from typing import List, Optional

class CompanySearchRequest(BaseModel):
    company: str
    document_types: List[str]
    years: List[int]

class CompanySearchResponse(BaseModel):
    status: str
    documents: List[dict]
    message: Optional[str] = None

class CompanyDocument(BaseModel):
    id: str
    company: str
    title: str
    document_type: str
    filing_date: str
    cik: str
    url: Optional[str] = None

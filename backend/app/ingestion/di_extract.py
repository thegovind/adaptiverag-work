from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from pathlib import Path
import json
from ..core.config import settings

async def extract_pdf_content(file_path: Path) -> dict:
    try:
        client = DocumentIntelligenceClient(
            settings.document_intel_account_url,
            AzureKeyCredential(settings.document_intel_key)
        )
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        poller = client.begin_analyze_document("prebuilt-layout", file_bytes)
        result = poller.result()
        
        return result.to_dict()
    except Exception as e:
        return {"content": f"Error extracting content: {str(e)}"}

async def extract_html_content(file_path: Path) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return {"content": text}
    except Exception as e:
        return {"content": f"Error extracting content: {str(e)}"}

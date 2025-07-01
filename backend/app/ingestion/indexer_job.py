from typing import List, Dict
import asyncio
import logging
from ..core.config import settings
from ..services.azure_services import get_azure_service_manager

logger = logging.getLogger(__name__)

async def create_search_index():
    """
    Create or update the search index - uses the new Azure Service Manager
    """
    try:
        azure_service = await get_azure_service_manager()
        result = await azure_service.ensure_search_index_exists()
        
        if result:
            logger.info("Search index created/updated successfully")
            return {"status": "success", "message": "Index created/updated"}
        else:
            logger.error("Failed to create/update search index")
            return {"status": "error", "message": "Failed to create index"}
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        return {"status": "error", "message": str(e)}

async def upsert_chunks(chunks: List[Dict]):
    """
    Upload chunks to Azure Search with enhanced logging and error handling
    Now uses the centralized Azure Service Manager
    """
    try:
        if not chunks:
            logger.warning("No chunks provided for upload")
            return
        
        logger.info(f"Starting upload of {len(chunks)} chunks using Azure Service Manager")
        
        # Use the centralized Azure Service Manager
        azure_service = await get_azure_service_manager()
        result = await azure_service.add_documents_to_index(chunks)
        
        if result:
            logger.info(f"Successfully uploaded {len(chunks)} chunks to search index")
        else:
            logger.error(f"Failed to upload chunks to search index")
            
        return result
        
    except Exception as e:
        logger.error(f"Critical error during chunk upload: {str(e)}")
        raise

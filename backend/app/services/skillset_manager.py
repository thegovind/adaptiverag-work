import logging
from typing import Dict, Any, Optional
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerSkillset,
    SearchIndexerSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexer,
    FieldMapping,
    OutputFieldMappingEntry as IndexerOutputFieldMapping
)
from azure.core.credentials import AzureKeyCredential
from ..core.config import settings

logger = logging.getLogger(__name__)

class SkillsetManager:
    """
    Manages Azure Search skillsets with Document Layout skill integration
    """
    
    def __init__(self):
        self.indexer_client = SearchIndexerClient(
            endpoint=settings.search_endpoint,
            credential=AzureKeyCredential(settings.search_admin_key)
        )
    
    async def create_document_layout_skillset(self, skillset_name: str = "document-layout-skillset") -> Optional[SearchIndexerSkillset]:
        """
        Create a skillset with Document Layout skill for enhanced document processing
        """
        try:
            document_layout_skill = SearchIndexerSkill(
                odata_type="#Microsoft.Skills.Vision.DocumentIntelligenceLayoutSkill",
                name="DocumentLayoutSkill",
                description="Extract text, tables, and structure from documents using Document Intelligence Layout model",
                context="/document",
                inputs=[
                    InputFieldMappingEntry(
                        name="file_data",
                        source="/document/file_data"
                    )
                ],
                outputs=[
                    OutputFieldMappingEntry(
                        name="content",
                        target_name="layoutContent"
                    ),
                    OutputFieldMappingEntry(
                        name="pages",
                        target_name="layoutPages"
                    ),
                    OutputFieldMappingEntry(
                        name="chunks",
                        target_name="layoutChunks"
                    ),
                    OutputFieldMappingEntry(
                        name="tables",
                        target_name="layoutTables"
                    ),
                    OutputFieldMappingEntry(
                        name="images",
                        target_name="layoutImages"
                    )
                ]
            )
            
            skillset = SearchIndexerSkillset(
                name=skillset_name,
                description="Skillset for processing financial documents with Document Layout skill",
                skills=[document_layout_skill],
                cognitive_services_account=None  # Using resource-based billing
            )
            
            result = self.indexer_client.create_or_update_skillset(skillset)
            logger.info(f"Created/updated skillset: {result.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating Document Layout skillset: {e}")
            return None
    
    async def create_blob_data_source(
        self, 
        data_source_name: str = "documents-datasource",
        container_name: str = "documents"
    ) -> Optional[SearchIndexerDataSourceConnection]:
        """
        Create a data source pointing to Azure Blob Storage for document processing
        """
        try:
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={settings.azure_storage_account_name};AccountKey={{STORAGE_KEY_PLACEHOLDER}};EndpointSuffix=core.windows.net"
            
            data_container = SearchIndexerDataContainer(
                name=container_name,
                query=None  # Process all files in container
            )
            
            data_source = SearchIndexerDataSourceConnection(
                name=data_source_name,
                description="Data source for financial documents in blob storage",
                type="azureblob",
                connection_string=connection_string,
                container=data_container
            )
            
            result = self.indexer_client.create_or_update_data_source(data_source)
            logger.info(f"Created/updated data source: {result.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating blob data source: {e}")
            return None
    
    async def create_document_indexer(
        self,
        indexer_name: str = "documents-indexer",
        data_source_name: str = "documents-datasource",
        skillset_name: str = "document-layout-skillset",
        target_index_name: str = None
    ) -> Optional[SearchIndexer]:
        """
        Create an indexer that uses the Document Layout skillset to process documents
        """
        try:
            if not target_index_name:
                target_index_name = settings.search_index
            
            field_mappings = [
                FieldMapping(
                    source_field_name="metadata_storage_name",
                    target_field_name="source"
                ),
                FieldMapping(
                    source_field_name="metadata_storage_path",
                    target_field_name="id",
                    mapping_function=None
                )
            ]
            
            output_field_mappings = [
                IndexerOutputFieldMapping(
                    source_field_name="/document/layoutContent",
                    target_field_name="content"
                ),
                IndexerOutputFieldMapping(
                    source_field_name="/document/layoutChunks",
                    target_field_name="chunks"
                ),
                IndexerOutputFieldMapping(
                    source_field_name="/document/layoutPages",
                    target_field_name="pages"
                ),
                IndexerOutputFieldMapping(
                    source_field_name="/document/layoutTables",
                    target_field_name="tables"
                ),
                IndexerOutputFieldMapping(
                    source_field_name="/document/layoutImages",
                    target_field_name="images"
                )
            ]
            
            indexer = SearchIndexer(
                name=indexer_name,
                description="Indexer for processing financial documents with Document Layout skill",
                data_source_name=data_source_name,
                target_index_name=target_index_name,
                skillset_name=skillset_name,
                field_mappings=field_mappings,
                output_field_mappings=output_field_mappings,
                is_disabled=False,
                schedule=None  # Run on-demand for now
            )
            
            result = self.indexer_client.create_or_update_indexer(indexer)
            logger.info(f"Created/updated indexer: {result.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating document indexer: {e}")
            return None
    
    async def run_indexer(self, indexer_name: str = "documents-indexer") -> bool:
        """
        Run the document indexer to process documents
        """
        try:
            self.indexer_client.run_indexer(indexer_name)
            logger.info(f"Started indexer run: {indexer_name}")
            return True
        except Exception as e:
            logger.error(f"Error running indexer: {e}")
            return False
    
    async def get_indexer_status(self, indexer_name: str = "documents-indexer") -> Optional[Dict[str, Any]]:
        """
        Get the status of the document indexer
        """
        try:
            status = self.indexer_client.get_indexer_status(indexer_name)
            return {
                "name": status.name,
                "status": status.status,
                "last_result": {
                    "status": status.last_result.status if status.last_result else None,
                    "error_message": status.last_result.error_message if status.last_result else None,
                    "start_time": status.last_result.start_time if status.last_result else None,
                    "end_time": status.last_result.end_time if status.last_result else None,
                    "item_count": status.last_result.item_count if status.last_result else 0,
                    "failed_item_count": status.last_result.failed_item_count if status.last_result else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting indexer status: {e}")
            return None
    
    async def setup_complete_pipeline(self) -> Dict[str, bool]:
        """
        Set up the complete Document Layout skill pipeline
        """
        results = {
            "skillset_created": False,
            "data_source_created": False,
            "indexer_created": False
        }
        
        try:
            skillset = await self.create_document_layout_skillset()
            results["skillset_created"] = skillset is not None
            
            data_source = await self.create_blob_data_source()
            results["data_source_created"] = data_source is not None
            
            indexer = await self.create_document_indexer()
            results["indexer_created"] = indexer is not None
            
            logger.info(f"Pipeline setup results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error setting up complete pipeline: {e}")
            return results

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)
from azure.core.credentials import AzureKeyCredential
from typing import List, Dict
import asyncio
from ..core.config import settings

async def create_search_index():
    index_client = SearchIndexClient(
        endpoint=settings.search_endpoint,
        credential=AzureKeyCredential(settings.search_admin_key)
    )
    
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="company", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="year", type=SearchFieldDataType.Int32, filterable=True, facetable=True),
    ]
    
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="hnsw-config")
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )
    
    semantic_config = SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    index = SearchIndex(
        name=settings.search_index,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"Created/updated index: {result.name}")
        return result
    except Exception as e:
        print(f"Error creating index: {e}")
        return None

async def upsert_chunks(chunks: List[Dict]):
    search_client = SearchClient(
        endpoint=settings.search_endpoint,
        index_name=settings.search_index,
        credential=AzureKeyCredential(settings.search_admin_key)
    )
    
    try:
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            result = search_client.upload_documents(documents=batch)
            print(f"Uploaded batch {i//batch_size + 1}: {len(batch)} documents")
            await asyncio.sleep(0.1)
        
        print(f"Successfully uploaded {len(chunks)} chunks to search index")
    except Exception as e:
        print(f"Error uploading chunks: {e}")

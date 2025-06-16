from semantic_kernel.functions import kernel_function
from typing import Annotated, List, Dict
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
from ..core.config import settings

class SearchTools:
    def __init__(self):
        self.search_client = SearchClient(
            endpoint=settings.search_endpoint,
            index_name=settings.search_index,
            credential=AzureKeyCredential(settings.search_admin_key)
        )
    
    @kernel_function(
        description="Search for documents in the 10-K filings knowledge base",
        name="search_documents"
    )
    async def search_documents(
        self,
        query: Annotated[str, "The search query for finding relevant documents"],
        top: Annotated[int, "Number of documents to retrieve"] = 10
    ) -> Annotated[str, "Search results with document content and metadata"]:
        """Search for documents using Azure AI Search with semantic ranking"""
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name="multimodal-rag-1750033945665-semantic-configuration",
                query_caption="extractive|highlight-false",
                semantic_query=query
            )
            
            documents = []
            for result in results:
                documents.append({
                    "content": result.get("content_text", ""),
                    "title": result.get("document_title", ""),
                    "source": result.get("content_path", ""),
                    "score": result.get("@search.score", 0),
                    "reranker_score": result.get("@search.reranker_score", 0)
                })
            
            formatted_results = []
            for i, doc in enumerate(documents, 1):
                formatted_results.append(
                    f"Document {i}: {doc['title']}\n"
                    f"Content: {doc['content'][:500]}...\n"
                    f"Source: {doc['source']}\n"
                    f"Relevance Score: {doc.get('reranker_score', doc['score']):.3f}\n"
                )
            
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Search error: {str(e)}"

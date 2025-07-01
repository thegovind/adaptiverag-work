"""
Azure AI Agents Service for Deep Research
Based on the Azure AI Agents sample for deep research functionality
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from app.core.config import settings
from app.services.token_usage_tracker import token_tracker, ServiceType, OperationType

logger = logging.getLogger(__name__)

class AzureAIAgentsService:
    """Azure AI Agents service for deep research functionality"""
    
    def __init__(self):
        self.project_client = None
        self.agents_client = None
        
    async def initialize(self):
        """Initialize the Azure AI Agents service"""
        try:
            from .azure_ai_project_service import azure_ai_project_service
            await azure_ai_project_service.initialize()
            
            self.project_client = azure_ai_project_service.get_project_client()
            self.agents_client = self.project_client.agents
            logger.info("Azure AI Agents service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Agents service: {e}")
            raise
    
    async def process_deep_research(self, 
                                  question: str, 
                                  session_id: str,
                                  tracking_id: Optional[str] = None) -> Dict[str, Any]:
        """Process deep research using Azure AI Agents"""
        try:
            logger.info(f"Processing deep research question: {question}")
            
            agent = await self.agents_client.create_agent(
                model="gpt-4",
                name="Deep Research Agent",
                instructions="You are a deep research assistant. Provide comprehensive, well-sourced answers with citations."
            )
            
            thread = await self.agents_client.create_thread()
            
            await self.agents_client.create_message(
                thread_id=thread.id,
                role="user",
                content=question
            )
            
            run = await self.agents_client.create_run(
                thread_id=thread.id,
                assistant_id=agent.id
            )
            
            completed_run = await self.agents_client.get_run(
                thread_id=thread.id,
                run_id=run.id
            )
            
            messages = await self.agents_client.list_messages(thread_id=thread.id)
            answer = messages.data[0].content[0].text.value if messages.data else "No response generated"
            
            token_usage = self._extract_token_usage_from_run(completed_run)
            
            if tracking_id:
                token_tracker.record_token_usage(
                    record_id=tracking_id,
                    prompt_tokens=token_usage.get("prompt_tokens", 0),
                    completion_tokens=token_usage.get("completion_tokens", 0),
                    success=True
                )
            
            return {
                "answer": answer,
                "citations": [],  # Extract from agent response
                "query_rewrites": [question],
                "token_usage": token_usage,
                "success": True,
                "retrieval_method": "azure_ai_agents_deep_research"
            }
            
        except Exception as e:
            logger.error(f"Deep research processing failed: {e}")
            if tracking_id:
                token_tracker.record_token_usage(
                    record_id=tracking_id,
                    prompt_tokens=0,
                    completion_tokens=0,
                    success=False,
                    error_message=str(e)
                )
            return {
                "answer": f"Error in Deep Research processing: {str(e)}",
                "citations": [],
                "query_rewrites": [],
                "token_usage": {"total_tokens": 0, "error": str(e)},
                "success": False
            }
    
    def _extract_token_usage_from_run(self, run: Any) -> Dict[str, int]:
        """Extract token usage from agent run"""
        try:
            if hasattr(run, 'usage'):
                usage = run.usage
                return {
                    "prompt_tokens": getattr(usage, 'prompt_tokens', 0),
                    "completion_tokens": getattr(usage, 'completion_tokens', 0),
                    "total_tokens": getattr(usage, 'total_tokens', 0)
                }
        except Exception as e:
            logger.warning(f"Could not extract token usage from run: {e}")
        
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

# Global instance
azure_ai_agents_service = AzureAIAgentsService()

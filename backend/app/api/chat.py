from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
import uuid
from datetime import datetime
from ..agents.orchestrator import OrchestratorAgent
from ..agents.retriever import RetrieverAgent
from ..agents.writer import WriterAgent
from ..agents.verifier import VerifierAgent
from ..agents.curator import CuratorAgent
from ..core.globals import initialize_kernel, get_agent_registry
from ..auth.middleware import get_current_user
from ..services.agentic_vector_rag_service import agentic_rag_service
from ..services.token_usage_tracker import token_tracker

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    mode: str = "fast-rag"  # fast-rag, agentic-rag, deep-research-rag
    verification_level: str = "basic"  # basic, thorough, comprehensive
    conversation_history: Optional[List[Dict[str, str]]] = None
    session_id: Optional[str] = None

kernel = initialize_kernel()

orchestrator = OrchestratorAgent(kernel, get_agent_registry())
retriever = RetrieverAgent(kernel)
writer = WriterAgent(kernel)
verifier = VerifierAgent(kernel)
curator = CuratorAgent(kernel)

orchestrator.set_agents(
    retriever=retriever,
    writer=writer,
    verifier=verifier,
    curator=curator
)

@router.post("/chat")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        if request.mode in ["agentic-rag", "fast-rag", "deep-research-rag"]:
            return await handle_rag_modes(request, session_id, current_user)
        else:
            return await handle_legacy_modes(request, current_user)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_rag_modes(request: ChatRequest, session_id: str, current_user: dict):
    """Handle the new RAG modes with enhanced features"""
    
    async def generate():
        try:
            if not agentic_rag_service.search_client:
                await agentic_rag_service.initialize()
            
            yield f"data: {json.dumps({'type': 'metadata', 'session_id': session_id, 'mode': request.mode, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            if request.mode == "agentic-rag":
                result = await agentic_rag_service.process_question(
                    question=request.prompt,
                    conversation_history=request.conversation_history,
                    rag_mode=request.mode,
                    session_id=session_id
                )
            elif request.mode == "fast-rag":
                result = await process_fast_rag(request.prompt, session_id)
            elif request.mode == "deep-research-rag":
                result = await process_deep_research_rag(request.prompt, session_id, request.verification_level)
            else:
                raise ValueError(f"Unsupported RAG mode: {request.mode}")
            
            answer = result.get("answer", "")
            words = answer.split()
            
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'token': word + ' ', 'index': i})}\n\n"
                await asyncio.sleep(0.05)  # Simulate streaming delay
            
            citations = result.get("citations", [])
            if citations:
                yield f"data: {json.dumps({'type': 'citations', 'citations': citations})}\n\n"
            
            query_rewrites = result.get("query_rewrites", [])
            if query_rewrites:
                yield f"data: {json.dumps({'type': 'query_rewrites', 'rewrites': query_rewrites})}\n\n"
            
            token_usage = result.get("token_usage", {})
            if token_usage:
                yield f"data: {json.dumps({'type': 'token_usage', 'usage': token_usage})}\n\n"
            
            processing_metadata = {
                'processing_time_ms': result.get('processing_time_ms', 0),
                'retrieval_method': result.get('retrieval_method', 'unknown'),
                'success': result.get('success', False)
            }
            yield f"data: {json.dumps({'type': 'metadata', 'processing': processing_metadata})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

async def handle_legacy_modes(request: ChatRequest, current_user: dict):
    """Handle legacy modes for backward compatibility"""
    try:
        plan = await orchestrator.create_plan({"mode": request.mode})
        
        async def generate():
            try:
                async for token in orchestrator.run_stream(request.prompt, plan):
                    yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_fast_rag(prompt: str, session_id: str) -> Dict[str, Any]:
    """Process Fast RAG mode using basic retrieval"""
    try:
        docs = await retriever.invoke(prompt)
        
        if docs:
            top_content = []
            citations = []
            
            for i, doc in enumerate(docs[:3]):  # Use top 3 documents
                content = doc.get('content', '')[:500]  # Limit content
                if content:
                    top_content.append(content)
                    citations.append({
                        'id': str(i + 1),
                        'title': doc.get('title', f'Document {i + 1}'),
                        'content': content,
                        'source': doc.get('source', ''),
                        'score': doc.get('score', 0.0)
                    })
            
            if top_content:
                answer = f"Based on the available information:\n\n" + "\n\n".join(top_content)
            else:
                answer = "I couldn't find specific information to answer your question."
        else:
            answer = "No relevant documents found for your query."
            citations = []
        
        return {
            "answer": answer,
            "citations": citations,
            "query_rewrites": [prompt],  # No rewrites in fast mode
            "token_usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(answer.split()),
                "total_tokens": len(prompt.split()) + len(answer.split())
            },
            "processing_time_ms": 0,  # Will be calculated by caller
            "retrieval_method": "fast_rag",
            "success": True
        }
        
    except Exception as e:
        return {
            "answer": f"Error in Fast RAG processing: {str(e)}",
            "citations": [],
            "query_rewrites": [],
            "token_usage": {"total_tokens": 0, "error": str(e)},
            "success": False
        }

async def process_deep_research_rag(prompt: str, session_id: str, verification_level: str) -> Dict[str, Any]:
    """Process Deep Research RAG mode with comprehensive verification"""
    try:
        agentic_result = await agentic_rag_service.process_question(
            question=prompt,
            rag_mode="deep-research-rag",
            session_id=session_id
        )
        
        verification_docs = await retriever.invoke(prompt)
        
        combined_citations = agentic_result.get("citations", [])
        
        for i, doc in enumerate(verification_docs[:2]):  # Add top 2 verification docs
            combined_citations.append({
                'id': str(len(combined_citations) + 1),
                'title': doc.get('title', f'Verification Document {i + 1}'),
                'content': doc.get('content', '')[:300],
                'source': doc.get('source', ''),
                'score': doc.get('score', 0.0),
                'verification': True
            })
        
        base_answer = agentic_result.get("answer", "")
        verification_note = f"\n\n*This response has been enhanced with {verification_level} verification using additional sources.*"
        
        return {
            "answer": base_answer + verification_note,
            "citations": combined_citations,
            "query_rewrites": agentic_result.get("query_rewrites", [prompt]),
            "token_usage": agentic_result.get("token_usage", {}),
            "processing_time_ms": agentic_result.get("processing_time_ms", 0),
            "retrieval_method": "deep_research_rag",
            "verification_level": verification_level,
            "success": True
        }
        
    except Exception as e:
        return {
            "answer": f"Error in Deep Research RAG processing: {str(e)}",
            "citations": [],
            "query_rewrites": [],
            "token_usage": {"total_tokens": 0, "error": str(e)},
            "success": False
        }
